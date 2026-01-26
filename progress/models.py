from django.db import models
from users.models import User
from courses.models import Lesson


class Progress(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={"role": "student"}
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
