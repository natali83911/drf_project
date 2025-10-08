from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

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
