from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Choice, Exam, Question, Subject

PW = "pw-12345-x"


class TeacherExamTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name="Maths")
        self.t1 = User.objects.create_user("t1", password=PW, role=User.Role.TEACHER)
        self.t2 = User.objects.create_user("t2", password=PW, role=User.Role.TEACHER)
        self.student = User.objects.create_user("s1", password=PW, role=User.Role.STUDENT)
        self.subject.teachers.add(self.t1, self.t2)
        self.exam = Exam.objects.create(
            title="Quiz 1", subject=self.subject, creator=self.t1, duration_minutes=30
        )
        self.detail = reverse("exams:exam_detail", args=[self.exam.pk])

    def test_anonymous_is_redirected(self):
        resp = self.client.get(reverse("exams:exam_list"))
        self.assertEqual(resp.status_code, 302)

    def test_student_is_forbidden(self):
        self.client.login(username="s1", password=PW)
        self.assertEqual(self.client.get(reverse("exams:exam_list")).status_code, 403)
        self.assertEqual(self.client.get(self.detail).status_code, 403)

    def test_other_teacher_gets_404(self):
        self.client.login(username="t2", password=PW)
        self.assertEqual(self.client.get(self.detail).status_code, 404)

    def test_owner_can_view(self):
        self.client.login(username="t1", password=PW)
        self.assertEqual(self.client.get(self.detail).status_code, 200)

    def test_cannot_publish_without_questions(self):
        self.client.login(username="t1", password=PW)
        self.client.post(reverse("exams:exam_publish", args=[self.exam.pk]))
        self.exam.refresh_from_db()
        self.assertEqual(self.exam.status, Exam.Status.DRAFT)

    def test_can_publish_valid_exam_then_it_is_locked(self):
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        self.exam.start_time = now
        self.exam.end_time = now + timedelta(hours=2)
        self.exam.save()
        q = Question.objects.create(exam=self.exam, text="2+2?", marks=1, order=1)
        Choice.objects.create(question=q, text="4", is_correct=True)
        Choice.objects.create(question=q, text="5", is_correct=False)

        self.client.login(username="t1", password=PW)
        self.client.post(reverse("exams:exam_publish", args=[self.exam.pk]))
        self.exam.refresh_from_db()
        self.assertEqual(self.exam.status, Exam.Status.PUBLISHED)

        # a published exam can no longer be edited
        resp = self.client.get(reverse("exams:exam_update", args=[self.exam.pk]))
        self.assertEqual(resp.status_code, 404)