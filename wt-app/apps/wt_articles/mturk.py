#!/usr/bin/env python

import uuid
from datetime import datetime

from boto.mturk.connection import MTurkConnection
from boto.mturk.question import Question, QuestionForm, QuestionContent, ExternalQuestion
from boto.mturk.question import AnswerSpecification, FreeTextAnswer, SelectionAnswer
from boto.mturk.question import Overview
#from boto.mturk.qualification import Qualifications, PercentAssignmentsAbandonedRequirement
#from boto.mturk.qualification import Requirement

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from pyango_view import str2img

from wt_articles.models import TranslationRequest, MTurkTranslatedSentence
from wt_articles.models import SourceArticle, SourceSentence
from wt_articles import MECHANICAL_TURK
from wt_languages.models import TARGET_LANGUAGE
from wt_languages.models import SOURCE_LANGUAGE

from mturk_manager.workflow import task_from_object, load_task_config, get_connection
from mturk_manager.workflow import TASKCONFIG_DEFAULT, DEFAULT_RETVAL
from mturk_manager.models import TaskConfig, TaskAttribute, HITItem
from mturk_manager.models import PENDING, ASSIGNABLE, IN_PROGRESS
from mturk_manager.models import HIT_ATTR_TASK_PAGE


############
# Settings #
############

DEFAULT_TASK_PAGE_SIZE = 4
DEFAULT_IMAGE_DIR = '/Users/jd/Desktop/pydjango_view'
DEFAULT_WEB_PATH = '/site_media/pydjango_view'
DEFAULT_PYDJANGO_WIDTH = 350
DEFAULT_IMAGE_HOST = 'http://j2labs.net'


###########################################
# Functions not required by mturk_manager #
###########################################

def handle_translation_request(trans_req, taskconfig_name=TASKCONFIG_DEFAULT):
    """
    handle_translation_request is an entry point from the management
    command 'translate_mturk'. It takes a Translation Request and breaks
    it into mturk hits representing the request parameters.
    """
    article = trans_req.article
    language = trans_req.target_language
    print 'Translate %s to %s' % (article.title, language)

    # the task config must exist already. not sure how to
    # handle this yet
    task_config = load_task_config(taskconfig_name)

    task_item = task_from_object(trans_req.article)
    task_item.name = 'Translate %s' % article.title
    task_item.config = task_config
    task_item.save()

    # Attach knowledge of target language
    task_attr = TaskAttribute(task_item=task_item,
                              key=TARGET_LANGUAGE,
                              value=language)
    task_attr.save()


def _gen_text_image(sentence, output_path):
    """
    dunno
    """
    web_path = DEFAULT_WEB_PATH
    width = DEFAULT_PYDJANGO_WIDTH
    extension = 'png'
    output = '%s/%s.%s' % (output_path, sentence.id, extension)
    dataurl = '%s/%s.%s' % (web_path, sentence.id, extension)
    retval = str2img(sentence.text,
                     #font='Nafees',
                     output=output,
                     width=width)
    data = {
        'type': 'image',
        'subtype': extension,
        'file_path': output,
        'dataurl': dataurl,
        'width': width,
        'sentence': sentence.text,
    }
    return data

def _gen_overview():
    overview_title = 'Translate these sentences'
    overview_content = """<p>Your task is to translate the Spanish sentences into English.  Please make sure that your English translation:</p>
<ul>
    <li>Is faithful to the original in both meaning and style</li>
    <li>Is grammatical, fluent, and natural-sounding English</li>
    <li>Does not add or delete information from the original text</li>
    <li>Does not contain any spelling errors</li>
</ul>
<p>When creating your translation, please follow these guidelines:</p>
<ul>
    <li><b>Do not use any machine translation systems (like transle.google.com)</b></li>
</ul>
"""

    overview = Overview()
    overview.append('Title', overview_title)
    overview.append('FormattedContent', overview_content)
    
    return overview

def assignment_has_answer(assignmentitem, segment_id):
    assignments = MTurkTranslatedSentence.objects.filter(
        assignment=assignmentitem
    ).filter(
        segment_id=segment_id
    )
    return len(assignments) == 1


#############################
# Required by mturk_manager #
#############################

### PENDING_FUNCTIONS

