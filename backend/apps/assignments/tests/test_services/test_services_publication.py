from __future__ import annotations

from django.test import TestCase

from apps.assignments.models import AssignmentAudience, AssignmentPublication
from apps.assignments.services import (
    archive_assignment_publication,
    assign_publication_to_course_enrollment,
    assign_publication_to_student,
    close_assignment_publication,
    publish_assignment_publication,
    update_assignment_publication,
)
from apps.assignments.tests.factories import (
    create_assignment,
    create_assignment_publication,
    create_course_enrollment,
    create_student_user,
)


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
