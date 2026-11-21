from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Choice, Exam, Question, Subject

from datetime import timedelta

from django.utils import timezone

from .models import Answer, Assignment, Attempt

from unittest.mock import patch

from .views import finalize_attempt

from django.template.loader import render_to_string

import json

from .views import ordered_questions

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

    def flag_url(self):
        return reverse("exams:exam_flag", args=[self.exam.pk])

    def test_flag_is_saved_without_an_answer(self):
        self.login("s1")
        self.client.post(self.start)
        q, right, wrong = self.questions[0]
        resp = self.client.post(self.flag_url(), {"question": q.id, "marked": "1"})
        self.assertEqual(resp.status_code, 200)
        answer = Answer.objects.get(question=q)
        self.assertTrue(answer.marked_for_review)
        self.assertIsNone(answer.selected_choice)

    def test_flag_and_answer_do_not_overwrite_each_other(self):
        self.login("s1")
        self.client.post(self.start)
        q, right, wrong = self.questions[0]
        self.client.post(self.flag_url(), {"question": q.id, "marked": "1"})
        self.client.post(self.autosave_url(), {"question": q.id, "choice": right.id})
        answer = Answer.objects.get(question=q)
        self.assertTrue(answer.marked_for_review)
        self.assertEqual(answer.selected_choice_id, right.id)
        # un-flagging keeps the chosen option
        self.client.post(self.flag_url(), {"question": q.id, "marked": "0"})
        answer.refresh_from_db()
        self.assertFalse(answer.marked_for_review)
        self.assertEqual(answer.selected_choice_id, right.id)

    def test_flag_rejects_bad_input(self):
        self.login("s1")
        self.client.post(self.start)
        q, right, wrong = self.questions[0]
        self.assertEqual(self.client.post(self.flag_url(), {"question": q.id, "marked": "yes"}).status_code, 400)
        self.assertEqual(self.client.post(self.flag_url(), {"question": "abc", "marked": "1"}).status_code, 400)
        self.assertEqual(self.client.post(self.flag_url(), {"question": 999999, "marked": "1"}).status_code, 400)
        self.assertFalse(Answer.objects.exists())

    def test_flag_rejected_after_submit(self):
        self.login("s1")
        self.client.post(self.start)
        q, right, wrong = self.questions[0]
        self.client.post(self.take, {"action": "submit"})
        resp = self.client.post(self.flag_url(), {"question": q.id, "marked": "1"})
        self.assertEqual(resp.status_code, 409)
        self.assertFalse(Answer.objects.filter(marked_for_review=True).exists())

    def test_flag_rejected_after_deadline(self):
        self.login("s1")
        self.client.post(self.start)
        attempt = Attempt.objects.get(student=self.s1, exam=self.exam)
        q, right, wrong = self.questions[0]
        late = attempt.started_at + timedelta(minutes=30, seconds=60)
        with patch("django.utils.timezone.now", return_value=late):
            resp = self.client.post(self.flag_url(), {"question": q.id, "marked": "1"})
        self.assertEqual(resp.status_code, 409)
        self.assertFalse(Answer.objects.exists())

    def test_flag_needs_an_assigned_student_with_a_started_attempt(self):
        q, right, wrong = self.questions[0]
        self.login("s2")  # not assigned to the exam
        self.assertEqual(self.client.post(self.flag_url(), {"question": q.id, "marked": "1"}).status_code, 404)
        self.client.logout()
        self.login("s1")  # assigned, but has not started
        self.assertEqual(self.client.post(self.flag_url(), {"question": q.id, "marked": "1"}).status_code, 404)

    def test_teacher_cannot_use_the_flag_endpoint(self):
        self.login("t1")
        q, right, wrong = self.questions[0]
        self.assertEqual(self.client.post(self.flag_url(), {"question": q.id, "marked": "1"}).status_code, 403)

    def test_a_flag_alone_does_not_change_the_score(self):
        self.login("s1")
        self.client.post(self.start)
        (q1, r1, w1), (q2, r2, w2) = self.questions
        self.client.post(self.flag_url(), {"question": q1.id, "marked": "1"})
        self.client.post(self.take, {"action": "submit", f"q_{q2.id}": r2.id})
        attempt = Attempt.objects.get(student=self.s1, exam=self.exam)
        self.assertEqual(attempt.score, 2)  # only Q2 answered (2 marks)

    def test_flag_is_restored_when_the_page_is_reloaded(self):
        self.login("s1")
        self.client.post(self.start)
        (q1, r1, w1), (q2, r2, w2) = self.questions
        self.client.post(self.flag_url(), {"question": q2.id, "marked": "1"})
        resp = self.client.get(self.take)
        flags = {q.id: q.saved_flag for q in resp.context["questions"]}
        self.assertEqual(flags, {q1.id: False, q2.id: True})
        self.assertContains(resp, 'data-flagged="1"')
        self.assertContains(resp, 'data-flagged="0"')

    def test_exam_page_has_the_submit_confirmation(self):
        self.login("s1")
        self.client.post(self.start)
        resp = self.client.get(self.take)
        self.assertContains(resp, 'id="submitModal"')
        self.assertContains(resp, 'id="submitbtn"')
        self.assertContains(resp, 'id="confirmSubmit"')

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

