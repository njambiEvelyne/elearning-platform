"""
This model helps in the management of users from the Django Admin
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ["username", "email", "role", "is_staff", "is_active"]
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("role", "profile_photo", "date_of_birth")}),
    )


admin.site.register(User, CustomUserAdmin)
