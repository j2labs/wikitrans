from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from tagging.fields import TagField
from tagging.models import Tag

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

MINIMAL = 1
SOME_SCHOOL = 2
SPEAKS_DAILY = 3
NEAR_NATIVE = 4
NATIVE = 5
COMPETENCY_RATING = (
    (MINIMAL, 'Minimal'),
    (SOME_SCHOOL, 'Some school'),
    (SPEAKS_DAILY, 'Speaks daily'),
    (NEAR_NATIVE, 'Near Native'),
    (NATIVE, 'Native'),
)

ENGLISH = 'en'
URDU = 'ur'
GIBBERISH = 'gb'
LANGUAGE_CHOICES = (
    (ENGLISH, 'English'),
    (URDU, 'Urdu'),
    (GIBBERISH, 'Gibberish'),
)

TARGET = 't'
SOURCE = 's'
BOTH = 'b'
TRANSLATION_OPTIONS = (
    (TARGET, 'Target'),
    (SOURCE, 'Source'),
    (BOTH, 'Both'),
)

class LanguageCompetancy(models.Model):
    user = models.ForeignKey(User)
    language = models.CharField(_('Language'),
                                max_length=2,
                                choices=LANGUAGE_CHOICES,
                                default=URDU)
    rating = models.IntegerField(_('rating'),
                                 choices=COMPETENCY_RATING,
                                 default=MINIMAL)
    updated = models.DateTimeField(_('Updated Date'))
    experience = models.IntegerField(_('How many years'))
    translation_options = models.CharField(_('Translation Options'),
                                           choices=TRANSLATION_OPTIONS,
                                           max_length=1)

    def __unicode__(self):
        return "%s :: %s" % (self.user, self.language)

    class Meta:
        ordering = ('-updated',)

    def get_absolute_url(self):
        return ('language_competancy', None, {
            'user': self.author.username,
            'language': self.language
    })
    get_absolute_url = models.permalink(get_absolute_url)

    # perhaps overriding will be necessary?
    #def save(self, force_insert=False, force_update=False):




    
    
