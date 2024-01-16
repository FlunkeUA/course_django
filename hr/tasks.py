from celery import shared_task
from django.core.mail import send_mail

from accounts import models
from hr.models import Employee, RequestStatistics
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth.models import User


@shared_task
def send_password_reset_emails():
    next_month = timezone.now().date() + timedelta(days=30)
    subject = "Зміна паролю необхідна"
    message_template = "Дорогий {}, будь ласка, змініть свій пароль до {}."

    for user in Employee.objects.all():
        message = message_template.format(user.username, next_month.strftime('%Y-%m-%d'))
        send_mail(
            subject,
            message,
            'from@example.com',
            [user.email],
            fail_silently=False,
        )


@shared_task
def send_daily_report():
    user_statistics = RequestStatistics.objects.values('user__username').annotate(
        request_count=models.Count('id'),
        exception_count=models.Sum(models.F('has_exception'))
    )

    report = "User Activity Report:\n\n"
    for user_stat in user_statistics:
        report += f"User: {user_stat['user__username']}, Requests: {user_stat['request_count']}, Exceptions: {user_stat['exception_count']}\n"

    subject = 'Daily User Activity Report'
    message = report
    from_email = 'your_email@example.com'
    admin_emails = [admin.email for admin in User.objects.filter(is_superuser=True)]

    send_mail(subject, message, from_email, admin_emails)
