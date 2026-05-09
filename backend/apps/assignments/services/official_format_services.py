from __future__ import annotations

from django.db import transaction

from apps.assignments.models import Assignment, AssignmentOfficialFormat


@transaction.atomic
def update_assignment_official_format(
    *,
    assignment: Assignment,
    **fields,
) -> AssignmentOfficialFormat:
    official_format, _ = AssignmentOfficialFormat.objects.get_or_create(
        assignment=assignment,
        defaults={
            "official_family": AssignmentOfficialFormat.OfficialFamilyChoices.NONE,
        },
    )

    for field_name, value in fields.items():
        setattr(official_format, field_name, value)

    official_format.full_clean()
    official_format.save()
    return official_format
