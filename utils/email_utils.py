# utils/email_utils.py

from django.core.mail import send_mail
from django.conf import settings

def send_reset_password_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )
