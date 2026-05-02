from __future__ import annotations

from django.db.models import Q
from django.utils import timezone

from apps.organizations.models import Group
from apps.organizations.selectors.group_selectors.common import _clean_str


def _active_join_code_q() -> Q:
    """Возвращает условие активного кода присоединения к группе."""

    return (
        Q(join_code_hash__gt="")
        & Q(join_code_is_active=True)
        & (
            Q(join_code_expires_at__isnull=True)
            | Q(join_code_expires_at__gt=timezone.now())
        )
    )


def get_groups_queryset(
    *,
    search: str | None = None,
    organization_id: int | None = None,
    department_id: int | None = None,
    study_form: str | None = None,
    status: str | None = None,
    academic_year: str | None = None,
    course_number: int | None = None,
    is_active: bool | None = None,
    has_active_join_code: bool | None = None,
):
    """Возвращает queryset учебных групп с фильтрацией."""

    queryset = Group.objects.select_related(
        "organization",
        "department",
    ).all()

    search = _clean_str(search)
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search)
            | Q(code__icontains=search)
            | Q(description__icontains=search)
            | Q(organization__name__icontains=search)
            | Q(organization__short_name__icontains=search)
            | Q(department__name__icontains=search)
            | Q(department__short_name__icontains=search)
        )

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if department_id is not None:
        queryset = queryset.filter(department_id=department_id)

    if study_form:
        queryset = queryset.filter(study_form=study_form)

    if status:
        queryset = queryset.filter(status=status)

    academic_year = _clean_str(academic_year)
    if academic_year:
        queryset = queryset.filter(academic_year=academic_year)

    if course_number is not None:
        queryset = queryset.filter(course_number=course_number)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    if has_active_join_code is True:
        queryset = queryset.filter(_active_join_code_q())

    if has_active_join_code is False:
        queryset = queryset.exclude(_active_join_code_q())

    return queryset.distinct().order_by(
        "organization__name",
        "name",
    )


def get_active_groups_queryset():
    """Возвращает активные учебные группы."""

    return get_groups_queryset(is_active=True)


def get_groups_by_organization_queryset(
    organization_id: int,
    *,
    only_active: bool = True,
):
    """Возвращает группы конкретной организации."""

    return get_groups_queryset(
        organization_id=organization_id,
        is_active=True if only_active else None,
    )


def get_groups_by_department_queryset(
    department_id: int,
    *,
    only_active: bool = True,
):
    """Возвращает группы конкретного подразделения."""

    return get_groups_queryset(
        department_id=department_id,
        is_active=True if only_active else None,
    )


def get_groups_with_active_join_code_queryset():
    """Возвращает группы с активным кодом присоединения."""

    return get_groups_queryset(has_active_join_code=True)


def get_group_with_active_join_code(group_id: int):
    """Возвращает группу с активным кодом присоединения по id."""

    return (
        get_groups_queryset(
            has_active_join_code=True,
        )
        .filter(id=group_id)
        .first()
    )
