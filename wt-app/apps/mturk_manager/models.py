from datetime import datetime

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _

class TaskConfig(models.Model):
    """
    TaskConfig is a general description of the info necessary for
    creating a HIT from a task.
    """
    name = models.CharField(_('Question Form Name'), max_length=255)
    max_assignments = models.PositiveIntegerField(_('Max number of Assignments'))
    title = models.CharField(_('Question Form Title'), max_length=255)
    description = models.TextField(_('Question Form Description'))
    reward = models.DecimalField(_('Reward Per Answer'), decimal_places=2, max_digits=2)
    bonus = models.DecimalField(_('Bonus'), decimal_places=2, max_digits=2)
    
    class Meta:
        ordering = ["name"]
    
    def __unicode__(self):
        return self.name

DISPOSED = -3
CANCELLED = -2
HAS_ERRORS = -1
PENDING = 0
IN_PROGRESS = 1
FINISHED = 2
TASKITEM_STATUSES = ( 
    (DISPOSED, 'Disposed'),
    (CANCELLED, 'Cancelled'),
    (HAS_ERRORS, 'Has errors'),
    (PENDING, 'Pending'),
    (IN_PROGRESS, 'In progress'),
    (FINISHED, 'Finished'),
)
class TaskItem(models.Model):
    """
    A model that represents the HIT and is mapped to an object that understands
    the task details
    """
    # Task data 
    name = models.CharField(_('Task Name'), max_length=255)
    config = models.ForeignKey(TaskConfig)
    creation_date = models.DateTimeField(_('Creation Date'),
                                         default=datetime.now)
    status = models.IntegerField(_('Task Status'),
                                 choices=TASKITEM_STATUSES,
                                 default=PENDING)

    # GFK
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    class Meta:
        ordering = ["name"]
    
    def __unicode__(self):
        return self.name    


# TODO Use requesterannotation instead
class TaskAttribute(models.Model):
    """
    TaskAttribute is a field that contains an additional information that
    must be known about the task.
    """
    task_item = models.ForeignKey(TaskItem, null=True, blank=True)
    key = models.CharField(_('Attribute Key'), max_length=255, null=True, blank=True)
    value = models.CharField(_('Attribute Value'), max_length=255, null=True, blank=True)

    class Meta:
        # apparently this doesn't work properly in sqlite...
        unique_together = (('task_item', 'key', 'value'))
        ordering = ["key"]

    def __unicode__(self):
        return u'%s:%s' % (self.task_item.id, self.key)

#PENDING = 0 
ASSIGNABLE = 1
REVIEWABLE = 2
REVIEWING = 3
DISPOSED = 4
HIT_STATUSES = ( 
    (PENDING, 'Pending'),
    (ASSIGNABLE, 'Assignable'),
    (REVIEWABLE, 'Reviewable'),
    (REVIEWING, 'Reviewing'),
    (DISPOSED, 'Disposed'),
)
HIT_ATTR_TASK_PAGE = 'Task Page'
class HITItem(models.Model):
    """
    A model that represents the HIT and is mapped to an object that understands
    the task details
    """
    # HIT data
    hitid = models.CharField(_('HITId'), max_length=50, null=True, blank=True)
    creation_date = models.DateTimeField(_('Creation Date'),
                                         default=datetime.now)
    status = models.IntegerField(_('HIT Status'),
                                 choices=HIT_STATUSES,
                                 default=PENDING)
    task = models.ForeignKey(TaskItem)
    task_page = models.IntegerField(_('Task Page Num'))
    annotation = models.CharField(_('Requester Annotation'),
                                  max_length=255)

    class Meta:
        ordering = ["creation_date"]

    def __unicode__(self):
        if self.hitid == None:
            return u'-1'
        else:
            return self.hitid

REJECTED=-1
#PENDING=0
ACCEPTED=1
ASSIGNMENT_STATUSES = (
    (REJECTED, 'Rejected'),
    (PENDING, 'Pending'),
    (ACCEPTED, 'Accepted'),
)
class AssignmentItem(models.Model):
    """
    A model that represents an assigned instance of the mapped HIT. This model
    has helper functions to generate description of task and relevant data.
    """
    # HIT data
    assignment_id = models.CharField(_('Assignment ID'), max_length=50, null=True, blank=True)
    accept_time = models.DateTimeField(_('Accept Time'), null=True, blank=True)
    submit_time = models.DateTimeField(_('Submit Time'), null=True, blank=True)
    status = models.IntegerField(_('Assignment Status'),
                                 choices=ASSIGNMENT_STATUSES,
                                 default=PENDING)
    hit = models.ForeignKey(HITItem)
    worker_id = models.CharField(_('Worker Id'), max_length=50, null=True, blank=True)
    wages_paid = models.DecimalField(_('Wages Paid'), decimal_places=2, max_digits=2, default='0.0')

    class Meta:
        ordering = ["accept_time"]
    
    def __unicode__(self):
        if self.assignment_id == None:
            return u'-1'
        else:
            return self.assignment_id


