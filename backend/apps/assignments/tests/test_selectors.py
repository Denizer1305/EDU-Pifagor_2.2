from __future__ import annotations

from django.test import TestCase

from apps.assignments.selectors import (
    get_assignment_audiences_queryset,
    get_assignment_by_id,
    get_assignment_publication_by_id,
    get_assignment_publications_queryset,
    get_assignments_queryset,
    get_available_publications_for_student_queryset,
    get_rubrics_queryset,
    get_student_submissions_queryset,
    get_submission_by_id,
    get_submission_reviews_queryset,
    get_submissions_queryset,
)
from apps.assignments.selectors.analytics_selectors import (
    get_assignment_statistics,
    get_course_assignment_dashboard,
    get_publication_statistics,
    get_student_assignment_progress,
)
from apps.assignments.tests.factories import (
    create_assignment,
    create_assignment_audience,
    create_assignment_publication,
    create_grade_record,
    create_review_comment,
    create_rubric,
    create_submission,
    create_student_user,
    create_teacher_user,
)
from apps.course.tests.factories import create_course_enrollment, create_course
from apps.assignments.models import AssignmentPublication


class AssignmentSelectorsTestCase(TestCase):
    def test_get_assignments_queryset_filters_by_author(self):
        teacher = create_teacher_user()
        target = create_assignment(author=teacher, title="Алгебра ЕГЭ")
        create_assignment(title="История")

        queryset = get_assignments_queryset(author_id=teacher.id)

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, target.id)

    def test_get_assignments_queryset_filters_by_search(self):
        target = create_assignment(title="Подготовка к ВПР 8 класс")
        create_assignment(title="Подготовка к олимпиаде")

        queryset = get_assignments_queryset(search="ВПР")

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, target.id)

    def test_get_assignment_by_id_returns_detail_queryset(self):
        assignment = create_assignment()

        found = get_assignment_by_id(assignment_id=assignment.id)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, assignment.id)


class PublicationSelectorsTestCase(TestCase):
    def test_get_assignment_publications_queryset(self):
        publication = create_assignment_publication()
        create_assignment_publication()

        queryset = get_assignment_publications_queryset(
            assignment_id=publication.assignment_id
        )

        self.assertGreaterEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().assignment_id, publication.assignment_id)

    def test_get_assignment_publication_by_id(self):
        publication = create_assignment_publication()

        found = get_assignment_publication_by_id(publication_id=publication.id)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, publication.id)

    def test_get_available_publications_for_student_queryset(self):
        student = create_student_user()
        course_enrollment = create_course_enrollment(student=student)
        publication = create_assignment_publication(
            course=course_enrollment.course,
            assignment=create_assignment(course=course_enrollment.course),
            status=AssignmentPublication.StatusChoices.PUBLISHED,
        )
        create_assignment_audience(
            publication=publication,
            audience_type="course_enrollment",
            course_enrollment=course_enrollment,
        )

        queryset = get_available_publications_for_student_queryset(student=student)

        self.assertIn(publication.id, list(queryset.values_list("id", flat=True)))


class AudienceSelectorsTestCase(TestCase):
    def test_get_assignment_audiences_queryset(self):
        student = create_student_user()
        audience = create_assignment_audience(student=student)

        queryset = get_assignment_audiences_queryset(student_id=student.id)

        self.assertGreaterEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, audience.id)


class SubmissionSelectorsTestCase(TestCase):
    def test_get_submissions_queryset(self):
        student = create_student_user()
        submission = create_submission(student=student)
        create_submission()

        queryset = get_submissions_queryset(student_id=student.id)

        self.assertGreaterEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().student_id, student.id)

    def test_get_student_submissions_queryset(self):
        student = create_student_user()
        submission = create_submission(student=student)
        create_submission()

        queryset = get_student_submissions_queryset(student=student)

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, submission.id)

    def test_get_submission_by_id(self):
        submission = create_submission()

        found = get_submission_by_id(submission_id=submission.id)

        self.assertIsNotNone(found)
        self.assertEqual(found.id, submission.id)


class ReviewAndRubricSelectorsTestCase(TestCase):
    def test_get_submission_reviews_queryset(self):
        comment = create_review_comment()

        queryset = get_submission_reviews_queryset(
            submission_id=comment.review.submission_id
        )

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, comment.review_id)

    def test_get_rubrics_queryset(self):
        teacher = create_teacher_user()
        rubric = create_rubric(author=teacher)
        create_rubric()

        queryset = get_rubrics_queryset(author_id=teacher.id)

        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().id, rubric.id)


class AnalyticsSelectorsTestCase(TestCase):
    def test_get_assignment_statistics(self):
        assignment = create_assignment()
        publication = create_assignment_publication(assignment=assignment)
        create_submission(
            assignment=assignment,
            publication=publication,
            final_score=10,
            percentage=80,
            passed=True,
            status="submitted",
        )

        payload = get_assignment_statistics(assignment=assignment)

        self.assertEqual(payload["assignment_id"], assignment.id)
        self.assertEqual(payload["submissions_count"], 1)

    def test_get_publication_statistics(self):
        publication = create_assignment_publication()
        create_submission(
            publication=publication,
            assignment=publication.assignment,
            final_score=7,
            percentage=70,
            passed=True,
            status="submitted",
        )

        payload = get_publication_statistics(publication=publication)

        self.assertEqual(payload["publication_id"], publication.id)
        self.assertEqual(payload["submissions_count"], 1)

    def test_get_student_assignment_progress(self):
        student = create_student_user()
        assignment = create_assignment()
        publication = create_assignment_publication(assignment=assignment)
        create_submission(
            student=student,
            assignment=assignment,
            publication=publication,
            status="reviewed",
            final_score=8,
            percentage=80,
            passed=True,
        )

        payload = get_student_assignment_progress(student=student, assignment=assignment)

        self.assertEqual(payload["student_id"], student.id)
        self.assertEqual(payload["assignment_id"], assignment.id)
        self.assertEqual(payload["attempts_count"], 1)

    def test_get_course_assignment_dashboard(self):
        teacher = create_teacher_user()
        course = create_course(author=teacher)
        assignment = create_assignment(author=teacher, course=course)
        publication = create_assignment_publication(
            assignment=assignment,
            course=course,
            status=AssignmentPublication.StatusChoices.PUBLISHED,
        )
        create_submission(
            publication=publication,
            assignment=assignment,
            status="submitted",
            final_score=9,
            percentage=90,
            passed=True,
        )

        payload = get_course_assignment_dashboard(course=course)

        self.assertEqual(payload["course_id"], publication.course.id)
        self.assertEqual(payload["submissions_count"], 1)
