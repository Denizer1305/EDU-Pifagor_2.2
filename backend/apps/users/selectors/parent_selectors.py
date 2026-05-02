from __future__ import annotations

from django.db.models import Q

from apps.users.models import ParentProfile, ParentStudent


def _parent_profile_has_field(field_name: str) -> bool:
    return field_name in {field.name for field in ParentProfile._meta.get_fields()}


def get_parent_profiles_queryset(
    *,
    search: str | None = None,
):
    queryset = ParentProfile.objects.select_related(
        "user",
        "user__profile",
        "user__reviewed_by",
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
            "work_place",
            "occupation",
            "notes",
            "emergency_contact_phone",
        ):
            if _parent_profile_has_field(field_name):
                q_obj |= Q(**{f"{field_name}__icontains": search})

        queryset = queryset.filter(q_obj)

    return queryset.distinct().order_by("-created_at")


def get_parent_profile_by_user_id(user_id: int):
    return (
        ParentProfile.objects.select_related(
            "user",
            "user__profile",
            "user__reviewed_by",
        )
        .filter(user_id=user_id)
        .first()
    )


def get_parent_student_links_queryset(
    *,
    parent_id: int | None = None,
    student_id: int | None = None,
    status: str | None = None,
    relation_type: str | None = None,
):
    queryset = ParentStudent.objects.select_related(
        "parent",
        "parent__profile",
        "student",
        "student__profile",
        "requested_by",
        "requested_by__profile",
        "approved_by",
        "approved_by__profile",
    )

    if parent_id is not None:
        queryset = queryset.filter(parent_id=parent_id)

    if student_id is not None:
        queryset = queryset.filter(student_id=student_id)

    if status:
        queryset = queryset.filter(status=status)

    if relation_type:
        queryset = queryset.filter(relation_type=relation_type)

    return queryset.order_by("-created_at")


def get_pending_parent_student_links_queryset():
    return get_parent_student_links_queryset(
        status=ParentStudent.LinkStatusChoices.PENDING,
    )


def get_approved_parent_student_links_queryset():
    return get_parent_student_links_queryset(
        status=ParentStudent.LinkStatusChoices.APPROVED,
    )


def get_parent_student_links_for_user(user):
    if not user or not user.is_authenticated:
        return ParentStudent.objects.none()

    return (
        get_parent_student_links_queryset()
        .filter(Q(parent=user) | Q(student=user))
        .distinct()
    )