def task_to_pages(task_item, retval=DEFAULT_RETVAL):
    """
    This is a bootstrapping function, meaning it puts a totally new
    retval in motion. It returns a list of lists represending pages
    of lists of sentences
    """
    source_article = task_item.content_object
    source_sentences = source_article.sourcesentence_set.all()
    page_map = []
    for i in xrange(0, len(source_sentences), DEFAULT_TASK_PAGE_SIZE):
        page_sentences = source_sentences[i:(i+DEFAULT_TASK_PAGE_SIZE)]
        page_map.append(page_sentences)
    return page_map
    
def prepare_media(task_item, retval=DEFAULT_RETVAL):
    """
    Works on the output of task_to_pages to create relevant media.
    Returns a list of lists of dictionary's. Each dictionary represents
    the source sentence AND now all the new information gathered from
    calling _gen_text_image(...)
    """
    text_to_image = lambda sentence: _gen_text_image(sentence, DEFAULT_IMAGE_DIR)
    results = [map(text_to_image, page) for page in retval]
    return results

def generate_question_forms(task_item, retval=DEFAULT_RETVAL):
    """
    Works on the output of prepare_media by generating a QuestionForm
    for each page in retval. Returns a list of QuestionForm instances.
    """
    pages = retval
    task_config = task_item.config
    overview = _gen_overview()

    retval = []
    for page in pages:
    
        qf = QuestionForm()
        qf.append(overview)

        for s in page:
            qc = QuestionContent()
            binary_content = {'type': s['type'],
                              'subtype': s['subtype'],
                              'dataurl': '%s%s' % (DEFAULT_IMAGE_HOST, s['dataurl']),
                              #'alttext': s['sentence']}
                              'alttext': 'no cheating!'}
            qc.append('Binary', binary_content)
            fta = FreeTextAnswer()
            ansp = AnswerSpecification(fta)
            q = Question(identifier=str(uuid.uuid4()),
                         content=qc,
                         answer_spec=ansp)
            qf.append(q)
        retval.append(qf)
    return retval

@transaction.commit_on_success
def submit_hits(task_item, retval=DEFAULT_RETVAL):
    """
    Works on the output of generate_question_forms by submitting each
    QuestionForm found and returns the output of each submission in a
    list.
    """
    task_config = task_item.config
    (host, mtc) = get_connection()
    question_forms = retval
    try:
        make_hit = lambda qf: mtc.create_hit(question=qf,
                                             max_assignments=task_config.max_assignments,
                                             title=task_config.title,
                                             description=task_config.description,
                                             reward=task_config.reward)
        hit_sets = map(make_hit, question_forms)
        for page_num, hit_set in enumerate(hit_sets):
            h = HITItem(hitid=hit_set[0].HITId,
                        status=ASSIGNABLE,
                        task=task_item,
                        task_page=page_num)
            task_item.status = IN_PROGRESS
            h.save()
            task_item.save()
        return hit_set
    except Exception as e:
        print type(e)
        print e.args
        raise

                    
### REVIEW_FUNCTIONS


def get_answer_data(task_item, retval=DEFAULT_RETVAL):
    hit_map = retval
    source_sentences = task_item.content_object.sourcesentence_set.all()
    # if this crashes, it's because the TARGET_LANGUAGE wasn't set when the hit
    # was created
    target_lang = task_item.taskattribute_set.filter(key=TARGET_LANGUAGE)[0].value
    (host, mtc) = get_connection()
    
    for hit_tuple in hit_map:
        hititem, assignmentitems = hit_tuple
        assignments = mtc.get_assignments(hititem.hitid)
        task_page = hititem.task_page
        # amazon and wikitrans *should* be in sync
        for ass,item in zip(assignments, assignmentitems):
            for i,ans in enumerate(ass.answers[0]):
                segment_id = task_page * DEFAULT_TASK_PAGE_SIZE + i
                ss = source_sentences[segment_id]
                if not assignment_has_answer(item, segment_id):
                    mts = MTurkTranslatedSentence(segment_id=segment_id,
                                                  source_sentence=ss,
                                                  text=ans.fields[0][1],
                                                  translated_by=ass.WorkerId,
                                                  translation_date=datetime.now(),
                                                  language=target_lang,
                                                  best=False, ### TODO figure something better out
                                                  end_of_paragraph=ss.end_of_paragraph,
                                                  assignment=item)
                    mts.save()

#           try:
#                # choose one
#                mtc.approve_assignment(a.AssignmentId)
#                #mtc.reject_assignment(a.AssignmentId)
#            except:
#                # Might raise EC2ReponseError
#                raise

                


