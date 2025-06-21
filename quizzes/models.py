from django.db import models
from users.models import User
from courses.models import Course


class Quiz(models.Model):
    title = models.CharField(max_length=255)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="quizzes")
    instructor = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={"role": "instructor"}
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_answer = models.CharField(
        max_length=1, choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")]
    )

    def __str__(self):
        return f"Q: {self.text}"


class Submission(models.Model):
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={"role": "student"}
    )
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(
        null=True, blank=True
    )  # Instructor will assign the score later

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}"


class Answer(models.Model):
    submission = models.ForeignKey(
        Submission, on_delete=models.CASCADE, related_name="answers"
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(
        max_length=1, choices=[("A", "A"), ("B", "B"), ("C", "C"), ("D", "D")]
    )

    def __str__(self):
        return f"{self.submission.student.username} - {self.question.text} ({self.selected_option})"
