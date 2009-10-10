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
#try:
#    from friends.models import Friendship
#    friends = True
#except ImportError:
#    friends = False
#
@login_required
def your_language_competancies(request, template_name="wt_languages/competancy_list.html"):
    lc = LanguageCompetancy.objects.filter(user__username=request.user.username)
    print lc

    return render_to_response(template_name, {
        "competancies": LanguageCompetancy.objects.filter(user__username=request.user.username),
    }, context_instance=RequestContext(request))

#@login_required
#def destroy(request, id):
#    language_competancy = LanguageCompetancy.objects.get(pk=id)
#    user = request.user
#    if language_competancy.user != request.user:
#            request.user.message_set.create(message="You can't delete competancies that aren't yours")
#            return HttpResponseRedirect(reverse("your_langauge_competancies"))
#
#    if request.method == "POST" and request.POST["action"] == "delete":
#        language_competancy.delete()
#        request.user.message_set.create(message=_("Successfully deleted competancy '%s'") % language_competancy)
#        return HttpResponseRedirect(reverse("your_langauge_competancies"))
#    else:
#        return HttpResponseRedirect(reverse("your_langauge_competancies"))
#
#    return render_to_response(context_instance=RequestContext(request))
#
@login_required
def new_language_competancy(request, form_class=LanguageCompetancyForm, template_name="wt_languages/new_competancy.html"):
    if request.method == "POST":
        if request.POST["action"] == "create":
            language_competancy_form = form_class(request.user, request.POST)
            if language_competancy_form.is_valid():
                language_competancy = language_competancy_form.save(commit=False)
                language_competancy.user = request.user
                language_competancy.updated = datetime.now()
                #if settings.BEHIND_PROXY:
                #    language_competancy.creator_ip = request.META["HTTP_X_FORWARDED_FOR"]
                #else:
                #    language_competancy.creator_ip = request.META['REMOTE_ADDR']
                language_competancy.save()
                # @@@ should message be different if published?
                request.user.message_set.create(message=_("Successfully saved competancy '%s'") % language_competancy)
                #if notification:
                #    # Send notification to interested parties
                #    notification.send((list of people who care), "blog_friend_post", {"post": blog})
            
                return HttpResponseRedirect(reverse("your_language_competancies"))
        else:
            language_competancy_form = form_class()
    else:
        language_competancy_form = form_class()

    return render_to_response(template_name, {
        "language_competancy_form": language_competancy_form
    }, context_instance=RequestContext(request))

#@login_required
#def edit(request, id, form_class=BlogForm, template_name="blog/edit.html"):
#    post = get_object_or_404(Post, id=id)
#
#    if request.method == "POST":
#        if post.author != request.user:
#            request.user.message_set.create(message="You can't edit posts that aren't yours")
#            return HttpResponseRedirect(reverse("blog_list_yours"))
#        if request.POST["action"] == "update":
#            blog_form = form_class(request.user, request.POST, instance=post)
#            if blog_form.is_valid():
#                blog = blog_form.save(commit=False)
#                blog.save()
#                request.user.message_set.create(message=_("Successfully updated post '%s'") % blog.title)
#                if notification:
#                    if blog.status == 2: # published
#                        if friends: # @@@ might be worth having a shortcut for sending to all friends
#                            notification.send((x['friend'] for x in Friendship.objects.friends_for_user(blog.author)), "blog_friend_post", {"post": blog})
#                
#                return HttpResponseRedirect(reverse("blog_list_yours"))
#        else:
#            blog_form = form_class(instance=post)
#    else:
#        blog_form = form_class(instance=post)
#
#    return render_to_response(template_name, {
#        "blog_form": blog_form,
#        "post": post,
#    }, context_instance=RequestContext(request))
#
