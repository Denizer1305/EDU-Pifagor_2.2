from __future__ import annotations

from apps.assignments.models import AssignmentAudience, AssignmentPublication
from apps.assignments.services import assign_publication_to_student
from apps.assignments.tests.factories import create_assignment_publication

COURSE_ENROLLMENT_AUDIENCE = getattr(
    AssignmentAudience.AudienceTypeChoices,
    "COURSE_ENROLLMENT",
    "course_enrollment",
)


def create_published_assigned_publication(
    *,
    assignment,
    student,
    teacher=None,
):
    """Создаёт опубликованную публикацию и назначает её студенту."""

    publication = create_assignment_publication(
        assignment=assignment,
        course=assignment.course,
        published_by=teacher or assignment.author,
        status=AssignmentPublication.StatusChoices.PUBLISHED,
    )
    assign_publication_to_student(
        publication=publication,
        student=student,
        audience_type=AssignmentAudience.AudienceTypeChoices.STUDENT,
        is_active=True,
    )
    return publication
