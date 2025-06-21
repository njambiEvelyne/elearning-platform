from django.urls import path

from courses import views
from .views import enroll_course

app_name = "enrollments"

urlpatterns = [
    path("enroll/<int:course_id>/", enroll_course, name="enroll_course"),
]
