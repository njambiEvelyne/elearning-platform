from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    instructor_dashboard,
    add_course,
    CourseViewSet,
    LessonViewSet,
    CourseDetailView,
)
from enrollments.views import enroll_course

app_name = "courses"  # Ensures the namespace is registered

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"lessons", LessonViewSet, basename="lesson")

urlpatterns = [
    path("enroll/<int:course_id>/", enroll_course, name="enroll_course"),
    path("instructor/", instructor_dashboard, name="instructor_dashboard"),
    path("instructor/add/", add_course, name="add_course"),
    path("add/", add_course, name="add_course"),
    path("", include(router.urls)),
    path("<int:course_id>/", CourseDetailView.as_view(), name="course_detail"),
]
