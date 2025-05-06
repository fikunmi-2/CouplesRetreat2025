from django.db import models
import uuid
from django.contrib.auth.models import User

class Registered(models.Model):
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    labourer = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'is_staff': True},
        related_name='assigned_couples'
    )
    s_name = models.CharField('Surname', max_length=120, null=False)
    f_name_m = models.CharField('Husband\'s First Name', max_length=120, null=False)
    phone_no_m = models.CharField('Husband\'s Phone Number', max_length=40, unique=True, null=False)
    email_m = models.EmailField('Husband\'s Email', null=True, blank=True, unique=False)
    f_name_f = models.CharField('Wife\'s First Name', max_length=120, null=False)
    phone_no_f = models.CharField('Wife\'s Phone Number', max_length=40, unique=True, null=False)
    email_f = models.EmailField('Wife\'s Email', null=True, blank=True, unique=False)
    year_married = models.IntegerField('Year Married', null=False)
    attended_previous = models.CharField('Attended Previous Version?', max_length=3, choices=[('Yes', 'Yes'), ('No', 'No')], null=False)
    how_heard_about_program = models.CharField('How You Heard About Program', max_length=255, null=False)
    comments = models.TextField('Comments', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    has_downloaded_tag = models.BooleanField(default=False)
    has_confirmed_attendance = models.BooleanField(default=False)
    is_present = models.BooleanField(default=False)

    def __str__(self):
        return self.s_name

class Resource(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    link = models.URLField()

    def __str__(self):
        return self.name
