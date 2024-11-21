from django.shortcuts import render

# Create your views here.
from django.core.mail import send_mail
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from django.conf import settings
from .filters import *
from .models import *
from .forms import *
from django.utils.translation import gettext as _
import pytz

from .tasks import send_notification


class PostsList(ListView):
    model = Post
    ordering = 'date_in'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_in_page'] = self.paginate_by
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs


class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

    def get_object(self, *args, **kwargs):
        obj = cache.get(f'post-{self.kwargs["pk"]}',
                        None)
        if not obj:
            obj = super().get_object(queryset=self.queryset)
            cache.set(f'post-{self.kwargs["pk"]}', obj)
        return obj


class PostsSearch(ListView):
    model = Post
    ordering = '-date_in'
    template_name = 'post_search.html'
    context_object_name = 'posts'

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class PostCreate(CreateView):
    permission_required = ('main.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user.author
        today = date.today()
        post_limit = Post.objects.filter(author=post.author, date_in__date=today).count()
        if post_limit >= 5:
            return render(self.request, template_name='post_limit.html', context={'author': post.author})
        post.save()
        return super().form_valid(form)


class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('main.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('main.delete_post',)
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('Posts_list')


class CategoryList(ListView):
    model = Category
    template_name = 'category_list.html'
    context_object_name = 'categories'


class CategoryDetail(DetailView):
    model = Category
    template_name = 'category.html'
    context_object_name = 'category'


@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscriber.add(user)

    send_mail(
        'Подписка на категорию',
        f'Вы успешно подписались на категорию: {category.category}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

    massage = 'Успешная подписка на категорию'
    return render(request, 'subscribe.html', {'category': category, 'massage': massage})


@login_required
def unsubscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)

    category.subscriber.remove(user)

    send_mail(
        'Отписка от категории',
        f'Вы успешно отписались от категории: {category.category}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

    massage = 'Вы успешно отписались категории'
    return render(request, 'unsubscribe.html', {'category': category, 'massage': massage})


class Index(View):
    def get(self, request):
        curent_time = timezone.now()

        models = Category.objects.all()

        context = {
            'models': models,
            'current_time': timezone.now(),
            'timezones': pytz.common_timezones
        }

        return HttpResponse(render(request, 'index.html', context))

    def post(self, request):
        request.session['django_timezone'] = request.POST['timezone']
        return redirect('/posts/categories')


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('Post_detail', pk=post.pk)  # Перенаправляем на страницу поста после добавления комментария
    else:
        form = CommentForm()

    return render(request, 'add_comment.html', {'form': form, 'post': post})


@csrf_exempt
@login_required
def user_comments(request):
    comments = Comment.objects.filter(user=request.user)
    return render(request, 'user_comments.html', {'comments': comments})


@login_required
def delete_comment(request):
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        print(f"Deleting comment ID: {comment_id}")  # Отладка
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)
        comment.delete()
        return JsonResponse({'success': True})


@login_required
def accept_comment(request):
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)
        comment.is_accepted = True
        comment.save()
        return JsonResponse({'success': True})


def delete_comment(request):
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        comment = get_object_or_404(Comment, id=comment_id)
        user_email = comment.user.email
        comment.delete()

        send_mail(
            'Ваш комментарий был удален',
            'Ваш комментарий был успешно удален.',
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )

        return JsonResponse({'success': True})


def accept_comment(request):
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')
        comment = get_object_or_404(Comment, id=comment_id)
        user_email = comment.user.email
        comment.accepted = True
        comment.save()

        send_mail(
            'Ваш комментарий был принят',
            'Ваш комментарий был успешно принят и ожидает ответа.',
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )

        return JsonResponse({'success': True})
