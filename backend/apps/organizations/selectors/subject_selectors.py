from __future__ import annotations

from apps.organizations.models import Subject, SubjectCategory


def get_subject_categories_queryset():
    return SubjectCategory.objects.all()


def get_active_subject_categories_queryset():
    return SubjectCategory.objects.filter(is_active=True)


def get_subjects_queryset():
    return Subject.objects.select_related("category").all()


def get_active_subjects_queryset():
    return Subject.objects.select_related("category").filter(is_active=True)
