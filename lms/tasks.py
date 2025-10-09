from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils.timezone import now

from .models import Course, Subscription


@shared_task
def send_course_update_email(course_id):

    course = Course.objects.get(id=course_id)
    subscriptions = Subscription.objects.filter(course=course).select_related("user")

    for subscription in subscriptions:
        user_email = subscription.user.email
        if user_email:
            send_mail(
                subject=f"Обновление курса: {course.title}",
                message=f"Курс '{course.title}' был обновлен. Загляните, чтобы узнать подробности.",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user_email],
                fail_silently=True,
            )


User = get_user_model()


@shared_task
def deactivate_inactive_users():
    one_month_ago = now() - timedelta(days=30)
    inactive_users = User.objects.filter(last_login__lt=one_month_ago, is_active=True)
    count = inactive_users.update(is_active=False)
    return f"{count} пользователи деактивированы из-за неактивности."
