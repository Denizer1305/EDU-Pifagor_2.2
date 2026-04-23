from __future__ import annotations

from django.db.models import Q

from apps.users.models import TeacherProfile


def _has_field(field_name: str) -> bool:
    return field_name in {field.name for field in TeacherProfile._meta.get_fields()}


def get_teacher_profiles_queryset(
    *,
    search: str | None = None,
    verification_status: str | None = None,
    requested_organization_id: int | None = None,
    requested_department_id: int | None = None,
):
    queryset = TeacherProfile.objects.select_related(
        "user",
        "user__profile",
        "user__reviewed_by",
        "requested_organization",
        "requested_department",
        "verified_by",
    )

    if search:
        search = search.strip()
        q_obj = (
            Q(user__email__icontains=search)
            | Q(user__profile__last_name__icontains=search)
            | Q(user__profile__first_name__icontains=search)
            | Q(user__profile__patronymic__icontains=search)
        )

        for field_name in (
            "public_title",
            "short_bio",
            "bio",
            "education",
            "experience",
            "achievements",
            "position",
            "employee_code",
            "education_info",
            "specialization",
        ):
            if _has_field(field_name):
                q_obj |= Q(**{f"{field_name}__icontains": search})

        queryset = queryset.filter(q_obj)

    if verification_status:
        queryset = queryset.filter(verification_status=verification_status)

    if requested_organization_id is not None:
        queryset = queryset.filter(requested_organization_id=requested_organization_id)

    if requested_department_id is not None:
        queryset = queryset.filter(requested_department_id=requested_department_id)

    return queryset.distinct().order_by("-created_at")


def get_pending_teacher_profiles_queryset():
    return get_teacher_profiles_queryset(
        verification_status=TeacherProfile.VerificationStatusChoices.PENDING,
    )


def get_approved_teacher_profiles_queryset():
    return get_teacher_profiles_queryset(
        verification_status=TeacherProfile.VerificationStatusChoices.APPROVED,
    )


def get_rejected_teacher_profiles_queryset():
    return get_teacher_profiles_queryset(
        verification_status=TeacherProfile.VerificationStatusChoices.REJECTED,
    )


def get_teacher_profile_by_user_id(user_id: int):
    return (
        TeacherProfile.objects.select_related(
            "user",
            "user__profile",
            "user__reviewed_by",
            "requested_organization",
            "requested_department",
            "verified_by",
        )
        .filter(user_id=user_id)
        .first()
    )
