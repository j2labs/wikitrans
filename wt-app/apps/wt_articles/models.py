from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import User

from wt_languages.models import LANGUAGE_CHOICES

import nltk.data
from BeautifulSoup import BeautifulSoup

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

class ArticleOfInterest(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    title_language = models.CharField(_('Title language'),
                                      max_length=2,
                                      choices=LANGUAGE_CHOICES)
    target_language = models.CharField(_('Target language'),
                                       max_length=2,
                                       choices=LANGUAGE_CHOICES)

    def __unicode__(self):
        return u"%s :: %s" % (self.title, self.target_language)

class SourceArticle(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    language = models.CharField(_('Language'),
                                max_length=2,
                                choices=LANGUAGE_CHOICES)
    #version = models.IntegerField(_('Version')) # @@@ try django-versioning
    import_date = models.DateTimeField(_('Import Date'))
    doc_id = models.CharField(_('Document ID'), max_length=512)
    source_text = models.TextField(_('Source Text'))
    sentences_processed = models.BooleanField(_('Sentences Processed'))

    def __unicode__(self):
        return u"%s :: %s" % (self.title, self.doc_id)

    def determine_splitter(self, language):
        for desc_pair in LANGUAGE_CHOICES:
            if desc_pair[0] == language:
                tokenizer = 'tokenizers/punkt/%s.pickle' % (desc_pair[1].lower())
                break
        try:
            tokenizer = nltk.data.load(tokenizer)
            return tokenizer
        except:
            raise AttributeError('%s not supported by sentence splitters' % (language))
            
    def save(self):
        # initial save for foriegn key based saves to work
        super(SourceArticle, self).save()
        soup = BeautifulSoup(self.source_text)
        sentences = list()
        segment_id = 0
        sent_detector = self.determine_splitter(self.language)
        for p in soup.findAll('p'):
            only_p = p.findAll(text=True)
            p_text = ''.join(only_p)
            for sentence in sent_detector.tokenize(p_text.strip()):
                s = SourceSentence(article=self, text=sentence, segment_id=segment_id)
                segment_id += 1
                s.save()
        self.sentences_processed = True
        super(SourceArticle, self).save()

class SourceSentence(models.Model):
    article = models.ForeignKey(SourceArticle)
    text = models.CharField(_('Sentence Text'), max_length=1024)
    segment_id = models.IntegerField(_('Segment ID'))

    def __unicode__(self):
        return u"%s" % (self.text)

class TranslatedArticle(models.Model):
    article = models.ForeignKey(SourceArticle)
    title = models.CharField(_('Title'), max_length=255)
    target_language = models.CharField(_('Target language'),
                                       max_length=2,
                                       choices=LANGUAGE_CHOICES)
    #version @@@ django-versioning
    def __unicode__(self):
        return '%s :: %s' % (article, title)

class TranslatedSentence(models.Model):
    segment_id = models.IntegerField(_('Segment ID'))
    source_sentence = models.ForeignKey(SourceSentence)
    user = models.ForeignKey(User)
    translation_date = models.DateTimeField(_('Import Date'))
    #version
    best = models.BooleanField(_('Best sentence'))

    def __unicode__(self):
        return '%s :: %s' % (self.source_sentence, self.best)

