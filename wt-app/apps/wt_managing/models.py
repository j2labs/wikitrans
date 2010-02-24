from datetime import datetime

from django.db import models
from django.db.transaction import commit_on_success
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from wt_articles.models import TranslatedArticle, TranslatedSentence

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

PENDING = 0
IN_PROGRESS = 1
FINISHED = 2
REVIEW_STATUSES = ( 
    (PENDING, 'Pending'),
    (IN_PROGRESS, 'In Progress'),
    (FINISHED, 'Finished'),
)
class ArticleReview(models.Model):
    translated_by = models.CharField(_('Translated by'), blank=True, max_length=255)
    translated_article = models.ForeignKey(TranslatedArticle)
    start_date = models.DateTimeField(_('Start Date'))
    finished_date = models.DateTimeField(_('Finished Date'), blank=True, null=True)
    status = models.IntegerField(_('Review Status'),
                                 choices=REVIEW_STATUSES,
                                 default=PENDING)

    @commit_on_success
    def bootstrap(self, ta):
        self.translated_article=ta
        self.start_date = datetime.now()
        self.save() # generates id for foreignkey in sentence review
        sentences = self.translated_article.sentences.all()
        sr_list = []
        for s in sentences:
            sr = SentenceReview(translated_sentence=s,
                                articlereview=self,
                                segment_id=s.segment_id)                                
            sr.save()
            sr_list.append(sr)
        return sr_list

    def __unicode__(self):
        return "%s :: %s" % (self.translated_by, self.id)

    class Meta:
        ordering = ('finished_date',)


class SentenceReview(models.Model):
    translated_sentence = models.ForeignKey(TranslatedSentence)
    articlereview = models.ForeignKey(ArticleReview)
    accepted = models.BooleanField(_('Accepted'), default=False)
    review_date = models.DateTimeField(_('Review Date'), null=True, default=datetime.now())
    segment_id = models.IntegerField(_('Segment ID'))
    status = models.IntegerField(_('Review Status'),
                                 choices=REVIEW_STATUSES,
                                 default=PENDING)

    def __unicode__(self):
        return "%s :: %s" % (self.articlereview.translated_by,
                             self.id)

    @commit_on_success
    def save(self, *args, **kwargs):
        self.translated_sentence.approved = self.accepted
        super(SentenceReview, self).save(*args, **kwargs)

    class Meta:
        ordering = ('accepted', 'segment_id',)
