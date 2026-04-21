from __future__ import annotations

from django.db.models import Q

from apps.users.models import Profile


def get_profiles_queryset(
    *,
    search: str | None = None,
    city: str | None = None,
    gender: str | None = None,
):
    queryset = Profile.objects.select_related(
        "user",
        "user__reviewed_by",
    )

    if search:
        search = search.strip()
        queryset = queryset.filter(
            Q(user__email__icontains=search)
            | Q(last_name__icontains=search)
            | Q(first_name__icontains=search)
            | Q(patronymic__icontains=search)
            | Q(phone__icontains=search)
        )

    if city:
        queryset = queryset.filter(city__icontains=city.strip())

    if gender:
        queryset = queryset.filter(gender=gender)

    return queryset.order_by("last_name", "first_name", "patronymic")


def get_profile_by_user_id(user_id: int):
    return (
        Profile.objects.select_related(
            "user",
            "user__reviewed_by",
        )
        .filter(user_id=user_id)
        .first()
    )
