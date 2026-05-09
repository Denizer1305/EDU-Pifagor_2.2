from __future__ import annotations

from django.db.models import Q

from apps.organizations.models import Subject, SubjectCategory


def _clean_str(value: str | None) -> str:
    return (value or "").strip()


def get_subject_categories_queryset(
    *,
    search: str | None = None,
    is_active: bool | None = None,
):
    queryset = SubjectCategory.objects.all()

    search = _clean_str(search)
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search)
            | Q(code__icontains=search)
            | Q(description__icontains=search)
        )

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    return queryset.order_by("name", "code")


def get_active_subject_categories_queryset():
    return get_subject_categories_queryset(is_active=True)


def get_subjects_queryset(
    *,
    search: str | None = None,
    category_id: int | None = None,
    is_active: bool | None = None,
):
    queryset = Subject.objects.select_related("category").all()

    search = _clean_str(search)
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search)
            | Q(short_name__icontains=search)
            | Q(description__icontains=search)
            | Q(category__name__icontains=search)
            | Q(category__code__icontains=search)
        )

    if category_id is not None:
        queryset = queryset.filter(category_id=category_id)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    return queryset.distinct().order_by("name")


def get_active_subjects_queryset():
    return get_subjects_queryset(is_active=True)
