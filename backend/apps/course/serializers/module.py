from __future__ import annotations

from rest_framework import serializers

from apps.course.models import CourseModule


class CourseModuleListSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = CourseModule
        fields = (
            "id",
            "title",
            "description",
            "order",
            "is_required",
            "is_published",
            "estimated_minutes",
            "lessons_count",
            "created_at",
            "updated_at",
        )

    def get_lessons_count(self, obj):
        return obj.lessons.count()


class CourseModuleDetailSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = CourseModule
        fields = (
            "id",
            "title",
            "description",
            "order",
            "is_required",
            "is_published",
            "estimated_minutes",
            "lessons",
            "created_at",
            "updated_at",
        )

    def get_lessons(self, obj):
        from apps.course.serializers.lesson import CourseLessonListSerializer

        queryset = obj.lessons.order_by("order", "id")
        if self.context.get("public_only"):
            queryset = queryset.filter(is_published=True)

        return CourseLessonListSerializer(
            queryset,
            many=True,
            context=self.context,
        ).data


class CourseModuleCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    order = serializers.IntegerField(required=False, min_value=1)
    is_required = serializers.BooleanField(default=True)
    is_published = serializers.BooleanField(default=True)


class CourseModuleUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    is_required = serializers.BooleanField(required=False)
    is_published = serializers.BooleanField(required=False)


class CourseModuleReorderSerializer(serializers.Serializer):
    module_ids_in_order = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
    )

    def validate_module_ids_in_order(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Список модулей содержит дубликаты.")
        return value
