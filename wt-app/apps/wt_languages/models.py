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
HINDI = 'hi'
SPANISH = 'es'
GERMAN = 'de'
FRENCH = 'fr'
CZECH = 'cs'
LANGUAGE_CHOICES = (
    (ENGLISH, 'English'),
    (URDU, 'Urdu'),
    (HINDI, 'Hindi'),
    (SPANISH, 'Spanish'),
    (GERMAN, 'German'),
    (FRENCH, 'French'),
    (CZECH, 'Czech'),
)

TARGET_LANGUAGE = 'target_language'
SOURCE_LANGUAGE = 'source_language'
BOTH = 'both'
TRANSLATION_OPTIONS = (
    (TARGET_LANGUAGE, 'Target'),
    (SOURCE_LANGUAGE, 'Source'),
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
                                           max_length=20)

    def __unicode__(self):
        return "%s :: %s" % (self.user, self.language)

    class Meta:
        ordering = ('-updated',)

    @models.permalink
    def get_absolute_url(self):
        return ('language_competancy_edit', [str(self.id)])




    
    
