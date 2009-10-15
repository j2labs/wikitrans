from django.conf.urls.defaults import *

from wt_articles import views, models
from wt_articles.forms import *


urlpatterns = patterns('',
    # article list
    url(r'^$', 'wt_articles.views.article_list', name="article_list"),
)
