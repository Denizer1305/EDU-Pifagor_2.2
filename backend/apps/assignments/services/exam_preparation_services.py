from __future__ import annotations

from django.db import transaction

from apps.assignments.models import Assignment, AssignmentOfficialFormat
from apps.assignments.services.assignment_services import create_assignment


@transaction.atomic
def create_vpr_preparation_assignment(
    *,
    author,
    title: str,
    subject=None,
    organization=None,
    course=None,
    lesson=None,
    assessment_year: int,
    grade_level: int,
    exam_subject_name: str,
    description: str = "",
    instructions: str = "",
) -> Assignment:
    return create_assignment(
        author=author,
        title=title,
        description=description,
        instructions=instructions,
        course=course,
        lesson=lesson,
        subject=subject,
        organization=organization,
        assignment_kind=Assignment.AssignmentKindChoices.VERIFICATION_WORK,
        control_scope=Assignment.ControlScopeChoices.STATE_EXAM_PREPARATION,
        status=Assignment.StatusChoices.DRAFT,
        visibility=Assignment.VisibilityChoices.ASSIGNED_ONLY,
        education_level=Assignment.EducationLevelChoices.SCHOOL,
        policy_data={
            "check_mode": "mixed",
            "grading_mode": "raw_score",
            "attempts_limit": 1,
            "allow_text_answer": True,
            "allow_file_upload": False,
            "show_results_immediately": False,
        },
        official_format_data={
            "official_family": AssignmentOfficialFormat.OfficialFamilyChoices.VPR,
            "assessment_year": assessment_year,
            "grade_level": grade_level,
            "exam_subject_name": exam_subject_name,
            "source_kind": AssignmentOfficialFormat.SourceKindChoices.TEACHER_ADAPTED,
            "is_preparation_only": True,
        },
    )


@transaction.atomic
def create_oge_preparation_assignment(
    *,
    author,
    title: str,
    subject=None,
    organization=None,
    course=None,
    lesson=None,
    assessment_year: int,
    grade_level: int = 9,
    exam_subject_name: str = "",
    description: str = "",
    instructions: str = "",
) -> Assignment:
    return create_assignment(
        author=author,
        title=title,
        description=description,
        instructions=instructions,
        course=course,
        lesson=lesson,
        subject=subject,
        organization=organization,
        assignment_kind=Assignment.AssignmentKindChoices.MOCK_EXAM,
        control_scope=Assignment.ControlScopeChoices.STATE_EXAM_PREPARATION,
        status=Assignment.StatusChoices.DRAFT,
        visibility=Assignment.VisibilityChoices.ASSIGNED_ONLY,
        education_level=Assignment.EducationLevelChoices.SCHOOL,
        policy_data={
            "check_mode": "mixed",
            "grading_mode": "raw_score",
            "attempts_limit": 1,
            "allow_text_answer": True,
            "allow_file_upload": True,
            "show_results_immediately": False,
        },
        official_format_data={
            "official_family": AssignmentOfficialFormat.OfficialFamilyChoices.OGE,
            "assessment_year": assessment_year,
            "grade_level": grade_level,
            "exam_subject_name": exam_subject_name,
            "source_kind": AssignmentOfficialFormat.SourceKindChoices.TEACHER_ADAPTED,
            "is_preparation_only": True,
        },
    )


@transaction.atomic
def create_ege_preparation_assignment(
    *,
    author,
    title: str,
    subject=None,
    organization=None,
    course=None,
    lesson=None,
    assessment_year: int,
    grade_level: int = 11,
    exam_subject_name: str = "",
    description: str = "",
    instructions: str = "",
) -> Assignment:
    return create_assignment(
        author=author,
        title=title,
        description=description,
        instructions=instructions,
        course=course,
        lesson=lesson,
        subject=subject,
        organization=organization,
        assignment_kind=Assignment.AssignmentKindChoices.MOCK_EXAM,
        control_scope=Assignment.ControlScopeChoices.STATE_EXAM_PREPARATION,
        status=Assignment.StatusChoices.DRAFT,
        visibility=Assignment.VisibilityChoices.ASSIGNED_ONLY,
        education_level=Assignment.EducationLevelChoices.SCHOOL,
        policy_data={
            "check_mode": "mixed",
            "grading_mode": "raw_score",
            "attempts_limit": 1,
            "allow_text_answer": True,
            "allow_file_upload": True,
            "show_results_immediately": False,
        },
        official_format_data={
            "official_family": AssignmentOfficialFormat.OfficialFamilyChoices.EGE,
            "assessment_year": assessment_year,
            "grade_level": grade_level,
            "exam_subject_name": exam_subject_name,
            "source_kind": AssignmentOfficialFormat.SourceKindChoices.TEACHER_ADAPTED,
            "is_preparation_only": True,
        },
    )


@transaction.atomic
def create_demo_exam_preparation_assignment(
    *,
    author,
    title: str,
    subject=None,
    organization=None,
    course=None,
    lesson=None,
    assessment_year: int,
    grade_level: int | None = None,
    exam_subject_name: str = "",
    education_level: str = Assignment.EducationLevelChoices.SPO,
    description: str = "",
    instructions: str = "",
) -> Assignment:
    return create_assignment(
        author=author,
        title=title,
        description=description,
        instructions=instructions,
        course=course,
        lesson=lesson,
        subject=subject,
        organization=organization,
        assignment_kind=Assignment.AssignmentKindChoices.DEMO_EXAM,
        control_scope=Assignment.ControlScopeChoices.STATE_EXAM_PREPARATION,
        status=Assignment.StatusChoices.DRAFT,
        visibility=Assignment.VisibilityChoices.ASSIGNED_ONLY,
        education_level=education_level,
        policy_data={
            "check_mode": "mixed",
            "grading_mode": "raw_score",
            "attempts_limit": 1,
            "allow_text_answer": True,
            "allow_file_upload": True,
            "show_results_immediately": False,
        },
        official_format_data={
            "official_family": AssignmentOfficialFormat.OfficialFamilyChoices.DEMO_EXAM,
            "assessment_year": assessment_year,
            "grade_level": grade_level,
            "exam_subject_name": exam_subject_name,
            "source_kind": AssignmentOfficialFormat.SourceKindChoices.TEACHER_ADAPTED,
            "is_preparation_only": True,
        },
    )
