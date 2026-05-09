from __future__ import annotations

from django.utils import timezone

from apps.education.tests.factories.common import (
    student_counter,
    teacher_counter,
    unwrap_factory_result,
)
from apps.users.tests.factories import (
    create_student_user as base_create_student_user,
)
from apps.users.tests.factories import (
    create_teacher_user as base_create_teacher_user,
)


def _activate_student_user(user):
    """Переводит тестового студента в активное подтверждённое состояние."""

    user.is_email_verified = True
    user.onboarding_status = "active"
    user.onboarding_completed_at = timezone.now()
    user.save(
        update_fields=(
            "is_email_verified",
            "onboarding_status",
            "onboarding_completed_at",
        )
    )

    if hasattr(user, "student_profile") and user.student_profile:
        user.student_profile.verification_status = "approved"
        user.student_profile.verified_at = timezone.now()

        update_fields = ["verification_status", "verified_at"]
        if hasattr(user.student_profile, "updated_at"):
            update_fields.append("updated_at")

        user.student_profile.save(update_fields=update_fields)

    return user


def _activate_teacher_user(user):
    """Переводит тестового преподавателя в активное подтверждённое состояние."""

    user.is_email_verified = True
    user.onboarding_status = "active"
    user.onboarding_completed_at = timezone.now()
    user.save(
        update_fields=(
            "is_email_verified",
            "onboarding_status",
            "onboarding_completed_at",
        )
    )

    if hasattr(user, "teacher_profile") and user.teacher_profile:
        user.teacher_profile.verification_status = "approved"
        user.teacher_profile.verified_at = timezone.now()

        update_fields = ["verification_status", "verified_at"]
        if hasattr(user.teacher_profile, "updated_at"):
            update_fields.append("updated_at")

        user.teacher_profile.save(update_fields=update_fields)

    return user


def create_student_user(
    *,
    email: str | None = None,
    password: str = "TestPass123!",
):
    """Создаёт активного тестового студента."""

    index = next(student_counter)

    if email is None:
        email = f"student_{index}@example.com"

    created = base_create_student_user(
        email=email,
        password=password,
    )
    user = unwrap_factory_result(created)
    return _activate_student_user(user)


def create_teacher_user(
    *,
    email: str | None = None,
    password: str = "TestPass123!",
):
    """Создаёт активного тестового преподавателя."""

    index = next(teacher_counter)

    if email is None:
        email = f"teacher_{index}@example.com"

    created = base_create_teacher_user(
        email=email,
        password=password,
    )
    user = unwrap_factory_result(created)
    return _activate_teacher_user(user)
