from __future__ import annotations

from django.test import TestCase

from apps.assignments.models import Submission
from apps.assignments.services import (
    create_new_submission_attempt,
    save_submission_answer,
    start_submission,
    submit_submission,
)
from apps.assignments.tests.factories import (
    create_assignment,
    create_assignment_policy,
    create_assignment_question,
    create_student_user,
)
from apps.assignments.tests.test_services.services_common import (
    create_published_assigned_publication,
)


class SubmissionServicesTestCase(TestCase):
    def test_start_submission(self):
        student = create_student_user()
        assignment = create_assignment()
        publication = create_published_assigned_publication(
            assignment=assignment,
            student=student,
        )

        submission = start_submission(
            publication=publication,
            student=student,
            variant=None,
        )

        self.assertIsNotNone(submission.pk)
        self.assertEqual(submission.student_id, student.id)
        self.assertEqual(submission.status, Submission.StatusChoices.IN_PROGRESS)

    def test_save_submission_answer(self):
        student = create_student_user()
        assignment = create_assignment()
        question = create_assignment_question(assignment=assignment)
        publication = create_published_assigned_publication(
            assignment=assignment,
            student=student,
        )

        submission = start_submission(
            publication=publication,
            student=student,
            variant=None,
        )

        answer = save_submission_answer(
            submission=submission,
            question=question,
            answer_text="Мой ответ",
            answer_json=None,
            selected_options_json=None,
            numeric_answer=None,
        )

        self.assertEqual(answer.submission_id, submission.id)
        self.assertEqual(answer.question_id, question.id)

    def test_submit_submission(self):
        student = create_student_user()
        assignment = create_assignment()
        question = create_assignment_question(assignment=assignment)
        publication = create_published_assigned_publication(
            assignment=assignment,
            student=student,
        )

        submission = start_submission(
            publication=publication,
            student=student,
            variant=None,
        )
        save_submission_answer(
            submission=submission,
            question=question,
            answer_text="Ответ",
            answer_json=None,
            selected_options_json=None,
            numeric_answer=None,
        )

        submitted = submit_submission(submission)

        self.assertEqual(submitted.status, Submission.StatusChoices.SUBMITTED)
        self.assertIsNotNone(submitted.submitted_at)

    def test_create_new_submission_attempt(self):
        student = create_student_user()
        assignment = create_assignment()
        create_assignment_policy(assignment, attempts_limit=2)

        publication = create_published_assigned_publication(
            assignment=assignment,
            student=student,
        )

        submission = start_submission(
            publication=publication,
            student=student,
            variant=None,
        )
        submission = submit_submission(submission)

        new_submission = create_new_submission_attempt(submission)

        self.assertNotEqual(new_submission.id, submission.id)
        self.assertEqual(
            new_submission.attempt_number,
            submission.attempt_number + 1,
        )
