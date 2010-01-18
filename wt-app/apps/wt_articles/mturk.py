#!/usr/bin/env python

import uuid

from boto.mturk.connection import MTurkConnection
from boto.mturk.question import Question, QuestionForm, QuestionContent, ExternalQuestion
from boto.mturk.question import AnswerSpecification, FreeTextAnswer, SelectionAnswer
from boto.mturk.question import Overview
#from boto.mturk.qualification import Qualifications, PercentAssignmentsAbandonedRequirement
#from boto.mturk.qualification import Requirement

from django.contrib.contenttypes.models import ContentType

from pyango_view import str2img

from wt_articles.models import TranslationRequest
from wt_articles.models import SourceArticle, SourceSentence
from wt_articles import MECHANICAL_TURK
from wt_languages.models import TARGET_LANGUAGE
from wt_languages.models import SOURCE_LANGUAGE

from mturk_manager.workflow import task_from_object,load_task_config, get_connection
from mturk_manager.workflow import TASKCONFIG_DEFAULT, DEFAULT_RETVAL
from mturk_manager.models import TaskConfig, TaskAttribute


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
    overview_content = """<p>Your task is to translate the Urdu sentences into English.  Please make sure that your English translation:</p>
<ul>
    <li>Is faithful to the original in both meaning and style</li>
    <li>Is grammatical, fluent, and natural-sounding English</li>
    <li>Does not add or delete information from the original text</li>
    <li>Does not contain any spelling errors</li>
</ul>
<p>When creating your translation, please follow these guidelines:</p>
<ul>
    <li><b>Do not use any machine translation systems (like translation.babylon.com)</b></li>
    <li><b>You may</b> look up a word on <a href="http://www.urduword.com/">an online dictionary</a> if you do not know its translation</li>
</ul>
<p>Afterwards, we'll ask you a few quick questions about your language abilities.</p>
"""

    overview = Overview()
    overview.append('Title', overview_title)
    overview.append('FormattedContent', overview_content)
    
    return overview


#############################
# Required by mturk_manager #
#############################

### PENDING_FUNCTIONS

def task_to_pages(task_item, retval=DEFAULT_RETVAL):
    """
    task_to_pages is a bootstrapping function. it sets retval to a
    new dictionary and populates it with a mapping of pages to
    source data for HITItems
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
    Expects a list of lists containing sentence segmented into pages
    """
    text_to_image = lambda sentence: _gen_text_image(sentence, DEFAULT_IMAGE_DIR)
    results = [map(text_to_image, page) for page in retval]
    return results

def generate_question_forms(task_item, retval=DEFAULT_RETVAL):
    """
    dunno
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
                              'alttext': s['sentence']}
            qc.append('Binary', binary_content)
            fta = FreeTextAnswer()
            ansp = AnswerSpecification(fta)
            q = Question(identifier=str(uuid.uuid4()),
                         content=qc,
                         answer_spec=ansp)
            qf.append(q)
        retval.append(qf)
    return retval

def submit_hits(task_item, retval=DEFAULT_RETVAL):
    """
    dunno
    """
    task_config = task_item.config
    mtc = get_connection()
    print 'MTC : %s' % mtc
    question_forms = retval
    for qf in question_forms:
        try:
            mtc.create_hit(question=qf,
                           max_assignments=task_config.max_assignments,
                           title=task_config.title,
                           description=task_config.description,
                           reward=task_config.reward)
        except Exception as e:
            print type(e)
            print e.args
            raise
 

### REVIEW_FUNCTIONS

def update_statuses(task_item, retval=DEFAULT_RETVAL):
    """
    dunno
    """
    print 'update_statuses'
    
