from __future__ import annotations

from apps.education.models import Curriculum, CurriculumItem


def get_curricula_queryset():
    return Curriculum.objects.select_related(
        "organization",
        "department",
        "academic_year",
    ).all()


def get_active_curricula_queryset():
    return Curriculum.objects.select_related(
        "organization",
        "department",
        "academic_year",
    ).filter(is_active=True)


def get_curriculum_items_queryset():
    return CurriculumItem.objects.select_related(
        "curriculum",
        "curriculum__organization",
        "curriculum__department",
        "curriculum__academic_year",
        "period",
        "subject",
        "subject__category",
    ).all()


def get_active_curriculum_items_queryset():
    return CurriculumItem.objects.select_related(
        "curriculum",
        "curriculum__organization",
        "curriculum__department",
        "curriculum__academic_year",
        "period",
        "subject",
        "subject__category",
    ).filter(is_active=True)
