from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.generic import TemplateView

from accounts.models import User
from accounts.permissions import RoleRequiredMixin
#from .permissions import RoleRequiredMixin
from django.http import HttpResponse


def welcome(request):
    return HttpResponse("Welcome to the Apex Exam Portal")

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
    allowed_roles = (User.Role.TEACHER,)
    template_name = "accounts/teacher_dashboard.html"


class StudentDashboardView(RoleRequiredMixin, TemplateView):
    allowed_roles = (User.Role.STUDENT,)
    template_name = "accounts/student_dashboard.html"