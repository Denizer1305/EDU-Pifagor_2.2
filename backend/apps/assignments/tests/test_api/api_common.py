from __future__ import annotations

from apps.assignments.models import AssignmentAudience

COURSE_ENROLLMENT_AUDIENCE = getattr(
    AssignmentAudience.AudienceTypeChoices,
    "COURSE_ENROLLMENT",
    "course_enrollment",
)
