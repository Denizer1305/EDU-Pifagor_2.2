from __future__ import annotations

from django.test import TestCase

from apps.assignments.models import AssignmentPublication, AssignmentAudience, Submission
from apps.assignments.services import (
    add_review_comment,
    approve_submission_review,
    archive_assignment,
    archive_assignment_publication,
    assign_publication_to_course_enrollment,
    assign_publication_to_student,
    close_assignment_publication,
    create_assignment,
    create_new_submission_attempt,
    create_grade_record_from_submission,
    duplicate_assignment,
    publish_assignment,
    publish_assignment_publication,
    reorder_assignment_questions,
    reorder_assignment_sections,
    reorder_assignment_variants,
    reorder_rubric_criteria,
    review_submission_answer,
    save_submission_answer,
    start_submission,
    start_submission_review,
    submit_submission,
    submit_submission_review,
    update_assignment,
    update_assignment_publication,
    update_rubric,
)
from apps.assignments.tests.factories import (
    create_assignment,
    create_assignment_policy,
    create_assignment_publication,
    create_assignment_question,
    create_assignment_section,
    create_assignment_variant,
    create_course_enrollment,
    create_rubric,
    create_rubric_criterion,
    create_student_user,
    create_teacher_user,
)


COURSE_ENROLLMENT_AUDIENCE = getattr(
    AssignmentAudience.AudienceTypeChoices,
    "COURSE_ENROLLMENT",
    "course_enrollment",
)


class AssignmentServicesTestCase(TestCase):
    def test_create_assignment_service(self):
        teacher = create_teacher_user()

        assignment = create_assignment(author=teacher, title="Новая работа")

        self.assertIsNotNone(assignment.pk)
        self.assertEqual(assignment.author_id, teacher.id)
        self.assertEqual(assignment.title, "Новая работа")

    def test_update_assignment_service(self):
        assignment = create_assignment(title="Старое название")

        updated = update_assignment(assignment, title="Новое название")

        self.assertEqual(updated.title, "Новое название")

    def test_publish_assignment_service(self):
        assignment = create_assignment()
        create_assignment_question(assignment=assignment)

        published = publish_assignment(assignment)

        self.assertEqual(
            published.status,
            published.StatusChoices.PUBLISHED,
        )

    def test_archive_assignment_service(self):
        assignment = create_assignment()
        create_assignment_question(assignment=assignment)
        assignment = publish_assignment(assignment)

        archived = archive_assignment(assignment)

        self.assertEqual(
            archived.status,
            archived.StatusChoices.ARCHIVED,
        )

    def test_duplicate_assignment_service(self):
        assignment = create_assignment()
        variant = create_assignment_variant(
            assignment=assignment,
            title="Вариант 1",
            variant_number=1,
            order=1,
        )
        section = create_assignment_section(assignment=assignment, variant=variant)
        create_assignment_question(
            assignment=assignment,
            variant=variant,
            section=section,
        )

        duplicated = duplicate_assignment(
            source_assignment=assignment,
            author=assignment.author,
            title="Копия работы",
        )

        self.assertNotEqual(duplicated.id, assignment.id)
        self.assertEqual(duplicated.title, "Копия работы")
        self.assertEqual(duplicated.variants.count(), assignment.variants.count())
        self.assertEqual(duplicated.questions.count(), assignment.questions.count())


class AssignmentStructureServicesTestCase(TestCase):
    def test_create_variant_section_question(self):
        assignment = create_assignment()

        variant = create_assignment_variant(assignment=assignment, title="Вариант 1")
        section = create_assignment_section(assignment=assignment, variant=variant)
        question = create_assignment_question(
            assignment=assignment,
            variant=variant,
            section=section,
        )

        self.assertEqual(variant.assignment_id, assignment.id)
        self.assertEqual(section.assignment_id, assignment.id)
        self.assertEqual(question.assignment_id, assignment.id)

    def test_reorder_variants(self):
        assignment = create_assignment()
        first = create_assignment_variant(
            assignment=assignment,
            title="Вариант 1",
            variant_number=1,
            order=1,
            is_default=True,
        )
        second = create_assignment_variant(
            assignment=assignment,
            title="Вариант 2",
            variant_number=2,
            order=2,
            is_default=False,
        )

        reordered = reorder_assignment_variants(
            assignment=assignment,
            variant_ids_in_order=[second.id, first.id],
        )

        self.assertEqual(reordered[0].id, second.id)

    def test_reorder_sections(self):
        assignment = create_assignment()
        first = create_assignment_section(assignment=assignment, order=1)
        second = create_assignment_section(assignment=assignment, order=2)

        reordered = reorder_assignment_sections(
            assignment=assignment,
            section_ids_in_order=[second.id, first.id],
        )

        self.assertEqual(reordered[0].id, second.id)

    def test_reorder_questions(self):
        assignment = create_assignment()
        first = create_assignment_question(assignment=assignment, order=1)
        second = create_assignment_question(assignment=assignment, order=2)

        reordered = reorder_assignment_questions(
            assignment=assignment,
            question_ids_in_order=[second.id, first.id],
        )

        self.assertEqual(reordered[0].id, second.id)


