from django.db import models


class Registered(models.Model):
	timestamp = models.CharField('Timestamp', max_length=120, null=True)
	s_name = models.CharField('Surname', max_length=120, null=True)
	f_name_m = models.CharField('Firstname Male', max_length=120, null=True)
	phone_no_m = models.CharField('Phone Number Male', max_length=40, null=True)
	email_m = models.EmailField('Email Male', null=True)
	f_name_f = models.CharField('Firstname Female', max_length=120, null=True)
	phone_no_f = models.CharField('Phone Number Female', max_length=40, null=True)
	email_f = models.EmailField('Email Female', null=True)
	no_of_years_married = models.CharField('Number of Years married', max_length=5, null=True)
	attended_previous = models.CharField('Attended Previous version?', max_length=120, null=True)
	how_heard_about_program = models.CharField('How you heard about program', max_length=120, null=True, blank=True)
	means_of_communication = models.CharField('Preferred means of communication', max_length=120, blank=True, null=True)
	comments = models.TextField(blank=True, null=True)
	present = models.CharField('Attendance', max_length=100, null=True)


	def __str__(self):
		return self.s_name