from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from wt_languages.models import LANGUAGE_CHOICES

import nltk.data
from BeautifulSoup import BeautifulSoup

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

class ArticleOfInterest(models.Model):
    title = models.CharField(_('Title'), max_length=255)
    language = models.CharField(_('Language'),
                                max_length=2,
                                choices=LANGUAGE_CHOICES)

    def __unicode__(self):
        return u"%s :: %s" % (self.title, self.language)

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

    def save(self):
        super(SourceArticle, self).save()
        print "w00t"
        soup = BeautifulSoup(self.source_text)
        sentences = list()
        segment_id = 0
        for p in soup.findAll('p'):
            only_p = p.findAll(text=True)
            p_text = ''.join(only_p)
            sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
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

#class TranslatedArticle(models.Model):
#    article = ForeignKey(Article)
#    target_language = 
#    version
#    list of translated sentences
#
#class TranslatedSentence(models.Model):
#    segment id
#    source sentence
#    user
#    date
#    parent
#    version
#    best (look for better way) # assume best until someone says otherwise
#
#class DesiredArticles(models.Model):
#    url
#    sourcel language
#    target language
#    ranking
