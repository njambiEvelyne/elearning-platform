from django.db import models
from users.models import User
from django.core.validators import FileExtensionValidator
import os

"""
The model handles the various courses as there are many courses in an institution

1. The title of the course should be stated
2. Brief description of the course
3. The instructor is authorised to add the courses and also the time at which the courses and lessons are added updates automatically
"""


class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        limit_choices_to={"role": "instructor"},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_total_lessons(self):
        return self.lessons.filter(status='published').count()
    
    def get_course_outline(self):
        return self.lessons.filter(status='published').order_by('order', 'created_at')


"""
Enhanced Lesson model with better content management
"""


class Lesson(models.Model):
    LESSON_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    content = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of lesson in course")
    duration_minutes = models.PositiveIntegerField(default=0, help_text="Estimated duration in minutes")
    status = models.CharField(max_length=10, choices=LESSON_STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['course', 'order', 'created_at']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


"""
Course Materials - Files that instructors can upload for their courses
"""


def course_material_upload_path(instance, filename):
    """Generate upload path for course materials"""
    return f'course_materials/{instance.course.id}/{filename}'


class CourseMaterial(models.Model):
    MATERIAL_TYPE_CHOICES = [
        ('pdf', 'PDF Document'),
        ('doc', 'Word Document'),
        ('ppt', 'Presentation'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('other', 'Other'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="materials")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="materials", null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to=course_material_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=[
            'pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'jpg', 'jpeg', 'png', 
            'gif', 'mp4', 'avi', 'mov', 'mp3', 'wav', 'zip', 'rar'
        ])]
    )
    material_type = models.CharField(max_length=10, choices=MATERIAL_TYPE_CHOICES, default='other')
    file_size = models.PositiveIntegerField(default=0, help_text="File size in bytes")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def get_file_extension(self):
        return os.path.splitext(self.file.name)[1].lower()
    
    def get_file_size_display(self):
        """Return human readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.file_size = self.file.size
            # Auto-detect material type based on file extension
            ext = self.get_file_extension()
            if ext in ['.pdf']:
                self.material_type = 'pdf'
            elif ext in ['.doc', '.docx']:
                self.material_type = 'doc'
            elif ext in ['.ppt', '.pptx']:
                self.material_type = 'ppt'
            elif ext in ['.jpg', '.jpeg', '.png', '.gif']:
                self.material_type = 'image'
            elif ext in ['.mp4', '.avi', '.mov']:
                self.material_type = 'video'
            elif ext in ['.mp3', '.wav']:
                self.material_type = 'audio'
        super().save(*args, **kwargs)
