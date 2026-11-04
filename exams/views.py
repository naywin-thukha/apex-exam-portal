from django.contrib import messages
from django.db import transaction
from django.db.models import Count, ProtectedError, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView,
)

from .models import Answer, Assignment, Attempt, Choice, Exam, Question
from .forms import AssignStudentsForm, ExamForm, QuestionForm, make_choice_formset
from .mixins import StudentRequiredMixin, TeacherRequiredMixin
from .models import Exam, Question
from django.http import HttpResponse, JsonResponse
from datetime import timedelta
from django.utils import timezone

GRACE_SECONDS = 5  # allowance for slow connections when saving near the deadline

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

class AssignStudentsView(TeacherRequiredMixin, View):
    """Job: choose which students may take this exam."""

    template_name = "exams/assign_students.html"

    def get_exam(self, request, pk):
        return get_object_or_404(Exam, pk=pk, creator=request.user)

    def get(self, request, pk):
        exam = self.get_exam(request, pk)
        form = AssignStudentsForm(exam=exam)
        return render(request, self.template_name, {"exam": exam, "form": form})

    def post(self, request, pk):
        exam = self.get_exam(request, pk)
        if exam.status == Exam.Status.CLOSED:
            messages.error(request, "This exam is closed.")
            return redirect("exams:exam_detail", pk=exam.pk)

        form = AssignStudentsForm(request.POST, exam=exam)
        if not form.is_valid():
            return render(request, self.template_name, {"exam": exam, "form": form})

        chosen = set(form.cleaned_data["students"])
        current = set(exam.students.all())
        removed = current - chosen
        started = [s for s in removed if exam.attempts.filter(student=s).exists()]
        if started:
            names = ", ".join(s.username for s in started)
            messages.error(request, f"Can't remove students who already started: {names}.")
            return render(request, self.template_name, {"exam": exam, "form": form})

        with transaction.atomic():
            Assignment.objects.filter(exam=exam, student__in=removed).delete()
            for student in chosen - current:
                Assignment.objects.create(exam=exam, student=student)
        messages.success(request, "Students updated.")
        return redirect("exams:exam_detail", pk=exam.pk)

def attempt_deadline(attempt):
    """Job: the moment this attempt must end: started_at + duration, but never after the exam's end time."""
    deadline = attempt.started_at + timedelta(minutes=attempt.exam.duration_minutes)
    if attempt.exam.end_time and attempt.exam.end_time < deadline:
        deadline = attempt.exam.end_time
    return deadline


def student_exam_or_404(request, pk):
    """Job: the exam must be published and assigned to this student."""
    return get_object_or_404(
        Exam, pk=pk, status=Exam.Status.PUBLISHED, assignments__student=request.user
    )


class StartExamView(StudentRequiredMixin, View):
    """Job: POST-only. Create the student's attempt if the rules allow it."""

    def post(self, request, pk):
        exam = student_exam_or_404(request, pk)
        now = timezone.now()

        attempt = Attempt.objects.filter(student=request.user, exam=exam).first()
        if attempt:
            if attempt.status == Attempt.Status.SUBMITTED:
                messages.info(request, "You have already submitted this exam.")
                return redirect("accounts:student_dashboard")
            return redirect("exams:exam_take", pk=exam.pk)

        if exam.start_time and now < exam.start_time:
            messages.error(request, "This exam has not opened yet.")
            return redirect("accounts:student_dashboard")
        if exam.end_time and now > exam.end_time:
            messages.error(request, "This exam is closed.")
            return redirect("accounts:student_dashboard")

        # get_or_create protects against a double click making two attempts
        Attempt.objects.get_or_create(student=request.user, exam=exam)
        return redirect("exams:exam_take", pk=exam.pk)

def finalize_attempt(attempt):
    """Job: lock the attempt and auto-grade it. Safe to call twice."""
    with transaction.atomic():
        # lock the row so a double click can't grade it twice
        attempt = Attempt.objects.select_for_update().select_related("exam").get(pk=attempt.pk)
        if attempt.status == Attempt.Status.SUBMITTED:
            return attempt

        score = (
            Answer.objects.filter(attempt=attempt, selected_choice__is_correct=True)
            .aggregate(t=Sum("question__marks"))["t"] or 0
        )
        total = attempt.exam.total_marks
        attempt.score = score
        attempt.total_marks = total
        attempt.percentage = round(score * 100 / total, 2) if total else 0
        attempt.status = Attempt.Status.SUBMITTED
        attempt.submitted_at = timezone.now()
        attempt.save()
    return attempt

