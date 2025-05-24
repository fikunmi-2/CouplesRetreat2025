from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class CustomUserCreationForm(forms.ModelForm):
    ROLE_CHOICES = [
        ('superuser', 'Superuser'),
        ('labourer', 'Labourer'),
    ]
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Password"
    )
    is_superuser = forms.BooleanField(required=False, label="Make Superuser")
    is_labourer = forms.BooleanField(required=False, label="Assign as Labourer")
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label="Email"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_superuser', 'is_labourer']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        is_superuser = cleaned_data.get('is_superuser')
        is_labourer = cleaned_data.get('is_labourer')

        if not is_superuser and not is_labourer:
            raise forms.ValidationError("User must be either a Superuser or a Labourer (or both).")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if self.cleaned_data['is_superuser'] and self.cleaned_data['is_labourer']:
            user.is_superuser = True
            user.is_staff = True
        elif self.cleaned_data['is_superuser']:
            user.is_superuser = True
            user.is_staff = False
        elif self.cleaned_data['is_labourer']:
            user.is_superuser = False
            user.is_staff = True
        else:
            user.is_superuser = False
            user.is_staff = False

        if commit:
            user.save()
        return user


class EditUserForm(forms.ModelForm):
    password = forms.CharField(
        label='New Password',
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    is_superuser = forms.BooleanField(
        required=False,
        label="Make Superuser"
    )
    is_labourer = forms.BooleanField(
        required=False,
        label="Assign as Labourer"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'is_superuser', 'is_labourer']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['is_labourer'].initial = self.instance.is_staff

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password)
        return password

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This username is already taken.")
        return username


    def save(self, commit=True):
        user = super().save(commit=False)

        user.is_staff = self.cleaned_data['is_labourer']
        user.is_superuser = self.cleaned_data['is_superuser']

        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)

        if commit:
            user.save()
        return user