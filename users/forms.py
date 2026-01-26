from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'id': 'email'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name',
            'id': 'first_name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name',
            'id': 'last_name'
        })
    )
    
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'role'
        })
    )
    
    profile_photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'id': 'profile_photo',
            'accept': 'image/*'
        })
    )
    
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'date_of_birth'
        })
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name", 
            "last_name",
            "email",
            "role",
            "profile_photo",
            "date_of_birth",
            "password1",
            "password2",
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username',
                'id': 'username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'id': 'password1'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'id': 'password2'
        })
        
        # Update field labels
        self.fields['username'].label = 'Username'
        self.fields['email'].label = 'Email Address'
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].label = 'Last Name'
        self.fields['role'].label = 'Account Type'
        self.fields['profile_photo'].label = 'Profile Photo (Optional)'
        self.fields['date_of_birth'].label = 'Date of Birth (Optional)'
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Confirm Password'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


"""
This is to allow for the addition of the users by the admin who's accorded this priiledge
"""


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ["username", "email", "role", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])  # Hash password
        if commit:
            user.save()
        return user
