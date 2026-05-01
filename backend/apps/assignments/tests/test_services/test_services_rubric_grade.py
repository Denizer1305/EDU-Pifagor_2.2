from __future__ import annotations

from django.test import TestCase

from apps.assignments.services import (
    create_grade_record_from_submission,
    reorder_rubric_criteria,
    save_submission_answer,
    start_submission,
    submit_submission,
    update_rubric,
)
from apps.assignments.tests.factories import (
    create_assignment,
    create_assignment_question,
    create_rubric,
    create_rubric_criterion,
    create_student_user,
    create_teacher_user,
)
from apps.assignments.tests.test_services.services_common import (
    create_published_assigned_publication,
)


class RubricAndGradeServicesTestCase(TestCase):
    def test_create_update_rubric_and_criterion(self):
        teacher = create_teacher_user()
        rubric = create_rubric(author=teacher, title="Рубрика 1")
        criterion1 = create_rubric_criterion(
            rubric=rubric,
            title="Критерий 1",
            order=1,
        )
        criterion2 = create_rubric_criterion(
            rubric=rubric,
            title="Критерий 2",
            order=2,
        )

        rubric = update_rubric(rubric, title="Рубрика 2")
        reordered = reorder_rubric_criteria(
            rubric=rubric,
            criterion_ids_in_order=[criterion2.id, criterion1.id],
        )

        self.assertEqual(rubric.title, "Рубрика 2")
        self.assertEqual(reordered[0].id, criterion2.id)

    def test_create_grade_record_from_submission(self):
        teacher = create_teacher_user()
        student = create_student_user()
        assignment = create_assignment(author=teacher)
        question = create_assignment_question(assignment=assignment)
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

        save_submission_answer(
            submission=submission,
            question=question,
            answer_text="Ответ",
            answer_json=None,
            selected_options_json=None,
            numeric_answer=None,
        )
        submission = submit_submission(submission)

        grade = create_grade_record_from_submission(
            submission=submission,
            graded_by=teacher,
            is_final=True,
        )

        self.assertEqual(grade.assignment_id, assignment.id)
        self.assertEqual(grade.student_id, student.id)
