from __future__ import annotations

from django.test import TestCase

from apps.assignments.services import (
    add_review_comment,
    approve_submission_review,
    review_submission_answer,
    save_submission_answer,
    start_submission,
    start_submission_review,
    submit_submission,
    submit_submission_review,
)
from apps.assignments.tests.factories import (
    create_assignment,
    create_assignment_question,
    create_student_user,
    create_teacher_user,
)
from apps.assignments.tests.test_services.services_common import (
    create_published_assigned_publication,
)


class ReviewServicesTestCase(TestCase):
    def test_start_review_review_answer_comment_and_submit(self):
        teacher = create_teacher_user()
        student = create_student_user()
        assignment = create_assignment(author=teacher)
        question = create_assignment_question(
            assignment=assignment,
            requires_manual_review=True,
        )
        publication = create_published_assigned_publication(
            assignment=assignment,
            student=student,
            teacher=teacher,
        )

        submission = start_submission(
            publication=publication,
            student=student,
            variant=None,
        )

        answer = save_submission_answer(
            submission=submission,
            question=question,
            answer_text="Ответ ученика",
            answer_json=None,
            selected_options_json=None,
            numeric_answer=None,
        )
        submission = submit_submission(submission)

        review = start_submission_review(
            submission=submission,
            reviewer=teacher,
        )

        reviewed_answer = review_submission_answer(
            submission_answer=answer,
            reviewer=teacher,
            manual_score=3,
            is_correct=True,
            review_status="reviewed",
        )

        comment = add_review_comment(
            review=review,
            message="Хорошо",
            created_by=teacher,
            comment_type="general",
            question=question,
            submission_answer=reviewed_answer,
            score_delta=None,
        )

        review = submit_submission_review(
            review=review,
            reviewer=teacher,
            feedback="Итоговая проверка",
            private_note="Для журнала",
            score=3,
            passed=True,
        )

        review = approve_submission_review(
            review=review,
            reviewer=teacher,
            score=3,
            feedback="Принято",
        )

        self.assertIsNotNone(comment.pk)
        self.assertEqual(review.submission_id, submission.id)
        self.assertTrue(review.passed)
