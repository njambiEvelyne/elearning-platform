from django.db import models
from users.models import User
from courses.models import Course
from django.utils import timezone
from datetime import timedelta


class Enrollment(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={"role": "student"}
    )
    course = models.ForeignKey(
        Course, related_name="enrollment", on_delete=models.CASCADE
    )
    # full_name = models.CharField(max_length=255)
    # email = models.EmailField()
    # phone_number = models.CharField(max_length=255, blank=True, null= True)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            "student",
            "course",
        ]  # A student cannot enroll twice in the same course

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"


class GuestPreview(models.Model):
    """
    Model to track guest (unauthenticated) temporary access to courses.
    Guests can preview courses without permanent enrollment.
    Access expires after a set duration.
    """
    course = models.ForeignKey(
        Course, related_name="guest_previews", on_delete=models.CASCADE
    )
    guest_email = models.EmailField()
    guest_session_id = models.CharField(max_length=255, unique=True)
    preview_started_at = models.DateTimeField(auto_now_add=True)
    last_accessed_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = [
            "course",
            "guest_session_id",
        ]
        verbose_name = "Guest Preview"
        verbose_name_plural = "Guest Previews"
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Guest preview expires after 24 hours
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if guest preview has expired"""
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"Guest preview of {self.course.title} by {self.guest_email}"
