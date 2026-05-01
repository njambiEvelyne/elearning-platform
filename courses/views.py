import os
from django.views import View
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404, FileResponse, HttpResponseForbidden
from django.utils import timezone

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Course, Lesson, LessonMaterial, CourseNote
from .serializers import CourseSerializer, LessonSerializer
from .forms import AdminCourseForm, LessonForm, LessonMaterialForm, CourseNoteForm
from .permissions import IsInstructorOrReadOnly
from enrollments.models import Enrollment
from users.models import User

import logging
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  REST API ViewSets (unchanged)
# ─────────────────────────────────────────────

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.filter(status='approved')
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrReadOnly]

    def list(self, request, *args, **kwargs):
        logger.debug(f"Queryset: {self.queryset}")
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        course = self.get_object()
        lessons = course.lessons.filter(status='published').order_by('order', 'created_at')
        serializer = LessonSerializer(lessons, many=True)
        return Response(serializer.data)


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrReadOnly]

    def get_queryset(self):
        if self.request.user.role == 'instructor':
            return Lesson.objects.filter(course__instructor=self.request.user)
        enrolled = Course.objects.filter(enrollment__student=self.request.user)
        return Lesson.objects.filter(course__in=enrolled, status='published')


# ─────────────────────────────────────────────
#  Public / Student views
# ─────────────────────────────────────────────

def courses_list(request):
    """Browse all approved courses — accessible to everyone."""
    courses = Course.objects.filter(status='approved').order_by('-created_at')
    enrolled_ids = []
    if request.user.is_authenticated and request.user.role == 'student':
        enrolled_ids = list(
            Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True)
        )
    return render(request, 'courses/courses_list.html', {
        'courses': courses,
        'enrolled_course_ids': enrolled_ids,
        'total_courses': courses.count(),
    })


class CourseDetailView(View):
    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id, status='approved')
        is_enrolled = False
        can_manage  = False
        lessons     = []

        if request.user.is_authenticated:
            is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
            can_manage  = request.user == course.instructor or request.user.role == 'admin'
            if is_enrolled or can_manage:
                lessons = course.lessons.filter(status='published').order_by('order', 'created_at')

        return render(request, 'courses/course_detail.html', {
            'course':       course,
            'is_enrolled':  is_enrolled,
            'can_manage':   can_manage,
            'lessons':      lessons,
            'lesson_count': course.lessons.filter(status='published').count(),
        })


class LessonDetailView(View):
    def get(self, request, course_id, lesson_id):
        course = get_object_or_404(Course, id=course_id, status='approved')
        lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access lessons.")
            return redirect('users:login')

        is_instructor = request.user == course.instructor or request.user.role == 'admin'
        is_enrolled   = Enrollment.objects.filter(student=request.user, course=course).exists()

        if not (is_enrolled or is_instructor):
            messages.error(request, "You must be enrolled to access lessons.")
            return redirect('courses:course_detail', course_id=course.id)

        if request.user.role == 'student' and lesson.status != 'published':
            raise Http404("Lesson not found")

        if is_instructor:
            all_lessons = course.lessons.all().order_by('order', 'created_at')
        else:
            all_lessons = course.lessons.filter(status='published').order_by('order', 'created_at')

        materials = lesson.materials.all().order_by('uploaded_at')

        return render(request, 'courses/lesson_detail.html', {
            'course':       course,
            'lesson':       lesson,
            'all_lessons':  all_lessons,
            'materials':    materials,
            'is_instructor': is_instructor,
            'is_enrolled':  is_enrolled,
        })


@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        messages.error(request, "Access denied.")
        return redirect('home')
    enrolled   = Course.objects.filter(enrollment__student=request.user, status='approved')
    available  = Course.objects.filter(status='approved').exclude(enrollment__student=request.user)
    return render(request, 'courses/student_dashboard.html', {
        'enrolled_courses':  enrolled,
        'available_courses': available,
    })


@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id, status='approved')
    if request.user.role != 'student':
        messages.error(request, "Only students can enroll.")
        return redirect('courses:course_detail', course_id=course.id)

    existing = Enrollment.objects.filter(student=request.user, course=course).first()
    if existing:
        return render(request, 'courses/enrollment_success.html', {
            'course': course, 'enrollment': existing,
            'already_enrolled': True, 'lessons_count': course.lessons.count(),
            'instructor': course.instructor,
        })

    enrollment = Enrollment.objects.create(student=request.user, course=course)
    return render(request, 'courses/enrollment_success.html', {
        'course': course, 'enrollment': enrollment,
        'already_enrolled': False, 'lessons_count': course.lessons.count(),
        'instructor': course.instructor,
    })