class OwnershipTests(TestCase):
    """A teacher cannot touch another teacher's exam. A student cannot use teacher pages."""

    def setUp(self):
        self.subject = Subject.objects.create(name="Maths")
        self.owner = User.objects.create_user("owner", password=PW, role=User.Role.TEACHER)
        self.other = User.objects.create_user("other", password=PW, role=User.Role.TEACHER)
        self.student = User.objects.create_user("s1", password=PW, role=User.Role.STUDENT)
        self.subject.teachers.add(self.owner, self.other)

        self.exam = Exam.objects.create(
            title="Private", subject=self.subject, creator=self.owner, duration_minutes=30
        )
        self.question = Question.objects.create(exam=self.exam, text="Q1", marks=1, order=1)
        Choice.objects.create(question=self.question, text="a", is_correct=True)
        Choice.objects.create(question=self.question, text="b", is_correct=False)

        pk, qpk = self.exam.pk, self.question.pk
        self.get_urls = [
            reverse("exams:exam_detail", args=[pk]),
            reverse("exams:exam_update", args=[pk]),
            reverse("exams:exam_delete", args=[pk]),
            reverse("exams:exam_students", args=[pk]),
            reverse("exams:exam_results", args=[pk]),
            reverse("exams:question_create", args=[pk]),
            reverse("exams:question_edit", args=[pk, qpk]),
        ]
        self.post_urls = [
            reverse("exams:exam_update", args=[pk]),
            reverse("exams:exam_delete", args=[pk]),
            reverse("exams:exam_publish", args=[pk]),
            reverse("exams:exam_unpublish", args=[pk]),
            reverse("exams:exam_students", args=[pk]),
            reverse("exams:question_create", args=[pk]),
            reverse("exams:question_edit", args=[pk, qpk]),
            reverse("exams:question_delete", args=[pk, qpk]),
        ]

    def test_other_teacher_gets_404_on_every_page(self):
        self.client.login(username="other", password=PW)
        for url in self.get_urls:
            self.assertEqual(self.client.get(url).status_code, 404, f"GET {url}")

    def test_other_teacher_cannot_change_anything(self):
        self.client.login(username="other", password=PW)
        for url in self.post_urls:
            self.assertEqual(self.client.post(url, {"title": "hacked"}).status_code, 404, f"POST {url}")
        # nothing changed
        self.exam.refresh_from_db()
        self.assertEqual(self.exam.title, "Private")
        self.assertEqual(self.exam.status, Exam.Status.DRAFT)
        self.assertTrue(Question.objects.filter(pk=self.question.pk).exists())
        self.assertEqual(self.exam.assignments.count(), 0)

    def test_student_is_blocked_from_every_teacher_page(self):
        self.client.login(username="s1", password=PW)
        for url in self.get_urls:
            self.assertEqual(self.client.get(url).status_code, 403, f"GET {url}")
        for url in self.post_urls:
            self.assertEqual(self.client.post(url, {}).status_code, 403, f"POST {url}")
        self.assertTrue(Exam.objects.filter(pk=self.exam.pk).exists())

    def test_anonymous_is_redirected_from_every_teacher_page(self):
        for url in self.get_urls:
            self.assertEqual(self.client.get(url).status_code, 302, f"GET {url}")

    def test_teacher_cannot_use_student_pages(self):
        self.client.login(username="owner", password=PW)
        for name in ("exam_start", "exam_take", "exam_autosave", "exam_result"):
            url = reverse(f"exams:{name}", args=[self.exam.pk])
            self.assertEqual(self.client.get(url).status_code, 403, name)


