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
from wt_languages.forms import *

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None

@login_required
def language_competancy_list(request, template_name="wt_languages/language_competancy_list.html"):
    competencies = LanguageCompetancy.objects.filter(user__username=request.user.username)

    return render_to_response(template_name, {
        "competancies": competencies,
    }, context_instance=RequestContext(request))

@login_required
def language_competancy_destroy(request, id):
    language_competancy = LanguageCompetancy.objects.get(pk=id)
    user = request.user
    if language_competancy.user != request.user:
            request.user.message_set.create(message="You can't delete competancies that aren't yours")
            return HttpResponseRedirect(reverse("language_competancy_list"))

    if request.method == "POST" and request.POST["action"] == "delete":
        language_competancy.delete()
        request.user.message_set.create(message=_("Successfully deleted competancy '%s'") % language_competancy)
        return HttpResponseRedirect(reverse("language_competancy_list"))
    else:
        return HttpResponseRedirect(reverse("language_competancy_list"))

    return render_to_response(context_instance=RequestContext(request))

@login_required
def language_competancy_new(request, form_class=LanguageCompetancyForm, template_name="wt_languages/language_competancy_new.html"):
    if request.method == "POST":
        if request.POST["action"] == "create":
            language_competancy_form = form_class(request.user, request.POST)
            if language_competancy_form.is_valid():
                language_competancy = language_competancy_form.save(commit=False)
                language_competancy.user = request.user
                language_competancy.updated = datetime.now()
                language_competancy.save()
                # @@@ should message be different if published?
                request.user.message_set.create(message=_("Successfully saved competancy '%s'") % language_competancy)
                return HttpResponseRedirect(reverse("language_competancy_list"))
        else:
            language_competancy_form = form_class()
    else:
        language_competancy_form = form_class()

    return render_to_response(template_name, {
        "language_competancy_form": language_competancy_form
    }, context_instance=RequestContext(request))

@login_required
def language_competancy_edit(request, id, form_class=LanguageCompetancyForm, template_name="wt_languages/language_competancy_edit.html"):
    competancy = get_object_or_404(LanguageCompetancy, id=id)

    if request.method == "POST":
        if competancy.user != request.user:
            request.user.message_set.create(message="You can't edit competancies that aren't yours")
            return HttpResponseRedirect(reverse("language_competancy_list"))
        if request.POST["action"] == "update":
            language_competancy_form = form_class(request.user, request.POST, instance=competancy)
            if language_competancy_form.is_valid():
                language_competancy = language_competancy_form.save(commit=False)
                language_competancy.save()
                request.user.message_set.create(message=_("Successfully updated copmetancy '%s'") % language_competancy)
                return HttpResponseRedirect(reverse("language_competancy_list"))
        else:
            language_competancy_form = form_class(instance=competancy)
    else:
        language_competancy_form = form_class(instance=competancy)

    return render_to_response(template_name, {
        "language_competancy_form": language_competancy_form,
        "competancy": competancy,
    }, context_instance=RequestContext(request))

