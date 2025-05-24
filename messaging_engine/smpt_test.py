import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "retreat.settings")  # replace 'retreat' with your project name
django.setup()


from django.core.mail import send_mail
from django.conf import settings

send_mail(
    subject='Test Email from Couples Retreat Project',
    message='This is a plain text test message sent from the Django shell.',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['fikunmi.aluko@gmail.com'],
    html_message='<p>This is a <strong>test email</strong> from your Django app.</p>',
)
