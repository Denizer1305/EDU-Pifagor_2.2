from __future__ import annotations

import logging
from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.core.exceptions import ValidationError

from apps.assignments.models import (
    Assignment,
    AssignmentAttachment,
    AssignmentPolicy,
    AssignmentQuestion,
    AssignmentSection,
    AssignmentVariant,
)

logger = logging.getLogger(__name__)


def _sum_decimal(queryset, field_name: str) -> Decimal:
    value = queryset.aggregate(total=Sum(field_name)).get("total")
    return value or Decimal("0")


@transaction.atomic
def create_assignment_variant(
    *,
    assignment: Assignment,
    title: str,
    code: str = "",
    description: str = "",
    variant_number: int,
    order: int = 1,
    is_default: bool = False,
    max_score=0,
    is_active: bool = True,
) -> AssignmentVariant:
    variant = AssignmentVariant(
        assignment=assignment,
        title=title,
        code=code,
        description=description,
        variant_number=variant_number,
        order=order,
        is_default=is_default,
        max_score=max_score,
        is_active=is_active,
    )
    variant.full_clean()
    variant.save()

    recalculate_assignment_variant_max_score(variant)
    recalculate_assignment_policy_max_score(assignment)
    return variant


@transaction.atomic
def update_assignment_variant(variant: AssignmentVariant, **fields) -> AssignmentVariant:
    for field_name, value in fields.items():
        setattr(variant, field_name, value)

    variant.full_clean()
    variant.save()

    recalculate_assignment_variant_max_score(variant)
    recalculate_assignment_policy_max_score(variant.assignment)
    return variant


@transaction.atomic
def delete_assignment_variant(variant: AssignmentVariant) -> None:
    assignment = variant.assignment
    variant.delete()
    recalculate_assignment_policy_max_score(assignment)


@transaction.atomic
def reorder_assignment_variants(*, assignment, variant_ids_in_order: list[int]):
    variants = list(
        AssignmentVariant.objects.filter(
            assignment=assignment,
            id__in=variant_ids_in_order,
        )
    )
    variants_map = {variant.id: variant for variant in variants}

    if len(variants_map) != len(variant_ids_in_order):
        raise ValidationError("Не все варианты найдены.")

    temp_base = 1000

    for index, variant_id in enumerate(variant_ids_in_order, start=1):
        variant = variants_map[variant_id]
        variant.order = temp_base + index
        variant.variant_number = temp_base + index
        variant.is_default = index == 1

    AssignmentVariant.objects.bulk_update(
        variants,
        ["order", "variant_number", "is_default", "updated_at"],
    )

    for index, variant_id in enumerate(variant_ids_in_order, start=1):
        variant = variants_map[variant_id]
        variant.order = index
        variant.variant_number = index

    AssignmentVariant.objects.bulk_update(
        variants,
        ["order", "variant_number", "updated_at"],
    )

    return list(
        AssignmentVariant.objects.filter(assignment=assignment).order_by("order", "id")
    )


@transaction.atomic
def create_assignment_section(
    *,
    assignment: Assignment,
    title: str,
    description: str = "",
    section_type: str = AssignmentSection.SectionTypeChoices.COMMON,
    order: int = 1,
    max_score=0,
    is_required: bool = True,
    variant=None,
) -> AssignmentSection:
    section = AssignmentSection(
        assignment=assignment,
        variant=variant,
        title=title,
        description=description,
        section_type=section_type,
        order=order,
        max_score=max_score,
        is_required=is_required,
    )
    section.full_clean()
    section.save()

    recalculate_assignment_variant_max_score(variant) if variant else None
    recalculate_assignment_policy_max_score(assignment)
    return section


@transaction.atomic
def update_assignment_section(section: AssignmentSection, **fields) -> AssignmentSection:
    old_variant = section.variant
    for field_name, value in fields.items():
        setattr(section, field_name, value)

    section.full_clean()
    section.save()

    if old_variant:
        recalculate_assignment_variant_max_score(old_variant)
    if section.variant:
        recalculate_assignment_variant_max_score(section.variant)
    recalculate_assignment_policy_max_score(section.assignment)
    return section


@transaction.atomic
def delete_assignment_section(section: AssignmentSection) -> None:
    assignment = section.assignment
    variant = section.variant
    section.delete()

    if variant:
        recalculate_assignment_variant_max_score(variant)
    recalculate_assignment_policy_max_score(assignment)


@transaction.atomic
def reorder_assignment_sections(
    *,
    assignment: Assignment,
    section_ids_in_order: list[int],
) -> list[AssignmentSection]:
    sections = list(assignment.sections.filter(id__in=section_ids_in_order))
    sections_map = {section.id: section for section in sections}

    ordered_sections: list[AssignmentSection] = []
    for index, section_id in enumerate(section_ids_in_order, start=1):
        section = sections_map.get(section_id)
        if section is None:
            continue
        section.order = index
        section.full_clean()
        section.save(update_fields=("order", "updated_at"))
        ordered_sections.append(section)

    return ordered_sections


