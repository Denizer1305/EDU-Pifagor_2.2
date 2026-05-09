from __future__ import annotations

from django.db.models import Max

from apps.assignments.models import (
    AssignmentPolicy,
    Submission,
)


def get_assignment_policy(assignment) -> AssignmentPolicy:
    """Возвращает политику работы или создаёт её с базовыми значениями."""

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


def get_next_attempt_number(publication, student) -> int:
    """Возвращает номер следующей попытки студента по публикации."""

    max_attempt = Submission.objects.filter(
        publication=publication,
        student=student,
    ).aggregate(value=Max("attempt_number"))["value"]

    return (max_attempt or 0) + 1
