from __future__ import annotations

from decimal import Decimal

from django.utils import timezone

from apps.assignments.models import (
    Appeal,
    GradeRecord,
    Rubric,
    RubricCriterion,
)
from apps.assignments.tests.factories.common import short_uuid
from apps.assignments.tests.factories.submission import create_submission
from apps.assignments.tests.factories.users import create_teacher_user


def create_rubric(author=None, organization=None, **kwargs):
    """Создаёт рубрику оценивания."""

    author = author or create_teacher_user()

    return Rubric.objects.create(
        title=kwargs.pop("title", f"Рубрика {short_uuid()}"),
        description=kwargs.pop("description", ""),
        assignment_kind=kwargs.pop("assignment_kind", "homework"),
        organization=organization,
        author=author,
        is_template=kwargs.pop("is_template", True),
        is_active=kwargs.pop("is_active", True),
        **kwargs,
    )


def create_rubric_criterion(rubric=None, **kwargs):
    """Создаёт критерий рубрики."""

    rubric = rubric or create_rubric()

    return RubricCriterion.objects.create(
        rubric=rubric,
        title=kwargs.pop("title", f"Критерий {short_uuid()}"),
        description=kwargs.pop("description", ""),
        max_score=kwargs.pop("max_score", Decimal("5")),
        order=kwargs.pop("order", 1),
        criterion_type=kwargs.pop("criterion_type", "score"),
        **kwargs,
    )


def create_grade_record(submission=None, graded_by=None, **kwargs):
    """Создаёт итоговую оценку по сдаче."""

    submission = submission or create_submission()
    graded_by = graded_by or submission.assignment.author

    return GradeRecord.objects.create(
        student=submission.student,
        assignment=submission.assignment,
        publication=submission.publication,
        submission=submission,
        grade_value=kwargs.pop("grade_value", "5"),
        grade_numeric=kwargs.pop("grade_numeric", Decimal("5")),
        grading_mode=kwargs.pop("grading_mode", "five_point"),
        is_final=kwargs.pop("is_final", True),
        graded_by=graded_by,
        graded_at=kwargs.pop("graded_at", timezone.now()),
        **kwargs,
    )


def create_appeal(submission=None, student=None, **kwargs):
    """Создаёт апелляцию по сдаче."""

    submission = submission or create_submission()
    student = student or submission.student

    return Appeal.objects.create(
        submission=submission,
        student=student,
        status=kwargs.pop("status", "pending"),
        reason=kwargs.pop("reason", "Не согласен с оценкой"),
        resolution=kwargs.pop("resolution", ""),
        resolved_by=kwargs.pop("resolved_by", None),
        resolved_at=kwargs.pop("resolved_at", None),
        **kwargs,
    )
