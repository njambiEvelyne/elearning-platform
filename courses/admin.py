from django.contrib import admin
from .models import Course, Lesson, LessonMaterial


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display  = ('title', 'instructor', 'status', 'created_at')
    list_filter   = ('status',)
    search_fields = ('title', 'instructor__username')
    list_editable = ('status',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display  = ('title', 'course', 'status', 'order', 'created_at')
    list_filter   = ('status',)
    search_fields = ('title', 'course__title')


@admin.register(LessonMaterial)
class LessonMaterialAdmin(admin.ModelAdmin):
    list_display  = ('title', 'lesson', 'extension', 'uploaded_by', 'uploaded_at')
    search_fields = ('title', 'lesson__title')
