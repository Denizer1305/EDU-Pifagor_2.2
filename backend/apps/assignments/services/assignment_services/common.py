from __future__ import annotations

from apps.assignments.models import Assignment, AssignmentPolicy


def get_or_create_assignment_policy(assignment: Assignment) -> AssignmentPolicy:
    """Возвращает политику работы или создаёт её с безопасными значениями по умолчанию."""

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
