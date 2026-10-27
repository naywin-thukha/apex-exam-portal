from django.contrib import messages
from django.db import transaction
from django.db.models import Count, ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView,
)

from .forms import ExamForm, QuestionForm, make_choice_formset
from .mixins import TeacherRequiredMixin
from .models import Exam, Question

def welcome(request):
    return HttpResponse("Welcome to the Apex Exam Portal")

class OwnExamMixin(TeacherRequiredMixin):
    """Job: every query is limited to the logged-in teacher's own exams."""

    def get_queryset(self):
        return Exam.objects.filter(creator=self.request.user)


class ExamListView(OwnExamMixin, ListView):
    template_name = "exams/exam_list.html"
    context_object_name = "exams"

    def get_queryset(self):
        return (
            super().get_queryset()
            .select_related("subject")
            .annotate(question_count=Count("questions"))
        )


class ExamFormMixin:
    """Job: shared form setup for create and edit."""
    form_class = ExamForm
    template_name = "exams/exam_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["teacher"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("exams:exam_detail", args=[self.object.pk])


class ExamCreateView(OwnExamMixin, ExamFormMixin, CreateView):
    def form_valid(self, form):
        form.instance.creator = self.request.user
        messages.success(self.request, "Exam created.")
        return super().form_valid(form)


class ExamUpdateView(OwnExamMixin, ExamFormMixin, UpdateView):
    def get_queryset(self):
        # only draft exams can be edited
        return super().get_queryset().filter(status=Exam.Status.DRAFT)

    def form_valid(self, form):
        messages.success(self.request, "Exam updated.")
        return super().form_valid(form)


class ExamDetailView(OwnExamMixin, DetailView):
    template_name = "exams/exam_detail.html"
    context_object_name = "exam"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["questions"] = self.object.questions.prefetch_related("choices")
        ctx["is_draft"] = self.object.status == Exam.Status.DRAFT
        return ctx


class ExamDeleteView(OwnExamMixin, DeleteView):
    template_name = "exams/exam_confirm_delete.html"
    success_url = reverse_lazy("exams:exam_list")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, "This exam already has student attempts, so it can't be deleted.")
            return redirect("exams:exam_detail", pk=self.object.pk)
        messages.success(self.request, "Exam deleted.")
        return response

class QuestionFormView(TeacherRequiredMixin, View):
    """Job: one page for adding AND editing a question with its options."""

    template_name = "exams/question_form.html"

    def load(self, request, exam_pk, pk=None):
        self.exam = get_object_or_404(Exam, pk=exam_pk, creator=request.user)
        self.question = get_object_or_404(Question, pk=pk, exam=self.exam) if pk else None

    def build_forms(self, request):
        Formset = make_choice_formset(4 if self.question is None else 1)
        data = request.POST if request.method == "POST" else None
        initial = {"order": self.exam.questions.count() + 1} if self.question is None else None
        qform = QuestionForm(data, instance=self.question, initial=initial)
        formset = Formset(data, instance=self.question)
        return qform, formset

    def show(self, request, qform, formset):
        return render(request, self.template_name, {
            "exam": self.exam, "question": self.question,
            "qform": qform, "formset": formset,
        })

    def locked(self, request):
        if self.exam.status != Exam.Status.DRAFT:
            messages.error(request, "Unpublish the exam before changing its questions.")
            return redirect("exams:exam_detail", pk=self.exam.pk)

    def get(self, request, **kwargs):
        self.load(request, **kwargs)
        return self.locked(request) or self.show(request, *self.build_forms(request))

    def post(self, request, **kwargs):
        self.load(request, **kwargs)
        blocked = self.locked(request)
        if blocked:
            return blocked
        qform, formset = self.build_forms(request)
        if qform.is_valid() and formset.is_valid():
            with transaction.atomic():
                question = qform.save(commit=False)
                question.exam = self.exam
                question.save()
                formset.instance = question
                formset.save()
            messages.success(request, "Question saved.")
            return redirect("exams:exam_detail", pk=self.exam.pk)
        return self.show(request, qform, formset)


class QuestionDeleteView(TeacherRequiredMixin, View):
    """Job: delete one question (POST only, draft exams only)."""

    def post(self, request, exam_pk, pk):
        exam = get_object_or_404(Exam, pk=exam_pk, creator=request.user)
        question = get_object_or_404(Question, pk=pk, exam=exam)
        if exam.status != Exam.Status.DRAFT:
            messages.error(request, "Unpublish the exam before changing its questions.")
        else:
            question.delete()
            messages.success(request, "Question deleted.")
        return redirect("exams:exam_detail", pk=exam.pk)


def publish_problem(exam):
    """Job: return a message if the exam is not ready to publish, else None."""
    if exam.status != Exam.Status.DRAFT:
        return "Only draft exams can be published."
    if not exam.start_time or not exam.end_time:
        return "Set a start time and end time first."
    questions = list(exam.questions.prefetch_related("choices"))
    if not questions:
        return "Add at least one question first."
    for q in questions:
        choices = list(q.choices.all())
        if len(choices) < 2 or sum(c.is_correct for c in choices) != 1:
            return f"Question {q.order} needs 2+ options with exactly one correct."
    return None


class ExamStatusView(TeacherRequiredMixin, View):
    """Job: POST-only. action is 'publish' or 'unpublish'."""

    action = None

    def post(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk, creator=request.user)
        if self.action == "publish":
            problem = publish_problem(exam)
            if problem:
                messages.error(request, problem)
            else:
                exam.status = Exam.Status.PUBLISHED
                exam.save(update_fields=["status", "updated_at"])
                messages.success(request, "Exam published.")
        else:
            if exam.status != Exam.Status.PUBLISHED:
                messages.error(request, "Only published exams can be unpublished.")
            elif exam.attempts.exists():
                messages.error(request, "Students have already started this exam.")
            else:
                exam.status = Exam.Status.DRAFT
                exam.save(update_fields=["status", "updated_at"])
                messages.success(request, "Exam moved back to draft.")
        return redirect("exams:exam_detail", pk=exam.pk)