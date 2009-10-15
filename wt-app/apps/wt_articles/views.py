import datetime
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import date_based
from django.conf import settings

from wt_languages.models import LanguageCompetancy
from wt_articles.models import SourceArticle,SourceSentence,TranslatedSentence
from wt_articles.forms import *

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

@login_required
def article_list(request, template_name="wt_articles/article_list.html"):
    
    #source_languages.add(request.user.native_language)
    #languages.add(request.user.display_language)
    
    user_competencies = LanguageCompetancy.objects.filter(user__username=request.user.username)
    target_articles = SourceArticle.objects.all()

    return render_to_response(template_name, {
        "articles": target_articles,
    }, context_instance=RequestContext(request))

