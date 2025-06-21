from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets
from django.contrib.auth.decorators import login_required

from courses.models import Course
from .models import Enrollment
from .serializers import EnrollmentSerializer
from .forms import EnrollmentForm


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer


@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student = request.user

    # Check if the student is already enrolled
    if Enrollment.objects.filter(student=student, course=course).exists():
        messages.warning(request, "You are already enrolled in this course.")
        return redirect("courses:course_detail", course_id=course.id)

    if request.method == "POST":
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.student = student  # Assign the logged-in student
            enrollment.course = course  # Assign the selected course
            enrollment.course = course
            enrollment.save()
            messages.success(request, "Enrollment successful!")
            return redirect("users:student_dashboard")  # Redirect to student dashboard
    else:
        form = EnrollmentForm(initial={"email": student.email})

    return render(
        request, "enrollments/enroll_form.html", {"form": form, "course": course}
    )


from django.http import JsonResponse
from django.core.paginator import Paginator


def enrollments_list(request):
    enrollments = Enrollment.objects.select_related("student").all()
    paginator = Paginator(enrollments, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    data = [{"id": e.id, "student": e.student.username} for e in page_obj]
    return JsonResponse({"enrollments": data})
