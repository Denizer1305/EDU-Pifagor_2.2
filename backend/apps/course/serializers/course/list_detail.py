from __future__ import annotations

from rest_framework import serializers

from apps.course.models import Course
from apps.course.serializers.course.common import build_absolute_media_url
from apps.course.serializers.course.short import (
    AcademicYearShortSerializer,
    EducationPeriodShortSerializer,
    GroupSubjectShortSerializer,
    OrganizationShortSerializer,
    SubjectShortSerializer,
    UserShortSerializer,
)
from apps.course.serializers.course.teachers import CourseTeacherSerializer


class CourseListSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)
    organization = OrganizationShortSerializer(read_only=True)
    subject = SubjectShortSerializer(read_only=True)
    academic_year = AcademicYearShortSerializer(read_only=True)
    period = EducationPeriodShortSerializer(read_only=True)
    cover_image_url = serializers.SerializerMethodField()
    teachers_count = serializers.SerializerMethodField()
    modules_count = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "uid",
            "code",
            "slug",
            "title",
            "subtitle",
            "course_type",
            "origin",
            "status",
            "visibility",
            "level",
            "language",
            "author",
            "organization",
            "subject",
            "academic_year",
            "period",
            "cover_image_url",
            "is_template",
            "is_active",
            "allow_self_enrollment",
            "estimated_minutes",
            "starts_at",
            "ends_at",
            "published_at",
            "teachers_count",
            "modules_count",
            "lessons_count",
            "created_at",
            "updated_at",
        )

    def get_cover_image_url(self, obj):
        return build_absolute_media_url(
            self.context.get("request"),
            obj.cover_image,
        )

    def get_teachers_count(self, obj):
        return obj.course_teachers.filter(is_active=True).count()

    def get_modules_count(self, obj):
        return obj.modules.count()

    def get_lessons_count(self, obj):
        return obj.lessons.count()


class CourseDetailSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)
    organization = OrganizationShortSerializer(read_only=True)
    subject = SubjectShortSerializer(read_only=True)
    academic_year = AcademicYearShortSerializer(read_only=True)
    period = EducationPeriodShortSerializer(read_only=True)
    group_subject = GroupSubjectShortSerializer(read_only=True)
    cover_image_url = serializers.SerializerMethodField()
    teachers = serializers.SerializerMethodField()
    modules = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "uid",
            "code",
            "slug",
            "title",
            "subtitle",
            "description",
            "course_type",
            "origin",
            "status",
            "visibility",
            "level",
            "language",
            "author",
            "organization",
            "subject",
            "academic_year",
            "period",
            "group_subject",
            "cover_image_url",
            "is_template",
            "is_active",
            "allow_self_enrollment",
            "enrollment_code",
            "estimated_minutes",
            "starts_at",
            "ends_at",
            "published_at",
            "archived_at",
            "teachers",
            "modules",
            "materials",
            "created_at",
            "updated_at",
        )

    def get_cover_image_url(self, obj):
        return build_absolute_media_url(
            self.context.get("request"),
            obj.cover_image,
        )

    def get_teachers(self, obj):
        queryset = obj.course_teachers.select_related("teacher").order_by("created_at", "id")
        return CourseTeacherSerializer(
            queryset,
            many=True,
            context=self.context,
        ).data

    def get_modules(self, obj):
        from apps.course.serializers.module import CourseModuleDetailSerializer

        queryset = obj.modules.order_by("order", "id")
        return CourseModuleDetailSerializer(
            queryset,
            many=True,
            context=self.context,
        ).data

    def get_materials(self, obj):
        from apps.course.serializers.lesson import CourseMaterialListSerializer

        queryset = obj.materials.filter(lesson__isnull=True).order_by("order", "id")
        return CourseMaterialListSerializer(
            queryset,
            many=True,
            context=self.context,
        ).data
