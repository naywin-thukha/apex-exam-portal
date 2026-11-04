from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Choice, Exam, Question, Subject

from datetime import timedelta

from django.utils import timezone

from .models import Answer, Assignment, Attempt

from unittest.mock import patch

from .views import finalize_attempt

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

    def autosave_url(self):
        return reverse("exams:exam_autosave", args=[self.exam.pk])

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

        def autosave_url(self):
         return reverse("exams:exam_autosave", args=[self.exam.pk])

    def test_autosave_stores_and_changes_answer(self):
        self.login("s1")
        self.client.post(self.start)
        q, right, wrong = self.questions[0]
        resp = self.client.post(self.autosave_url(), {"question": q.id, "choice": right.id})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Answer.objects.get(question=q).selected_choice_id, right.id)
        self.client.post(self.autosave_url(), {"question": q.id, "choice": wrong.id})
        self.assertEqual(Answer.objects.filter(question=q).count(), 1)
        self.assertEqual(Answer.objects.get(question=q).selected_choice_id, wrong.id)

    def test_autosave_rejects_option_from_another_question(self):
        self.login("s1")
        self.client.post(self.start)
        (q1, r1, w1), (q2, r2, w2) = self.questions
        resp = self.client.post(self.autosave_url(), {"question": q1.id, "choice": r2.id})
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(Answer.objects.exists())

    def test_autosave_rejected_after_submit(self):
        self.login("s1")
        self.client.post(self.start)
        q, right, wrong = self.questions[0]
        self.client.post(self.take, {"action": "submit", f"q_{q.id}": right.id})
        resp = self.client.post(self.autosave_url(), {"question": q.id, "choice": wrong.id})
        self.assertEqual(resp.status_code, 409)
        self.assertEqual(Answer.objects.get(question=q).selected_choice_id, right.id)

    def test_autosave_rejected_after_deadline(self):
        from unittest.mock import patch
        self.login("s1")
        self.client.post(self.start)
        attempt = Attempt.objects.get(student=self.s1, exam=self.exam)
        q, right, wrong = self.questions[0]
        late = attempt.started_at + timedelta(minutes=30, seconds=60)
        with patch("django.utils.timezone.now", return_value=late):
            resp = self.client.post(self.autosave_url(), {"question": q.id, "choice": right.id})
        self.assertEqual(resp.status_code, 409)
        self.assertFalse(Answer.objects.exists())

    def test_autosave_needs_a_started_attempt(self):
        self.login("s1")
        q, right, wrong = self.questions[0]
        resp = self.client.post(self.autosave_url(), {"question": q.id, "choice": right.id})
        self.assertEqual(resp.status_code, 404)

    def test_autosave_unassigned_student_gets_404(self):
        self.login("s2")
        q, right, wrong = self.questions[0]
        resp = self.client.post(self.autosave_url(), {"question": q.id, "choice": right.id})
        self.assertEqual(resp.status_code, 404)

