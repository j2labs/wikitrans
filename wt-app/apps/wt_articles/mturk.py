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

#from mturk_manager.models import TASKITEM_STATUSES, PENDING, TaskItem
from mturk_manager.workflow import task_from_object

def handle_translation_request(trans_req):
    article = trans_req.article
    language = trans_req.target_language
    print 'Translate %s to %s' % (article.title, language)
    #task_item = task_from_object(trans_req.article,
    #                             language)
    
    
def split_task_to_hits(task_item, task_config, task_set_size=9):
    """
    split_task_to_hits is a function mturk_manager expects.
    tasks a task item and breaks it into hits managing
    as many task as task_set_size permits.
    """
    # Gather pertinent info
    source_article = task_item.content_object
    source_sentences = source_article.sourcesentence_set.all()

    for s in source_sentences:
        print s.text

    # taskination
    #hit_items = break_into_hits()
    #for hit_item in hit_items:
    #    hit_item = hit_from_object(content_object)
    #    #hit_item.finish()
        

    # handle relevant media
    #img_sentence_info = _gen_images(source_sentences)

    # break up task into hits with a pagesize of 10

    # submit hits to Amazon

    # mark HITItem tasks created successfully as Assignable

    # return list of HITItems created to handle the tasks
    

def _gen_images(sentences):
    sentences = []
    width = 350
    extension = 'png'
    for s in urdu_sentences:
        output = '%s/%s.%s' % ('/Users/jd/Projects/playpen/botolearn/pydjango_view', s.id, extension)
        dataurl = '%s/%s.%s' % ('/site_media/pydjango_view', s.id, extension)
        retval = str2img(s.text,
                         #font='Nafees',
                         output=output,
                         width=width)
        data = {
            'type': 'image',
            'subtype': extension,
            'file_path': output,
            'dataurl': dataurl,
            'width': width,
            'text': s.text,
            }
        sentences.append(data)
    return sentences
