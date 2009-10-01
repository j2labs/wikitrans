from django.conf.urls.defaults import *

from wt_languages import views, models
from wt_languages.forms import *


urlpatterns = patterns('',
    # your language competancies
    url(r'^$', 'wt_languages.views.your_language_competancies', name="your_language_competancies"),

    # new competancy
    url(r'^new/$', 'wt_languages.views.new_language_competancy', name='new_language_competancy'),

    # edit blog post
    #url(r'^edit/(\d+)/$', 'blog.views.edit', name='blog_edit'),

    #destory blog post
    #url(r'^destroy/(\d+)/$', 'blog.views.destroy', name='blog_destroy'),

    # ajax validation
    #(r'^validate/$', 'ajax_validation.views.validate', {'form_class': BlogForm, 'callback': lambda request, *args, **kwargs: {'user': request.user}}, 'blog_form_validate'),
)
