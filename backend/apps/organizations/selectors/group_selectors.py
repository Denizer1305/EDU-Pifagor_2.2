from __future__ import annotations

from django.db.models import Q
from django.utils import timezone

from apps.organizations.models import Group, GroupCurator, TeacherOrganization, TeacherSubject


def _clean_str(value: str | None) -> str:
    return (value or "").strip()


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
        queryset = queryset.filter(
            join_code_hash__gt="",
            join_code_is_active=True,
        ).filter(
            Q(join_code_expires_at__isnull=True)
            | Q(join_code_expires_at__gt=timezone.now())
        )

    if has_active_join_code is False:
        queryset = queryset.exclude(
            pk__in=get_groups_queryset(
                has_active_join_code=True
            ).values_list("pk", flat=True)
        )

    return queryset.distinct().order_by("organization__name", "name")


def get_active_groups_queryset():
    return get_groups_queryset(is_active=True)


def get_groups_by_organization_queryset(
    organization_id: int,
    *,
    only_active: bool = True,
):
    return get_groups_queryset(
        organization_id=organization_id,
        is_active=True if only_active else None,
    )


def get_groups_by_department_queryset(
    department_id: int,
    *,
    only_active: bool = True,
):
    return get_groups_queryset(
        department_id=department_id,
        is_active=True if only_active else None,
    )


def get_groups_with_active_join_code_queryset():
    return get_groups_queryset(has_active_join_code=True)


def get_group_with_active_join_code(group_id: int):
    return get_groups_queryset(
        has_active_join_code=True,
    ).filter(id=group_id).first()


def get_group_curators_queryset(
    *,
    group_id: int | None = None,
    teacher_id: int | None = None,
    is_primary: bool | None = None,
    is_active: bool | None = None,
    current_only: bool = False,
):
    queryset = GroupCurator.objects.select_related(
        "group",
        "group__organization",
        "group__department",
        "teacher",
        "teacher__profile",
    ).all()

    if group_id is not None:
        queryset = queryset.filter(group_id=group_id)

    if teacher_id is not None:
        queryset = queryset.filter(teacher_id=teacher_id)

    if is_primary is not None:
        queryset = queryset.filter(is_primary=is_primary)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    if current_only:
        today = timezone.localdate()
        queryset = queryset.filter(
            is_active=True,
        ).filter(
            Q(starts_at__isnull=True) | Q(starts_at__lte=today),
            Q(ends_at__isnull=True) | Q(ends_at__gte=today),
        )

    return queryset.order_by(
        "-is_primary",
        "-is_active",
        "group__name",
        "teacher__profile__last_name",
        "teacher__profile__first_name",
    )


def get_active_group_curators_queryset(*, group_id: int | None = None):
    return get_group_curators_queryset(
        group_id=group_id,
        current_only=True,
    )


def get_teacher_organizations_queryset(
    *,
    teacher_id: int | None = None,
    organization_id: int | None = None,
    is_primary: bool | None = None,
    is_active: bool | None = None,
    current_only: bool = False,
):
    queryset = TeacherOrganization.objects.select_related(
        "teacher",
        "teacher__profile",
        "organization",
    ).all()

    if teacher_id is not None:
        queryset = queryset.filter(teacher_id=teacher_id)

    if organization_id is not None:
        queryset = queryset.filter(organization_id=organization_id)

    if is_primary is not None:
        queryset = queryset.filter(is_primary=is_primary)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    if current_only:
        today = timezone.localdate()
        queryset = queryset.filter(
            is_active=True,
        ).filter(
            Q(starts_at__isnull=True) | Q(starts_at__lte=today),
            Q(ends_at__isnull=True) | Q(ends_at__gte=today),
        )

    return queryset.order_by(
        "teacher__profile__last_name",
        "teacher__profile__first_name",
        "organization__name",
    )


def get_active_teacher_organizations_queryset(
    *,
    teacher_id: int | None = None,
    organization_id: int | None = None,
):
    return get_teacher_organizations_queryset(
        teacher_id=teacher_id,
        organization_id=organization_id,
        current_only=True,
    )


def get_teacher_subjects_queryset(
    *,
    teacher_id: int | None = None,
    subject_id: int | None = None,
    is_primary: bool | None = None,
    is_active: bool | None = None,
):
    queryset = TeacherSubject.objects.select_related(
        "teacher",
        "teacher__profile",
        "subject",
        "subject__category",
    ).all()

    if teacher_id is not None:
        queryset = queryset.filter(teacher_id=teacher_id)

    if subject_id is not None:
        queryset = queryset.filter(subject_id=subject_id)

    if is_primary is not None:
        queryset = queryset.filter(is_primary=is_primary)

    if is_active is not None:
        queryset = queryset.filter(is_active=is_active)

    return queryset.order_by(
        "teacher__profile__last_name",
        "teacher__profile__first_name",
        "subject__name",
    )


def get_active_teacher_subjects_queryset(
    *,
    teacher_id: int | None = None,
    subject_id: int | None = None,
):
    return get_teacher_subjects_queryset(
        teacher_id=teacher_id,
        subject_id=subject_id,
        is_active=True,
    )
