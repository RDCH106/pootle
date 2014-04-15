#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009-2013 Zuza Software Foundation
#
# This file is part of Pootle.
#
# Pootle is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# Pootle is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Pootle; if not, see <http://www.gnu.org/licenses/>.

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.encoding import iri_to_uri
from django.utils.http import is_safe_url

from profiles.views import edit_profile

from pootle_misc.baseurl import redirect

from .forms import UserForm, pootle_profile_form_factory


def profile_edit(request):
    # FIXME: better to whitelist fields rather than blacklisting them
    excluded = ('user', 'rate', 'review_rate', 'score', 'ui_lang', )

    return edit_profile(request,
                        form_class=pootle_profile_form_factory(excluded),
                        template_name='profiles/settings/profile.html')


@login_required
def edit_personal_info(request):
    if request.POST:
        post = request.POST.copy()
        user_form = UserForm(post, instance=request.user)

        if user_form.is_valid():
            user_form.save()
            response = redirect(reverse('profiles_profile_detail',
                                args=[request.user.username]))
    else:
        user_form = UserForm(instance=request.user)

    template_vars = {
        'form': user_form,
    }

    return render_to_response('profiles/settings/personal.html', template_vars,
                              context_instance=RequestContext(request))


def redirect_after_login(request):
    redirect_to = request.REQUEST.get(auth.REDIRECT_FIELD_NAME, None)

    if not is_safe_url(url=redirect_to, host=request.get_host()):
        redirect_to = iri_to_uri(reverse('profiles_profile_detail',
                                 args=[request.user.username]))

    return redirect(redirect_to)


def login(request):
    """Log the user in."""
    if request.user.is_authenticated():
        return redirect_after_login(request)
    else:
        if request.POST:
            form = AuthenticationForm(request, data=request.POST)
            next = request.POST.get(auth.REDIRECT_FIELD_NAME, '')

            # Do login here.
            if form.is_valid():
                auth.login(request, form.get_user())

                language = request.POST.get('language')
                request.session['django_language'] = language

                return redirect_after_login(request)
        else:
            form = AuthenticationForm(request)
            next = request.GET.get(auth.REDIRECT_FIELD_NAME, '')

        context = {
            'form': form,
            'next': next,
        }

        return render_to_response("login.html", context,
                                  context_instance=RequestContext(request))


def logout(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('/')
