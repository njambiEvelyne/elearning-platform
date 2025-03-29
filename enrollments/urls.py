from django.urls import path
from .views import enroll_course

urlpatterns = [
    path('enroll/<int:course_id>/', enroll_course, name='enroll_course'),
]