class ExamTakeView(StudentRequiredMixin, View):
    """Job: show the questions, save answers, and submit."""

    template_name = "exams/exam_take.html"

    def load(self, request, pk):
        self.exam = student_exam_or_404(request, pk)
        self.attempt = get_object_or_404(Attempt, student=request.user, exam=self.exam)

    def seconds_left(self):
        return int((attempt_deadline(self.attempt) - timezone.now()).total_seconds())

    def save_answers(self, request):
        for q in self.exam.questions.prefetch_related("choices"):
            raw = request.POST.get(f"q_{q.id}")
            valid_ids = {str(c.id) for c in q.choices.all()}
            if raw in valid_ids:  # ignore anything that isn't one of this question's options
                Answer.objects.update_or_create(
                    attempt=self.attempt, question=q,
                    defaults={"selected_choice_id": int(raw)},
                )

    def get(self, request, pk):
        self.load(request, pk)
        if self.attempt.status == Attempt.Status.SUBMITTED:
            return redirect("accounts:student_dashboard")

        left = self.seconds_left()
        if left <= 0:
            finalize_attempt(self.attempt)
            messages.info(request, "Time was up, so your exam was submitted automatically.")
            return redirect("accounts:student_dashboard")

        questions = list(self.exam.questions.prefetch_related("choices"))
        saved = {a.question_id: a.selected_choice_id for a in self.attempt.answers.all()}
        for q in questions:
            q.saved_choice_id = saved.get(q.id)

        return render(request, self.template_name, {
            "exam": self.exam, "attempt": self.attempt,
            "questions": questions, "remaining": left,
        })

    def post(self, request, pk):
        self.load(request, pk)
        if self.attempt.status == Attempt.Status.SUBMITTED:
            return redirect("accounts:student_dashboard")

        too_late = self.seconds_left() < -GRACE_SECONDS
        if not too_late:
            with transaction.atomic():
                self.save_answers(request)

        if too_late or request.POST.get("action") == "submit":
            finalize_attempt(self.attempt)
            if too_late:
                messages.error(request, "Time was up. Your exam was submitted with the answers saved earlier.")
            else:
                messages.success(request, "Exam submitted.")
            return redirect("accounts:student_dashboard")

        messages.success(request, "Answers saved.")
        return redirect("exams:exam_take", pk=self.exam.pk)

class ResultView(StudentRequiredMixin, View):
    """Job: the student's own result for a submitted exam."""

    def get(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk, assignments__student=request.user)
        attempt = get_object_or_404(
            Attempt, student=request.user, exam=exam, status=Attempt.Status.SUBMITTED
        )

        review = None
        if exam.show_answers:
            chosen_by_q = {
                a.question_id: a.selected_choice
                for a in attempt.answers.select_related("selected_choice")
            }
            review = []
            for q in exam.questions.prefetch_related("choices"):
                chosen = chosen_by_q.get(q.id)
                correct = next((c for c in q.choices.all() if c.is_correct), None)
                review.append({
                    "question": q,
                    "chosen": chosen,
                    "correct": correct,
                    "is_right": bool(chosen and chosen.is_correct),
                })

        return render(request, "exams/result.html", {
            "exam": exam, "attempt": attempt, "review": review,
        })


class ExamResultsView(TeacherRequiredMixin, View):
    """Job: the teacher's results table for one of their exams."""

    def get(self, request, pk):
        exam = get_object_or_404(Exam, pk=pk, creator=request.user)

        # grade attempts whose time ran out but were never submitted
        now = timezone.now()
        for attempt in exam.attempts.filter(status=Attempt.Status.IN_PROGRESS).select_related("exam"):
            if attempt_deadline(attempt) < now:
                finalize_attempt(attempt)

        attempts = {a.student_id: a for a in exam.attempts.all()}
        rows = [
            {"student": s, "attempt": attempts.get(s.id)}
            for s in exam.students.order_by("username")
        ]

        done = [a for a in attempts.values() if a.status == Attempt.Status.SUBMITTED]
        stats = None
        if done:
            stats = {
                "count": len(done),
                "average": round(sum(a.percentage for a in done) / len(done), 2),
                "highest": max(a.percentage for a in done),
            }

        return render(request, "exams/exam_results.html", {
            "exam": exam, "rows": rows, "stats": stats,
        })


class AutosaveView(StudentRequiredMixin, View):
    """Job: store ONE answer as soon as the student clicks an option."""

    def post(self, request, pk):
        exam = student_exam_or_404(request, pk)
        attempt = get_object_or_404(Attempt, student=request.user, exam=exam)

        if attempt.status == Attempt.Status.SUBMITTED:
            return JsonResponse({"ok": False, "error": "submitted"}, status=409)
        left = int((attempt_deadline(attempt) - timezone.now()).total_seconds())
        if left < -GRACE_SECONDS:
            return JsonResponse({"ok": False, "error": "time_up"}, status=409)

        try:
            question_id = int(request.POST.get("question"))
            choice_id = int(request.POST.get("choice"))
        except (TypeError, ValueError):
            return JsonResponse({"ok": False, "error": "bad_request"}, status=400)

        # the option must belong to that question, and the question to this exam
        choice = Choice.objects.filter(
            pk=choice_id, question_id=question_id, question__exam=exam
        ).first()
        if choice is None:
            return JsonResponse({"ok": False, "error": "bad_request"}, status=400)

        Answer.objects.update_or_create(
            attempt=attempt, question_id=question_id,
            defaults={"selected_choice": choice},
        )
        return JsonResponse({"ok": True})