from __future__ import annotations

from django.db.models import Q

from apps.users.models import StudentProfile


def get_student_profiles_queryset(
    *,
    search: str | None = None,
    verification_status: str | None = None,
    requested_organization_id: int | None = None,
    requested_department_id: int | None = None,
    requested_group_id: int | None = None,
):
    queryset = StudentProfile.objects.select_related(
        "user",
        "user__profile",
        "user__reviewed_by",
        "requested_organization",
        "requested_department",
        "requested_group",
        "verified_by",
    )

    if search:
        search = search.strip()
        queryset = queryset.filter(
            Q(user__email__icontains=search)
            | Q(user__profile__last_name__icontains=search)
            | Q(user__profile__first_name__icontains=search)
            | Q(user__profile__patronymic__icontains=search)
            | Q(student_code__icontains=search)
            | Q(submitted_group_code__icontains=search)
        )

    if verification_status:
        queryset = queryset.filter(verification_status=verification_status)

    if requested_organization_id is not None:
        queryset = queryset.filter(
            requested_organization_id=requested_organization_id,
        )

    if requested_department_id is not None:
        queryset = queryset.filter(
            requested_department_id=requested_department_id,
        )

    if requested_group_id is not None:
        queryset = queryset.filter(
            requested_group_id=requested_group_id,
        )

    return queryset.distinct().order_by("-created_at")


def get_pending_student_profiles_queryset():
    return get_student_profiles_queryset(
        verification_status=StudentProfile.VerificationStatusChoices.PENDING,
    )


def get_approved_student_profiles_queryset():
    return get_student_profiles_queryset(
        verification_status=StudentProfile.VerificationStatusChoices.APPROVED,
    )


def get_rejected_student_profiles_queryset():
    return get_student_profiles_queryset(
        verification_status=StudentProfile.VerificationStatusChoices.REJECTED,
    )


def get_student_profile_by_user_id(user_id: int):
    return (
        StudentProfile.objects.select_related(
            "user",
            "user__profile",
            "user__reviewed_by",
            "requested_organization",
            "requested_department",
            "requested_group",
            "verified_by",
        )
        .filter(user_id=user_id)
        .first()
    )
