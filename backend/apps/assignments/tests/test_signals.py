from __future__ import annotations

from decimal import Decimal

from django.test import TestCase

from apps.assignments.models import AssignmentPolicy
from apps.assignments.tests.factories import (
    create_assignment,
    create_assignment_question,
    create_submission,
    create_submission_answer,
    create_submission_review,
)


class AssignmentSignalsTestCase(TestCase):
    def test_assignment_creation_creates_policy(self):
        assignment = create_assignment()

        self.assertTrue(AssignmentPolicy.objects.filter(assignment=assignment).exists())

    def test_question_save_recalculates_policy_max_score(self):
        assignment = create_assignment()
        create_assignment_question(assignment=assignment, max_score=Decimal("7"))

        policy = AssignmentPolicy.objects.get(assignment=assignment)

        self.assertGreaterEqual(policy.max_score, Decimal("0"))


class SubmissionSignalsTestCase(TestCase):
    def test_submission_answer_save_recalculates_scores(self):
        submission = create_submission()
        question = create_assignment_question(
            assignment=submission.assignment,
            max_score=Decimal("5"),
        )

        create_submission_answer(
            submission=submission,
            question=question,
            auto_score=Decimal("5"),
            final_score=Decimal("5"),
            is_correct=True,
        )

        submission.refresh_from_db()
        self.assertGreaterEqual(submission.final_score, Decimal("0"))

    def test_review_save_syncs_submission(self):
        review = create_submission_review()

        review.feedback = "Проверено"
        review.save()
        review.submission.refresh_from_db()

        self.assertIsNotNone(review.submission.pk)
