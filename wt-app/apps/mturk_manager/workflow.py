#!/usr/bin/env python

import uuid
import dateutil.parser

from boto.mturk.connection import MTurkConnection
from boto.mturk.question import Question, QuestionForm, QuestionContent, ExternalQuestion
from boto.mturk.question import AnswerSpecification, FreeTextAnswer, SelectionAnswer
from boto.mturk.question import Overview
#from boto.mturk.qualification import Qualifications, PercentAssignmentsAbandonedRequirement
#from boto.mturk.qualification import Requirement

from django.contrib.contenttypes.models import ContentType

from mturk_manager.models import TaskConfig, TaskItem, HITItem, AssignmentItem
from mturk_manager.models import REVIEWABLE, PENDING


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
REVIEWABLE_FUNCTIONS = (
    'get_answer_data',
)

DEFAULT_RETVAL = None
TASKCONFIG_DEFAULT='default'


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
    mtc =  MTurkConnection(aws_access_key_id=access_key,
                           aws_secret_access_key=secret_key,
                           host=host)
    return (host, mtc)

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


#########################
# HIT Related functions #
#########################

class HITItemError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def mark_hit_reviewable(hitid):
    """
    Changes status of hit 'Reviewable'
    """
    hit_set = HITItem.objects.filter(hitid__exact=hitid)
    if len(hit_set) == 1:
        hit = hit_set[0]
        hit.status = REVIEWABLE
        hit.save()

def check_for_reviewables():
    """
    dunno
    """
    (host, mtc) = get_connection()
    reviewables = mtc.get_reviewable_hits()
    for h in reviewables:
        mark_hit_reviewable(h.HITId)
    return reviewables


################################
# Assignment related functions #
################################

def get_assignment_data(shallow_hitids):
    """
    dunno
    """
    hit_map = []
    (host, mtc) = get_connection()
    print 'HITS :: %s' % [h.HITId for h in shallow_hitids]
    for h in shallow_hitids:
        hitid = h.HITId
        hit_set = HITItem.objects.filter(hitid__exact=hitid)
        if len(hit_set) == 1:
            hit = hit_set[0]
            print 'Getting assignment data for hit %s' % h.HITId
            assignments = mtc.get_assignments(h.HITId)
            new_asses = []
            if len(assignments) > 0:
                for a in assignments:
                    # Skip assignments we've already collected
                    ass_set = AssignmentItem.objects.filter(assignment_id__exact=a.AssignmentId)
                    if len(ass_set) < 1:
                        new_assignment = AssignmentItem()
                        new_assignment.assignment_id = a.AssignmentId
                        new_assignment.accept_time = dateutil.parser.parse(a.AcceptTime)
                        new_assignment.submit_time = dateutil.parser.parse(a.SubmitTime)
                        new_assignment.status = PENDING
                        new_assignment.hit = hit
                        new_assignment.worker_id = a.WorkerId
                        new_assignment.save()
                        new_asses.append(new_assignment)
                    else:
                        new_asses.append(ass_set[0])
                hit_map.append((hit, new_asses))
    return hit_map


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

def handle_task(task_item, function_list, first_retval=DEFAULT_RETVAL):
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
    retval = first_retval
    for function_name in function_list:
        function = getattr(module, function_name)
        retval = function(task_item, retval=retval)

        
def handle_pending_task(task_item):
    """
    Accepts a Task Item and calls each function in
    PENDING_FUNCTIONS to submit the task as HITS to Amazon.
    """
    handle_task(task_item, PENDING_FUNCTIONS)

def handle_reviewable_task(task_item):
    """
    Accepts a Task Item and calls each function in
    REVIEWABLE_FUNCTIONS to submit the task as HITS to Amazon.
    """
    #handle_task(task_item, REVIEWABLE_FUNCTIONS)
    reviewables = check_for_reviewables()
    hit_map = get_assignment_data(reviewables)
    handle_task(task_item,
                REVIEWABLE_FUNCTIONS,
                first_retval=hit_map)

    
