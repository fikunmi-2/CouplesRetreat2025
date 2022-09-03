from django import forms
from django.forms import ModelForm
from .models import Registered


class RegisterForm(ModelForm):
	class Meta:
		model = Registered
		fields = ('s_name', 'f_name_m', 'phone_no_m', 'email_m', 'f_name_f', 'phone_no_f',
			'email_f', 'no_of_years_married', 'attended_previous', 'how_heard_about_program', 'means_of_communication', 'present', 'comments')
		widgets = { 
			's_name': forms.TextInput(attrs={'class': 'form-control'}), 
			'f_name_m': forms.TextInput(attrs={'class': 'form-control'}),
			'phone_no_m': forms.TextInput(attrs={'class': 'form-control'}),
			'email_m': forms.EmailInput(attrs={'class': 'form-control'}),
			'f_name_f': forms.TextInput(attrs={'class': 'form-control'}),
			'phone_no_f': forms.TextInput(attrs={'class': 'form-control'}),
			'email_f': forms.EmailInput(attrs={'class': 'form-control'}),
			'no_of_years_married': forms.TextInput(attrs={'class': 'form-control'}), 
			'attended_previous': forms.TextInput(attrs={'class': 'form-control'}),
			'how_heard_about_program': forms.Select(attrs={'class': 'form-control'}),
			'means_of_communication': forms.TextInput(attrs={'class': 'form-control'}),
			'present': forms.TextInput(attrs={'class': 'form-control'}),
			'comments': forms.Textarea(attrs={'class': 'form-control'})
		}