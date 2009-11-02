from django.conf.urls.defaults import *

from wt_articles import views
from wt_articles.forms import *


urlpatterns = patterns('wt_articles.views',
    url(r'^$', 'landing', name="articles_landing"),

    url(r'^source/(?P<source>\w+)/(?P<title>[-_+()a-zA-Z0-9]+)/(?P<aid>\d+)',
        'show_source', name="articles_show_source"),
    url(r'^source/(?P<source>\w+)/(?P<title>[-_+()a-zA-Z0-9]+)/',
        'show_source', name="articles_show_source"),

    url(r'^translated/(?P<source>\w+)-(?P<target>\w+)/(?P<title>[-_+()a-zA-Z0-9]+)/(?P<aid>\d+)',
        'show_translated', name="articles_show_translated"),
    url(r'^translated/(?P<source>\w+)-(?P<target>\w+)/(?P<title>[-_+()a-zA-Z0-9]+)/',
        'show_translated', name="articles_show_translated"),

    url(r'^list/', 'article_list', name="article_list"),
    url(r'^search/', 'article_search', name="article_search"),
    url(r'^translatable/', 'translatable_list', name="translatable_list"),

    url(r'^translate/new/(?P<source>\w+)-(?P<target>\w+)/(?P<title>[-_+()a-zA-Z0-9]+)/(?P<aid>\d+)',
        'translate_from_scratch', name="translate_from_scratch"),
)
