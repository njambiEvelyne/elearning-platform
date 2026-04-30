from django.urls import path

from courses import views
from .views import enroll_course, guest_preview_course

app_name = "enrollments"

urlpatterns = [
    path("enroll/<int:course_id>/", enroll_course, name="enroll_course"),
    path("preview/<int:course_id>/", guest_preview_course, name="guest_preview"),
]

