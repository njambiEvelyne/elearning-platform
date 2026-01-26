#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elearning.settings')
django.setup()

from django.core.management import execute_from_command_line

# Run makemigrations with default values
try:
    execute_from_command_line(['manage.py', 'makemigrations', '--empty', 'courses'])
    execute_from_command_line(['manage.py', 'makemigrations', '--empty', 'progress'])
    print("Migration files created successfully!")
except Exception as e:
    print(f"Error creating migrations: {e}")