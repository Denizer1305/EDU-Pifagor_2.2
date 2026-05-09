from __future__ import annotations

from rest_framework import serializers

from apps.course.models import Course
from apps.course.serializers.course.common import build_absolute_media_url
from apps.course.serializers.course.short import (
    OrganizationShortSerializer,
    SubjectShortSerializer,
)


class CoursePublicListSerializer(serializers.ModelSerializer):
    organization = OrganizationShortSerializer(read_only=True)
    subject = SubjectShortSerializer(read_only=True)
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "code",
            "slug",
            "title",
            "subtitle",
            "course_type",
            "level",
            "organization",
            "subject",
            "cover_image_url",
            "estimated_minutes",
            "starts_at",
            "ends_at",
            "published_at",
        )

    def get_cover_image_url(self, obj):
        return build_absolute_media_url(
            self.context.get("request"),
            obj.cover_image,
        )


class CoursePublicDetailSerializer(serializers.ModelSerializer):
    organization = OrganizationShortSerializer(read_only=True)
    subject = SubjectShortSerializer(read_only=True)
    cover_image_url = serializers.SerializerMethodField()
    modules = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "code",
            "slug",
            "title",
            "subtitle",
            "description",
            "course_type",
            "level",
            "organization",
            "subject",
            "cover_image_url",
            "estimated_minutes",
            "starts_at",
            "ends_at",
            "published_at",
            "modules",
            "materials",
        )

    def get_cover_image_url(self, obj):
        return build_absolute_media_url(
            self.context.get("request"),
            obj.cover_image,
        )

    def get_modules(self, obj):
        from apps.course.serializers.module import CourseModuleDetailSerializer

        queryset = obj.modules.filter(is_published=True).order_by("order", "id")
        return CourseModuleDetailSerializer(
            queryset,
            many=True,
            context={**self.context, "public_only": True},
        ).data

    def get_materials(self, obj):
        from apps.course.serializers.lesson import CourseMaterialListSerializer

        queryset = obj.materials.filter(
            lesson__isnull=True,
            is_visible=True,
        ).order_by("order", "id")
        return CourseMaterialListSerializer(
            queryset,
            many=True,
            context=self.context,
        ).data