class PublicationAndAudienceServicesTestCase(TestCase):
    def test_create_and_update_publication(self):
        assignment = create_assignment()
        publication = create_assignment_publication(
            assignment=assignment,
            notes="Черновик",
        )

        updated = update_assignment_publication(
            publication,
            notes="Опубликовано позже",
        )

        self.assertEqual(updated.notes, "Опубликовано позже")

    def test_publish_close_archive_publication(self):
        publication = create_assignment_publication()

        publication = publish_assignment_publication(publication)
        self.assertEqual(
            publication.status,
            AssignmentPublication.StatusChoices.PUBLISHED,
        )

        publication = close_assignment_publication(publication)
        self.assertEqual(
            publication.status,
            AssignmentPublication.StatusChoices.CLOSED,
        )

        publication = archive_assignment_publication(publication)
        self.assertEqual(
            publication.status,
            AssignmentPublication.StatusChoices.ARCHIVED,
        )

    def test_assign_publication_to_student(self):
        student = create_student_user()
        publication = create_assignment_publication()

        audience = assign_publication_to_student(
            publication=publication,
            student=student,
            audience_type=AssignmentAudience.AudienceTypeChoices.STUDENT,
            is_active=True,
        )

        self.assertEqual(audience.student_id, student.id)
        self.assertEqual(audience.publication_id, publication.id)

    def test_assign_publication_to_course_enrollment(self):
        enrollment = create_course_enrollment()
        publication = create_assignment_publication(course=enrollment.course)

        audience = assign_publication_to_course_enrollment(
            publication=publication,
            course_enrollment=enrollment,
            is_active=True,
        )

        self.assertEqual(audience.course_enrollment_id, enrollment.id)


class SubmissionServicesTestCase(TestCase):
    def _create_published_assigned_publication(self, *, assignment, student):
        publication = create_assignment_publication(
            assignment=assignment,
            course=assignment.course,
            published_by=assignment.author,
            status=AssignmentPublication.StatusChoices.PUBLISHED,
        )
        assign_publication_to_student(
            publication=publication,
            student=student,
            audience_type=AssignmentAudience.AudienceTypeChoices.STUDENT,
            is_active=True,
        )
        return publication

    def test_start_submission(self):
        student = create_student_user()
        assignment = create_assignment()
        publication = self._create_published_assigned_publication(
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
        publication = self._create_published_assigned_publication(
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
        publication = self._create_published_assigned_publication(
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

        publication = self._create_published_assigned_publication(
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


class ReviewServicesTestCase(TestCase):
    def _create_published_assigned_publication(self, *, assignment, student, teacher):
        publication = create_assignment_publication(
            assignment=assignment,
            course=assignment.course,
            published_by=teacher,
            status=AssignmentPublication.StatusChoices.PUBLISHED,
        )
        assign_publication_to_student(
            publication=publication,
            student=student,
            audience_type=AssignmentAudience.AudienceTypeChoices.STUDENT,
            is_active=True,
        )
        return publication

    def test_start_review_review_answer_comment_and_submit(self):
        teacher = create_teacher_user()
        student = create_student_user()
        assignment = create_assignment(author=teacher)
        question = create_assignment_question(
            assignment=assignment,
            requires_manual_review=True,
        )
        publication = self._create_published_assigned_publication(
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


class RubricAndGradeServicesTestCase(TestCase):
    def _create_published_assigned_publication(self, *, assignment, student, teacher):
        publication = create_assignment_publication(
            assignment=assignment,
            course=assignment.course,
            published_by=teacher,
            status=AssignmentPublication.StatusChoices.PUBLISHED,
        )
        assign_publication_to_student(
            publication=publication,
            student=student,
            audience_type=AssignmentAudience.AudienceTypeChoices.STUDENT,
            is_active=True,
        )
        return publication

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
        publication = self._create_published_assigned_publication(
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
