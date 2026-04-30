from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
import uuid

from courses.models import Course
from .models import Enrollment, GuestPreview
from .serializers import EnrollmentSerializer
from .forms import EnrollmentForm, GuestPreviewForm


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


def guest_preview_course(request, course_id):
    """
    Allow guests (unauthenticated users) to preview courses without permanent enrollment.
    Creates a temporary GuestPreview record that expires after 24 hours.
    """
    course = get_object_or_404(Course, id=course_id)
    
    # Check if user is already authenticated
    if request.user.is_authenticated:
        messages.info(request, "You are logged in. You can enroll in courses directly.")
        return redirect("courses:course_detail", course_id=course.id)
    
    # Generate or retrieve guest session ID
    guest_session_id = request.session.get('guest_session_id')
    if not guest_session_id:
        guest_session_id = str(uuid.uuid4())
        request.session['guest_session_id'] = guest_session_id
    
    if request.method == "POST":
        form = GuestPreviewForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            
            # Check if this guest already has preview access (within 24 hours)
            existing_preview = GuestPreview.objects.filter(
                course=course,
                guest_session_id=guest_session_id,
                guest_email=email
            ).first()
            
            if existing_preview and not existing_preview.is_expired():
                # Reuse existing preview
                preview = existing_preview
                preview.last_accessed_at = timezone.now()
                preview.save()
                messages.info(request, f"Welcome back! You can preview {course.title} for the next 24 hours.")
            else:
                # Create new guest preview
                preview = GuestPreview.objects.create(
                    course=course,
                    guest_email=email,
                    guest_session_id=guest_session_id
                )
                messages.success(request, f"Guest preview access granted! You can access {course.title} for 24 hours.")
            
            # Store in session for verification
            request.session['guest_course_id'] = course_id
            request.session['guest_email'] = email
            
            return redirect("courses:course_detail", course_id=course.id)
    else:
        form = GuestPreviewForm()
    
    context = {
        'form': form,
        'course': course,
        'is_guest': True
    }
    return render(request, "enrollments/guest_preview_form.html", context)


def enrollments_list(request):
    enrollments = Enrollment.objects.select_related("student").all()
    paginator = Paginator(enrollments, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    data = [{"id": e.id, "student": e.student.username} for e in page_obj]
    return JsonResponse({"enrollments": data})
