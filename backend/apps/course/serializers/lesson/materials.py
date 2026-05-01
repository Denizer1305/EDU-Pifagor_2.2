from __future__ import annotations

from rest_framework import serializers

from apps.course.models import CourseLesson, CourseMaterial
from apps.course.serializers.lesson.common import build_absolute_media_url


class CourseMaterialListSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = CourseMaterial
        fields = (
            "id",
            "title",
            "description",
            "material_type",
            "file_url",
            "external_url",
            "order",
            "is_downloadable",
            "is_visible",
            "created_at",
            "updated_at",
        )

    def get_file_url(self, obj):
        return build_absolute_media_url(
            self.context.get("request"),
            obj.file,
        )


class CourseMaterialDetailSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    course_id = serializers.IntegerField(source="course.id", read_only=True)
    lesson_id = serializers.IntegerField(
        source="lesson.id",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = CourseMaterial
        fields = (
            "id",
            "course_id",
            "lesson_id",
            "title",
            "description",
            "material_type",
            "file_url",
            "external_url",
            "order",
            "is_downloadable",
            "is_visible",
            "created_at",
            "updated_at",
        )

    def get_file_url(self, obj):
        return build_absolute_media_url(
            self.context.get("request"),
            obj.file,
        )


class CourseMaterialCreateSerializer(serializers.Serializer):
    lesson = serializers.PrimaryKeyRelatedField(
        queryset=CourseLesson.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )
    material_type = serializers.ChoiceField(
        choices=CourseMaterial.MaterialTypeChoices.choices,
        default=CourseMaterial.MaterialTypeChoices.FILE,
    )
    file = serializers.FileField(
        required=False,
        allow_null=True,
        default=None,
    )
    external_url = serializers.URLField(
        required=False,
        allow_blank=True,
        default="",
    )
    order = serializers.IntegerField(
        required=False,
        min_value=1,
    )
    is_downloadable = serializers.BooleanField(default=True)
    is_visible = serializers.BooleanField(default=True)

    def validate_lesson(self, value):
        course = self.context.get("course")
        if value is not None and course is not None and value.course_id != course.id:
            raise serializers.ValidationError(
                "Урок должен принадлежать выбранному курсу."
            )

        return value


class CourseMaterialUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(
        max_length=255,
        required=False,
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    material_type = serializers.ChoiceField(
        choices=CourseMaterial.MaterialTypeChoices.choices,
        required=False,
    )
    file = serializers.FileField(
        required=False,
        allow_null=True,
    )
    external_url = serializers.URLField(
        required=False,
        allow_blank=True,
    )
    is_downloadable = serializers.BooleanField(required=False)
    is_visible = serializers.BooleanField(required=False)
