from django.conf.urls.defaults import *

from wt_managing import views, models
from wt_languages.forms import *

urlpatterns = patterns('wt_managing.views',
    url(r'^$', 'reviewable_article_list', name="reviewable_article_list"),
    url(r'^sentences/', 'reviewable_sentence_list', name="reviewable_sentence_list"),
    url(r'^(?P<source>\w+)-(?P<target>\w+)/(?P<title>[-_+()a-zA-Z0-9]+)/(?P<aid>\d+)',
        'review_translatedarticle', name="review_translatedarticle"),
)
