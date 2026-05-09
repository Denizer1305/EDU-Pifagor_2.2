from __future__ import annotations

from decimal import Decimal

from apps.assignments.models import (
    Assignment,
    AssignmentOfficialFormat,
    AssignmentPolicy,
)
from apps.assignments.tests.factories.common import short_uuid
from apps.assignments.tests.factories.users import create_teacher_user


def create_assignment(
    author=None,
    course=None,
    lesson=None,
    subject=None,
    organization=None,
    title: str | None = None,
    **kwargs,
):
    """Создаёт тестовую работу Assignment."""

    author = author or create_teacher_user()

    assignment = Assignment.objects.create(
        author=author,
        course=course,
        lesson=lesson,
        subject=subject,
        organization=organization,
        title=title or f"Работа {short_uuid()}",
        subtitle=kwargs.pop("subtitle", ""),
        description=kwargs.pop("description", ""),
        instructions=kwargs.pop("instructions", ""),
        assignment_kind=kwargs.pop(
            "assignment_kind",
            Assignment.AssignmentKindChoices.HOMEWORK,
        ),
        control_scope=kwargs.pop(
            "control_scope",
            Assignment.ControlScopeChoices.LEARNING_ACTIVITY,
        ),
        status=kwargs.pop("status", Assignment.StatusChoices.DRAFT),
        visibility=kwargs.pop(
            "visibility",
            Assignment.VisibilityChoices.ASSIGNED_ONLY,
        ),
        education_level=kwargs.pop(
            "education_level",
            Assignment.EducationLevelChoices.SCHOOL,
        ),
        is_template=kwargs.pop("is_template", False),
        is_active=kwargs.pop("is_active", True),
        **kwargs,
    )

    AssignmentPolicy.objects.get_or_create(
        assignment=assignment,
        defaults={
            "check_mode": AssignmentPolicy.CheckModeChoices.MANUAL,
            "grading_mode": AssignmentPolicy.GradingModeChoices.RAW_SCORE,
            "max_score": Decimal("0"),
            "passing_score": Decimal("0"),
            "attempts_limit": 1,
            "allow_text_answer": True,
        },
    )
    return assignment


def create_assignment_policy(assignment=None, **kwargs):
    """Создаёт или обновляет политику работы."""

    assignment = assignment or create_assignment()
    policy, _ = AssignmentPolicy.objects.update_or_create(
        assignment=assignment,
        defaults={
            "check_mode": kwargs.pop(
                "check_mode",
                AssignmentPolicy.CheckModeChoices.MANUAL,
            ),
            "grading_mode": kwargs.pop(
                "grading_mode",
                AssignmentPolicy.GradingModeChoices.RAW_SCORE,
            ),
            "max_score": kwargs.pop("max_score", Decimal("100")),
            "passing_score": kwargs.pop("passing_score", Decimal("40")),
            "attempts_limit": kwargs.pop("attempts_limit", 1),
            "allow_text_answer": kwargs.pop("allow_text_answer", True),
            **kwargs,
        },
    )
    return policy


def create_assignment_official_format(assignment=None, **kwargs):
    """Создаёт или обновляет официальный формат работы."""

    assignment = assignment or create_assignment()
    official_format, _ = AssignmentOfficialFormat.objects.update_or_create(
        assignment=assignment,
        defaults={
            "official_family": kwargs.pop("official_family", "vpr"),
            "assessment_year": kwargs.pop("assessment_year", 2024),
            "grade_level": kwargs.pop("grade_level", "8"),
            "exam_subject_name": kwargs.pop("exam_subject_name", "Математика"),
            "source_kind": kwargs.pop("source_kind", "official_demo"),
            "source_title": kwargs.pop("source_title", "ВПР 2024"),
            "source_url": kwargs.pop("source_url", ""),
            "format_version": kwargs.pop("format_version", "1.0"),
            "is_preparation_only": kwargs.pop("is_preparation_only", True),
            "has_answer_key": kwargs.pop("has_answer_key", True),
            "has_scoring_criteria": kwargs.pop("has_scoring_criteria", True),
            "has_official_demo_source": kwargs.pop("has_official_demo_source", True),
            **kwargs,
        },
    )
    return official_format
