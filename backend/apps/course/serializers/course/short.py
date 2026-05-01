from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.education.models import AcademicYear, EducationPeriod, GroupSubject
from apps.organizations.models import Organization, Subject

User = get_user_model()


class UserShortSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "full_name")

    def get_full_name(self, obj):
        profile = getattr(obj, "profile", None)
        if profile is not None and getattr(profile, "full_name", ""):
            return profile.full_name

        first_name = getattr(profile, "first_name", "") if profile else ""
        last_name = getattr(profile, "last_name", "") if profile else ""
        patronymic = getattr(profile, "patronymic", "") if profile else ""

        parts = [last_name, first_name, patronymic]
        return " ".join(part for part in parts if part).strip() or obj.email


class OrganizationShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "short_name")


class SubjectShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ("id", "name", "short_name")


class AcademicYearShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ("id", "name", "start_date", "end_date")


class EducationPeriodShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationPeriod
        fields = ("id", "name", "code", "period_type", "sequence")


class GroupSubjectShortSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source="group.name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)

    class Meta:
        model = GroupSubject
        fields = (
            "id",
            "group_name",
            "subject_name",
            "academic_year_name",
        )
