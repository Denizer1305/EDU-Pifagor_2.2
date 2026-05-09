from __future__ import annotations

from django.apps import apps

from apps.assignments.models import AssignmentAudience


def student_in_group_audience(publication, student) -> bool:
    """Проверяет, входит ли студент в одну из групп аудитории публикации."""

    group_ids = list(
        publication.audiences.filter(
            audience_type=AssignmentAudience.AudienceTypeChoices.GROUP,
            is_active=True,
            group__isnull=False,
        ).values_list("group_id", flat=True)
    )

    if not group_ids:
        return False

    StudentGroupEnrollment = apps.get_model("education", "StudentGroupEnrollment")
    return StudentGroupEnrollment.objects.filter(
        student=student,
        group_id__in=group_ids,
    ).exists()


def student_in_course(publication, student) -> bool:
    """Проверяет, зачислен ли студент на курс публикации."""

    if publication.course_id is None:
        return False

    CourseEnrollment = apps.get_model("course", "CourseEnrollment")
    return CourseEnrollment.objects.filter(
        course=publication.course,
        student=student,
    ).exists()


def is_student_assigned(publication, student) -> bool:
    """Проверяет, назначена ли публикация конкретному студенту."""

    audiences = publication.audiences.filter(is_active=True)

    if not audiences.exists():
        return False

    if audiences.filter(
        audience_type=AssignmentAudience.AudienceTypeChoices.ALL_COURSE_STUDENTS,
    ).exists():
        return student_in_course(publication, student)

    if audiences.filter(
        audience_type__in=(
            AssignmentAudience.AudienceTypeChoices.STUDENT,
            AssignmentAudience.AudienceTypeChoices.SELECTED_STUDENTS,
        ),
        student=student,
    ).exists():
        return True

    if audiences.filter(course_enrollment__student=student).exists():
        return True

    return student_in_group_audience(publication, student)
