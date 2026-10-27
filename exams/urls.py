from django.urls import path
from . import views

app_name = "exams"

urlpatterns = [
    path("", views.welcome, name="welcome"),
    path("teacher/exams/", views.ExamListView.as_view(), name="exam_list"),
    path("teacher/exams/new/", views.ExamCreateView.as_view(), name="exam_create"),
    path("teacher/exams/<int:pk>/", views.ExamDetailView.as_view(), name="exam_detail"),
    path("teacher/exams/<int:pk>/edit/", views.ExamUpdateView.as_view(), name="exam_update"),
    path("teacher/exams/<int:pk>/delete/", views.ExamDeleteView.as_view(), name="exam_delete"),
    path("teacher/exams/<int:exam_pk>/questions/new/", views.QuestionFormView.as_view(), name="question_create"),
    path("teacher/exams/<int:exam_pk>/questions/<int:pk>/edit/", views.QuestionFormView.as_view(), name="question_edit"),
    path("teacher/exams/<int:exam_pk>/questions/<int:pk>/delete/", views.QuestionDeleteView.as_view(), name="question_delete"),
    path("teacher/exams/<int:pk>/publish/", views.ExamStatusView.as_view(action="publish"), name="exam_publish"),
    path("teacher/exams/<int:pk>/unpublish/", views.ExamStatusView.as_view(action="unpublish"), name="exam_unpublish"),
]