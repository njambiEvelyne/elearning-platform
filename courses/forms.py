from django import forms
from django.core.exceptions import ValidationError
from .models import Course, Lesson, LessonMaterial, CourseNote
from users.models import User

CTRL = 'form-control'
PILL_CTRL = 'form-control'


class AdminCourseForm(forms.ModelForm):
    """Admin creates / edits a course and assigns it to an instructor."""

    instructor = forms.ModelChoiceField(
        queryset=User.objects.filter(role='instructor'),
        required=False,
        empty_label='— Assign instructor later —',
        widget=forms.Select(attrs={'class': CTRL}),
    )

    class Meta:
        model  = Course
        fields = ['title', 'description', 'instructor', 'status']
        widgets = {
            'title':       forms.TextInput(attrs={'class': CTRL, 'placeholder': 'Course title'}),
            'description': forms.Textarea(attrs={'class': CTRL, 'rows': 4, 'placeholder': 'Course description'}),
            'status':      forms.Select(attrs={'class': CTRL}),
        }


class LessonForm(forms.ModelForm):
    """Instructor adds / edits a lesson (text notes + video URL)."""

    class Meta:
        model  = Lesson
        fields = ['title', 'content', 'video_url', 'order', 'duration_minutes', 'status']
        widgets = {
            'title':            forms.TextInput(attrs={'class': CTRL, 'placeholder': 'Lesson title'}),
            'content':          forms.Textarea(attrs={'class': CTRL, 'rows': 8,
                                                      'placeholder': 'Write lesson notes here…'}),
            'video_url':        forms.URLInput(attrs={'class': CTRL,
                                                      'placeholder': 'https://youtube.com/watch?v=… (optional)'}),
            'order':            forms.NumberInput(attrs={'class': CTRL, 'min': '0'}),
            'duration_minutes': forms.NumberInput(attrs={'class': CTRL, 'min': '0',
                                                         'placeholder': 'e.g. 30'}),
            'status':           forms.Select(attrs={'class': CTRL}),
        }


class LessonMaterialForm(forms.ModelForm):
    """Instructor uploads a PDF / DOC / DOCX file to a lesson."""

    ALLOWED = ['.pdf', '.doc', '.docx']

    class Meta:
        model  = LessonMaterial
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': CTRL, 'placeholder': 'e.g. Week 1 Notes'}),
            'file':  forms.FileInput(attrs={'class': CTRL, 'accept': '.pdf,.doc,.docx'}),
        }

    def clean_file(self):
        f = self.cleaned_data.get('file')
        if f:
            import os
            _, ext = os.path.splitext(f.name)
            if ext.lower() not in self.ALLOWED:
                raise ValidationError(
                    f"Only {', '.join(self.ALLOWED)} files are allowed. "
                    f"You uploaded: {ext or 'unknown'}"
                )
        return f


class CourseNoteForm(forms.ModelForm):
    """Instructor uploads a course-level PDF / DOC / DOCX note."""

    ALLOWED = ['.pdf', '.doc', '.docx']

    class Meta:
        model  = CourseNote
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': CTRL, 'placeholder': 'e.g. Course Overview, Week 1 Slides'}),
            'file':  forms.FileInput(attrs={'class': CTRL, 'accept': '.pdf,.doc,.docx'}),
        }

    def clean_file(self):
        f = self.cleaned_data.get('file')
        if f:
            import os
            _, ext = os.path.splitext(f.name)
            if ext.lower() not in self.ALLOWED:
                raise ValidationError(
                    f"Only {', '.join(self.ALLOWED)} files are allowed. "
                    f"You uploaded: {ext or 'unknown'}"
                )
        return f
