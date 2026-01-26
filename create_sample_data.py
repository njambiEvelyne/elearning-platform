#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elearning.settings')
django.setup()

from courses.models import Course
from users.models import User

# Create instructor if doesn't exist
instructor, created = User.objects.get_or_create(
    username='instructor1',
    defaults={
        'email': 'instructor@example.com',
        'role': 'instructor',
        'first_name': 'John',
        'last_name': 'Instructor'
    }
)

if created:
    instructor.set_password('pass123')
    instructor.save()
    print(f"Created instructor: {instructor.username}")

# Create sample courses
courses_data = [
    {
        'title': 'Introduction to Python',
        'description': 'Learn Python programming from scratch with hands-on projects and real-world examples.'
    },
    {
        'title': 'Web Development with Django',
        'description': 'Build powerful web applications using Django framework and modern web technologies.'
    },
    {
        'title': 'Data Science Fundamentals',
        'description': 'Introduction to data science, analytics, and machine learning concepts.'
    },
    {
        'title': 'JavaScript for Beginners',
        'description': 'Master JavaScript programming and create interactive web applications.'
    },
    {
        'title': 'Database Design & SQL',
        'description': 'Learn database design principles and SQL query optimization techniques.'
    }
]

for course_data in courses_data:
    course, created = Course.objects.get_or_create(
        title=course_data['title'],
        defaults={
            'description': course_data['description'],
            'instructor': instructor
        }
    )
    if created:
        print(f"Created course: {course.title}")
    else:
        print(f"Course already exists: {course.title}")

print("Sample data creation completed!")