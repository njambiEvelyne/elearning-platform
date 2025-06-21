from django import forms
from .models import Course
from .models import Course

"""
This form is meant to enable the instructors to be able to add courses without logging in as admins
"""


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description"]
