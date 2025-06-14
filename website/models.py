from django.db import models
import uuid
from django.contrib.auth.models import User

class Breakouts(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    code_name = models.CharField(max_length=20, unique=True)
    max_capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.title

    def slots_remaining(self):
        return self.max_capacity - self.registered_set.count()

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
    is_present_day2 = models.BooleanField(default=False)
    labourer_note = models.TextField("Labourer Note", blank=True)
    breakout = models.ForeignKey(Breakouts, on_delete=models.SET_NULL, null=True, blank=True, related_name='registered_set')

    def __str__(self):
        return self.s_name

class Resource(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    link = models.URLField()
    priority = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Question(models.Model):
    surname = models.CharField(max_length=100)
    unique_id = models.UUIDField()
    text = models.TextField()
    remember = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q from {self.surname} @ {self.created_at.strftime('%Y-%m-%d %H:%M')}"