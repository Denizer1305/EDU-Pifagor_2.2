from __future__ import annotations

from apps.organizations.models import Group, GroupCurator, TeacherOrganization, TeacherSubject


def get_groups_queryset():
    return Group.objects.select_related(
        "organization",
        "department",
    ).all()


def get_active_groups_queryset():
    return Group.objects.select_related(
        "organization",
        "department",
    ).filter(is_active=True)


def get_group_curators_queryset():
    return GroupCurator.objects.select_related(
        "group",
        "group__organization",
        "teacher",
        "teacher__profile",
    ).all()


def get_teacher_organizations_queryset():
    return TeacherOrganization.objects.select_related(
        "teacher",
        "teacher__profile",
        "organization",
    ).all()


def get_teacher_subjects_queryset():
    return TeacherSubject.objects.select_related(
        "teacher",
        "teacher__profile",
        "subject",
        "subject__category",
    ).all()
