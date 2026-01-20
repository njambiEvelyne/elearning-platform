from django import forms
from .models import Course, Lesson

"""
This form is meant to enable the instructors to be able to add courses without logging in as admins
"""


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["title", "description"]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter course title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter course description'}),
        }


class LessonForm(forms.ModelForm):
    """
    Form for instructors to add and edit lessons
    """
    class Meta:
        model = Lesson
        fields = ["title", "content", "video_url", "order", "duration_minutes", "status"]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter lesson title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'Enter lesson content'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/video (optional)'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'placeholder': 'Duration in minutes'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
