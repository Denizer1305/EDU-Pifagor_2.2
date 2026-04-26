from __future__ import annotations

import logging
from copy import deepcopy

from django.db import transaction

from apps.assignments.models import (
    Assignment,
    AssignmentOfficialFormat,
    AssignmentPolicy,
)

logger = logging.getLogger(__name__)


def _get_or_create_assignment_policy(assignment: Assignment) -> AssignmentPolicy:
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
    return policy


@transaction.atomic
def create_assignment(
    *,
    author,
    title: str,
    subtitle: str = "",
    description: str = "",
    instructions: str = "",
    course=None,
    lesson=None,
    subject=None,
    organization=None,
    assignment_kind: str = Assignment.AssignmentKindChoices.HOMEWORK,
    control_scope: str = Assignment.ControlScopeChoices.LEARNING_ACTIVITY,
    status: str = Assignment.StatusChoices.DRAFT,
    visibility: str = Assignment.VisibilityChoices.ASSIGNED_ONLY,
    education_level: str = Assignment.EducationLevelChoices.SCHOOL,
    is_template: bool = False,
    is_active: bool = True,
    policy_data: dict | None = None,
    official_format_data: dict | None = None,
) -> Assignment:
    logger.info(
        "create_assignment started author_id=%s title=%s",
        getattr(author, "id", None),
        title,
    )

    assignment = Assignment(
        title=title,
        subtitle=subtitle,
        description=description,
        instructions=instructions,
        course=course,
        lesson=lesson,
        subject=subject,
        organization=organization,
        author=author,
        assignment_kind=assignment_kind,
        control_scope=control_scope,
        status=status,
        visibility=visibility,
        education_level=education_level,
        is_template=is_template,
        is_active=is_active,
    )
    assignment.full_clean()
    assignment.save()

    policy_payload = {
        "check_mode": AssignmentPolicy.CheckModeChoices.MANUAL,
        "grading_mode": AssignmentPolicy.GradingModeChoices.RAW_SCORE,
        "max_score": 0,
        "passing_score": 0,
        "attempts_limit": 1,
        "allow_text_answer": True,
    }
    if policy_data:
        policy_payload.update(policy_data)

    policy = AssignmentPolicy(assignment=assignment, **policy_payload)
    policy.full_clean()
    policy.save()

    if official_format_data:
        official_format = AssignmentOfficialFormat(
            assignment=assignment,
            **official_format_data,
        )
        official_format.full_clean()
        official_format.save()

    logger.info("create_assignment completed id=%s", assignment.id)
    return assignment


@transaction.atomic
def update_assignment(assignment: Assignment, **fields) -> Assignment:
    logger.info("update_assignment started assignment_id=%s", assignment.id)

    policy_data = fields.pop("policy_data", None)
    official_format_data = fields.pop("official_format_data", None)

    for field_name, value in fields.items():
        setattr(assignment, field_name, value)

    assignment.full_clean()
    assignment.save()

    if policy_data is not None:
        policy = _get_or_create_assignment_policy(assignment)
        for field_name, value in policy_data.items():
            setattr(policy, field_name, value)
        policy.full_clean()
        policy.save()

    if official_format_data is not None:
        official_format, _ = AssignmentOfficialFormat.objects.get_or_create(
            assignment=assignment,
            defaults={
                "official_family": AssignmentOfficialFormat.OfficialFamilyChoices.NONE,
            },
        )
        for field_name, value in official_format_data.items():
            setattr(official_format, field_name, value)
        official_format.full_clean()
        official_format.save()

    logger.info("update_assignment completed assignment_id=%s", assignment.id)
    return assignment


@transaction.atomic
def publish_assignment(assignment: Assignment) -> Assignment:
    logger.info("publish_assignment started assignment_id=%s", assignment.id)

    assignment.status = Assignment.StatusChoices.PUBLISHED
    assignment.is_active = True
    assignment.full_clean()
    assignment.save()

    logger.info("publish_assignment completed assignment_id=%s", assignment.id)
    return assignment


@transaction.atomic
def archive_assignment(assignment: Assignment) -> Assignment:
    logger.info("archive_assignment started assignment_id=%s", assignment.id)

    assignment.status = Assignment.StatusChoices.ARCHIVED
    assignment.is_active = False
    assignment.full_clean()
    assignment.save()

    logger.info("archive_assignment completed assignment_id=%s", assignment.id)
    return assignment


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
    from apps.assignments.services.assignment_structure_services import (
        create_assignment_attachment,
        create_assignment_question,
        create_assignment_section,
        create_assignment_variant,
    )

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

    if copy_policy and hasattr(source_assignment, "policy"):
        source_policy = source_assignment.policy
        target_policy = new_assignment.policy
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

    if copy_official_format and hasattr(source_assignment, "official_format"):
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
            assignment=new_assignment,
            **official_data,
        )
        official_format.full_clean()
        official_format.save()

    variant_map: dict[int, object] = {}
    section_map: dict[int, object] = {}

    if copy_variants:
        for variant in source_assignment.variants.all():
            new_variant = create_assignment_variant(
                assignment=new_assignment,
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

    if copy_sections:
        for section in source_assignment.sections.all():
            new_section = create_assignment_section(
                assignment=new_assignment,
                variant=variant_map.get(section.variant_id),
                title=section.title,
                description=section.description,
                section_type=section.section_type,
                order=section.order,
                max_score=section.max_score,
                is_required=section.is_required,
            )
            section_map[section.id] = new_section

    if copy_questions:
        for question in source_assignment.questions.all():
            create_assignment_question(
                assignment=new_assignment,
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

    if copy_attachments:
        for attachment in source_assignment.attachments.all():
            create_assignment_attachment(
                assignment=new_assignment,
                variant=variant_map.get(attachment.variant_id),
                title=attachment.title,
                attachment_type=attachment.attachment_type,
                file=attachment.file,
                external_url=attachment.external_url,
                is_visible_to_students=attachment.is_visible_to_students,
                order=attachment.order,
            )

    logger.info(
        "duplicate_assignment completed new_assignment_id=%s",
        new_assignment.id,
    )
    return new_assignment
