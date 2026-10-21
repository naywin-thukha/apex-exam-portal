from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.dashboard_redirect, name="home"),
    path("dashboard/admin/", views.AdminDashboardView.as_view(), name="admin_dashboard"),
    path("dashboard/teacher/", views.TeacherDashboardView.as_view(), name="teacher_dashboard"),
    path("dashboard/student/", views.StudentDashboardView.as_view(), name="student_dashboard"),
]