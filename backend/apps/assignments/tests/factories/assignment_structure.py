from __future__ import annotations

from decimal import Decimal

from apps.assignments.models import (
    AssignmentAttachment,
    AssignmentQuestion,
    AssignmentSection,
    AssignmentVariant,
)
from apps.assignments.tests.factories.assignment import create_assignment
from apps.assignments.tests.factories.common import create_test_pdf_file, short_uuid


def create_assignment_variant(assignment=None, **kwargs):
    """Создаёт вариант работы."""

    assignment = assignment or create_assignment()

    last_variant = assignment.variants.order_by("-variant_number", "-order").first()
    next_variant_number = 1 if last_variant is None else last_variant.variant_number + 1
    next_order = 1 if last_variant is None else last_variant.order + 1

    return AssignmentVariant.objects.create(
        assignment=assignment,
        title=kwargs.pop("title", f"Вариант {short_uuid()}"),
        code=kwargs.pop("code", f"VAR-{short_uuid()}"),
        description=kwargs.pop("description", ""),
        variant_number=kwargs.pop("variant_number", next_variant_number),
        order=kwargs.pop("order", next_order),
        is_default=kwargs.pop("is_default", last_variant is None),
        max_score=kwargs.pop("max_score", Decimal("0")),
        is_active=kwargs.pop("is_active", True),
        **kwargs,
    )


def create_assignment_section(assignment=None, variant=None, **kwargs):
    """Создаёт секцию работы."""

    assignment = assignment or (variant.assignment if variant else create_assignment())
    section_type_default = AssignmentSection.SectionTypeChoices.choices[0][0]

    return AssignmentSection.objects.create(
        assignment=assignment,
        variant=variant,
        title=kwargs.pop("title", f"Секция {short_uuid()}"),
        description=kwargs.pop("description", ""),
        section_type=kwargs.pop("section_type", section_type_default),
        order=kwargs.pop("order", 1),
        max_score=kwargs.pop("max_score", Decimal("0")),
        is_required=kwargs.pop("is_required", True),
        **kwargs,
    )


def create_assignment_question(assignment=None, variant=None, section=None, **kwargs):
    """Создаёт вопрос работы."""

    assignment = assignment or (
        variant.assignment
        if variant
        else section.assignment
        if section
        else create_assignment()
    )

    return AssignmentQuestion.objects.create(
        assignment=assignment,
        variant=variant,
        section=section,
        question_type=kwargs.pop("question_type", "single_choice"),
        prompt=kwargs.pop("prompt", f"Вопрос {short_uuid()}"),
        description=kwargs.pop("description", ""),
        answer_options_json=kwargs.pop(
            "answer_options_json",
            [{"id": "a", "text": "1"}, {"id": "b", "text": "2"}],
        ),
        correct_answer_json=kwargs.pop("correct_answer_json", {"id": "a"}),
        validation_rules_json=kwargs.pop("validation_rules_json", {}),
        explanation=kwargs.pop("explanation", ""),
        max_score=kwargs.pop("max_score", Decimal("5")),
        order=kwargs.pop("order", 1),
        is_required=kwargs.pop("is_required", True),
        requires_manual_review=kwargs.pop("requires_manual_review", False),
        **kwargs,
    )


def create_assignment_attachment(assignment=None, variant=None, **kwargs):
    """Создаёт вложение к работе."""

    assignment = assignment or (variant.assignment if variant else create_assignment())
    file_obj = kwargs.pop(
        "file",
        create_test_pdf_file(
            name="assignment.pdf",
            content=b"%PDF-1.4 test file",
        ),
    )

    return AssignmentAttachment.objects.create(
        assignment=assignment,
        variant=variant,
        title=kwargs.pop("title", "Файл задания"),
        attachment_type=kwargs.pop("attachment_type", "file"),
        file=file_obj,
        external_url=kwargs.pop("external_url", ""),
        is_visible_to_students=kwargs.pop("is_visible_to_students", True),
        order=kwargs.pop("order", 1),
        **kwargs,
    )
