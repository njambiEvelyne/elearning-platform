from django.db import models
from users.models import User

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

    def __str__(self):
        return self.title


"""
It is allowed for the URL field to be empty as not all lessons are to use videos

content can take in text like PDF's
"""


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    content = models.TextField()
    video_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="enrolled_students"
    )  # Important: Use a related_name
    enrolled_at = models.DateTimeField(auto_now_add=True)
