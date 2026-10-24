from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView

from exams.models import Attempt, Exam

from .models import User
from .permissions import RoleRequiredMixin

ROLE_HOME = {
    User.Role.ADMIN: "accounts:admin_dashboard",
    User.Role.TEACHER: "accounts:teacher_dashboard",
    User.Role.STUDENT: "accounts:student_dashboard",
}


@login_required
def dashboard_redirect(request):
    """Job: after login, send the user to the dashboard for their role."""
    return redirect(ROLE_HOME[request.user.role])


class AdminDashboardView(RoleRequiredMixin, TemplateView):
    allowed_roles = (User.Role.ADMIN,)
    template_name = "accounts/admin_dashboard.html"


class TeacherDashboardView(RoleRequiredMixin, TemplateView):
    """Job: show the teacher's own subjects and exams."""

    allowed_roles = (User.Role.TEACHER,)
    template_name = "accounts/teacher_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["exams"] = (
            Exam.objects.filter(creator=user)
            .select_related("subject")
            .annotate(
                num_questions=Count("questions", distinct=True),
                num_attempts=Count("attempts", distinct=True),
            )
        )
        context["subjects"] = user.subjects.all()
        return context


class StudentDashboardView(RoleRequiredMixin, TemplateView):
    """Job: show the published exams assigned to this student."""

    allowed_roles = (User.Role.STUDENT,)
    template_name = "accounts/student_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        now = timezone.now()
        exams = list(
            Exam.objects.filter(
                assignments__student=user,
                status=Exam.Status.PUBLISHED,
            ).select_related("subject")
        )
        attempts = {a.exam_id: a for a in Attempt.objects.filter(student=user)}
        for exam in exams:
            exam.attempt = attempts.get(exam.id)
            exam.not_started = exam.start_time is not None and exam.start_time > now
            exam.is_over = exam.end_time is not None and exam.end_time < now
        context["exams"] = exams
        return context