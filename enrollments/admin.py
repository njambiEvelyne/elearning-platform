from django.contrib import admin
from .models import Enrollment, GuestPreview


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('enrolled_at', 'course')
    search_fields = ('student__username', 'course__title')
    readonly_fields = ('enrolled_at',)


@admin.register(GuestPreview)
class GuestPreviewAdmin(admin.ModelAdmin):
    list_display = ('guest_email', 'course', 'preview_started_at', 'expires_at', 'is_expired_status')
    list_filter = ('preview_started_at', 'expires_at', 'course')
    search_fields = ('guest_email', 'course__title', 'guest_session_id')
    readonly_fields = ('preview_started_at', 'last_accessed_at', 'guest_session_id')
    
    def is_expired_status(self, obj):
        """Display expiration status as a colored indicator"""
        from django.utils.html import format_html
        if obj.is_expired():
            return format_html('<span style="color: red;">❌ Expired</span>')
        else:
            return format_html('<span style="color: green;">✅ Active</span>')
    is_expired_status.short_description = 'Status'
    
    fieldsets = (
        ('Guest Information', {
            'fields': ('guest_email', 'guest_session_id')
        }),
        ('Course', {
            'fields': ('course',)
        }),
        ('Timeline', {
            'fields': ('preview_started_at', 'last_accessed_at', 'expires_at')
        }),
    )

