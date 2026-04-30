from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    # API
    CourseViewSet, LessonViewSet,
    # Public / student
    courses_list, CourseDetailView, LessonDetailView,
    student_dashboard, enroll_course, unenroll_course,
    # Admin — course management
    admin_course_list, admin_add_course, admin_edit_course, admin_delete_course,
    # Instructor — lesson management
    instructor_dashboard, manage_lessons,
    add_lesson, edit_lesson, delete_lesson,
    # Instructor — material management
    manage_materials, add_material, delete_material, download_material,
)

app_name = "courses"

router = DefaultRouter()
router.register(r"api/courses", CourseViewSet, basename="course")
router.register(r"api/lessons", LessonViewSet, basename="lesson")

urlpatterns = [
    # ── Student ──────────────────────────────────────────
    path("",                                    student_dashboard,  name="student_dashboard"),
    path("browse/",                             courses_list,       name="courses_list"),
    path("<int:course_id>/",                    CourseDetailView.as_view(), name="course_detail"),
    path("<int:course_id>/enroll/",             enroll_course,      name="enroll_course"),
    path("<int:course_id>/unenroll/",           unenroll_course,    name="unenroll_course"),
    path("<int:course_id>/lessons/<int:lesson_id>/",
         LessonDetailView.as_view(), name="lesson_detail"),

    # ── Admin — course management ─────────────────────────
    path("admin/",                              admin_course_list,  name="admin_course_list"),
    path("admin/add/",                          admin_add_course,   name="add_course"),
    path("admin/<int:course_id>/edit/",         admin_edit_course,  name="edit_course"),
    path("admin/<int:course_id>/delete/",       admin_delete_course, name="delete_course"),

    # ── Instructor — lesson management ───────────────────
    path("instructor/",                         instructor_dashboard, name="instructor_dashboard"),
    path("<int:course_id>/lessons/",            manage_lessons,     name="manage_lessons"),
    path("<int:course_id>/lessons/add/",        add_lesson,         name="add_lesson"),
    path("<int:course_id>/lessons/<int:lesson_id>/edit/",
         edit_lesson,   name="edit_lesson"),
    path("<int:course_id>/lessons/<int:lesson_id>/delete/",
         delete_lesson, name="delete_lesson"),

    # ── Instructor — material management ─────────────────
    path("<int:course_id>/lessons/<int:lesson_id>/materials/",
         manage_materials, name="manage_materials"),
    path("<int:course_id>/lessons/<int:lesson_id>/materials/add/",
         add_material,     name="add_material"),
    path("<int:course_id>/lessons/<int:lesson_id>/materials/<int:material_id>/delete/",
         delete_material,  name="delete_material"),
    path("materials/<int:material_id>/download/",
         download_material, name="download_material"),

    # ── API ───────────────────────────────────────────────
    path("", include(router.urls)),
]
