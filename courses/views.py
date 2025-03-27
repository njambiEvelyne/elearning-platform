from rest_framework import viewsets
from .permissions import IsInstructorOrReadOnly
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from rest_framework.permissions import IsAuthenticated

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrReadOnly]
    def list(self, request, *args, **kwargs):
        print("Queryset:", self.queryset)  # Debugging line
        return super().list(request, *args, **kwargs)

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsInstructorOrReadOnly]


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Course
from .forms import CourseForm  

@login_required
def instructor_dashboard(request):
    if request.user.role != 'instructor':  # Ensure only instructors can access
        return redirect('home')

    courses = Course.objects.filter(instructor=request.user)
    return render(request, 'courses/instructor_dashboard.html', {'courses': courses})

@login_required
def add_course(request):
    if request.user.role != 'instructor':
        return redirect('home')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            return redirect('instructor_dashboard')
    else:
        form = CourseForm()

    return render(request, 'courses/add_course.html', {'form': form})


@login_required
def add_course(request):
    if request.user.role != 'instructor':  # Restrict access
        return redirect('instructor_dashboard')

    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user  # Set instructor as the creator
            course.save()
            return redirect('course_list')  # Redirect to courses page
    else:
        form = CourseForm()
    
    return render(request, 'courses/add_course.html', {'form': form})