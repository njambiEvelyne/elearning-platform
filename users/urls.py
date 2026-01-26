from django.urls import path, reverse_lazy
from django.contrib.auth.views import LogoutView
from .views import (
    CustomLoginView,
    RegisterUserView,
    add_user,
    dashboard_redirect,
    admin_dashboard,
    instructor_dashboard,
    student_dashboard,
    custom_logout,
)

app_name = "users"


urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", custom_logout, name="logout"),
    path("register/", RegisterUserView.as_view(), name="register"),
    path("dashboard/", dashboard_redirect, name="dashboard_redirect"),
    path("admin/dashboard/", admin_dashboard, name="admin_dashboard"),
    path("instructor/dashboard/", instructor_dashboard, name="instructor_dashboard"),
    path("student/dashboard/", student_dashboard, name="student_dashboard"),
    path("add-user/", add_user, name="add_user"),
]
