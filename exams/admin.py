from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import Answer, Assignment, Attempt, Choice, Exam, Question, Subject


class ChoiceFormSet(BaseInlineFormSet):
    """Exactly one correct choice, at least two choices."""

    def clean(self):
        super().clean()
        live = [
            f.cleaned_data
            for f in self.forms
            if f.cleaned_data and not f.cleaned_data.get("DELETE")
        ]
        if len(live) < 2:
            raise ValidationError("A question needs at least 2 choices.")
        if sum(1 for c in live if c.get("is_correct")) != 1:
            raise ValidationError("Mark exactly one choice as correct.")


class ChoiceInline(admin.TabularInline):
    model = Choice
    formset = ChoiceFormSet
    extra = 4
    min_num = 2


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0
    fields = ("order", "text", "marks")
    show_change_link = True


class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 0


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name",)
    filter_horizontal = ("teachers",)


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "creator", "status", "duration_minutes", "start_time", "end_time")
    list_filter = ("status", "subject")
    inlines = [QuestionInline, AssignmentInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("__str__", "exam", "marks")
    list_filter = ("exam",)
    inlines = [ChoiceInline]


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("student", "exam", "status", "started_at", "submitted_at", "score", "percentage")
    list_filter = ("status", "exam")
    inlines = [AnswerInline]


admin.site.register(Choice)
admin.site.register(Assignment)
admin.site.register(Answer)