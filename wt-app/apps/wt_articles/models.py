from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import User

from wt_languages.models import LANGUAGE_CHOICES

import nltk.data
from BeautifulSoup import BeautifulSoup
from datetime import datetime

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
    source_language = models.CharField(_('Source Language'),
                                       max_length=2,
                                       choices=LANGUAGE_CHOICES)
    target_language = models.CharField(_('Target Language'),
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
        sentences = list()
        segment_id = 0
        soup = BeautifulSoup(self.source_text)
        sent_detector = self.determine_splitter(self.source_language)
        # initial save for foriegn key based saves to work
        # save should occur after sent_detector is loaded
        super(SourceArticle, self).save()
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

    class Meta:
        ordering = ('segment_id','article')

    def __unicode__(self):
        return u"%s" % (self.text)

class TranslatedSentence(models.Model):
    segment_id = models.IntegerField(_('Segment ID'))
    source_sentence = models.ForeignKey(SourceSentence)
    translation = models.CharField(_('Translated Text'), blank=True, max_length=1024)
    translated_by = models.CharField(_('Translated by'), blank=True, max_length=255)
    language = models.CharField(_('Language'), blank=True, max_length=2)
    translation_date = models.DateTimeField(_('Import Date'))
    #version
    best = models.BooleanField(_('Best sentence'))

    class Meta:
        ordering = ('segment_id',)

    def __unicode__(self):
        return '%s :: %s' % (self.translation, self.best)

class TranslatedArticle(models.Model):
    article = models.ForeignKey(SourceArticle)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='parent_set')
    title = models.CharField(_('Title'), max_length=255)
    timestamp = models.DateTimeField(_('Timestamp'))
    language = models.CharField(_('Language'),
                                max_length=2,
                                choices=LANGUAGE_CHOICES)
    sentences = models.ManyToManyField(TranslatedSentence)

    def set_sentences(self, translated_sentences):
        source_sentences = self.article.sourcesentence_set.order_by('segment_id')
        source_segment_ids = [s.segment_id for s in source_sentences]
        translated_segment_ids = [s.segment_id for s in translated_sentences]
        if len(source_segment_ids) != len(translated_segment_ids):
            raise ValueException('Number of translated sentences doesn\'t match number of source sentences')
        if source_segment_ids != translated_segment_ids:
            ValueException('Segment id lists do not match')
        translated_article_list = [ts.source_sentence.article for ts in translated_sentences]
        if len(translated_article_list) != 1 and translated_article_list[0] != self.article:
            raise ValueException('Not all translated sentences derive from the source article')
        for ts in translated_sentences:
            self.sentences.add(ts)
        
    #version @@@ django-versioning
    def __unicode__(self):
        return '%s :: %s' % (self.title, self.article)
