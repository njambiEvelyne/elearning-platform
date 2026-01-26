from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    instructor_dashboard,
    add_course,
    CourseViewSet,
    LessonViewSet,
    CourseDetailView,
    LessonDetailView,
    manage_lessons,
    add_lesson,
    edit_lesson,
    delete_lesson,
    student_dashboard,
    enroll_course,
    unenroll_course,
    courses_list,
)

app_name = "courses"

router = DefaultRouter()
router.register(r"api/courses", CourseViewSet, basename="course")
router.register(r"api/lessons", LessonViewSet, basename="lesson")

urlpatterns = [
    # Course management
    path("", student_dashboard, name="student_dashboard"),
    path("browse/", courses_list, name="courses_list"),
    path("instructor/", instructor_dashboard, name="instructor_dashboard"),
    path("instructor/add/", add_course, name="add_course"),
    path("<int:course_id>/", CourseDetailView.as_view(), name="course_detail"),
    path("<int:course_id>/enroll/", enroll_course, name="enroll_course"),
    path("<int:course_id>/unenroll/", unenroll_course, name="unenroll_course"),
    
    # Lesson management for instructors
    path("<int:course_id>/lessons/", manage_lessons, name="manage_lessons"),
    path("<int:course_id>/lessons/add/", add_lesson, name="add_lesson"),
    path("<int:course_id>/lessons/<int:lesson_id>/edit/", edit_lesson, name="edit_lesson"),
    path("<int:course_id>/lessons/<int:lesson_id>/delete/", delete_lesson, name="delete_lesson"),
    
    # Lesson viewing for students
    path("<int:course_id>/lessons/<int:lesson_id>/", LessonDetailView.as_view(), name="lesson_detail"),
    
    # API routes
    path("", include(router.urls)),
]
