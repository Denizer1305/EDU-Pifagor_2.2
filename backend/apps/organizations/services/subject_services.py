from __future__ import annotations

import logging

from django.db import transaction

from apps.organizations.models import Subject, SubjectCategory

logger = logging.getLogger(__name__)


@transaction.atomic
def create_subject_category(*, code: str, name: str, description: str = "", is_active: bool = True) -> SubjectCategory:
    logger.info("create_subject_category started code=%s", code)
    subject_category = SubjectCategory(
        code=code.strip(),
        name=name.strip(),
        description=description.strip(),
        is_active=is_active,
    )
    subject_category.full_clean()
    subject_category.save()
    logger.info("create_subject_category completed id=%s", subject_category.id)
    return subject_category


@transaction.atomic
def update_subject_category(*, subject_category: SubjectCategory, **validated_data) -> SubjectCategory:
    logger.info("update_subject_category started id=%s fields=%s", subject_category.id, sorted(validated_data.keys()))
    for (
        field, value,
    ) in validated_data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(subject_category, field, value)

    subject_category.full_clean()
    subject_category.save()
    logger.info("update_subject_category completed id=%s", subject_category.id)
    return subject_category


@transaction.atomic
def create_subject(
    *,
    category: SubjectCategory,
    name: str,
    short_name: str = "",
    description: str = "",
    is_active: bool = True,
) -> Subject:
    logger.info("create_subject started name=%s", name.strip())
    subject = Subject(
        category=category,
        name=name.strip(),
        short_name=short_name.strip(),
        description=description.strip(),
        is_active=is_active,
    )
    subject.full_clean()
    subject.save()
    logger.info("create_subject completed id=%s", subject.id)
    return subject


@transaction.atomic
def update_subject(*, subject: Subject, **validated_data) -> Subject:
    logger.info("update_subject started id=%s fields=%s", subject.id, sorted(validated_data.keys()))
    for (
        field, value,
    ) in validated_data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(subject, field, value)

    subject.full_clean()
    subject.save()
    logger.info("update_subject completed id=%s", subject.id)
    return subject
