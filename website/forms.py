from django import forms
from django.forms import ModelForm
from .models import *
import phonenumbers

class RegisterForm(ModelForm):
    class Meta:
        model = Registered
        fields = [
            's_name', 'f_name_m', 'phone_no_m', 'email_m',
            'f_name_f', 'phone_no_f', 'email_f', 'year_married',
            'attended_previous', 'how_heard_about_program', 'comments',
        ]
        widgets = {
            's_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Surname'}),
            'f_name_m': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Husband\'s First Name'}),
            'phone_no_m': forms.TextInput(attrs={'class': 'form-control phone-input', 'placeholder': 'Husband\'s Phone'}),
            'email_m': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Husband\'s Email'}),
            'f_name_f': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wife\'s First Name'}),
            'phone_no_f': forms.TextInput(attrs={'class': 'form-control phone-input', 'placeholder': 'Wife\'s Phone'}),
            'email_f': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Wife\'s Email'}),
            'year_married': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year Married', 'maxlength': '4'}),
            'attended_previous': forms.Select(choices=[('Yes', 'Yes'), ('No', 'No')], attrs={'class': 'form-control'}),
            'how_heard_about_program': forms.Select(choices=[
                ('Flyer', 'Flyer'),
                ('Friend', 'Friend'),
                ('Church', 'Church'),
                ('Social Media', 'Social Media'),
                ('Other', 'Other'),
            ], attrs={'class': 'form-control', 'id': 'heardAboutSelect'}),
            'comments': forms.Textarea(attrs = {'class': 'form-control', 'placeholder': 'Write your comments here...', 'rows': 3})
        }

    def clean_s_name(self):
        s_name = self.cleaned_data['s_name'].strip().capitalize()
        if ' ' in s_name:
            raise forms.ValidationError("Surname should not contain spaces.")
        return s_name

    def clean_f_name_m(self):
        f_name_m = self.cleaned_data['f_name_m'].strip().capitalize()
        if ' ' in f_name_m:
            raise forms.ValidationError("First name should not contain spaces.")
        return f_name_m

    def clean_f_name_f(self):
        f_name_f = self.cleaned_data['f_name_f'].strip().capitalize()
        if ' ' in f_name_f:
            raise forms.ValidationError("First name should not contain spaces.")
        return f_name_f

    def clean_phone_no_m(self):
        phone_no_m = self.cleaned_data['phone_no_m']
        return self.validate_phone(phone_no_m)

    def clean_phone_no_f(self):
        phone_no_f = self.cleaned_data['phone_no_f']
        return self.validate_phone(phone_no_f)

    def validate_phone(self, phone_number):
        try:
            # Add '+' if missing
            if not phone_number.startswith("+"):
                phone_number = "+" + phone_number
            parsed_number = phonenumbers.parse(phone_number, None)
            if not phonenumbers.is_valid_number(parsed_number):
                raise forms.ValidationError(f"'Invalid phone number format. {phone_number}'")
        except phonenumbers.phonenumberutil.NumberParseException:
            raise forms.ValidationError("Invalid phone number.")

        # Strip out the "+" before saving
        return phone_number.lstrip("+")

    def clean_year_married(self):
        year = self.cleaned_data['year_married']
        if not (1500 <= year <= 2025):
            raise forms.ValidationError("Please enter a valid 4-digit year between 1500 and 2025.")
        return year

    def clean_how_heard_about_program(self):
        how_heard = self.cleaned_data['how_heard_about_program']
        return how_heard  # Save selected option

class BreakoutForm(forms.ModelForm):
    class Meta:
        model = Breakouts
        fields = ['title', 'description', 'code_name', 'max_capacity']

    title = forms.CharField(
        label="Breakout Title",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    code_name = forms.CharField(
        label="Code Name (for tag)",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    max_capacity = forms.IntegerField(
        label="Maximum Number of Participants",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class FeedbackForm(forms.ModelForm):
    SATISFACTION_CHOICES = [
        ('Very satisfied', 'Very satisfied'),
        ('Satisfied', 'Satisfied'),
        ('Neutral', 'Neutral'),
        ('Dissatisfied', 'Dissatisfied'),
        ('Very dissatisfied', 'Very dissatisfied'),
    ]

    USABILITY_CHOICES = [
        ('Very easy', 'Very easy'),
        ('Easy', 'Easy'),
        ('Neutral', 'Neutral'),
        ('Difficult', 'Difficult'),
        ('Very difficult', 'Very difficult'),
    ]

    COMPLETION_CHOICES = [
        ('Everything worked perfectly', 'Everything worked perfectly'),
        ('Yes, mostly smooth', 'Yes, mostly smooth'),
        ('Neutral', 'Neutral'),
        ('I had a few issues', 'I had a few issues'),
        ('No, I couldn’t do most things', 'No, I couldn’t do most things'),
    ]

    satisfaction = forms.ChoiceField(
        choices=SATISFACTION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Satisfaction"
    )
    usability = forms.ChoiceField(
        choices=USABILITY_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Ease of Use"
    )
    completion = forms.ChoiceField(
        choices=COMPLETION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Completion"
    )
    suggestions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label="Suggestions"
    )
    seminar_ideas = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label="Seminar Ideas"
    )

    class Meta:
        model = Feedback
        fields = ['satisfaction', 'usability', 'completion', 'suggestions', 'seminar_ideas']