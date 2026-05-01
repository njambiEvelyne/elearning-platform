import os
from django.db import models
from users.models import User


def lesson_material_upload_path(instance, filename):
    """Store materials under media/courses/<course_id>/lessons/<lesson_id>/"""
    return f"courses/{instance.lesson.course.id}/lessons/{instance.lesson.id}/{filename}"


def course_note_upload_path(instance, filename):
    """Store course-level notes under media/courses/<course_id>/notes/"""
    return f"courses/{instance.course.id}/notes/{filename}"


class Course(models.Model):
    STATUS_CHOICES = [
        ('pending',  'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    title       = models.CharField(max_length=255)
    description = models.TextField()
    instructor  = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_courses',
        limit_choices_to={'role': 'instructor'},
    )
    created_by  = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_courses',
        limit_choices_to={'role': 'admin'},
    )
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='approved')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def is_available(self):
        return self.status == 'approved'


class Lesson(models.Model):
    STATUS_CHOICES = [
        ('draft',     'Draft'),
        ('published', 'Published'),
    ]

    course           = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title            = models.CharField(max_length=255)
    content          = models.TextField(blank=True, help_text='Written notes / lesson text')
    video_url        = models.URLField(blank=True, null=True, help_text='YouTube / Vimeo / any video URL')
    order            = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=0)
    status           = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['course', 'order', 'created_at']

    def __str__(self):
        return f"{self.course.title} — {self.title}"


class LessonMaterial(models.Model):
    ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx']

    lesson      = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='materials')
    title       = models.CharField(max_length=255, help_text='Display name for this file')
    file        = models.FileField(upload_to=lesson_material_upload_path)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.lesson.title} — {self.title}"

    @property
    def extension(self):
        _, ext = os.path.splitext(self.file.name)
        return ext.lower()

    @property
    def icon(self):
        ext = self.extension
        if ext == '.pdf':
            return 'fa-file-pdf'
        if ext in ('.doc', '.docx'):
            return 'fa-file-word'
        return 'fa-file'

    @property
    def filename(self):
        return os.path.basename(self.file.name)


class CourseNote(models.Model):
    """Course-level notes uploaded directly by the instructor."""
    ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx']

    course      = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='notes')
    title       = models.CharField(max_length=255)
    file        = models.FileField(upload_to=course_note_upload_path)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} — {self.title}"

    @property
    def extension(self):
        _, ext = os.path.splitext(self.file.name)
        return ext.lower()

    @property
    def icon(self):
        ext = self.extension
        if ext == '.pdf':
            return 'fa-file-pdf'
        if ext in ('.doc', '.docx'):
            return 'fa-file-word'
        return 'fa-file'

    @property
    def filename(self):
        return os.path.basename(self.file.name)
