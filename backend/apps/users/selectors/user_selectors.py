from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import Q

from apps.users.constants import ROLE_ADMIN, ROLE_PARENT, ROLE_STUDENT, ROLE_TEACHER


User = get_user_model()


def get_users_queryset(
    *,
    search: str | None = None,
    registration_type: str | None = None,
    onboarding_status: str | None = None,
    is_active: bool | None = None,
):
    queryset = User.objects.select_related(
        "profile",
        "reviewed_by",
    ).prefetch_related(
        "user_roles__role",
    )

    if search:
        search = search.strip()
        queryset = queryset.filter(
            Q(email__icontains=search)
            | Q(profile__last_name__icontains=search)
            | Q(profile__first_name__icontains=search)
            | Q(profile__patronymic__icontains=search)
            | Q(review_comment__icontains=search)
        )

    if registration_type:
        queryset = queryset.filter(registration_type=registration_type)

    if onboarding_status:
        queryset = queryset.filter(onboarding_status=onboarding_status)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    return queryset.distinct().order_by("-created_at")


def get_user_with_related(user_id: int):
    return (
        User.objects.select_related(
            "profile",
            "reviewed_by",
        )
        .prefetch_related(
            "user_roles__role",
        )
        .filter(id=user_id)
        .first()
    )


def get_active_users_queryset():
    return get_users_queryset(is_active=True)


def get_pending_users_queryset():
    return get_users_queryset(
        onboarding_status=User.OnboardingStatusChoices.PENDING,
    )


def get_users_by_registration_type_queryset(*, registration_type: str):
    return get_users_queryset(
        registration_type=registration_type,
    )


def get_students_queryset():
    return get_users_queryset().filter(
        user_roles__role__code=ROLE_STUDENT,
        user_roles__is_active=True,
    ).distinct()


def get_teachers_queryset():
    return get_users_queryset().filter(
        user_roles__role__code=ROLE_TEACHER,
        user_roles__is_active=True,
    ).distinct()


def get_parents_queryset():
    return get_users_queryset().filter(
        user_roles__role__code=ROLE_PARENT,
        user_roles__is_active=True,
    ).distinct()


def get_admins_queryset():
    return get_users_queryset().filter(
        user_roles__role__code=ROLE_ADMIN,
        user_roles__is_active=True,
    ).distinct()
