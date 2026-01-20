from django.views import View
from rest_framework import viewsets
from .permissions import IsInstructorOrReadOnly
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from enrollments.models import Enrollment
from rest_framework.permissions import IsAuthenticated
import logging
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from .models import Course
from .forms import CourseForm

logger = logging.getLogger(__name__)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrReadOnly]

    def list(self, request, *args, **kwargs):
        logger.debug(f"Queryset: {self.queryset}")  # Better debugging
        return super().list(request, *args, **kwargs)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrReadOnly]


class CourseDetailView(View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        return render(request, "courses/course_detail.html", {"course": course})




@login_required
def instructor_dashboard(request):
    if request.user.role != "instructor":
        return redirect("home")

    courses = Course.objects.filter(instructor=request.user)
    return render(request, "courses/instructor_dashboard.html", {"courses": courses})


@login_required
def add_course(request):
    if request.user.role != "instructor":
        return redirect("instructor_dashboard")

    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            return redirect("instructor_dashboard")

    else:
        form = CourseForm()

    return render(request, "courses/add_course.html", {"form": form})


@login_required
def student_dashboard(request):
    """Display courses available for students or the ones they are enrolled in"""

    if request.user.role != "student":  # Ensure only students can access
        return redirect("home")

    # Show only courses the student is enrolled in
    enrolled_courses = Course.objects.filter(enrollment__student=request.user)

    return render(
        request, "students/student_dashboard.html", {"courses": enrolled_courses}
    )


@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user, course=course
    )

    if created:
        return redirect("student_dashboard")
    else:
        return redirect("course_detail", course_id=course.id)
