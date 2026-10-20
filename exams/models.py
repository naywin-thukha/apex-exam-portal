from django.conf import settings
from django.db import models
from django.db.models import Sum


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # Teachers are linked to the subjects they may teach/manage.
    teachers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="subjects",
        blank=True,
        limit_choices_to={"role": "teacher"},
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Exam(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        CLOSED = "closed", "Closed"

    title = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="exams")
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_exams",
        limit_choices_to={"role": "teacher"},
    )
    instructions = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField()
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)
    show_answers = models.BooleanField(
        default=False, help_text="Let students see correct answers after submitting."
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Assignment",
        related_name="assigned_exams",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def total_marks(self):
        return self.questions.aggregate(t=Sum("marks"))["t"] or 0

    def __str__(self):
        return self.title


class Assignment(models.Model):
    """Which students may take which exam."""

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="assignments")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assignments",
        limit_choices_to={"role": "student"},
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["exam", "student"], name="unique_exam_student_assignment")
        ]

    def __str__(self):
        return f"{self.student} -> {self.exam}"


class Question(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
    marks = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["exam", "order", "id"]

    def __str__(self):
        return f"Q{self.order}: {self.text[:60]}"


class Choice(models.Model):
    """SRS 'Answer Option'. Exactly one correct per question (validated in admin/forms)."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text[:60]


class Attempt(models.Model):
    """SRS Submission + Result: one attempt per student per exam."""

    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In progress"
        SUBMITTED = "submitted", "Submitted"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="attempts"
    )
    exam = models.ForeignKey(Exam, on_delete=models.PROTECT, related_name="attempts")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.IN_PROGRESS)
    started_at = models.DateTimeField(auto_now_add=True)  # server-side timer anchor
    submitted_at = models.DateTimeField(null=True, blank=True)
    score = models.PositiveIntegerField(null=True, blank=True)
    total_marks = models.PositiveIntegerField(null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "exam"], name="unique_student_exam_attempt")
        ]

    def __str__(self):
        return f"{self.student} / {self.exam} ({self.status})"


class Answer(models.Model):
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(Question, on_delete=models.PROTECT, related_name="answers")
    selected_choice = models.ForeignKey(
        Choice, on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["attempt", "question"], name="unique_attempt_question_answer")
        ]

    def __str__(self):
        return f"{self.attempt_id}:{self.question_id}"