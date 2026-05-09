from __future__ import annotations

from django.test import TestCase

from apps.assignments.services import (
    archive_assignment,
    duplicate_assignment,
    publish_assignment,
    update_assignment,
)
from apps.assignments.services import (
    create_assignment as create_assignment_service,
)
from apps.assignments.tests.factories import (
    create_assignment as create_assignment_factory,
)
from apps.assignments.tests.factories import (
    create_assignment_question,
    create_assignment_section,
    create_assignment_variant,
    create_teacher_user,
)


class AssignmentServicesTestCase(TestCase):
    def test_create_assignment_service(self):
        teacher = create_teacher_user()

        assignment = create_assignment_service(
            author=teacher,
            title="Новая работа",
        )

        self.assertIsNotNone(assignment.pk)
        self.assertEqual(assignment.author_id, teacher.id)
        self.assertEqual(assignment.title, "Новая работа")

    def test_update_assignment_service(self):
        assignment = create_assignment_factory(title="Старое название")

        updated = update_assignment(assignment, title="Новое название")

        self.assertEqual(updated.title, "Новое название")

    def test_publish_assignment_service(self):
        assignment = create_assignment_factory()
        create_assignment_question(assignment=assignment)

        published = publish_assignment(assignment)

        self.assertEqual(
            published.status,
            published.StatusChoices.PUBLISHED,
        )

    def test_archive_assignment_service(self):
        assignment = create_assignment_factory()
        create_assignment_question(assignment=assignment)
        assignment = publish_assignment(assignment)

        archived = archive_assignment(assignment)

        self.assertEqual(
            archived.status,
            archived.StatusChoices.ARCHIVED,
        )

    def test_duplicate_assignment_service(self):
        assignment = create_assignment_factory()
        variant = create_assignment_variant(
            assignment=assignment,
            title="Вариант 1",
            variant_number=1,
            order=1,
        )
        section = create_assignment_section(
            assignment=assignment,
            variant=variant,
        )
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
