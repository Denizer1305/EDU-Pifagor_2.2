from __future__ import annotations

import django_filters
from django.db.models import Q

from apps.users.models import (
    ParentProfile,
    ParentStudent,
    Profile,
    Role,
    StudentProfile,
    TeacherProfile,
    User,
    UserRole,
)


def _has_model_field(model, field_name: str) -> bool:
    return field_name in {field.name for field in model._meta.get_fields()}


def _filter_exact_if_field_exists(queryset, model, field_name: str, value):
    if value in (None, ""):
        return queryset
    if not _has_model_field(model, field_name):
        return queryset
    return queryset.filter(**{field_name: value})


def _filter_gte_if_field_exists(queryset, model, field_name: str, value):
    if value in (None, ""):
        return queryset
    if not _has_model_field(model, field_name):
        return queryset
    return queryset.filter(**{f"{field_name}__gte": value})


def _filter_lte_if_field_exists(queryset, model, field_name: str, value):
    if value in (None, ""):
        return queryset
    if not _has_model_field(model, field_name):
        return queryset
    return queryset.filter(**{f"{field_name}__lte": value})


class UserFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_q")
    registration_type = django_filters.CharFilter(field_name="registration_type")
    onboarding_status = django_filters.CharFilter(field_name="onboarding_status")
    is_email_verified = django_filters.BooleanFilter(method="filter_is_email_verify")
    is_active = django_filters.BooleanFilter(field_name="is_active")
    is_staff = django_filters.BooleanFilter(field_name="is_staff")
    is_superuser = django_filters.BooleanFilter(field_name="is_superuser")

    created_at_from = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_at_to = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = User
        fields = (
            "registration_type",
            "onboarding_status",
            "is_active",
            "is_staff",
            "is_superuser",
        )

    def filter_q(self, queryset, name, value):
        value = (value or "").strip()
        if not value:
            return queryset

        return queryset.filter(
            Q(email__icontains=value)
            | Q(profile__last_name__icontains=value)
            | Q(profile__first_name__icontains=value)
            | Q(profile__patronymic__icontains=value)
        ).distinct()

    def filter_is_email_verify(self, queryset, name, value):
        return _filter_exact_if_field_exists(queryset, User, "is_email_verified", value)


class RoleFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_q")
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = Role
        fields = ("is_active",)

    def filter_q(self, queryset, name, value):
        value = (value or "").strip()
        if not value:
            return queryset

        return queryset.filter(
            Q(code__icontains=value)
            | Q(name__icontains=value)
            | Q(description__icontains=value)
        )


class UserRoleFilter(django_filters.FilterSet):
    user_id = django_filters.NumberFilter(field_name="user_id")
    role_id = django_filters.NumberFilter(field_name="role_id")
    role_code = django_filters.CharFilter(field_name="role__code", lookup_expr="iexact")
    assigned_at_from = django_filters.DateTimeFilter(field_name="assigned_at", lookup_expr="gte")
    assigned_at_to = django_filters.DateTimeFilter(field_name="assigned_at", lookup_expr="lte")

    class Meta:
        model = UserRole
        fields = (
            "user_id",
            "role_id",
            "role_code",
        )


class ProfileFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_q")
    gender = django_filters.CharFilter(field_name="gender")
    city = django_filters.CharFilter(field_name="city", lookup_expr="icontains")

    class Meta:
        model = Profile
        fields = (
            "gender",
            "city",
        )

    def filter_q(self, queryset, name, value):
        value = (value or "").strip()
        if not value:
            return queryset

        return queryset.filter(
            Q(user__email__icontains=value)
            | Q(last_name__icontains=value)
            | Q(first_name__icontains=value)
            | Q(patronymic__icontains=value)
            | Q(phone__icontains=value)
        ).distinct()


class TeacherProfileFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_q")
    verification_status = django_filters.CharFilter(field_name="verification_status")
    requested_organization_id = django_filters.NumberFilter(field_name="requested_organization_id")
    requested_department_id = django_filters.NumberFilter(field_name="requested_department_id")
    is_public_profile = django_filters.BooleanFilter(method="filter_is_public_profile")
    experience_years_min = django_filters.NumberFilter(method="filter_experience_years_min")
    experience_years_max = django_filters.NumberFilter(method="filter_experience_years_max")

    class Meta:
        model = TeacherProfile
        fields = (
            "verification_status",
            "requested_organization_id",
            "requested_department_id",
        )

    def filter_q(self, queryset, name, value):
        value = (value or "").strip()
        if not value:
            return queryset

        q_obj = (
            Q(user__email__icontains=value)
            | Q(user__profile__last_name__icontains=value)
            | Q(user__profile__first_name__icontains=value)
        )

        if _has_model_field(TeacherProfile, "position"):
            q_obj |= Q(position__icontains=value)

        if _has_model_field(TeacherProfile, "employee_code"):
            q_obj |= Q(employee_code__icontains=value)

        if _has_model_field(TeacherProfile, "specialization"):
            q_obj |= Q(specialization__icontains=value)

        if _has_model_field(TeacherProfile, "education"):
            q_obj |= Q(education__icontains=value)

        if _has_model_field(TeacherProfile, "education_info"):
            q_obj |= Q(education_info__icontains=value)

        return queryset.filter(q_obj).distinct()

    def filter_is_public_profile(self, queryset, name, value):
        return _filter_exact_if_field_exists(queryset, TeacherProfile, "is_public_profile", value)

    def filter_experience_years_min(self, queryset, name, value):
        return _filter_gte_if_field_exists(queryset, TeacherProfile, "experience_years", value)

    def filter_experience_years_max(self, queryset, name, value):
        return _filter_lte_if_field_exists(queryset, TeacherProfile, "experience_years", value)


class StudentProfileFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_q")
    verification_status = django_filters.CharFilter(field_name="verification_status")
    requested_organization_id = django_filters.NumberFilter(field_name="requested_organization_id")
    requested_department_id = django_filters.NumberFilter(field_name="requested_department_id")
    requested_group_id = django_filters.NumberFilter(field_name="requested_group_id")
    admission_year = django_filters.NumberFilter(method="filter_admission_year")
    graduation_year = django_filters.NumberFilter(method="filter_graduation_year")

    class Meta:
        model = StudentProfile
        fields = (
            "verification_status",
            "requested_organization_id",
            "requested_department_id",
            "requested_group_id",
        )

    def filter_q(self, queryset, name, value):
        value = (value or "").strip()
        if not value:
            return queryset

        q_obj = (
            Q(user__email__icontains=value)
            | Q(user__profile__last_name__icontains=value)
            | Q(user__profile__first_name__icontains=value)
        )

        if _has_model_field(StudentProfile, "student_code"):
            q_obj |= Q(student_code__icontains=value)

        if _has_model_field(StudentProfile, "submitted_group_code"):
            q_obj |= Q(submitted_group_code__icontains=value)

        return queryset.filter(q_obj).distinct()

    def filter_admission_year(self, queryset, name, value):
        return _filter_exact_if_field_exists(queryset, StudentProfile, "admission_year", value)

    def filter_graduation_year(self, queryset, name, value):
        return _filter_exact_if_field_exists(queryset, StudentProfile, "graduation_year", value)


class ParentProfileFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_q")

    class Meta:
        model = ParentProfile
        fields = ()

    def filter_q(self, queryset, name, value):
        value = (value or "").strip()
        if not value:
            return queryset

        q_obj = (
            Q(user__email__icontains=value)
            | Q(user__profile__last_name__icontains=value)
            | Q(user__profile__first_name__icontains=value)
            | Q(user__profile__patronymic__icontains=value)
        )

        if _has_model_field(ParentProfile, "work_place"):
            q_obj |= Q(work_place__icontains=value)

        return queryset.filter(q_obj).distinct()


class ParentStudentFilter(django_filters.FilterSet):
    parent_id = django_filters.NumberFilter(field_name="parent_id")
    student_id = django_filters.NumberFilter(field_name="student_id")
    relation_type = django_filters.CharFilter(field_name="relation_type")
    status = django_filters.CharFilter(field_name="status")
    is_primary = django_filters.BooleanFilter(method="filter_is_primary")

    class Meta:
        model = ParentStudent
        fields = (
            "parent_id",
            "student_id",
            "relation_type",
            "status",
        )

    def filter_is_primary(self, queryset, name, value):
        return _filter_exact_if_field_exists(queryset, ParentStudent, "is_primary", value)