class GradingTests(TestCase):
    def setUp(self):
        self.subject = Subject.objects.create(name="Maths")
        self.teacher = User.objects.create_user("t1", password=PW, role=User.Role.TEACHER)
        self.student = User.objects.create_user("s1", password=PW, role=User.Role.STUDENT)
        now = timezone.now()
        self.exam = Exam.objects.create(
            title="Graded", subject=self.subject, creator=self.teacher,
            duration_minutes=30, status=Exam.Status.PUBLISHED,
            start_time=now - timedelta(hours=1), end_time=now + timedelta(hours=2),
        )
        Assignment.objects.create(exam=self.exam, student=self.student)

        # marks 1, 2, 3 -> total 6
        self.qs = []
        for order, marks in enumerate((1, 2, 3), start=1):
            q = Question.objects.create(exam=self.exam, text=f"Q{order}", marks=marks, order=order)
            right = Choice.objects.create(question=q, text="right", is_correct=True)
            wrong = Choice.objects.create(question=q, text="wrong", is_correct=False)
            self.qs.append((q, right, wrong))

    def graded(self, picks):
        """picks: list of 'right' / 'wrong' / None for each question, in order."""
        attempt = Attempt.objects.create(student=self.student, exam=self.exam)
        for (q, right, wrong), pick in zip(self.qs, picks):
            if pick:
                Answer.objects.create(
                    attempt=attempt, question=q,
                    selected_choice=right if pick == "right" else wrong,
                )
        return finalize_attempt(attempt)

    def test_all_correct(self):
        a = self.graded(["right", "right", "right"])
        self.assertEqual((a.score, a.total_marks), (6, 6))
        self.assertEqual(float(a.percentage), 100.0)
        self.assertEqual(a.status, Attempt.Status.SUBMITTED)
        self.assertIsNotNone(a.submitted_at)

    def test_all_wrong(self):
        a = self.graded(["wrong", "wrong", "wrong"])
        self.assertEqual((a.score, a.total_marks), (0, 6))
        self.assertEqual(float(a.percentage), 0.0)

    def test_unanswered(self):
        a = self.graded([None, None, None])
        self.assertEqual((a.score, a.total_marks), (0, 6))
        self.assertEqual(float(a.percentage), 0.0)

    def test_partial(self):
        # Q1 (1 mark) right, Q2 (2 marks) wrong, Q3 (3 marks) right -> 4 of 6
        a = self.graded(["right", "wrong", "right"])
        self.assertEqual((a.score, a.total_marks), (4, 6))
        self.assertAlmostEqual(float(a.percentage), 66.67, places=2)

    def test_zero_questions_does_not_crash(self):
        empty = Exam.objects.create(
            title="Empty", subject=self.subject, creator=self.teacher,
            duration_minutes=10, status=Exam.Status.PUBLISHED,
        )
        attempt = Attempt.objects.create(student=self.student, exam=empty)
        a = finalize_attempt(attempt)
        self.assertEqual((a.score, a.total_marks), (0, 0))
        self.assertEqual(float(a.percentage), 0.0)

    def test_finalize_twice_does_not_change_score(self):
        a = self.graded(["right", "right", "right"])
        # tamper with the stored answers, then "submit" again
        Answer.objects.filter(attempt=a).update(selected_choice=self.qs[0][2])
        again = finalize_attempt(a)
        self.assertEqual(again.score, 6)
        a.refresh_from_db()
        self.assertEqual(a.score, 6)

    def test_submit_twice_through_the_page(self):
        self.client.login(username="s1", password=PW)
        self.client.post(reverse("exams:exam_start", args=[self.exam.pk]))
        take = reverse("exams:exam_take", args=[self.exam.pk])
        (q1, r1, w1), (q2, r2, w2), (q3, r3, w3) = self.qs
        data = {"action": "submit", f"q_{q1.id}": r1.id, f"q_{q2.id}": r2.id, f"q_{q3.id}": r3.id}
        self.client.post(take, data)
        self.client.post(take, {"action": "submit", f"q_{q1.id}": w1.id})
        attempt = Attempt.objects.get(student=self.student, exam=self.exam)
        self.assertEqual(attempt.score, 6)

    def _start_and_answer_first(self):
        """Student starts and saves the first question correctly. Returns (attempt, take_url)."""
        self.client.login(username="s1", password=PW)
        self.client.post(reverse("exams:exam_start", args=[self.exam.pk]))
        take = reverse("exams:exam_take", args=[self.exam.pk])
        q1, r1, w1 = self.qs[0]
        self.client.post(take, {"action": "save", f"q_{q1.id}": r1.id})
        return Attempt.objects.get(student=self.student, exam=self.exam), take

    def test_submit_exactly_at_the_deadline_is_accepted(self):
        attempt, take = self._start_and_answer_first()
        deadline = attempt.started_at + timedelta(minutes=30)
        q2, r2, w2 = self.qs[1]
        with patch("django.utils.timezone.now", return_value=deadline):
            self.client.post(take, {"action": "submit", f"q_{q2.id}": r2.id})
        attempt.refresh_from_db()
        # Q1 (1) + Q2 (2): the answer sent exactly at the deadline still counts
        self.assertEqual(attempt.score, 3)
        self.assertEqual(attempt.status, Attempt.Status.SUBMITTED)

    def test_submit_long_after_deadline_ignores_new_answers(self):
        attempt, take = self._start_and_answer_first()
        late = attempt.started_at + timedelta(minutes=30, seconds=60)
        q2, r2, w2 = self.qs[1]
        with patch("django.utils.timezone.now", return_value=late):
            self.client.post(take, {"action": "submit", f"q_{q2.id}": r2.id})
        attempt.refresh_from_db()
        # only the answer saved earlier counts; Q2 sent too late is ignored
        self.assertEqual(attempt.score, 1)
        self.assertEqual(attempt.status, Attempt.Status.SUBMITTED)

    def test_opening_page_at_the_deadline_auto_submits(self):
        attempt, take = self._start_and_answer_first()
        deadline = attempt.started_at + timedelta(minutes=30)
        with patch("django.utils.timezone.now", return_value=deadline):
            self.client.get(take)
        attempt.refresh_from_db()
        self.assertEqual(attempt.status, Attempt.Status.SUBMITTED)
        self.assertEqual(attempt.score, 1)