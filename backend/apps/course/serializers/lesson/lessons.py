from __future__ import annotations

from rest_framework import serializers

from apps.course.models import CourseLesson, CourseModule
from apps.course.serializers.lesson.materials import CourseMaterialListSerializer


class CourseLessonListSerializer(serializers.ModelSerializer):
    materials_count = serializers.SerializerMethodField()

    class Meta:
        model = CourseLesson
        fields = (
            "id",
            "title",
            "subtitle",
            "description",
            "lesson_type",
            "order",
            "estimated_minutes",
            "is_required",
            "is_preview",
            "is_published",
            "available_from",
            "video_url",
            "external_url",
            "materials_count",
            "created_at",
            "updated_at",
        )

    def get_materials_count(self, obj):
        return obj.materials.count()


class CourseLessonDetailSerializer(serializers.ModelSerializer):
    materials = serializers.SerializerMethodField()
    module_id = serializers.IntegerField(source="module.id", read_only=True)
    course_id = serializers.IntegerField(source="course.id", read_only=True)

    class Meta:
        model = CourseLesson
        fields = (
            "id",
            "course_id",
            "module_id",
            "title",
            "subtitle",
            "description",
            "content",
            "lesson_type",
            "order",
            "estimated_minutes",
            "is_required",
            "is_preview",
            "is_published",
            "available_from",
            "video_url",
            "external_url",
            "materials",
            "created_at",
            "updated_at",
        )

    def get_materials(self, obj):
        queryset = obj.materials.order_by("order", "id")
        if self.context.get("public_only"):
            queryset = queryset.filter(is_visible=True)

        return CourseMaterialListSerializer(
            queryset,
            many=True,
            context=self.context,
        ).data


class CourseLessonCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    subtitle = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default="",
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )
    content = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
    )
    lesson_type = serializers.ChoiceField(
        choices=CourseLesson.LessonTypeChoices.choices,
        default=CourseLesson.LessonTypeChoices.TEXT,
    )
    order = serializers.IntegerField(
        required=False,
        min_value=1,
    )
    estimated_minutes = serializers.IntegerField(
        required=False,
        min_value=0,
        default=0,
    )
    is_required = serializers.BooleanField(default=True)
    is_preview = serializers.BooleanField(default=False)
    is_published = serializers.BooleanField(default=True)
    available_from = serializers.DateTimeField(
        required=False,
        allow_null=True,
        default=None,
    )
    video_url = serializers.URLField(
        required=False,
        allow_blank=True,
        default="",
    )
    external_url = serializers.URLField(
        required=False,
        allow_blank=True,
        default="",
    )

    def validate(self, attrs):
        lesson_type = attrs.get("lesson_type")

        if lesson_type == CourseLesson.LessonTypeChoices.VIDEO and not attrs.get("video_url"):
            raise serializers.ValidationError(
                {"video_url": "Для видеоурока необходимо указать ссылку на видео."}
            )

        if (
            lesson_type
            in {
                CourseLesson.LessonTypeChoices.LINK,
                CourseLesson.LessonTypeChoices.WEBINAR,
            }
            and not attrs.get("external_url")
        ):
            raise serializers.ValidationError(
                {"external_url": "Для этого типа урока необходимо указать внешнюю ссылку."}
            )

        return attrs


class CourseLessonUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(
        max_length=255,
        required=False,
    )
    subtitle = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    content = serializers.CharField(
        required=False,
        allow_blank=True,
    )
    lesson_type = serializers.ChoiceField(
        choices=CourseLesson.LessonTypeChoices.choices,
        required=False,
    )
    estimated_minutes = serializers.IntegerField(
        required=False,
        min_value=0,
    )
    is_required = serializers.BooleanField(required=False)
    is_preview = serializers.BooleanField(required=False)
    is_published = serializers.BooleanField(required=False)
    available_from = serializers.DateTimeField(
        required=False,
        allow_null=True,
    )
    video_url = serializers.URLField(
        required=False,
        allow_blank=True,
    )
    external_url = serializers.URLField(
        required=False,
        allow_blank=True,
    )

    def validate(self, attrs):
        lesson = self.context.get("lesson")

        lesson_type = attrs.get(
            "lesson_type",
            getattr(lesson, "lesson_type", None),
        )
        video_url = attrs.get(
            "video_url",
            getattr(lesson, "video_url", ""),
        )
        external_url = attrs.get(
            "external_url",
            getattr(lesson, "external_url", ""),
        )

        if lesson_type == CourseLesson.LessonTypeChoices.VIDEO and not video_url:
            raise serializers.ValidationError(
                {"video_url": "Для видеоурока необходимо указать ссылку на видео."}
            )

        if (
            lesson_type
            in {
                CourseLesson.LessonTypeChoices.LINK,
                CourseLesson.LessonTypeChoices.WEBINAR,
            }
            and not external_url
        ):
            raise serializers.ValidationError(
                {"external_url": "Для этого типа урока необходимо указать внешнюю ссылку."}
            )

        return attrs


class CourseLessonMoveSerializer(serializers.Serializer):
    target_module = serializers.PrimaryKeyRelatedField(
        queryset=CourseModule.objects.all(),
    )
    new_order = serializers.IntegerField(
        required=False,
        min_value=1,
    )


class CourseLessonReorderSerializer(serializers.Serializer):
    lesson_ids_in_order = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
    )

    def validate_lesson_ids_in_order(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Список уроков содержит дубликаты.")

        return value
