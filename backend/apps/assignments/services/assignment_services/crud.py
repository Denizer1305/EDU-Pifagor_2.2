from __future__ import annotations

import logging

from django.db import transaction

from apps.assignments.models import (
    Assignment,
    AssignmentOfficialFormat,
    AssignmentPolicy,
)
from apps.assignments.services.assignment_services.common import (
    get_or_create_assignment_policy,
)

logger = logging.getLogger(__name__)


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
    """Создаёт образовательную работу и связанные настройки."""

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
    """Обновляет работу и связанные вложенные настройки."""

    logger.info("update_assignment started assignment_id=%s", assignment.id)

    policy_data = fields.pop("policy_data", None)
    official_format_data = fields.pop("official_format_data", None)

    for field_name, value in fields.items():
        setattr(assignment, field_name, value)

    assignment.full_clean()
    assignment.save()

    if policy_data is not None:
        policy = get_or_create_assignment_policy(assignment)
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
