from __future__ import annotations

from apps.education.models import GroupSubject, TeacherGroupSubject


def get_group_subjects_queryset():
    return GroupSubject.objects.select_related(
        "group",
        "group__organization",
        "group__department",
        "subject",
        "subject__category",
        "academic_year",
        "period",
    ).all()


def get_active_group_subjects_queryset():
    return GroupSubject.objects.select_related(
        "group",
        "group__organization",
        "group__department",
        "subject",
        "subject__category",
        "academic_year",
        "period",
    ).filter(is_active=True)


def get_teacher_group_subjects_queryset():
    return TeacherGroupSubject.objects.select_related(
        "teacher",
        "teacher__profile",
        "group_subject",
        "group_subject__group",
        "group_subject__group__organization",
        "group_subject__subject",
        "group_subject__subject__category",
        "group_subject__academic_year",
        "group_subject__period",
    ).all()


def get_active_teacher_group_subjects_queryset():
    return TeacherGroupSubject.objects.select_related(
        "teacher",
        "teacher__profile",
        "group_subject",
        "group_subject__group",
        "group_subject__group__organization",
        "group_subject__subject",
        "group_subject__subject__category",
        "group_subject__academic_year",
        "group_subject__period",
    ).filter(is_active=True)
