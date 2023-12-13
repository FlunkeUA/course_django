from celery import shared_task
from django.core.mail import send_mail
from hr.models import Employee, RequestStatistics
from django.utils import timezone
from datetime import timedelta


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
    statistics = RequestStatistics.objects.all()

    report_body = "Звіт про кількість запитів та винятків за вчорашній день:\n\n"
    for stat in statistics:
        report_body += f"Користувач: {stat.user.username}\n"
        report_body += f"Кількість запитів: {stat.requests_count}\n"
        report_body += f"Кількість винятків: {stat.exceptions_count}\n\n"

    admins = Employee.objects.filter(is_admin=True)

    subject = "Щоденний звіт про кількість запитів та винятків"
    send_mail(
        subject,
        report_body,
        'from@example.com',
        [admin.email for admin in admins],
        fail_silently=False,
    )
