from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.course.models import Course, CourseAssignment, CourseEnrollment


@transaction.atomic
def assign_course_to_group(
    *,
    course: Course,
    group,
    assigned_by=None,
    starts_at=None,
    ends_at=None,
    is_active: bool = True,
    auto_enroll: bool = True,
    notes: str = "",
) -> CourseAssignment:
    assignment, created = CourseAssignment.objects.get_or_create(
        course=course,
        group=group,
        defaults={
            "assignment_type": CourseAssignment.AssignmentTypeChoices.GROUP,
            "assigned_by": assigned_by,
            "starts_at": starts_at,
            "ends_at": ends_at,
            "is_active": is_active,
            "auto_enroll": auto_enroll,
            "notes": notes,
        },
    )

    if not created:
        assignment.assignment_type = CourseAssignment.AssignmentTypeChoices.GROUP
        assignment.assigned_by = assigned_by
        assignment.starts_at = starts_at
        assignment.ends_at = ends_at
        assignment.is_active = is_active
        assignment.auto_enroll = auto_enroll
        assignment.notes = notes
        assignment.full_clean()
        assignment.save(
            update_fields=[
                "assignment_type",
                "assigned_by",
                "starts_at",
                "ends_at",
                "is_active",
                "auto_enroll",
                "notes",
                "updated_at",
            ]
        )

    return assignment


@transaction.atomic
def assign_course_to_student(
    *,
    course: Course,
    student,
    assigned_by=None,
    starts_at=None,
    ends_at=None,
    is_active: bool = True,
    auto_enroll: bool = True,
    notes: str = "",
) -> CourseAssignment:
    assignment, created = CourseAssignment.objects.get_or_create(
        course=course,
        student=student,
        defaults={
            "assignment_type": CourseAssignment.AssignmentTypeChoices.STUDENT,
            "assigned_by": assigned_by,
            "starts_at": starts_at,
            "ends_at": ends_at,
            "is_active": is_active,
            "auto_enroll": auto_enroll,
            "notes": notes,
        },
    )

    if not created:
        assignment.assignment_type = CourseAssignment.AssignmentTypeChoices.STUDENT
        assignment.assigned_by = assigned_by
        assignment.starts_at = starts_at
        assignment.ends_at = ends_at
        assignment.is_active = is_active
        assignment.auto_enroll = auto_enroll
        assignment.notes = notes
        assignment.full_clean()
        assignment.save(
            update_fields=[
                "assignment_type",
                "assigned_by",
                "starts_at",
                "ends_at",
                "is_active",
                "auto_enroll",
                "notes",
                "updated_at",
            ]
        )

    if auto_enroll:
        create_course_enrollment(
            course=course,
            student=student,
            assignment=assignment,
        )

    return assignment


@transaction.atomic
def remove_course_assignment(*, assignment: CourseAssignment) -> None:
    if assignment.enrollments.exists():
        assignment.is_active = False
        assignment.full_clean()
        assignment.save(update_fields=["is_active", "updated_at"])
        return

    assignment.delete()


@transaction.atomic
def create_course_enrollment(
    *,
    course: Course,
    student,
    assignment: CourseAssignment | None = None,
    status: str = CourseEnrollment.StatusChoices.ENROLLED,
) -> CourseEnrollment:
    if course.status == Course.StatusChoices.ARCHIVED:
        raise ValidationError({"course": "Нельзя зачислить на архивный курс."})

    enrollment, created = CourseEnrollment.objects.get_or_create(
        course=course,
        student=student,
        defaults={
            "assignment": assignment,
            "status": status,
        },
    )

    if not created:
        changed = False

        if assignment is not None and enrollment.assignment_id != assignment.id:
            enrollment.assignment = assignment
            changed = True

        if enrollment.status == CourseEnrollment.StatusChoices.CANCELLED:
            enrollment.status = CourseEnrollment.StatusChoices.ENROLLED
            changed = True

        if changed:
            enrollment.full_clean()
            enrollment.save(update_fields=["assignment", "status", "updated_at"])

    return enrollment


@transaction.atomic
def cancel_course_enrollment(*, enrollment: CourseEnrollment) -> CourseEnrollment:
    enrollment.status = CourseEnrollment.StatusChoices.CANCELLED
    enrollment.full_clean()
    enrollment.save(update_fields=["status", "updated_at"])
    return enrollment
