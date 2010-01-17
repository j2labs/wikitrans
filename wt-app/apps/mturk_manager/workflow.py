#!/usr/bin/env python

import uuid

from boto.mturk.connection import MTurkConnection
from boto.mturk.question import Question, QuestionForm, QuestionContent, ExternalQuestion
from boto.mturk.question import AnswerSpecification, FreeTextAnswer, SelectionAnswer
from boto.mturk.question import Overview
#from boto.mturk.qualification import Qualifications, PercentAssignmentsAbandonedRequirement
#from boto.mturk.qualification import Requirement

from django.contrib.contenttypes.models import ContentType

from mturk_manager.models import TaskConfig,TaskItem

"""
These functions are required to exist in application/mturk.py.
They create the interaction between workflow and data.
This serves to allow an interface language to be determined with
minimal effort required. Each function receives a task_item and
task_config.

Each function is currently blocking to ensure sequential handling.
This allows each function to also return nothing and operate on
data only. I'm interested in better ways of acheiving this goal.

eg. split_task_to_hits(task_item, task_config)

FUNCTION_ARGS represents the string used for the arguments.
"""
CREATE_FUNCTIONS = (
    'split_task_to_hits',
)
REVIEW_FUNCTIONS = (
    'fetch_reviewables',
)

FUNCTION_ARGS = '(task_item, task_config)'


##################################
# Connectivity related functions #
##################################

def get_mturk_config():
    """
    returns a tuple containing the access key, secret key and host.
    expects to find these settings in a local_settings.py next to the
    standard settings.py
    """
    try:
        from local_settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_HOST
        return (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_HOST)
    except ImportError:
        raise

def get_connection():
    """
    Returns a connection to mechanical turk using parameters found
    in local_settings.
    """
    access_key, secret_key, host = get_mturk_config()
    return MTurkConnection(aws_access_key_id=access_key,
                           aws_secret_access_key=secret_key,
                           host=host)

#################################
# Task Config related functions #
#################################

class TaskConfigError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def load_task_config(config_name):
    config_set = TaskConfig.objects.filter(name__exact=config_name)
    if len(config_set) is not 1:
        raise TaskConfigError('ERROR: could not find single hit config with name: %s' % config_name)
    task_config = config_set[0]
    return task_config


###############################
# Task Item related functions #
###############################

class TaskItemError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def task_from_object(content_object):
    """
    Returns a hit_item that only has the generic relation in place
    based on the object (o) argument
    """
    ctype = ContentType.objects.get_for_model(content_object)
    task_item = TaskItem(content_object=content_object,
                         object_id=content_object.id,
                         content_type=ctype)
    return task_item

def create_task(content_object, config_name):
    """
    Accepts a content object and a TaskConfig name. It then generates the
    hit structure in boto and submits the hit to Amazon.
    """
    # Load the task config and create task
    task_config = load_task_config(config_name)
    task_item = task_from_object(content_object)

    app_name = task_item.content_type.app_label
    #module = namedAny(app_name + '.mturk')
    module_name = app_name + '.mturk'
    module = __import__(module_name)
    missingFuncs = filter(lambda f : not hasattr(module, f), FUNCTIONS)
    if missingFuncs:
        error_string = 'Missing implementations in %s for :: %s'
        raise TaskItemError(error_string % (module_name, ', '.join(missingFuncs)))

    # 1. Loop over each function in FUNCTIONS
    # 2. Generate the string representing each function call iteration
    # 3. Use exec to call function
    for function in CREATE_FUNCTIONS:
        fun_string = '%s%s' % (function, FUNCTION_ARGS)
        exec fun_string in globals(), locals()
