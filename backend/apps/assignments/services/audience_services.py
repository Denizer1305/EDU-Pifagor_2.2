from __future__ import annotations

import logging

from django.apps import apps
from django.db import transaction

from apps.assignments.models import AssignmentAudience, AssignmentPublication

logger = logging.getLogger(__name__)


@transaction.atomic
def assign_publication_to_group(
    *,
    publication: AssignmentPublication,
    group,
    is_active: bool = True,
) -> AssignmentAudience:
    audience, _ = AssignmentAudience.objects.get_or_create(
        publication=publication,
        audience_type=AssignmentAudience.AudienceTypeChoices.GROUP,
        group=group,
        defaults={"is_active": is_active},
    )
    audience.is_active = is_active
    audience.full_clean()
    audience.save()

    logger.info(
        "assign_publication_to_group completed publication_id=%s group_id=%s",
        publication.id,
        group.id,
    )
    return audience


@transaction.atomic
def assign_publication_to_student(
    *,
    publication: AssignmentPublication,
    student,
    audience_type: str = AssignmentAudience.AudienceTypeChoices.STUDENT,
    is_active: bool = True,
) -> AssignmentAudience:
    audience, _ = AssignmentAudience.objects.get_or_create(
        publication=publication,
        audience_type=audience_type,
        student=student,
        defaults={"is_active": is_active},
    )
    audience.is_active = is_active
    audience.full_clean()
    audience.save()

    logger.info(
        "assign_publication_to_student completed publication_id=%s student_id=%s",
        publication.id,
        student.id,
    )
    return audience


@transaction.atomic
def assign_publication_to_course_enrollment(
    *,
    publication: AssignmentPublication,
    course_enrollment,
    is_active: bool = True,
) -> AssignmentAudience:
    audience, _ = AssignmentAudience.objects.get_or_create(
        publication=publication,
        audience_type=AssignmentAudience.AudienceTypeChoices.STUDENT,
        student=course_enrollment.student,
        course_enrollment=course_enrollment,
        defaults={"is_active": is_active},
    )
    audience.is_active = is_active
    audience.full_clean()
    audience.save()

    logger.info(
        "assign_publication_to_course_enrollment completed publication_id=%s enrollment_id=%s",
        publication.id,
        course_enrollment.id,
    )
    return audience


@transaction.atomic
def assign_publication_to_all_course_students(
    *,
    publication: AssignmentPublication,
    create_individual_audiences: bool = False,
) -> list[AssignmentAudience]:
    if publication.course_id is None:
        raise ValueError("Для назначения всем студентам публикация должна быть привязана к курсу.")

    created_items: list[AssignmentAudience] = []

    audience, _ = AssignmentAudience.objects.get_or_create(
        publication=publication,
        audience_type=AssignmentAudience.AudienceTypeChoices.ALL_COURSE_STUDENTS,
        defaults={"is_active": True},
    )
    audience.is_active = True
    audience.full_clean()
    audience.save()
    created_items.append(audience)

    if create_individual_audiences:
        CourseEnrollment = apps.get_model("course", "CourseEnrollment")
        enrollments = CourseEnrollment.objects.filter(course=publication.course)

        for enrollment in enrollments:
            created_items.append(
                assign_publication_to_course_enrollment(
                    publication=publication,
                    course_enrollment=enrollment,
                    is_active=True,
                )
            )

    logger.info(
        "assign_publication_to_all_course_students completed publication_id=%s count=%s",
        publication.id,
        len(created_items),
    )
    return created_items


@transaction.atomic
def remove_assignment_audience(audience: AssignmentAudience) -> AssignmentAudience:
    audience.is_active = False
    audience.full_clean()
    audience.save(update_fields=("is_active", "updated_at"))

    logger.info("remove_assignment_audience completed audience_id=%s", audience.id)
    return audience
