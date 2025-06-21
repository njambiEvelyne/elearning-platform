from rest_framework import permissions


class IsInstructorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow only instructors to edit courses and lessons.
    Students can only view them.
    """

    def has_permission(self, request, view):
        # Allow all users to view (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only allow instructors to create, edit, or delete
        return request.user.is_authenticated and request.user.role == "instructor"

    def has_object_permission(self, request, view, obj):
        # Allow read-only access for all users
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only the course instructor or admin can modify the object
        return request.user.is_authenticated and (
            request.user.role == "instructor" or request.user.is_staff
        )
