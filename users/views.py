from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from rest_framework import viewsets, permissions
from .serializers import UserSerializer
from django.views.generic import CreateView
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from .models import User
from .forms import CustomUserCreationForm, UserCreationForm


class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Allow filtering users based on their role.
        Admins can view all users, while instructors and students see only themselves.
        """
        user = self.request.user
        if user.role == "admin":
            return User.objects.all()
        return User.objects.filter(id=user.id)


class CustomLoginView(LoginView):
    template_name = "users/login.html"

    def get_success_url(self):
        return reverse_lazy("users:dashboard_redirect")

    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().first_name or form.get_user().username}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)


def custom_logout(request):
    logout(request)
    return redirect("login")


class RegisterUserView(CreateView):
    template_name = "users/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        messages.success(
            self.request, 
            f"Welcome {user.first_name}! Your account has been created successfully. You can now log in."
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request, 
            "Please correct the errors below and try again."
        )
        return super().form_invalid(form)


@login_required
def dashboard_redirect(request):
    user = request.user

    if user.role == "admin":
        return redirect("users:admin_dashboard")
    elif user.role == "instructor":
        return redirect("users:instructor_dashboard")
    elif user.role == "student":
        return redirect("users:student_dashboard")
    else:
        return redirect("home")


@login_required
def admin_dashboard(request):
    return render(request, "users/admin_dashboard.html")


@login_required
def instructor_dashboard(request):
    return render(request, "users/instructor_dashboard.html")


from courses.models import Course


@login_required
def student_dashboard(request):
    # Get courses the student is enrolled in through the Enrollment model
    from enrollments.models import Enrollment
    enrolled_courses = Course.objects.filter(enrollment__student=request.user)
    available_courses = Course.objects.exclude(enrollment__student=request.user)

    return render(
        request,
        "users/student_dashboard.html",
        {
            "enrolled_courses": enrolled_courses,
            "available_courses": available_courses,
        },
    )


def home(request):
    return render(request, "home.html")


@login_required
def add_user(request):
    if not request.user.is_superuser:  # Ensure only superusers can access
        return redirect("admin_dashboard")  # Redirect to admin panel instead of home

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("admin_dashboard")
    else:
        form = UserCreationForm()

    return render(request, "users/add_user.html", {"form": form})