class StudentIsolationTests(TestCase):
    """A student cannot see or change another student's attempt."""

    def setUp(self):
        self.subject = Subject.objects.create(name="Maths")
        self.teacher = User.objects.create_user("t1", password=PW, role=User.Role.TEACHER)
        self.a = User.objects.create_user("alice", password=PW, role=User.Role.STUDENT)
        self.b = User.objects.create_user("bob", password=PW, role=User.Role.STUDENT)
        now = timezone.now()
        self.exam = Exam.objects.create(
            title="Shared", subject=self.subject, creator=self.teacher,
            duration_minutes=30, status=Exam.Status.PUBLISHED,
            start_time=now - timedelta(hours=1), end_time=now + timedelta(hours=1),
        )
        Assignment.objects.create(exam=self.exam, student=self.a)
        Assignment.objects.create(exam=self.exam, student=self.b)
        self.q = Question.objects.create(exam=self.exam, text="Q1", marks=1, order=1)
        self.right = Choice.objects.create(question=self.q, text="a", is_correct=True)
        self.wrong = Choice.objects.create(question=self.q, text="b", is_correct=False)

        # Alice takes and submits the exam
        self.client.login(username="alice", password=PW)
        self.client.post(reverse("exams:exam_start", args=[self.exam.pk]))
        self.client.post(
            reverse("exams:exam_take", args=[self.exam.pk]),
            {"action": "submit", f"q_{self.q.id}": self.right.id},
        )
        self.client.logout()

    def test_bob_does_not_get_alices_result(self):
        self.client.login(username="bob", password=PW)
        resp = self.client.get(reverse("exams:exam_result", args=[self.exam.pk]))
        self.assertEqual(resp.status_code, 404)

    def test_bob_cannot_change_alices_answers(self):
        self.client.login(username="bob", password=PW)
        # bob has not started, so there is no attempt to write to
        resp = self.client.post(
            reverse("exams:exam_autosave", args=[self.exam.pk]),
            {"question": self.q.id, "choice": self.wrong.id},
        )
        self.assertEqual(resp.status_code, 404)
        alice_attempt = Attempt.objects.get(student=self.a, exam=self.exam)
        self.assertEqual(Answer.objects.get(attempt=alice_attempt).selected_choice_id, self.right.id)
        self.assertEqual(alice_attempt.score, 1)

    def test_bobs_own_attempt_is_separate(self):
        self.client.login(username="bob", password=PW)
        self.client.post(reverse("exams:exam_start", args=[self.exam.pk]))
        self.client.post(
            reverse("exams:exam_take", args=[self.exam.pk]),
            {"action": "submit", f"q_{self.q.id}": self.wrong.id},
        )
        self.assertEqual(Attempt.objects.get(student=self.b, exam=self.exam).score, 0)
        self.assertEqual(Attempt.objects.get(student=self.a, exam=self.exam).score, 1)

class ErrorPageTests(TestCase):
    def setUp(self):
        self.student = User.objects.create_user("s1", password=PW, role=User.Role.STUDENT)

    def test_404_uses_the_custom_page(self):
        self.client.login(username="s1", password=PW)
        resp = self.client.get("/this/does/not/exist/")
        self.assertEqual(resp.status_code, 404)
        self.assertContains(resp, "Page not found", status_code=404)

    def test_404_for_anonymous_visitor_also_works(self):
        resp = self.client.get("/this/does/not/exist/")
        self.assertContains(resp, "Page not found", status_code=404)

    def test_500_page_is_standalone_and_renders(self):
        html = render_to_string("500.html")
        self.assertIn("Something went wrong", html)
        self.assertNotIn("{%", html)  # no unrendered template tags

    def test_403_page_renders(self):
        html = render_to_string("403.html")
        self.assertIn("Not allowed", html)