@login_required
def unenroll_course(request, course_id):
    course     = get_object_or_404(Course, id=course_id)
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()

    if not enrollment:
        messages.info(request, "You are not enrolled in this course.")
        return redirect('courses:course_detail', course_id=course.id)

    if request.method == 'POST':
        enrollment.delete()
        return render(request, 'courses/unenrollment_success.html', {
            'course': course, 'lessons_count': course.lessons.count(),
            'instructor': course.instructor,
        })

    return render(request, 'courses/unenroll_confirm.html', {
        'course': course, 'enrollment': enrollment,
        'lessons_count': course.lessons.count(), 'instructor': course.instructor,
    })


# ─────────────────────────────────────────────
#  ADMIN — course management
# ─────────────────────────────────────────────

def _require_admin(request):
    if not request.user.is_authenticated or request.user.role != 'admin':
        messages.error(request, "Admin access required.")
        return redirect('home')
    return None


@login_required
def admin_course_list(request):
    guard = _require_admin(request)
    if guard:
        return guard
    courses = Course.objects.all().order_by('-created_at')
    return render(request, 'courses/admin_course_list.html', {'courses': courses})


@login_required
def admin_add_course(request):
    guard = _require_admin(request)
    if guard:
        return guard
    if request.method == 'POST':
        form = AdminCourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.created_by = request.user
            course.save()
            messages.success(request, f"Course '{course.title}' created.")
            return redirect('courses:admin_course_list')
    else:
        form = AdminCourseForm()
    return render(request, 'courses/admin_course_form.html', {'form': form, 'action': 'Create'})


@login_required
def admin_edit_course(request, course_id):
    guard = _require_admin(request)
    if guard:
        return guard
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        form = AdminCourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f"Course '{course.title}' updated.")
            return redirect('courses:admin_course_list')
    else:
        form = AdminCourseForm(instance=course)
    return render(request, 'courses/admin_course_form.html', {
        'form': form, 'course': course, 'action': 'Edit'
    })


@login_required
def admin_delete_course(request, course_id):
    guard = _require_admin(request)
    if guard:
        return guard
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        title = course.title
        course.delete()
        messages.success(request, f"Course '{title}' deleted.")
        return redirect('courses:admin_course_list')
    return render(request, 'courses/delete_course.html', {'course': course})


# ─────────────────────────────────────────────
#  INSTRUCTOR — lesson & material management
# ─────────────────────────────────────────────

def _require_instructor(request, course):
    """Return redirect if user is not the assigned instructor."""
    if not request.user.is_authenticated:
        return redirect('users:login')
    if request.user != course.instructor and request.user.role != 'admin':
        messages.error(request, "You are not assigned to this course.")
        return redirect('courses:instructor_dashboard')
    return None


@login_required
def instructor_dashboard(request):
    if request.user.role not in ('instructor', 'admin'):
        messages.error(request, "Instructor access required.")
        return redirect('home')
    courses = Course.objects.filter(instructor=request.user).prefetch_related('lessons')
    total_lessons  = sum(c.lessons.count() for c in courses)
    total_students = sum(c.enrollment.count() for c in courses)
    return render(request, 'courses/instructor_dashboard.html', {
        'courses':        courses,
        'total_lessons':  total_lessons,
        'total_students': total_students,
    })


@login_required
def manage_lessons(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    guard  = _require_instructor(request, course)
    if guard:
        return guard
    lessons = course.lessons.all().order_by('order', 'created_at')
    return render(request, 'courses/manage_lessons.html', {
        'course': course, 'lessons': lessons
    })


@login_required
def add_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    guard  = _require_instructor(request, course)
    if guard:
        return guard
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, f"Lesson '{lesson.title}' added.")
            return redirect('courses:manage_lessons', course_id=course.id)
    else:
        form = LessonForm()
    return render(request, 'courses/lesson_form.html', {
        'form': form, 'course': course, 'action': 'Add'
    })


@login_required
def edit_lesson(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    guard  = _require_instructor(request, course)
    if guard:
        return guard
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson)
        if form.is_valid():
            form.save()
            messages.success(request, f"Lesson '{lesson.title}' updated.")
            return redirect('courses:manage_lessons', course_id=course.id)
    else:
        form = LessonForm(instance=lesson)
    return render(request, 'courses/lesson_form.html', {
        'form': form, 'course': course, 'lesson': lesson, 'action': 'Edit'
    })


@login_required
def delete_lesson(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    guard  = _require_instructor(request, course)
    if guard:
        return guard
    if request.method == 'POST':
        title = lesson.title
        lesson.delete()
        messages.success(request, f"Lesson '{title}' deleted.")
        return redirect('courses:manage_lessons', course_id=course.id)
    return render(request, 'courses/delete_lesson.html', {
        'course': course, 'lesson': lesson
    })


# ── Materials ──

@login_required
def add_material(request, course_id, lesson_id):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)
    guard  = _require_instructor(request, course)
    if guard:
        return guard
    if request.method == 'POST':
        form = LessonMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            mat = form.save(commit=False)
            mat.lesson      = lesson
            mat.uploaded_by = request.user
            mat.save()
            messages.success(request, f"'{mat.title}' uploaded successfully.")
            return redirect('courses:manage_materials', course_id=course.id, lesson_id=lesson.id)
    else:
        form = LessonMaterialForm()
    return render(request, 'courses/material_form.html', {
        'form': form, 'course': course, 'lesson': lesson, 'action': 'Upload'
    })


