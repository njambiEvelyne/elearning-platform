from django.views import View
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .permissions import IsInstructorOrReadOnly
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from enrollments.models import Enrollment, GuestPreview
from rest_framework.permissions import IsAuthenticated
import logging
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CourseForm, LessonForm
from django.http import Http404
from django.utils import timezone

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
        is_guest_preview = False
        guest_email = None
        lessons = []
        can_manage = False
        
        if request.user.is_authenticated:
            is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
            can_manage = request.user == course.instructor
            if is_enrolled or request.user.role == 'instructor':
                lessons = course.lessons.filter(status='published').order_by('order', 'created_at')
        else:
            # Check if guest has valid preview access
            guest_session_id = request.session.get('guest_session_id')
            guest_email = request.session.get('guest_email')
            guest_course_id = request.session.get('guest_course_id')
            
            if guest_session_id and guest_email and guest_course_id == course_id:
                guest_preview = GuestPreview.objects.filter(
                    course=course,
                    guest_session_id=guest_session_id,
                    guest_email=guest_email
                ).first()
                
                if guest_preview and not guest_preview.is_expired():
                    is_guest_preview = True
                    guest_preview.last_accessed_at = timezone.now()
                    guest_preview.save()
                    # Show first lesson only for guest preview
                    first_lesson = course.lessons.filter(status='published').order_by('order', 'created_at').first()
                    if first_lesson:
                        lessons = [first_lesson]
        
        context = {
            'course': course,
            'is_enrolled': is_enrolled,
            'is_guest_preview': is_guest_preview,
            'guest_email': guest_email,
            'lessons': lessons,
            'can_manage': can_manage,
            'lesson_count': course.lessons.filter(status='published').count(),
            'can_preview': not is_enrolled and not request.user.is_authenticated
        }
        return render(request, "courses/course_detail.html", context)


class LessonDetailView(View):
    def get(self, request, course_id, lesson_id):
        course = get_object_or_404(Course, id=course_id)
        lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
        
        is_instructor = False
        is_enrolled = False
        is_guest_preview = False
        guest_email = None
        
        if request.user.is_authenticated:
            # Check if user can access this lesson
            is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
            is_instructor = request.user == course.instructor
            
            if not (is_enrolled or is_instructor):
                messages.error(request, "You must be enrolled in this course to access lessons.")
                return redirect('courses:course_detail', course_id=course.id)
            
            # Only show published lessons to students
            if request.user.role == 'student' and lesson.status != 'published':
                raise Http404("Lesson not found")
        else:
            # Check if guest has valid preview access
            guest_session_id = request.session.get('guest_session_id')
            guest_email_session = request.session.get('guest_email')
            guest_course_id = request.session.get('guest_course_id')
            
            if guest_session_id and guest_email_session and guest_course_id == course_id:
                guest_preview = GuestPreview.objects.filter(
                    course=course,
                    guest_session_id=guest_session_id,
                    guest_email=guest_email_session
                ).first()
                
                if guest_preview and not guest_preview.is_expired():
                    is_guest_preview = True
                    guest_email = guest_email_session
                    guest_preview.last_accessed_at = timezone.now()
                    guest_preview.save()
                    
                    # Guests can only view the first published lesson
                    first_lesson = course.lessons.filter(status='published').order_by('order', 'created_at').first()
                    if not first_lesson or first_lesson.id != lesson.id:
                        messages.warning(request, "As a guest, you can only preview the first lesson. Please register to access all lessons.")
                        return redirect('courses:course_detail', course_id=course.id)
                else:
                    messages.error(request, "Your guest preview has expired or is invalid. Please start a new preview or register.")
                    return redirect('courses:course_detail', course_id=course.id)
            else:
                messages.error(request, "You must be enrolled in this course to access lessons. You can start a guest preview instead.")
                return redirect('courses:course_detail', course_id=course.id)
        
        # Get all lessons for navigation
        if is_instructor:
            all_lessons = course.lessons.all().order_by('order', 'created_at')
        else:
            all_lessons = course.lessons.filter(status='published').order_by('order', 'created_at')
            # Guests can only see the first lesson
            if is_guest_preview:
                all_lessons = all_lessons[:1]
        
        context = {
            'course': course,
            'lesson': lesson,
            'all_lessons': all_lessons,
            'is_instructor': is_instructor,
            'is_enrolled': is_enrolled,
            'is_guest_preview': is_guest_preview,
            'guest_email': guest_email,
        }
        return render(request, "courses/lesson_detail.html", context)


@login_required
def instructor_dashboard(request):
    if request.user.role != "instructor":
        messages.error(request, "Access denied. Instructor role required.")
        return redirect("home")

    courses = Course.objects.filter(instructor=request.user).prefetch_related('lessons')
    total_lessons = sum(c.lessons.count() for c in courses)
    total_students = sum(
        Enrollment.objects.filter(course=c).count() for c in courses
    )
    context = {
        'courses': courses,
        'total_lessons': total_lessons,
        'total_students': total_students,
    }
    return render(request, "courses/instructor_dashboard.html", context)


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
def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Course '{course.title}' updated successfully!")
            return redirect("courses:instructor_dashboard")
    else:
        form = CourseForm(instance=course)

    return render(request, "courses/add_course.html", {"form": form, "course": course, "editing": True})


@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, instructor=request.user)

    if request.method == "POST":
        title = course.title
        course.delete()
        messages.success(request, f"Course '{title}' deleted successfully.")
        return redirect("courses:instructor_dashboard")

    return render(request, "courses/delete_course.html", {"course": course})


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
