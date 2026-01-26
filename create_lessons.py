#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elearning.settings')
django.setup()

from courses.models import Course, Lesson

# Create lessons for each course
courses = Course.objects.all()

lessons_data = {
    'Introduction to Python': [
        {'title': 'Python Basics and Syntax', 'content': 'Learn the fundamentals of Python programming language.'},
        {'title': 'Variables and Data Types', 'content': 'Understanding different data types in Python.'},
        {'title': 'Control Structures', 'content': 'If statements, loops, and conditional logic.'},
        {'title': 'Functions and Modules', 'content': 'Creating reusable code with functions.'},
    ],
    'Web Development with Django': [
        {'title': 'Django Introduction', 'content': 'Getting started with Django framework.'},
        {'title': 'Models and Database', 'content': 'Creating models and working with databases.'},
        {'title': 'Views and Templates', 'content': 'Building dynamic web pages.'},
        {'title': 'Forms and User Input', 'content': 'Handling user input and forms.'},
        {'title': 'Authentication System', 'content': 'User registration and login.'},
    ],
    'Data Science Fundamentals': [
        {'title': 'Introduction to Data Science', 'content': 'Overview of data science concepts.'},
        {'title': 'Data Analysis with Pandas', 'content': 'Working with data using Pandas library.'},
        {'title': 'Data Visualization', 'content': 'Creating charts and graphs.'},
    ],
    'JavaScript for Beginners': [
        {'title': 'JavaScript Basics', 'content': 'Introduction to JavaScript programming.'},
        {'title': 'DOM Manipulation', 'content': 'Interacting with web page elements.'},
        {'title': 'Event Handling', 'content': 'Responding to user interactions.'},
        {'title': 'Async Programming', 'content': 'Promises and async/await.'},
    ],
    'Database Design & SQL': [
        {'title': 'Database Fundamentals', 'content': 'Introduction to database concepts.'},
        {'title': 'SQL Basics', 'content': 'Writing basic SQL queries.'},
        {'title': 'Advanced SQL', 'content': 'Joins, subqueries, and optimization.'},
    ]
}

for course in courses:
    if course.title in lessons_data:
        for lesson_data in lessons_data[course.title]:
            lesson, created = Lesson.objects.get_or_create(
                course=course,
                title=lesson_data['title'],
                defaults={'content': lesson_data['content']}
            )
            if created:
                print(f"Created lesson: {lesson.title} for {course.title}")

print("Lessons creation completed!")