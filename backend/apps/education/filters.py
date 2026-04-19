from __future__ import annotations

import django_filters

from apps.education.models import (
    AcademicYear,
    Curriculum,
    CurriculumItem,
    EducationPeriod,
    GroupSubject,
    StudentGroupEnrollment,
    TeacherGroupSubject,
)


class AcademicYearFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
    )
    is_current = django_filters.BooleanFilter(
        field_name="is_current",
    )
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
    )
    start_date = django_filters.DateFromToRangeFilter(
        field_name="start_date",
    )
    end_date = django_filters.DateFromToRangeFilter(
        field_name="end_date",
    )

    class Meta:
        model = AcademicYear
        fields = (
            "name", "is_current",
            "is_active", "start_date",
            "end_date",
        )


class EducationPeriodFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
    )
    code = django_filters.CharFilter(
        field_name="code",
        lookup_expr="icontains",
    )
    academic_year = django_filters.NumberFilter(
        field_name="academic_year_id",
    )
    period_type = django_filters.CharFilter(
        field_name="period_type",
    )
    sequence = django_filters.RangeFilter(
        field_name="sequence",
    )
    is_current = django_filters.BooleanFilter(
        field_name="is_current",
    )
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
    )

    class Meta:
        model = EducationPeriod
        fields = (
            "name", "code",
            "academic_year", "period_type",
            "sequence", "is_current",
            "is_active",
        )


class StudentGroupEnrollmentFilter(django_filters.FilterSet):
    student = django_filters.NumberFilter(
        field_name="student_id",
    )
    group = django_filters.NumberFilter(
        field_name="group_id",
    )
    academic_year = django_filters.NumberFilter(
        field_name="academic_year_id",
    )
    status = django_filters.CharFilter(
        field_name="status",
    )
    is_primary = django_filters.BooleanFilter(
        field_name="is_primary",
    )
    enrollment_date = django_filters.DateFromToRangeFilter(
        field_name="enrollment_date",
    )
    completion_date = django_filters.DateFromToRangeFilter(
        field_name="completion_date",
    )
    journal_number = django_filters.RangeFilter(
        field_name="journal_number",
    )

    class Meta:
        model = StudentGroupEnrollment
        fields = (
            "student", "group",
            "academic_year", "status",
            "is_primary", "enrollment_date",
            "completion_date", "journal_number",
        )


class GroupSubjectFilter(django_filters.FilterSet):
    group = django_filters.NumberFilter(
        field_name="group_id",
    )
    subject = django_filters.NumberFilter(
        field_name="subject_id",
    )
    academic_year = django_filters.NumberFilter(
        field_name="academic_year_id",
    )
    period = django_filters.NumberFilter(
        field_name="period_id",
    )
    assessment_type = django_filters.CharFilter(
        field_name="assessment_type",
    )
    is_required = django_filters.BooleanFilter(
        field_name="is_required",
    )
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
    )
    planned_hours = django_filters.RangeFilter(
        field_name="planned_hours",
    )
    contact_hours = django_filters.RangeFilter(
        field_name="contact_hours",
    )
    independent_hours = django_filters.RangeFilter(
        field_name="independent_hours",
    )

    class Meta:
        model = GroupSubject
        fields = (
            "group", "subject",
            "academic_year", "period",
            "assessment_type", "is_required",
            "is_active", "planned_hours",
            "contact_hours", "independent_hours",
        )


class TeacherGroupSubjectFilter(django_filters.FilterSet):
    teacher = django_filters.NumberFilter(
        field_name="teacher_id",
    )
    group_subject = django_filters.NumberFilter(
        field_name="group_subject_id",
    )
    role = django_filters.CharFilter(
        field_name="role",
    )
    is_primary = django_filters.BooleanFilter(
        field_name="is_primary",
    )
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
    )
    starts_at = django_filters.DateFromToRangeFilter(
        field_name="starts_at",
    )
    ends_at = django_filters.DateFromToRangeFilter(
        field_name="ends_at",
    )
    planned_hours = django_filters.RangeFilter(
        field_name="planned_hours",
    )

    class Meta:
        model = TeacherGroupSubject
        fields = (
            "teacher", "group_subject",
            "role", "is_primary",
            "is_active", "starts_at",
            "ends_at", "planned_hours",
        )


class CurriculumFilter(django_filters.FilterSet):
    organization = django_filters.NumberFilter(
        field_name="organization_id",
    )
    department = django_filters.NumberFilter(
        field_name="department_id",
    )
    academic_year = django_filters.NumberFilter(
        field_name="academic_year_id",
    )
    code = django_filters.CharFilter(
        field_name="code",
        lookup_expr="icontains",
    )
    name = django_filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
    )
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
    )
    total_hours = django_filters.RangeFilter(
        field_name="total_hours",
    )

    class Meta:
        model = Curriculum
        fields = (
            "organization", "department",
            "academic_year", "code",
            "name", "is_active",
            "total_hours",
        )


class CurriculumItemFilter(django_filters.FilterSet):
    curriculum = django_filters.NumberFilter(
        field_name="curriculum_id",
    )
    period = django_filters.NumberFilter(
        field_name="period_id",
    )
    subject = django_filters.NumberFilter(
        field_name="subject_id",
    )
    assessment_type = django_filters.CharFilter(
        field_name="assessment_type",
    )
    is_required = django_filters.BooleanFilter(
        field_name="is_required",
    )
    is_active = django_filters.BooleanFilter(
        field_name="is_active",
    )
    sequence = django_filters.RangeFilter(
        field_name="sequence",
    )
    planned_hours = django_filters.RangeFilter(
        field_name="planned_hours",
    )
    contact_hours = django_filters.RangeFilter(
        field_name="contact_hours",
    )
    independent_hours = django_filters.RangeFilter(
        field_name="independent_hours",
    )

    class Meta:
        model = CurriculumItem
        fields = (
            "curriculum", "period",
            "subject", "assessment_type",
            "is_required", "is_active",
            "sequence", "planned_hours",
            "contact_hours", "independent_hours",
        )
