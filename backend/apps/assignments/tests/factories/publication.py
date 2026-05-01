from __future__ import annotations

from django.utils import timezone

from apps.assignments.models import (
    AssignmentAudience,
    AssignmentPublication,
)
from apps.assignments.tests.factories.assignment import create_assignment
from apps.assignments.tests.factories.course import (
    create_course,
    create_group_with_enrollment,
)
from apps.assignments.tests.factories.users import create_student_user


def create_assignment_publication(
    assignment=None,
    course=None,
    lesson=None,
    published_by=None,
    **kwargs,
):
    """Создаёт публикацию работы."""

    assignment = assignment or create_assignment()

    if course is None:
        course = assignment.course

    if course is None:
        course = create_course(author=assignment.author)

    if lesson is None:
        lesson = assignment.lesson

    published_by = published_by or assignment.author

    return AssignmentPublication.objects.create(
        assignment=assignment,
        course=course,
        lesson=lesson,
        published_by=published_by,
        title_override=kwargs.pop("title_override", ""),
        starts_at=kwargs.pop("starts_at", timezone.now()),
        due_at=kwargs.pop("due_at", timezone.now() + timezone.timedelta(days=7)),
        available_until=kwargs.pop(
            "available_until",
            timezone.now() + timezone.timedelta(days=10),
        ),
        status=kwargs.pop("status", AssignmentPublication.StatusChoices.DRAFT),
        is_active=kwargs.pop("is_active", True),
        notes=kwargs.pop("notes", ""),
        **kwargs,
    )


def create_assignment_audience(
    publication=None,
    audience_type=None,
    student=None,
    group=None,
    course_enrollment=None,
    **kwargs,
):
    """Создаёт аудиторию публикации работы."""

    publication = publication or create_assignment_publication()

    if audience_type is None:
        audience_type = AssignmentAudience.AudienceTypeChoices.STUDENT

    if audience_type in {
        AssignmentAudience.AudienceTypeChoices.STUDENT,
        AssignmentAudience.AudienceTypeChoices.SELECTED_STUDENTS,
    } and student is None and course_enrollment is None:
        student = create_student_user()

    if audience_type == AssignmentAudience.AudienceTypeChoices.GROUP and group is None:
        group, _ = create_group_with_enrollment()

    if course_enrollment is not None and student is None:
        student = getattr(course_enrollment, "student", None)

    return AssignmentAudience.objects.create(
        publication=publication,
        audience_type=audience_type,
        group=group,
        student=student,
        course_enrollment=course_enrollment,
        is_active=kwargs.pop("is_active", True),
        **kwargs,
    )
