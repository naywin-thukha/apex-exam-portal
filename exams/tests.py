from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Choice, Exam, Question, Subject

from datetime import timedelta

from django.utils import timezone

from .models import Answer, Assignment, Attempt

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


class StudentExamFlowTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name="Maths")
        self.teacher = User.objects.create_user("t1", password=PW, role=User.Role.TEACHER)
        self.s1 = User.objects.create_user("s1", password=PW, role=User.Role.STUDENT)
        self.s2 = User.objects.create_user("s2", password=PW, role=User.Role.STUDENT)
        now = timezone.now()
        self.exam = Exam.objects.create(
            title="Quiz", subject=self.subject, creator=self.teacher,
            duration_minutes=30, status=Exam.Status.PUBLISHED,
            start_time=now - timedelta(hours=1), end_time=now + timedelta(hours=1),
        )
        Assignment.objects.create(exam=self.exam, student=self.s1)

        # two questions, 2 marks each; the first choice of each is correct
        self.questions = []
        for i in (1, 2):
            q = Question.objects.create(exam=self.exam, text=f"Q{i}", marks=2, order=i)
            right = Choice.objects.create(question=q, text="right", is_correct=True)
            wrong = Choice.objects.create(question=q, text="wrong", is_correct=False)
            self.questions.append((q, right, wrong))

        self.start = reverse("exams:exam_start", args=[self.exam.pk])
        self.take = reverse("exams:exam_take", args=[self.exam.pk])

    def login(self, name):
        self.client.login(username=name, password=PW)

    def test_assigned_student_can_start(self):
        self.login("s1")
        self.client.post(self.start)
        self.assertTrue(Attempt.objects.filter(student=self.s1, exam=self.exam).exists())

    def test_unassigned_student_cannot_start(self):
        self.login("s2")
        resp = self.client.post(self.start)
        self.assertEqual(resp.status_code, 404)
        self.assertFalse(Attempt.objects.filter(student=self.s2).exists())

    def test_draft_exam_is_hidden(self):
        self.exam.status = Exam.Status.DRAFT
        self.exam.save()
        self.login("s1")
        self.assertEqual(self.client.post(self.start).status_code, 404)

    def test_cannot_start_before_open_time(self):
        self.exam.start_time = timezone.now() + timedelta(hours=1)
        self.exam.end_time = timezone.now() + timedelta(hours=2)
        self.exam.save()
        self.login("s1")
        self.client.post(self.start)
        self.assertFalse(Attempt.objects.filter(student=self.s1).exists())

    def test_cannot_start_after_close_time(self):
        self.exam.start_time = timezone.now() - timedelta(hours=2)
        self.exam.end_time = timezone.now() - timedelta(hours=1)
        self.exam.save()
        self.login("s1")
        self.client.post(self.start)
        self.assertFalse(Attempt.objects.filter(student=self.s1).exists())

    def test_double_start_makes_one_attempt(self):
        self.login("s1")
        self.client.post(self.start)
        self.client.post(self.start)
        self.assertEqual(Attempt.objects.filter(student=self.s1, exam=self.exam).count(), 1)

    def test_submit_grades_correctly(self):
        self.login("s1")
        self.client.post(self.start)
        (q1, r1, w1), (q2, r2, w2) = self.questions
        self.client.post(self.take, {
            "action": "submit", f"q_{q1.id}": r1.id, f"q_{q2.id}": w2.id,
        })
        attempt = Attempt.objects.get(student=self.s1, exam=self.exam)
        self.assertEqual(attempt.status, Attempt.Status.SUBMITTED)
        self.assertEqual(attempt.score, 2)
        self.assertEqual(attempt.total_marks, 4)
        self.assertEqual(float(attempt.percentage), 50.0)

    def test_submitted_attempt_cannot_be_changed(self):
        self.login("s1")
        self.client.post(self.start)
        (q1, r1, w1), _ = self.questions
        self.client.post(self.take, {"action": "submit", f"q_{q1.id}": r1.id})
        # try to change the answer afterwards
        self.client.post(self.take, {"action": "submit", f"q_{q1.id}": w1.id})
        attempt = Attempt.objects.get(student=self.s1, exam=self.exam)
        self.assertEqual(attempt.score, 2)
        self.assertEqual(Answer.objects.get(attempt=attempt, question=q1).selected_choice_id, r1.id)

    def test_expired_attempt_is_graded_on_return(self):
        self.login("s1")
        self.client.post(self.start)
        attempt = Attempt.objects.get(student=self.s1, exam=self.exam)
        (q1, r1, w1), _ = self.questions
        Answer.objects.create(attempt=attempt, question=q1, selected_choice=r1)
        # pretend the attempt started long ago
        Attempt.objects.filter(pk=attempt.pk).update(started_at=timezone.now() - timedelta(hours=3))
        self.client.get(self.take)
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, Attempt.Status.SUBMITTED)
        self.assertEqual(attempt.score, 2)

    def test_answer_from_another_question_is_ignored(self):
        self.login("s1")
        self.client.post(self.start)
        (q1, r1, w1), (q2, r2, w2) = self.questions
        # option of Q2 posted as the answer to Q1
        self.client.post(self.take, {"action": "save", f"q_{q1.id}": r2.id})
        attempt = Attempt.objects.get(student=self.s1, exam=self.exam)
        self.assertFalse(Answer.objects.filter(attempt=attempt, question=q1).exists())

    def test_result_page_only_for_own_submitted_attempt(self):
        result = reverse("exams:exam_result", args=[self.exam.pk])
        self.login("s1")
        self.client.post(self.start)
        # not submitted yet
        self.assertEqual(self.client.get(result).status_code, 404)
        self.client.post(self.take, {"action": "submit"})
        self.assertEqual(self.client.get(result).status_code, 200)
        # a different student cannot see it
        self.client.logout()
        self.login("s2")
        self.assertEqual(self.client.get(result).status_code, 404)

    def test_student_cannot_open_teacher_results(self):
        self.login("s1")
        resp = self.client.get(reverse("exams:exam_results", args=[self.exam.pk]))
        self.assertEqual(resp.status_code, 403)

    def test_teacher_results_page_works(self):
        self.login("t1")
        resp = self.client.get(reverse("exams:exam_results", args=[self.exam.pk]))
        self.assertEqual(resp.status_code, 200)