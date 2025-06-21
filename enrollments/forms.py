from django import forms


class EnrollmentForm(forms.Form):
    full_name = forms.CharField(max_length=255)
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15, required=False)
