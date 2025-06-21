from django.db import models
from users.models import User
from courses.models import Course


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
