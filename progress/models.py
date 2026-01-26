from django.db import models
from users.models import User
from courses.models import Lesson, Course
from django.utils import timezone


class Progress(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={"role": "student"}
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_minutes = models.PositiveIntegerField(default=0, help_text="Time spent on lesson in minutes")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        unique_together = ['student', 'lesson']
        ordering = ['-updated_at']

    def __str__(self):
        status = "Completed" if self.completed else "In Progress"
        return f"{self.student.username} - {self.lesson.title} ({status})"
    
    def save(self, *args, **kwargs):
        if self.completed and not self.completed_at:
            self.completed_at = timezone.now()
        elif not self.completed:
            self.completed_at = None
        super().save(*args, **kwargs)


class CourseProgress(models.Model):
    """Track overall course progress for students"""
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={"role": "student"}
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    lessons_completed = models.PositiveIntegerField(default=0)
    total_lessons = models.PositiveIntegerField(default=0)
    progress_percentage = models.FloatField(default=0.0)
    last_accessed = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-last_accessed']

    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.progress_percentage:.1f}%)"
    
    def update_progress(self):
        """Update progress based on completed lessons"""
        completed_lessons = Progress.objects.filter(
            student=self.student,
            lesson__course=self.course,
            completed=True
        ).count()
        
        total_lessons = self.course.lessons.filter(status='published').count()
        
        self.lessons_completed = completed_lessons
        self.total_lessons = total_lessons
        self.progress_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        self.save()
        
        return self.progress_percentage
