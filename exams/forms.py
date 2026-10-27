from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import Choice, Exam, Question

DT_FORMAT = "%Y-%m-%dT%H:%M"


class BootstrapMixin:
    """Job: gives every field Bootstrap styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "form-check-input"
            elif isinstance(widget, forms.Select):
                widget.attrs["class"] = "form-select"
            else:
                widget.attrs["class"] = "form-control"


class ExamForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Exam
        fields = [
            "title", "subject", "instructions", "duration_minutes",
            "start_time", "end_time", "show_answers",
        ]
        widgets = {
            "instructions": forms.Textarea(attrs={"rows": 3}),
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}, format=DT_FORMAT),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}, format=DT_FORMAT),
        }

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_time"].input_formats = [DT_FORMAT]
        self.fields["end_time"].input_formats = [DT_FORMAT]
        if teacher is not None:
            # a teacher may only pick subjects they are linked to
            self.fields["subject"].queryset = teacher.subjects.all()

    def clean(self):
        data = super().clean()
        start, end = data.get("start_time"), data.get("end_time")
        if start and end and end <= start:
            self.add_error("end_time", "End time must be after the start time.")
        if data.get("duration_minutes") == 0:
            self.add_error("duration_minutes", "Duration must be at least 1 minute.")
        return data

class QuestionForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Question
        fields = ["text", "marks", "order"]
        widgets = {"text": forms.Textarea(attrs={"rows": 3})}

    def clean_marks(self):
        marks = self.cleaned_data["marks"]
        if marks < 1:
            raise ValidationError("Marks must be at least 1.")
        return marks


class ChoiceForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Choice
        fields = ["text", "is_correct"]


class BaseChoiceFormSet(BaseInlineFormSet):
    """Job: enforces at least 2 options and exactly 1 correct."""

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        filled = correct = 0
        for form in self.forms:
            data = form.cleaned_data
            if not data or data.get("DELETE"):
                continue
            filled += 1
            if data.get("is_correct"):
                correct += 1
        if filled < 2:
            raise ValidationError("Give at least two options.")
        if correct != 1:
            raise ValidationError("Mark exactly one option as correct.")


def make_choice_formset(extra):
    return inlineformset_factory(
        Question, Choice,
        form=ChoiceForm, formset=BaseChoiceFormSet,
        fields=("text", "is_correct"),
        extra=extra, can_delete=True,
    )