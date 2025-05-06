from django.contrib import admin
from .models import Message, Recipient  # Import your models

# Register the models
admin.site.register(Message)
admin.site.register(Recipient)
