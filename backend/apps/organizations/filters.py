from __future__ import annotations

import django_filters
from django.db.models import Q
from django.utils import timezone

from apps.organizations.models import (
    Department,
    Group,
    GroupCurator,
    Organization,
    OrganizationType,
    Subject,
    SubjectCategory,
    TeacherOrganization,
    TeacherSubject,
)


class OrganizationTypeFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(field_name="code", lookup_expr="icontains")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = OrganizationType
        fields = (
            "code", "name",
            "is_active",
        )


class OrganizationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    short_name = django_filters.CharFilter(field_name="short_name", lookup_expr="icontains")
    city = django_filters.CharFilter(field_name="city", lookup_expr="icontains")
    is_active = django_filters.BooleanFilter(field_name="is_active")
    type = django_filters.NumberFilter(field_name="type_id")
    created_at = django_filters.DateFromToRangeFilter(field_name="created_at")

    teacher_registration_code_is_active = django_filters.BooleanFilter(
        method="filter_teacher_registration_code_is_active",
    )

    class Meta:
        model = Organization
        fields = (
            "name", "short_name",
            "city", "is_active",
            "type", "created_at",
            "teacher_registration_code_is_active",
        )

    def filter_teacher_registration_code_is_active(self, queryset, name, value):
        active_queryset = queryset.filter(
            teacher_registration_code_hash__gt="",
            teacher_registration_code_is_active=True,
        ).filter(
            Q(teacher_registration_code_expires_at__isnull=True)
            | Q(teacher_registration_code_expires_at__gt=timezone.now())
        )

        if value is True:
            return active_queryset

        if value is False:
            return queryset.exclude(pk__in=active_queryset.values_list("pk", flat=True))

        return queryset


class DepartmentFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    short_name = django_filters.CharFilter(field_name="short_name", lookup_expr="icontains")
    organization = django_filters.NumberFilter(field_name="organization_id")
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = Department
        fields = (
            "name", "short_name",
            "organization", "is_active",
        )


class SubjectCategoryFilter(django_filters.FilterSet):
    code = django_filters.CharFilter(field_name="code", lookup_expr="icontains")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = SubjectCategory
        fields = (
            "code", "name",
            "is_active",
        )


class SubjectFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    short_name = django_filters.CharFilter(field_name="short_name", lookup_expr="icontains")
    category = django_filters.NumberFilter(field_name="category_id")
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = Subject
        fields = (
            "name", "short_name",
            "category", "is_active",
        )


class GroupFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    code = django_filters.CharFilter(field_name="code", lookup_expr="icontains")
    organization = django_filters.NumberFilter(field_name="organization_id")
    department = django_filters.NumberFilter(field_name="department_id")
    study_form = django_filters.CharFilter(field_name="study_form")
    status = django_filters.CharFilter(field_name="status")
    is_active = django_filters.BooleanFilter(field_name="is_active")
    course_number = django_filters.RangeFilter(field_name="course_number")
    admission_year = django_filters.RangeFilter(field_name="admission_year")
    graduation_year = django_filters.RangeFilter(field_name="graduation_year")
    academic_year = django_filters.CharFilter(field_name="academic_year", lookup_expr="icontains")
    created_at = django_filters.DateFromToRangeFilter(field_name="created_at")

    join_code_is_active = django_filters.BooleanFilter(
        method="filter_join_code_is_active",
    )

    class Meta:
        model = Group
        fields = (
            "name", "code",
            "organization", "department",
            "study_form", "status",
            "is_active", "course_number",
            "admission_year", "graduation_year",
            "academic_year", "created_at",
            "join_code_is_active",
        )

    def filter_join_code_is_active(self, queryset, name, value):
        active_queryset = queryset.filter(
            join_code_hash__gt="",
            join_code_is_active=True,
        ).filter(
            Q(join_code_expires_at__isnull=True)
            | Q(join_code_expires_at__gt=timezone.now())
        )

        if value is True:
            return active_queryset

        if value is False:
            return queryset.exclude(pk__in=active_queryset.values_list("pk", flat=True))

        return queryset


class GroupCuratorFilter(django_filters.FilterSet):
    group = django_filters.NumberFilter(field_name="group_id")
    teacher = django_filters.NumberFilter(field_name="teacher_id")
    is_primary = django_filters.BooleanFilter(field_name="is_primary")
    is_active = django_filters.BooleanFilter(field_name="is_active")
    starts_at = django_filters.DateFromToRangeFilter(field_name="starts_at")
    ends_at = django_filters.DateFromToRangeFilter(field_name="ends_at")
    current_only = django_filters.BooleanFilter(method="filter_current_only")

    class Meta:
        model = GroupCurator
        fields = (
            "group", "teacher",
            "is_primary", "is_active",
            "starts_at", "ends_at",
            "current_only",
        )

    def filter_current_only(self, queryset, name, value):
        if value is not True:
            return queryset

        today = timezone.localdate()
        return queryset.filter(
            is_active=True,
        ).filter(
            Q(starts_at__isnull=True) | Q(starts_at__lte=today),
            Q(ends_at__isnull=True) | Q(ends_at__gte=today),
        )


class TeacherOrganizationFilter(django_filters.FilterSet):
    teacher = django_filters.NumberFilter(field_name="teacher_id")
    organization = django_filters.NumberFilter(field_name="organization_id")
    position = django_filters.CharFilter(field_name="position", lookup_expr="icontains")
    employment_type = django_filters.CharFilter(field_name="employment_type")
    is_primary = django_filters.BooleanFilter(field_name="is_primary")
    is_active = django_filters.BooleanFilter(field_name="is_active")
    starts_at = django_filters.DateFromToRangeFilter(field_name="starts_at")
    ends_at = django_filters.DateFromToRangeFilter(field_name="ends_at")
    current_only = django_filters.BooleanFilter(method="filter_current_only")

    class Meta:
        model = TeacherOrganization
        fields = (
            "teacher", "organization",
            "position", "employment_type",
            "is_primary", "is_active",
            "starts_at", "ends_at",
            "current_only",
        )

    def filter_current_only(self, queryset, name, value):
        if value is not True:
            return queryset

        today = timezone.localdate()
        return queryset.filter(
            is_active=True,
        ).filter(
            Q(starts_at__isnull=True) | Q(starts_at__lte=today),
            Q(ends_at__isnull=True) | Q(ends_at__gte=today),
        )


class TeacherSubjectFilter(django_filters.FilterSet):
    teacher = django_filters.NumberFilter(field_name="teacher_id")
    subject = django_filters.NumberFilter(field_name="subject_id")
    subject_category = django_filters.NumberFilter(field_name="subject__category_id")
    is_primary = django_filters.BooleanFilter(field_name="is_primary")
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = TeacherSubject
        fields = (
            "teacher", "subject",
            "subject_category", "is_primary",
            "is_active",
        )
