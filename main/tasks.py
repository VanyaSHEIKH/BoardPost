from celery import shared_task
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import *
from datetime import *
from django.utils import timezone


@shared_task
def send_notification(subscriber_email, subscriber_username, categories, post_title, post_url):
    message = (
        f'Здравствуйте, {subscriber_username}!\n\n'
        f'В категории "{", ".join(categories)}" добавлена новая новость: {post_title}.\n\n'
        f'Вы можете прочитать статью по следующей ссылке: {settings.SITE_URL}{post_url}'
    )
    try:
        send_mail(
            subject='Новая новость в вашей категории',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[subscriber_email],
        )
        print(f'Уведомление отправлено {subscriber_email}')
    except Exception as e:
        print(f'Ошибка при отправке уведомления {subscriber_email}: {e}')


@shared_task
def send_comment_notification(user_email, post_title, comment_text, post_url):
    subject = f'Ваш комментарий к "{post_title}"'
    message = f'Вы оставили комментарий: "{comment_text}".\n\nСсылка на пост: {settings.SITE_URL}{post_url}'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])



@shared_task
def send_weekly_celery():
    today = timezone.now()
    last_week = today - timedelta(days=7)
    posts = Post.objects.filter(date_in__gte=last_week)
    categories = posts.values_list('category__category', flat=True).distinct()
    subscribers = set(
        User.objects.filter(categories__category__in=categories).values_list('email', flat=True)
    )
    html_content = render_to_string('account/email/week_post.html', {
        'link': settings.SITE_URL,
        'posts': posts,
    })
    msg = EmailMultiAlternatives(
        subject='Объявления в любимой категории за неделю',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=list(subscribers),
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()


