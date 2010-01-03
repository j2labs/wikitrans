from datetime import datetime
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.generic import date_based
from django.conf import settings
from django.forms.formsets import formset_factory

from wt_articles.models import SourceArticle,TranslatedArticle
from wt_articles.models import SourceSentence,TranslatedSentence
from wt_articles.models import FeaturedTranslation, latest_featured_article
from wt_articles.models import ArticleOfInterest
from wt_articles.forms import TranslatedSentenceMappingForm,TranslationRequestForm
from wt_articles.utils import sentences_as_html, target_pairs_by_user
from wt_articles.utils import user_compatible_articles
from wt_articles.utils import user_compatible_target_articles
from wt_articles.utils import user_compatible_source_articles

from urllib import quote_plus, unquote_plus

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

def landing(request, template_name="wt_articles/landing.html"):
    featured_translation = latest_featured_article()
    featured_text = u'No translations are featured'
    if featured_translation != None:
        featured_text = sentences_as_html(featured_translation.article.sentences.all())

    recent_translations = TranslatedArticle.objects.all()[:5]
    
    return render_to_response(template_name, {
        "featured_translation": featured_text,
        "recent_translations": recent_translations,
    }, context_instance=RequestContext(request))


def show_source(request, title, source, aid=None, template_name="wt_articles/show_article.html"):
    title = unquote_plus(title)
    
    if aid != None:
        sa_set = SourceArticle.objects.filter(id=aid)
    else:
        sa_set = SourceArticle.objects.filter(language=source,
                                              title=title).order_by('-timestamp')
    if len(sa_set) > 0:
        article_text = sentences_as_html(sa_set[0].sourcesentence_set.all())
    else:
        article_text = None

    return render_to_response(template_name, {
        "title": title,
        "article_text": article_text,
    }, context_instance=RequestContext(request))

def show_translated(request, title, source, target, aid=None, template_name="wt_articles/show_article.html"):
    title = unquote_plus(title)
    
    if aid != None:
        ta_set = TranslatedArticle.objects.filter(id=aid)
    else:
        ta_set = TranslatedArticle.objects.filter(article__language=source,
                                                  language=target,
                                                  title=title).order_by('-timestamp')
    if len(ta_set) > 0:
        article_text = sentences_as_html(ta_set[0].sentences.all())
    else:
        article_text = None
    
    return render_to_response(template_name, {
        "title": title,
        "article_text": article_text,
    }, context_instance=RequestContext(request))

def article_search(request, template_name="wt_articles/article_list.html"):
    if request.method == "POST" and request.POST.has_key('search'):
        name = request.POST['search']
        articles = TranslatedArticle.objects.filter(title__icontains=name)
        print articles
    else:
        articles = []
    return render_to_response(template_name, {
        'articles': articles,
    }, context_instance=RequestContext(request))
 
    
@login_required
def article_list(request, template_name="wt_articles/article_list.html"):
    articles = user_compatible_articles(request.user)
    from django.utils.encoding import smart_unicode

    return render_to_response(template_name, {
        "articles": articles,
    }, context_instance=RequestContext(request))

@login_required
def translatable_list(request, template_name="wt_articles/article_list.html"):
    import copy
    user = request.user
    source_articles = user_compatible_source_articles(request.user)
    articles = []
    for sa in source_articles:
        lang_pairs = target_pairs_by_user(user, sa.language)
        for pair in lang_pairs:
            article = copy.deepcopy(sa)
            article.target = pair[0]
            article.link = u'/articles/translate/new/%s' % (article.get_relative_url(pair[1]))
            articles.append(article)
    
    return render_to_response(template_name, {
        "articles": articles,
        "translatable": True,
    }, context_instance=RequestContext(request))

@login_required
def translate_from_scratch(request, source, target, title, aid, template_name="wt_articles/translate_form.html"):
    """
    aid in this context is the source article id
    """
    sa_set = SourceArticle.objects.filter(id=aid)
    if len(sa_set) < 1:
        no_match = True
        return render_to_response(template_name,
                                  {"no_match": True},
                                  context_instance=RequestContext(request))
    article = sa_set[0]
    ss_list = article.sourcesentence_set.all()
    TranslatedSentenceSet = formset_factory(TranslatedSentenceMappingForm, extra=0)
    if request.method == "POST":
        formset = TranslatedSentenceSet(request.POST, request.FILES)
        if formset.is_valid():
            ts_list = []
            ta = TranslatedArticle()
            for form in formset.forms:
                ss = form.cleaned_data['source_sentence']
                text = form.cleaned_data['text']
                ts = TranslatedSentence(segment_id=ss.segment_id,
                                        source_sentence=ss,
                                        text=text,
                                        translated_by=request.user.username,
                                        translation_date=datetime.now(),
                                        language=target,
                                        best=True, ### TODO figure something better out
                                        end_of_paragraph=ss.end_of_paragraph)
                ts_list.append(ts)
            ta.article = ss.article
            ta.title = ss.article.title
            ta.timestamp = datetime.now()
            ta.language = target
            ta.save()
            for ts in ts_list:
                ts.save()
            ta.sentences = ts_list
            ta.save()
            return HttpResponseRedirect(ta.get_absolute_url())
    else:
        initial_ss_set = [{'source_sentence': s} for s in ss_list]
        formset = TranslatedSentenceSet(initial=initial_ss_set)
    for form,s in zip(formset.forms,ss_list):
        form.fields['text'].label = s.text
    
    return render_to_response(template_name, {
        "formset": formset,
        "title": article.title,
    }, context_instance=RequestContext(request))

@login_required
def request_translation(request, form_class=TranslationRequestForm, template_name="wt_articles/request_form.html"):
    """
    aid in this context is the source article id
    """
    if request.method == "POST":
        request_form = form_class(request.POST)
        if request_form.is_valid():
            title = request_form.cleaned_data['title']
            title_language = request_form.cleaned_data['title_language']
            target_language = request_form.cleaned_data['target_language']
            exists = ArticleOfInterest.objects.filter(title__exact=title,
                                                      title_language__exact=title_language,
                                                      target_language__exact=target_language)
            if len(exists) < 1:
                translation_request = request_form.save(commit=False)
                translation_request.date = datetime.now()
                translation_request.save()
            return render_to_response("wt_articles/requests_thankyou.html", {},
                                      context_instance=RequestContext(request))
    else:
        request_form = form_class()
        
    return render_to_response(template_name, {
        "request_form": request_form,
    }, context_instance=RequestContext(request))
