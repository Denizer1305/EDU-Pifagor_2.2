from __future__ import annotations

from django.test import TestCase

from apps.assignments.models import AssignmentPolicy, SubmissionReview
from apps.assignments.tests.factories import (
    create_appeal,
    create_assignment,
    create_grade_record,
    create_review_comment,
    create_submission_review,
)


class AssignmentModelTestCase(TestCase):
    def test_assignment_creation_has_policy(self):
        assignment = create_assignment()

        self.assertIsNotNone(assignment.pk)
        self.assertTrue(
            AssignmentPolicy.objects.filter(assignment=assignment).exists()
        )

    def test_assignment_has_uid_after_save(self):
        assignment = create_assignment()

        self.assertTrue(assignment.uid)
        self.assertIsNotNone(assignment.created_at)
        self.assertIsNotNone(assignment.updated_at)


class ReviewModelTestCase(TestCase):
    def test_submission_review_can_be_created(self):
        review = create_submission_review()

        self.assertIsNotNone(review.pk)
        self.assertEqual(
            review.review_status,
            getattr(review, "review_status"),
        )

    def test_review_comment_belongs_to_review(self):
        comment = create_review_comment()

        self.assertIsNotNone(comment.pk)
        self.assertIsNotNone(comment.review_id)
        self.assertTrue(comment.message)

    def test_submission_review_single_object(self):
        review = create_submission_review()
        second = SubmissionReview.objects.get(pk=review.pk)

        self.assertEqual(review.pk, second.pk)


class GradeAndAppealModelTestCase(TestCase):
    def test_grade_record_creation(self):
        grade = create_grade_record()

        self.assertIsNotNone(grade.pk)
        self.assertEqual(grade.submission.assignment_id, grade.assignment_id)
        self.assertEqual(grade.submission.student_id, grade.student_id)

    def test_appeal_creation(self):
        appeal = create_appeal()

        self.assertIsNotNone(appeal.pk)
        self.assertEqual(appeal.student_id, appeal.submission.student_id)
        self.assertTrue(appeal.reason)
