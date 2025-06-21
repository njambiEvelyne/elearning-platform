from django.db import models

from django.contrib.auth.models import AbstractUser

"""
Creating the users of the platform
"""


class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("instructor", "Instructor"),
        ("student", "Student"),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="student")
    profile_photo = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.username
