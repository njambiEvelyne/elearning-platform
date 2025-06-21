from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from quizzes.serializers import AnswerSerializer
from .models import User
from rest_framework import serializers

User = get_user_model()


class RegisterUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [AllowAny]


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "id", "username", "email", "password"


def create(self, validated_data):
    user = User.objects.create_user(
        username=validated_data["username"],
        email=validated_data["email"],
        password=validated_data["password"],
    )
    return user
