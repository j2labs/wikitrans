from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _

ASSIGNABLE = 0
REVIEWABLE = 1
STATUSES = ( 
    (ASSIGNABLE, 'Assignable'),
    (REVIEWABLE, 'Reviewable'),
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

    # GFK
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    class Meta:
        ordering = ["creation_date"]
    
    def __unicode__(self):
        return self.hitid

