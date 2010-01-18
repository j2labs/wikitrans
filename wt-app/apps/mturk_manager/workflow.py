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
attaches itself to a task_config.

Functions can pass values to each other using retval. The return
value of the previous call is used for input to the current call,
hopefully allowing some interesting chaining of workflows.

eg. retval = function_name(task_item, retval=retval)

PENDING_FUNCTIONS is an example of a list of functions used.
"""
PENDING_FUNCTIONS = (
    'task_to_pages',
    'prepare_media',
    'generate_question_forms',
    'submit_hits',
)
REVIEW_FUNCTIONS = (
    'update_statuses',
)

DEFAULT_RETVAL = None
TASKCONFIG_DEFAULT='workflow test'


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
    """
    Loads a config and complains if more than, or less than, one is found.
    """
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


############################
# Module related functions #
############################

def import_mturk_handler(task_item):
    """
    Uses the task item to determine the relevant application implementing
    an mturk file. Attempts to load using __import__(module_name).
    Passes along raised ImportError if one is thrown.
    """
    app_name = task_item.content_type.app_label
    module_name = app_name + '.mturk'
    __import__(module_name) # module = namedAny(module_name)
    return module_name
    
def inspect_module(module_name, function_list):
    import sys
    """
    Accepts a module and a list of functions and checks if module has
    implemented each function in the list.
    Throws TaskItemError if any are found missing.
    """
    module = sys.modules[module_name]
    missingFuncs = filter(lambda f : not hasattr(module, f), function_list)
    if missingFuncs:
        error_string = 'Missing implementations in %s for :: %s'
        raise TaskItemError(error_string % (module_name, ', '.join(missingFuncs)))
    return module


##############################
# Workflow utility functions #
##############################

def handle_task(task_item, function_list):
    """
    Accepts a content object and a TaskConfig name. It then generates the
    hit structure in boto and submits the hit to Amazon.
    """
    task_config = task_item.config

    # Let exceptions just go here. They should alert the programmer that
    # something diesn;t look right.
    module_name = import_mturk_handler(task_item)
    module = inspect_module(module_name, function_list)

    # Loop across each function in function list and call
    # functions are called expecting a return value, which they pass into
    # the next call for a piping effect.
    retval = DEFAULT_RETVAL
    for function_name in function_list:
        function = getattr(module, function_name)
        retval = function(task_item, retval=retval)

        
def handle_pending_task(task_item):
    """
    Accepts a Task Item and calls each function in
    PENDING_FUNCTIONS to submit the task as HITS to Amazon.
    """
    handle_task(task_item, PENDING_FUNCTIONS)

def handle_review_task(task_item):
    """
    Accepts a Task Item and calls each function in
    REVIEW_FUNCTIONS to submit the task as HITS to Amazon.
    """
    handle_task(task_item, REVIEW_FUNCTIONS)
    
