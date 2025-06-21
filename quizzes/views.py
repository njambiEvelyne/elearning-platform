from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Quiz, Question, Submission, Answer
from .serializers import (
    QuizSerializer,
    QuestionSerializer,
    SubmissionSerializer,
    AnswerSerializer,
)
from rest_framework.response import Response
from rest_framework.decorators import action


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]


class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]
    """"
    This will allow the instructor to assign scores
    """

    @action(detail=True, methods=["post"], url_path="grade")
    def grade_submission(self, request, pk=None):
        submission = self.get_object()
        if submission.quiz.instructor != request.user:
            return Response(
                {"error": "Only the instructor can grade this submission."}, status=403
            )

        score = request.data.get("score")
        if score is None:
            return Response({"error": "Score is required."}, status=400)

        submission.score = score
        submission.save()
        return Response({"message": "Score assigned successfully."})


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated]
