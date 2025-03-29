from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from courses.views import CourseViewSet, LessonViewSet
from enrollments.views import EnrollmentViewSet
from progress.views import ProgressViewSet
from quizzes.views import QuestionViewSet, SubmissionViewSet, QuizViewSet, AnswerViewSet
from users.views import UserViewset
from django.views.generic import TemplateView

# Create the API router
router = DefaultRouter()
router.register(r'users', UserViewset)
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'progress', ProgressViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'submissions', SubmissionViewSet)
router.register(r'answers', AnswerViewSet)  

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),  
    path("admin/", admin.site.urls),

    # Main API entry point (DefaultRouter handles API root)
    path("api/", include(router.urls)),  
    path("api-auth/", include("rest_framework.urls")), 

    # Include users and courses with namespaces
    path("users/", include("users.urls", namespace="users")),  
    path("courses/", include("courses.urls", namespace="courses")),  # FIX: Register courses with namespace
]
