from __future__ import annotations

import logging
from copy import deepcopy

from django.db import transaction

from apps.assignments.models import (
    Assignment,
    AssignmentOfficialFormat,
)
from apps.assignments.services.assignment_services.crud import create_assignment

from apps.assignments.services.assignment_structure_services import (
        create_assignment_attachment,
        create_assignment_variant,
        create_assignment_section,
        create_assignment_question,
    )

logger = logging.getLogger(__name__)


def _copy_assignment_policy(source_assignment: Assignment, target_assignment: Assignment) -> None:
    """Копирует настройки проверки и оценивания."""

    if not hasattr(source_assignment, "policy"):
        return

    source_policy = source_assignment.policy
    target_policy = target_assignment.policy

    policy_fields = (
        "check_mode",
        "grading_mode",
        "max_score",
        "passing_score",
        "attempts_limit",
        "time_limit_minutes",
        "recommended_time_minutes",
        "shuffle_questions",
        "shuffle_answers",
        "show_results_immediately",
        "show_correct_answers_after_submit",
        "allow_late_submission",
        "late_penalty_percent",
        "auto_submit_on_timeout",
        "requires_manual_review",
        "allow_file_upload",
        "allow_text_answer",
        "allow_photo_upload",
    )

    for field_name in policy_fields:
        setattr(target_policy, field_name, getattr(source_policy, field_name))

    target_policy.full_clean()
    target_policy.save()


def _copy_assignment_official_format(
    source_assignment: Assignment,
    target_assignment: Assignment,
) -> None:
    """Копирует официальный формат работы."""

    if not hasattr(source_assignment, "official_format"):
        return

    source_official = source_assignment.official_format
    official_data = {
        "official_family": source_official.official_family,
        "assessment_year": source_official.assessment_year,
        "grade_level": source_official.grade_level,
        "exam_subject_name": source_official.exam_subject_name,
        "source_kind": source_official.source_kind,
        "source_title": source_official.source_title,
        "source_url": source_official.source_url,
        "format_version": source_official.format_version,
        "is_preparation_only": source_official.is_preparation_only,
        "has_answer_key": source_official.has_answer_key,
        "has_scoring_criteria": source_official.has_scoring_criteria,
        "has_official_demo_source": source_official.has_official_demo_source,
    }

    official_format = AssignmentOfficialFormat(
        assignment=target_assignment,
        **official_data,
    )
    official_format.full_clean()
    official_format.save()


def _copy_assignment_variants(
    source_assignment: Assignment,
    target_assignment: Assignment,
) -> dict[int, object]:
    """Копирует варианты работы и возвращает карту old_id -> new_variant."""

    variant_map: dict[int, object] = {}

    for variant in source_assignment.variants.all():
        new_variant = create_assignment_variant(
            assignment=target_assignment,
            title=variant.title,
            code=variant.code,
            description=variant.description,
            variant_number=variant.variant_number,
            order=variant.order,
            is_default=variant.is_default,
            max_score=variant.max_score,
            is_active=variant.is_active,
        )
        variant_map[variant.id] = new_variant

    return variant_map


def _copy_assignment_sections(
    source_assignment: Assignment,
    target_assignment: Assignment,
    variant_map: dict[int, object],
) -> dict[int, object]:
    """Копирует секции работы и возвращает карту old_id -> new_section."""

    section_map: dict[int, object] = {}

    for section in source_assignment.sections.all():
        new_section = create_assignment_section(
            assignment=target_assignment,
            variant=variant_map.get(section.variant_id),
            title=section.title,
            description=section.description,
            section_type=section.section_type,
            order=section.order,
            max_score=section.max_score,
            is_required=section.is_required,
        )
        section_map[section.id] = new_section

    return section_map


def _copy_assignment_questions(
    source_assignment: Assignment,
    target_assignment: Assignment,
    variant_map: dict[int, object],
    section_map: dict[int, object],
) -> None:
    """Копирует вопросы работы."""

    for question in source_assignment.questions.all():
        create_assignment_question(
            assignment=target_assignment,
            variant=variant_map.get(question.variant_id),
            section=section_map.get(question.section_id),
            question_type=question.question_type,
            prompt=question.prompt,
            description=question.description,
            answer_options_json=deepcopy(question.answer_options_json),
            correct_answer_json=deepcopy(question.correct_answer_json),
            validation_rules_json=deepcopy(question.validation_rules_json),
            explanation=question.explanation,
            max_score=question.max_score,
            order=question.order,
            is_required=question.is_required,
            requires_manual_review=question.requires_manual_review,
        )


def _copy_assignment_attachments(
    source_assignment: Assignment,
    target_assignment: Assignment,
    variant_map: dict[int, object],
) -> None:
    """Копирует вложения работы."""

    for attachment in source_assignment.attachments.all():
        create_assignment_attachment(
            assignment=target_assignment,
            variant=variant_map.get(attachment.variant_id),
            title=attachment.title,
            attachment_type=attachment.attachment_type,
            file=attachment.file,
            external_url=attachment.external_url,
            is_visible_to_students=attachment.is_visible_to_students,
            order=attachment.order,
        )


@transaction.atomic
def duplicate_assignment(
    *,
    source_assignment: Assignment,
    author,
    title: str | None = None,
    subtitle: str | None = None,
    copy_policy: bool = True,
    copy_official_format: bool = True,
    copy_variants: bool = True,
    copy_sections: bool = True,
    copy_questions: bool = True,
    copy_attachments: bool = False,
) -> Assignment:
    """Создаёт копию работы вместе с выбранными частями структуры."""

    logger.info(
        "duplicate_assignment started source_assignment_id=%s",
        source_assignment.id,
    )

    new_assignment = create_assignment(
        author=author,
        title=title or f"{source_assignment.title} (копия)",
        subtitle=subtitle if subtitle is not None else source_assignment.subtitle,
        description=source_assignment.description,
        instructions=source_assignment.instructions,
        course=source_assignment.course,
        lesson=source_assignment.lesson,
        subject=source_assignment.subject,
        organization=source_assignment.organization,
        assignment_kind=source_assignment.assignment_kind,
        control_scope=source_assignment.control_scope,
        status=Assignment.StatusChoices.DRAFT,
        visibility=source_assignment.visibility,
        education_level=source_assignment.education_level,
        is_template=source_assignment.is_template,
        is_active=source_assignment.is_active,
        policy_data=None,
        official_format_data=None,
    )

    if copy_policy:
        _copy_assignment_policy(source_assignment, new_assignment)

    if copy_official_format:
        _copy_assignment_official_format(source_assignment, new_assignment)

    variant_map: dict[int, object] = {}
    section_map: dict[int, object] = {}

    if copy_variants:
        variant_map = _copy_assignment_variants(source_assignment, new_assignment)

    if copy_sections:
        section_map = _copy_assignment_sections(
            source_assignment,
            new_assignment,
            variant_map,
        )

    if copy_questions:
        _copy_assignment_questions(
            source_assignment,
            new_assignment,
            variant_map,
            section_map,
        )

    if copy_attachments:
        _copy_assignment_attachments(
            source_assignment,
            new_assignment,
            variant_map,
        )

    logger.info(
        "duplicate_assignment completed new_assignment_id=%s",
        new_assignment.id,
    )
    return new_assignment
