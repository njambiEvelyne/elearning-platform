from rest_framework import serializers
from .models import Quiz, Question, Submission, Answer


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = "__all__"


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = "__all__"


class SubmissionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, write_only=True)

    class Meta:
        model = Submission
        fields = "__all__"

    def create(self, validated_data):
        answers_data = validated_data.pop("answers")
        submission = Submission.objects.create(**validated_data)
        for answer_data in answers_data:
            Answer.objects.create(submission=submission, **answer_data)
        return submission
