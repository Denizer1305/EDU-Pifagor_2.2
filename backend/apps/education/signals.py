from __future__ import annotations

from django.db.models.signals import pre_save
from django.dispatch import receiver

from apps.education.models import (
    AcademicYear,
    Curriculum,
    CurriculumItem,
    EducationPeriod,
    GroupSubject,
    StudentGroupEnrollment,
    TeacherGroupSubject,
)


def _strip_or_empty(value):
    return value.strip() if isinstance(value, str) else value


@receiver(pre_save, sender=AcademicYear)
def normalize_academic_year_fields(sender, instance, **kwargs):
    instance.name = _strip_or_empty(instance.name)
    instance.description = _strip_or_empty(instance.description)


@receiver(pre_save, sender=EducationPeriod)
def normalize_education_period_fields(sender, instance, **kwargs):
    instance.name = _strip_or_empty(instance.name)
    instance.code = _strip_or_empty(instance.code)
    instance.description = _strip_or_empty(instance.description)


@receiver(pre_save, sender=StudentGroupEnrollment)
def normalize_student_group_enrollment_fields(sender, instance, **kwargs):
    instance.notes = _strip_or_empty(instance.notes)


@receiver(pre_save, sender=GroupSubject)
def normalize_group_subject_fields(sender, instance, **kwargs):
    instance.notes = _strip_or_empty(instance.notes)


@receiver(pre_save, sender=TeacherGroupSubject)
def normalize_teacher_group_subject_fields(sender, instance, **kwargs):
    instance.notes = _strip_or_empty(instance.notes)


@receiver(pre_save, sender=Curriculum)
def normalize_curriculum_fields(sender, instance, **kwargs):
    instance.code = _strip_or_empty(instance.code)
    instance.name = _strip_or_empty(instance.name)
    instance.description = _strip_or_empty(instance.description)


@receiver(pre_save, sender=CurriculumItem)
def normalize_curriculum_item_fields(sender, instance, **kwargs):
    instance.notes = _strip_or_empty(instance.notes)