from django.test import Client


class LoginCsrfTests(TestCase):
    def setUp(self):
        User.objects.create_user("s1", password=PW, role=User.Role.STUDENT)
        self.url = reverse("accounts:login")

    def test_login_without_csrf_token_is_rejected(self):
        client = Client(enforce_csrf_checks=True)
        resp = client.post(self.url, {"username": "s1", "password": PW})
        self.assertEqual(resp.status_code, 403)

    def test_login_page_contains_a_csrf_token(self):
        resp = Client(enforce_csrf_checks=True).get(self.url)
        self.assertContains(resp, "csrfmiddlewaretoken")

    def test_login_works_with_the_token_from_the_page(self):
        client = Client(enforce_csrf_checks=True)
        page = client.get(self.url)
        token = page.cookies["csrftoken"].value
        resp = client.post(
            self.url,
            {"username": "s1", "password": PW, "csrfmiddlewaretoken": token},
        )
        self.assertEqual(resp.status_code, 302)

class ShuffleTests(TestCase):
    QUESTIONS = 8  # enough that two students almost never get the same order by chance

    def setUp(self):
        self.subject = Subject.objects.create(name="Maths")
        self.teacher = User.objects.create_user("t1", password=PW, role=User.Role.TEACHER)
        now = timezone.now()
        self.exam = Exam.objects.create(
            title="Shuffle", subject=self.subject, creator=self.teacher,
            duration_minutes=30, status=Exam.Status.PUBLISHED,
            start_time=now - timedelta(hours=1), end_time=now + timedelta(hours=2),
            shuffle_questions=True, shuffle_options=True,
        )
        self.students = []
        for i in range(6):
            s = User.objects.create_user(f"s{i}", password=PW, role=User.Role.STUDENT)
            Assignment.objects.create(exam=self.exam, student=s)
            self.students.append(s)

        self.questions = []
        for n in range(1, self.QUESTIONS + 1):
            q = Question.objects.create(exam=self.exam, text=f"Q{n}", marks=1, order=n)
            for k in range(4):  # the first option is the correct one
                Choice.objects.create(question=q, text=f"opt {k}", is_correct=(k == 0))
            self.questions.append(q)

        self.start_url = reverse("exams:exam_start", args=[self.exam.pk])
        self.take_url = reverse("exams:exam_take", args=[self.exam.pk])

    def start(self, index=0):
        """Log in as student `index`, click Start, return the attempt."""
        student = self.students[index]
        self.client.login(username=student.username, password=PW)
        self.client.post(self.start_url)
        return Attempt.objects.get(student=student, exam=self.exam)

    def shown(self):
        """The question ids the student page shows, in order (and the response)."""
        resp = self.client.get(self.take_url)
        self.assertEqual(resp.status_code, 200)
        return [q.id for q in resp.context["questions"]], resp

    def test_orders_are_saved_when_the_attempt_starts(self):
        attempt = self.start()
        self.assertEqual(
            sorted(attempt.question_order), sorted(q.id for q in self.questions)
        )
        for q in self.questions:
            self.assertEqual(
                sorted(attempt.option_order[str(q.id)]),
                sorted(c.id for c in q.choices.all()),
            )

    def test_shuffling_off_keeps_the_normal_order(self):
        Exam.objects.filter(pk=self.exam.pk).update(shuffle_questions=False, shuffle_options=False)
        attempt = self.start()
        self.assertEqual(attempt.question_order, [q.id for q in self.questions])
        for q in self.questions:
            self.assertEqual(
                attempt.option_order[str(q.id)], sorted(c.id for c in q.choices.all())
            )

    def test_different_students_get_different_orders(self):
        attempts = [self.start(i) for i in range(6)]
        question_orders = {tuple(a.question_order) for a in attempts}
        option_orders = {json.dumps(a.option_order, sort_keys=True) for a in attempts}
        self.assertGreater(len(question_orders), 1)
        self.assertGreater(len(option_orders), 1)

    def test_order_is_stable_after_reloads(self):
        attempt = self.start()
        first, _ = self.shown()
        for _ in range(3):
            again, _ = self.shown()
            self.assertEqual(again, first)
        attempt.refresh_from_db()
        self.assertEqual(first, attempt.question_order)

    def test_clicking_start_twice_does_not_reshuffle(self):
        attempt = self.start()
        before = list(attempt.question_order)
        self.client.post(self.start_url)
        attempt.refresh_from_db()
        self.assertEqual(attempt.question_order, before)
        self.assertEqual(Attempt.objects.filter(exam=self.exam).count(), 1)

    def test_page_is_drawn_from_the_saved_order(self):
        attempt = self.start()
        wanted = list(reversed(attempt.question_order))
        Attempt.objects.filter(pk=attempt.pk).update(question_order=wanted)
        ids, _ = self.shown()
        self.assertEqual(ids, wanted)

    def test_options_are_drawn_from_the_saved_order(self):
        attempt = self.start()
        q = self.questions[0]
        wanted = list(reversed(attempt.option_order[str(q.id)]))
        new_options = dict(attempt.option_order)
        new_options[str(q.id)] = wanted
        Attempt.objects.filter(pk=attempt.pk).update(option_order=new_options)
        _, resp = self.shown()
        page_q = next(x for x in resp.context["questions"] if x.id == q.id)
        self.assertEqual([c.id for c in page_q.ordered_choices], wanted)
        self.assertEqual([c.letter for c in page_q.ordered_choices], list("ABCD"))

    def test_grading_is_unchanged_by_the_order(self):
        attempt = self.start()
        data = {"action": "submit"}
        for q in self.questions:
            data[f"q_{q.id}"] = q.choices.get(is_correct=True).id
        self.client.post(self.take_url, data)
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, self.QUESTIONS)
        self.assertEqual(attempt.total_marks, self.QUESTIONS)

    def test_a_wrong_answer_is_still_wrong_in_any_order(self):
        attempt = self.start()
        data = {"action": "submit"}
        for q in self.questions:
            data[f"q_{q.id}"] = q.choices.get(is_correct=False, text="opt 1").id
        self.client.post(self.take_url, data)
        attempt.refresh_from_db()
        self.assertEqual(attempt.score, 0)

    def test_old_attempt_without_an_order_gets_one_and_keeps_it(self):
        student = self.students[0]
        self.client.login(username=student.username, password=PW)
        attempt = Attempt.objects.create(student=student, exam=self.exam)  # no order saved
        first, _ = self.shown()
        attempt.refresh_from_db()
        self.assertIsNotNone(attempt.question_order)
        second, _ = self.shown()
        self.assertEqual(first, second)

    def test_a_question_missing_from_the_saved_order_is_not_lost(self):
        attempt = self.start()
        keep = attempt.question_order[0]
        Attempt.objects.filter(pk=attempt.pk).update(question_order=[keep])
        ids, _ = self.shown()
        self.assertEqual(ids[0], keep)
        self.assertEqual(sorted(ids), sorted(q.id for q in self.questions))

    def test_typed_letters_are_replaced_by_the_pages_own(self):
        attempt = self.start()
        q = Question.objects.create(exam=self.exam, text="Lettered", marks=1, order=99)
        for text in ("A. (5, 10, 7)", "B) two", "C. x = 3", "plain"):
            Choice.objects.create(question=q, text=text, is_correct=(text == "plain"))
        page_q = next(x for x in ordered_questions(self.exam, attempt) if x.id == q.id)
        shown = {c.text: c.display_text for c in page_q.ordered_choices}
        self.assertEqual(shown["A. (5, 10, 7)"], "(5, 10, 7)")
        self.assertEqual(shown["B) two"], "two")
        self.assertEqual(shown["C. x = 3"], "x = 3")
        self.assertEqual(shown["plain"], "plain")
        self.assertEqual(sorted(c.letter for c in page_q.ordered_choices), list("ABCD"))
    