@login_required
def manage_materials(request, course_id, lesson_id):
    course    = get_object_or_404(Course, id=course_id)
    lesson    = get_object_or_404(Lesson, id=lesson_id, course=course)
    guard     = _require_instructor(request, course)
    if guard:
        return guard
    materials = lesson.materials.all().order_by('uploaded_at')
    return render(request, 'courses/manage_materials.html', {
        'course': course, 'lesson': lesson, 'materials': materials
    })


@login_required
def delete_material(request, course_id, lesson_id, material_id):
    course   = get_object_or_404(Course, id=course_id)
    lesson   = get_object_or_404(Lesson, id=lesson_id, course=course)
    material = get_object_or_404(LessonMaterial, id=material_id, lesson=lesson)
    guard    = _require_instructor(request, course)
    if guard:
        return guard
    if request.method == 'POST':
        # Delete the actual file from disk
        if material.file and os.path.isfile(material.file.path):
            os.remove(material.file.path)
        title = material.title
        material.delete()
        messages.success(request, f"'{title}' deleted.")
        return redirect('courses:manage_materials', course_id=course.id, lesson_id=lesson.id)
    return render(request, 'courses/delete_material.html', {
        'course': course, 'lesson': lesson, 'material': material
    })


@login_required
def download_material(request, material_id):
    """Serve a material file — only enrolled students, instructors, or admins."""
    material = get_object_or_404(LessonMaterial, id=material_id)
    course   = material.lesson.course

    is_instructor = request.user == course.instructor or request.user.role == 'admin'
    is_enrolled   = Enrollment.objects.filter(student=request.user, course=course).exists()

    if not (is_instructor or is_enrolled):
        return HttpResponseForbidden("You do not have access to this file.")

    response = FileResponse(material.file.open('rb'), as_attachment=True,
                            filename=material.filename)
    return response


@login_required
def course_notes(request, course_id):
    """List all notes uploaded for a course."""
    course = get_object_or_404(Course, id=course_id)
    guard  = _require_instructor(request, course)
    if guard:
        return guard
    notes = course.notes.all().order_by('-uploaded_at')
    return render(request, 'courses/course_notes.html', {
        'course': course,
        'notes':  notes,
    })


@login_required
def upload_course_note(request, course_id):
    """Upload a PDF/DOC/DOCX note directly to a course."""
    course = get_object_or_404(Course, id=course_id)
    guard  = _require_instructor(request, course)
    if guard:
        return guard
    if request.method == 'POST':
        form = CourseNoteForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.course      = course
            note.uploaded_by = request.user
            note.save()
            messages.success(request, f"'{note.title}' uploaded successfully.")
            return redirect('courses:course_notes', course_id=course.id)
    else:
        form = CourseNoteForm()
    return render(request, 'courses/upload_course_note.html', {
        'form': form, 'course': course,
    })


@login_required
def delete_course_note(request, course_id, note_id):
    """Delete a course-level note."""
    course = get_object_or_404(Course, id=course_id)
    note   = get_object_or_404(CourseNote, id=note_id, course=course)
    guard  = _require_instructor(request, course)
    if guard:
        return guard
    if request.method == 'POST':
        if note.file and os.path.isfile(note.file.path):
            os.remove(note.file.path)
        title = note.title
        note.delete()
        messages.success(request, f"'{title}' deleted.")
        return redirect('courses:course_notes', course_id=course.id)
    return render(request, 'courses/delete_course_note.html', {
        'course': course, 'note': note,
    })


@login_required
def download_course_note(request, note_id):
    """Serve a course note — enrolled students, instructor, or admin only."""
    note   = get_object_or_404(CourseNote, id=note_id)
    course = note.course
    is_instructor = request.user == course.instructor or request.user.role == 'admin'
    is_enrolled   = Enrollment.objects.filter(student=request.user, course=course).exists()
    if not (is_instructor or is_enrolled):
        return HttpResponseForbidden("You do not have access to this file.")
    response = FileResponse(note.file.open('rb'), as_attachment=True, filename=note.filename)
    return response


# ─────────────────────────────────────────────
#  Legacy aliases kept so old URLs don't break
# ─────────────────────────────────────────────
add_course    = admin_add_course
edit_course   = admin_edit_course
delete_course = admin_delete_course
