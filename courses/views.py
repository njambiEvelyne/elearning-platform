from django.views import View
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .permissions import IsInstructorOrReadOnly
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from enrollments.models import Enrollment
from rest_framework.permissions import IsAuthenticated
import logging
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CourseForm, LessonForm
from django.http import Http404

logger = logging.getLogger(__name__)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrReadOnly]

    def list(self, request, *args, **kwargs):
        logger.debug(f"Queryset: {self.queryset}")
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        """Get all published lessons for a course"""
        course = self.get_object()
        lessons = course.lessons.filter(status='published').order_by('order', 'created_at')
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrReadOnly]

    def get_queryset(self):
        """Filter lessons based on user role"""
        if self.request.user.role == 'instructor':
            # Instructors see all their lessons
            return Lesson.objects.filter(course__instructor=self.request.user)
        else:
            # Students see only published lessons from enrolled courses
            enrolled_courses = Course.objects.filter(enrollment__student=self.request.user)
            return Lesson.objects.filter(course__in=enrolled_courses, status='published')


class CourseDetailView(View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        is_enrolled = False
        lessons = []
        
        if request.user.is_authenticated:
            is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
            if is_enrolled or request.user.role == 'instructor':
                lessons = course.lessons.filter(status='published').order_by('order', 'created_at')
        
        context = {
            'course': course,
            'is_enrolled': is_enrolled,
            'lessons': lessons,
            'can_manage': request.user.is_authenticated and request.user == course.instructor
        }
        return render(request, "courses/course_detail.html", context)


class LessonDetailView(View):
    def get(self, request, course_id, lesson_id):
        course = get_object_or_404(Course, id=course_id)
        lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
        
        # Check if user can access this lesson
        if not request.user.is_authenticated:
            return redirect('users:login')
        
        # Check enrollment or instructor access
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
        is_instructor = request.user == course.instructor
        
        if not (is_enrolled or is_instructor):
            messages.error(request, "You must be enrolled in this course to access lessons.")
            return redirect('courses:course_detail', course_id=course.id)
        
        # Only show published lessons to students
        if request.user.role == 'student' and lesson.status != 'published':
            raise Http404("Lesson not found")
        
        # Get all lessons for navigation
        if is_instructor:
            all_lessons = course.lessons.all().order_by('order', 'created_at')
        else:
            all_lessons = course.lessons.filter(status='published').order_by('order', 'created_at')
        
        context = {
            'course': course,
            'lesson': lesson,
            'all_lessons': all_lessons,
            'is_instructor': is_instructor
        }
        return render(request, "courses/lesson_detail.html", context)


@login_required
def instructor_dashboard(request):
    if request.user.role != "instructor":
        messages.error(request, "Access denied. Instructor role required.")
        return redirect("home")

    courses = Course.objects.filter(instructor=request.user)
    return render(request, "courses/instructor_dashboard.html", {"courses": courses})


@login_required
def add_course(request):
    if request.user.role != "instructor":
        messages.error(request, "Access denied. Instructor role required.")
        return redirect("home")

    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, f"Course '{course.title}' created successfully!")
            return redirect("courses:instructor_dashboard")
    else:
        form = CourseForm()

    return render(request, "courses/add_course.html", {"form": form})


@login_required
def manage_lessons(request, course_id):
    """View for instructors to manage lessons in their course"""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lessons = course.lessons.all().order_by('order', 'created_at')
    
    context = {
        'course': course,
        'lessons': lessons
    }
    return render(request, "courses/manage_lessons.html", context)


@login_required
def add_lesson(request, course_id):
    """Add a new lesson to a course"""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    
    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, f"Lesson '{lesson.title}' added successfully!")
            return redirect("courses:manage_lessons", course_id=course.id)
    else:
        form = LessonForm()
    
    context = {
        'form': form,
        'course': course,
        'action': 'Add'
    }
    return render(request, "courses/lesson_form.html", context)


