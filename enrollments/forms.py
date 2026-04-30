from django import forms


class EnrollmentForm(forms.Form):
    full_name = forms.CharField(max_length=255)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15, required=False)


class GuestPreviewForm(forms.Form):
    """
    Simple form for guests to request course preview access without permanent enrollment.
    Only requires an email address.
    """
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email to preview this course',
            'required': True
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required to preview the course.")
        return email
