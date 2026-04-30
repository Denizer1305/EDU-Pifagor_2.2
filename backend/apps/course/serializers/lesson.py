from __future__ import annotations

from rest_framework import serializers

from apps.course.models import CourseLesson, CourseMaterial, CourseModule


def _build_absolute_media_url(request, file_field) -> str:
    if not file_field:
        return ""

    try:
        url = file_field.url
    except Exception:
        return ""

    if request is not None:
        return request.build_absolute_uri(url)
    return url


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
        return _build_absolute_media_url(self.context.get("request"), obj.file)


class CourseMaterialDetailSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    course_id = serializers.IntegerField(source="course.id", read_only=True)
    lesson_id = serializers.IntegerField(source="lesson.id", read_only=True, allow_null=True)

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
        return _build_absolute_media_url(self.context.get("request"), obj.file)


class CourseMaterialCreateSerializer(serializers.Serializer):
    lesson = serializers.PrimaryKeyRelatedField(
        queryset=CourseLesson.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, default="")
    material_type = serializers.ChoiceField(
        choices=CourseMaterial.MaterialTypeChoices.choices,
        default=CourseMaterial.MaterialTypeChoices.FILE,
    )
    file = serializers.FileField(required=False, allow_null=True, default=None)
    external_url = serializers.URLField(required=False, allow_blank=True, default="")
    order = serializers.IntegerField(required=False, min_value=1)
    is_downloadable = serializers.BooleanField(default=True)
    is_visible = serializers.BooleanField(default=True)

    def validate_lesson(self, value):
        course = self.context.get("course")
        if value is not None and course is not None and value.course_id != course.id:
            raise serializers.ValidationError("Урок должен принадлежать выбранному курсу.")
        return value


class CourseMaterialUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    material_type = serializers.ChoiceField(
        choices=CourseMaterial.MaterialTypeChoices.choices,
        required=False,
    )
    file = serializers.FileField(required=False, allow_null=True)
    external_url = serializers.URLField(required=False, allow_blank=True)
    is_downloadable = serializers.BooleanField(required=False)
    is_visible = serializers.BooleanField(required=False)


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
    subtitle = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    description = serializers.CharField(required=False, allow_blank=True, default="")
    content = serializers.CharField(required=False, allow_blank=True, default="")
    lesson_type = serializers.ChoiceField(
        choices=CourseLesson.LessonTypeChoices.choices,
        default=CourseLesson.LessonTypeChoices.TEXT,
    )
    order = serializers.IntegerField(required=False, min_value=1)
    estimated_minutes = serializers.IntegerField(required=False, min_value=0, default=0)
    is_required = serializers.BooleanField(default=True)
    is_preview = serializers.BooleanField(default=False)
    is_published = serializers.BooleanField(default=True)
    available_from = serializers.DateTimeField(required=False, allow_null=True, default=None)
    video_url = serializers.URLField(required=False, allow_blank=True, default="")
    external_url = serializers.URLField(required=False, allow_blank=True, default="")

    def validate(self, attrs):
        lesson_type = attrs.get("lesson_type")
        if lesson_type == CourseLesson.LessonTypeChoices.VIDEO and not attrs.get("video_url"):
            raise serializers.ValidationError(
                {"video_url": "Для видеоурока необходимо указать ссылку на видео."}
            )

        if lesson_type in {
            CourseLesson.LessonTypeChoices.LINK,
            CourseLesson.LessonTypeChoices.WEBINAR,
        } and not attrs.get("external_url"):
            raise serializers.ValidationError(
                {"external_url": "Для этого типа урока необходимо указать внешнюю ссылку."}
            )

        return attrs


class CourseLessonUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False)
    subtitle = serializers.CharField(max_length=255, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    content = serializers.CharField(required=False, allow_blank=True)
    lesson_type = serializers.ChoiceField(
        choices=CourseLesson.LessonTypeChoices.choices,
        required=False,
    )
    estimated_minutes = serializers.IntegerField(required=False, min_value=0)
    is_required = serializers.BooleanField(required=False)
    is_preview = serializers.BooleanField(required=False)
    is_published = serializers.BooleanField(required=False)
    available_from = serializers.DateTimeField(required=False, allow_null=True)
    video_url = serializers.URLField(required=False, allow_blank=True)
    external_url = serializers.URLField(required=False, allow_blank=True)

    def validate(self, attrs):
        lesson = self.context.get("lesson")
        lesson_type = attrs.get("lesson_type", getattr(lesson, "lesson_type", None))
        video_url = attrs.get("video_url", getattr(lesson, "video_url", ""))
        external_url = attrs.get("external_url", getattr(lesson, "external_url", ""))

        if lesson_type == CourseLesson.LessonTypeChoices.VIDEO and not video_url:
            raise serializers.ValidationError(
                {"video_url": "Для видеоурока необходимо указать ссылку на видео."}
            )

        if lesson_type in {
            CourseLesson.LessonTypeChoices.LINK,
            CourseLesson.LessonTypeChoices.WEBINAR,
        } and not external_url:
            raise serializers.ValidationError(
                {"external_url": "Для этого типа урока необходимо указать внешнюю ссылку."}
            )

        return attrs


class CourseLessonMoveSerializer(serializers.Serializer):
    target_module = serializers.PrimaryKeyRelatedField(queryset=CourseModule.objects.all())
    new_order = serializers.IntegerField(required=False, min_value=1)


class CourseLessonReorderSerializer(serializers.Serializer):
    lesson_ids_in_order = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
    )

    def validate_lesson_ids_in_order(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Список уроков содержит дубликаты.")
        return value