@transaction.atomic
def create_assignment_question(
    *,
    assignment: Assignment,
    prompt: str,
    question_type: str = AssignmentQuestion.QuestionTypeChoices.SHORT_TEXT,
    description: str = "",
    answer_options_json=None,
    correct_answer_json=None,
    validation_rules_json=None,
    explanation: str = "",
    max_score=0,
    order: int = 1,
    is_required: bool = True,
    requires_manual_review: bool = False,
    variant=None,
    section=None,
) -> AssignmentQuestion:
    question = AssignmentQuestion(
        assignment=assignment,
        variant=variant,
        section=section,
        question_type=question_type,
        prompt=prompt,
        description=description,
        answer_options_json=answer_options_json or [],
        correct_answer_json=correct_answer_json or {},
        validation_rules_json=validation_rules_json or {},
        explanation=explanation,
        max_score=max_score,
        order=order,
        is_required=is_required,
        requires_manual_review=requires_manual_review,
    )
    question.full_clean()
    question.save()

    if variant:
        recalculate_assignment_variant_max_score(variant)
    recalculate_assignment_policy_max_score(assignment)
    return question


@transaction.atomic
def update_assignment_question(question: AssignmentQuestion, **fields) -> AssignmentQuestion:
    old_variant = question.variant
    old_assignment = question.assignment

    for field_name, value in fields.items():
        setattr(question, field_name, value)

    question.full_clean()
    question.save()

    if old_variant:
        recalculate_assignment_variant_max_score(old_variant)
    if question.variant:
        recalculate_assignment_variant_max_score(question.variant)

    recalculate_assignment_policy_max_score(old_assignment)
    if question.assignment_id != old_assignment.id:
        recalculate_assignment_policy_max_score(question.assignment)

    return question


@transaction.atomic
def delete_assignment_question(question: AssignmentQuestion) -> None:
    assignment = question.assignment
    variant = question.variant
    question.delete()

    if variant:
        recalculate_assignment_variant_max_score(variant)
    recalculate_assignment_policy_max_score(assignment)


@transaction.atomic
def reorder_assignment_questions(
    *,
    assignment: Assignment,
    question_ids_in_order: list[int],
) -> list[AssignmentQuestion]:
    questions = list(assignment.questions.filter(id__in=question_ids_in_order))
    questions_map = {question.id: question for question in questions}

    ordered_questions: list[AssignmentQuestion] = []
    for index, question_id in enumerate(question_ids_in_order, start=1):
        question = questions_map.get(question_id)
        if question is None:
            continue
        question.order = index
        question.full_clean()
        question.save(update_fields=("order", "updated_at"))
        ordered_questions.append(question)

    recalculate_assignment_policy_max_score(assignment)
    return ordered_questions


@transaction.atomic
def create_assignment_attachment(
    *,
    assignment: Assignment,
    title: str,
    attachment_type: str = AssignmentAttachment.AttachmentTypeChoices.REFERENCE,
    file=None,
    external_url: str = "",
    is_visible_to_students: bool = True,
    order: int = 1,
    variant=None,
) -> AssignmentAttachment:
    attachment = AssignmentAttachment(
        assignment=assignment,
        variant=variant,
        title=title,
        attachment_type=attachment_type,
        file=file,
        external_url=external_url,
        is_visible_to_students=is_visible_to_students,
        order=order,
    )
    attachment.full_clean()
    attachment.save()
    return attachment


@transaction.atomic
def update_assignment_attachment(
    attachment: AssignmentAttachment,
    **fields,
) -> AssignmentAttachment:
    for field_name, value in fields.items():
        setattr(attachment, field_name, value)

    attachment.full_clean()
    attachment.save()
    return attachment


@transaction.atomic
def delete_assignment_attachment(attachment: AssignmentAttachment) -> None:
    attachment.delete()


@transaction.atomic
def recalculate_assignment_variant_max_score(variant: AssignmentVariant | None) -> AssignmentVariant | None:
    if variant is None:
        return None

    variant.max_score = _sum_decimal(
        variant.questions.all(),
        "max_score",
    )
    variant.full_clean()
    variant.save(update_fields=("max_score", "updated_at"))
    return variant


@transaction.atomic
def recalculate_assignment_policy_max_score(assignment: Assignment) -> AssignmentPolicy:
    policy, _ = AssignmentPolicy.objects.get_or_create(
        assignment=assignment,
        defaults={
            "check_mode": AssignmentPolicy.CheckModeChoices.MANUAL,
            "grading_mode": AssignmentPolicy.GradingModeChoices.RAW_SCORE,
            "max_score": 0,
            "passing_score": 0,
            "attempts_limit": 1,
            "allow_text_answer": True,
        },
    )

    if assignment.variants.exists():
        default_variant = (
            assignment.variants.filter(is_default=True).order_by("order", "id").first()
            or assignment.variants.order_by("order", "id").first()
        )
        max_score = default_variant.max_score if default_variant else Decimal("0")
    else:
        max_score = _sum_decimal(assignment.questions.all(), "max_score")

    policy.max_score = max_score
    if policy.passing_score > policy.max_score:
        policy.passing_score = policy.max_score
    policy.full_clean()
    policy.save(update_fields=("max_score", "passing_score", "updated_at"))
    return policy