@login_required
def edit_lesson(request, course_id, lesson_id):
    """Edit an existing lesson"""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    
    if request.method == "POST":
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, f"Lesson '{lesson.title}' updated successfully!")
            return redirect("courses:manage_lessons", course_id=course.id)
    else:
        form = LessonForm(instance=lesson)
    
    context = {
        'form': form,
        'course': course,
        'lesson': lesson,
        'action': 'Edit'
    }
    return render(request, "courses/lesson_form.html", context)


@login_required
def delete_lesson(request, course_id, lesson_id):
    """Delete a lesson"""
    course = get_object_or_404(Course, id=course_id, instructor=request.user)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    
    if request.method == "POST":
        lesson_title = lesson.title
        lesson.delete()
        messages.success(request, f"Lesson '{lesson_title}' deleted successfully!")
        return redirect("courses:manage_lessons", course_id=course.id)
    
    context = {
        'course': course,
        'lesson': lesson
    }
    return render(request, "courses/delete_lesson.html", context)


@login_required
def student_dashboard(request):
    """Display courses available for students or the ones they are enrolled in"""
    if request.user.role != "student":
        messages.error(request, "Access denied. Student role required.")
        return redirect("home")

    # Show courses the student is enrolled in
    enrolled_courses = Course.objects.filter(enrollment__student=request.user)
    # Show available courses for enrollment
    available_courses = Course.objects.exclude(enrollment__student=request.user)

    context = {
        'enrolled_courses': enrolled_courses,
        'available_courses': available_courses
    }
    return render(request, "courses/student_dashboard.html", context)


@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.user.role != 'student':
        messages.error(request, "Only students can enroll in courses.")
        return redirect("courses:course_detail", course_id=course.id)
    
    # Check if already enrolled
    existing_enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    
    if existing_enrollment:
        # Already enrolled - show a warm message
        context = {
            'course': course,
            'enrollment': existing_enrollment,
            'already_enrolled': True,
            'lessons_count': course.lessons.count(),
            'instructor': course.instructor,
        }
        return render(request, "courses/enrollment_success.html", context)
    
    # Process enrollment
    enrollment = Enrollment.objects.create(student=request.user, course=course)
    
    # Show success page with warm welcome
    context = {
        'course': course,
        'enrollment': enrollment,
        'already_enrolled': False,
        'lessons_count': course.lessons.count(),
        'instructor': course.instructor,
    }
    return render(request, "courses/enrollment_success.html", context)


@login_required
def unenroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    if request.user.role != 'student':
        messages.error(request, "Only students can manage course enrollments.")
        return redirect("courses:course_detail", course_id=course.id)
    
    # Check if enrolled
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    
    if not enrollment:
        messages.info(request, "You are not enrolled in this course.")
        return redirect("courses:course_detail", course_id=course.id)
    
    if request.method == 'POST':
        # Process unenrollment
        enrollment.delete()
        
        # Show unenrollment confirmation page
        context = {
            'course': course,
            'lessons_count': course.lessons.count(),
            'instructor': course.instructor,
            'unenrolled': True,
        }
        return render(request, "courses/unenrollment_success.html", context)
    
    # Show confirmation page
    context = {
        'course': course,
        'enrollment': enrollment,
        'lessons_count': course.lessons.count(),
        'instructor': course.instructor,
    }
    return render(request, "courses/unenroll_confirm.html", context)


def courses_list(request):
    """
    Display all available courses for browsing.
    Accessible to both authenticated and non-authenticated users.
    """
    courses = Course.objects.all().order_by('-created_at')
    
    # If user is authenticated and is a student, get their enrollments
    enrolled_course_ids = []
    if request.user.is_authenticated and request.user.role == 'student':
        enrolled_course_ids = list(
            Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True)
        )
    
    context = {
        'courses': courses,
        'enrolled_course_ids': enrolled_course_ids,
        'total_courses': courses.count(),
    }
    return render(request, "courses/courses_list.html", context)
