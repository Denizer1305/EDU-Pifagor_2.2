from __future__ import annotations

from django.test import TestCase

from apps.assignments.services import (
    create_assignment_question as create_assignment_question_service,
    create_assignment_section as create_assignment_section_service,
    create_assignment_variant as create_assignment_variant_service,
    reorder_assignment_questions,
    reorder_assignment_sections,
    reorder_assignment_variants,
)
from apps.assignments.tests.factories import (
    create_assignment,
    create_assignment_question,
    create_assignment_section,
    create_assignment_variant,
)


class AssignmentStructureServicesTestCase(TestCase):
    def test_create_variant_section_question(self):
        assignment = create_assignment()

        variant = create_assignment_variant_service(
            assignment=assignment,
            title="Вариант 1",
            variant_number=1,
            order=1,
        )
        section = create_assignment_section_service(
            assignment=assignment,
            variant=variant,
            title="Секция 1",
        )
        question = create_assignment_question_service(
            assignment=assignment,
            variant=variant,
            section=section,
            prompt="Вопрос 1",
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
