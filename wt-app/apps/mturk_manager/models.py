from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _

class HITConfig(models.Model):
    name = models.CharField(_('Question Form Name'), max_length=255)
    max_assignments = models.PositiveIntegerField(_('Max number of Assignments'))
    title = models.CharField(_('Question Form Title'), max_length='255')
    description = models.TextField(_('Question Form Description'))
    reward = models.DecimalField(_('Reward'), decimal_places=2, max_digits=2)
    bonus = models.DecimalField(_('Bonus'), decimal_places=2, max_digits=2)
    
    class Meta:
        ordering = ["name"]
    
    def __unicode__(self):
        return self.name

    
ASSIGNABLE = 0
REVIEWABLE = 1
REVIEWING = 2
DISPOSED = 3
STATUSES = ( 
    (ASSIGNABLE, 'Assignable'),
    (REVIEWABLE, 'Reviewable'),
    (REVIEWING, 'Reviewing'),
    (DISPOSED, 'Disposed'),
)
class HITItem(models.Model):
    """
    A model that represents the HIT and is mapped to an object that understands
    the task details
    """
    # HIT data 
    hitid = models.CharField(_('HITId'), max_length=50)
    creation_date = models.DateTimeField(_('Creation Date'))
    status = models.IntegerField(_('HIT Status'),
                                 choices=STATUSES,
                                 default=ASSIGNABLE)
    config = models.ForeignKey(HITConfig)

    # GFK
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    class Meta:
        ordering = ["creation_date"]
    
    def __unicode__(self):
        return self.hitid

