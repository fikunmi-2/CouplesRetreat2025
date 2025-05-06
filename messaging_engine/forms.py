from django import forms
from .models import MessageTemplate

class MessageTemplateForm(forms.ModelForm):
    class Meta:
        model = MessageTemplate
        fields = ['title', 'subject', 'content_sms', 'content_email_whatsapp']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Message Title'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Message Subject'}),
            'content_sms': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Enter Message Content (SMS)', 'rows': 3}),
            'content_email_whatsapp': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Enter Message Content (Email and WhatsApp)',
                       'rows': 5}),
        }

    # Validation for the 'title' field
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title or len(title) < 3:
            raise forms.ValidationError("Title must be at least 3 characters long.")
        return title

    # Validation for the 'subject' field
    def clean_subject(self):
        subject = self.cleaned_data.get('subject')
        if not subject or len(subject) < 5:
            raise forms.ValidationError("Subject must be at least 5 characters long.")
        return subject

    # # Validation for the 'content_sms' field
    # def clean_content_sms(self):
    #     content_sms = self.cleaned_data.get('content_sms')
    #     if len(content_sms) > 160:
    #         raise forms.ValidationError("SMS content cannot exceed 160 characters.")
    #     # if not content_sms or len(content_sms) < 100:
    #     #     raise forms.ValidationError("SMS content must be at least 100 characters.")
    #     return content_sms
    #
    # # Validation for the 'content_email_whatsapp' field
    # def clean_content_email_whatsapp(self):
    #     content_email_whatsapp = self.cleaned_data.get('content_email_whatsapp')
    #     if not content_email_whatsapp or len(content_email_whatsapp) < 100:
    #         raise forms.ValidationError("Email/WhatsApp content must be at least 100 characters long.")
    #     return content_email_whatsapp

    # General form validation
    # def clean(self):
    #     cleaned_data = super().clean()
    #     title = cleaned_data.get('title')
    #     subject = cleaned_data.get('subject')
    #
    #     # Example: Ensure title and subject are not identical
    #     if title and subject and title.strip().lower() == subject.strip().lower():
    #         raise forms.ValidationError("Title and Subject cannot be identical.")
    #
    #     return cleaned_data