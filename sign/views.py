from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView
from .models import BaseRegisterForm
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from main.models import Author


class BaseRegisterView(CreateView):
    model = User
    form_class = BaseRegisterForm
    success_url = '/'


@login_required
def upgrade_me(request):
    user = request.user
    basic_group = Group.objects.get(name='basic')
    authors_group = Group.objects.get(name='author')

    if basic_group in user.groups.all():
        basic_group.user_set.remove(user)

    if authors_group not in user.groups.all():
        authors_group.user_set.add(user)

        if not Author.objects.filter(user=user).exists():
            Author.objects.create(user=user)

    return redirect('/posts/')


# Create your views here.
