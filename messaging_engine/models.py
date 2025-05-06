from django.db import models
from website.models import Registered
from uuid import UUID

# Create your models here.

class MessageTemplate(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=225)
    subject = models.CharField(max_length=225)
    content_sms = models.TextField(blank=True, null=True)
    content_email_whatsapp = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Recipient(models.Model):
    registered_ref = models.UUIDField(null=True, blank=True)
    s_name = models.CharField(max_length=100, null=True, blank=True)
    f_name_m = models.CharField(max_length=100, null=True, blank=True)
    phone_no_m = models.CharField(max_length=20, null=True, blank=True)
    email_m = models.EmailField(null=True, blank=True)
    f_name_f = models.CharField(max_length=100, null=True, blank=True)
    phone_no_f = models.CharField(max_length=20, null=True, blank=True)
    email_f = models.EmailField(null=True, blank=True)
    is_user = models.BooleanField(default=False)  # Distinguishes database users from external data
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.s_name} - {self.f_name_m if self.f_name_m else 'Unknown'}"

class MessageLog(models.Model):
    recipient = models.ForeignKey('Recipient', on_delete=models.CASCADE)
    message = models.ForeignKey('Message', on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=50)  # Store the actual phone number used
    message_content = models.TextField()  # Store the actual message sent
    channel = models.CharField(max_length=50)  # SMS, Email, WhatsApp
    status = models.CharField(max_length=20)  # Pending, Success, Failure
    response_data = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    template = models.ForeignKey('MessageTemplate', on_delete=models.CASCADE)
    delivery_method = models.JSONField()
    delivery_time = models.CharField(max_length=20)
    schedule_date = models.DateField(null=True, blank=True)
    schedule_time = models.TimeField(null=True, blank=True)
    recipients = models.ManyToManyField(Recipient, related_name='messages')
    status = models.CharField(max_length=20, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Message ID {self.id} - Status: {self.status}"


