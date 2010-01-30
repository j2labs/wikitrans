from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from wt_articles.models import TranslatedSentence

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

PENDING = 0
IN_PROGRESS = 1
FINISHED = 2
TRANSLATIONREVIEW_STATUSES = ( 
    (PENDING, 'Pending'),
    (IN_PROGRESS, 'In Progress'),
    (FINISHED, 'Finished'),
)
class TranslationReview(models.Model):
    user = models.ForeignKey(User)
    translated_sentence = models.ForeignKey(TranslatedSentence)
    accepted = models.BooleanField(_('Accepted'))
    review_date = models.DateTimeField(_('Review Date'))
    status = models.IntegerField(_('Review Status'),
                                 choices=TRANSLATIONREVIEW_STATUSES,
                                 default=PENDING)

    def __unicode__(self):
        return "%s :: %s" % (self.user, self.id)

    class Meta:
        ordering = ('accepted',)
