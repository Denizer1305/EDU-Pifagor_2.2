from __future__ import annotations

from rest_framework import serializers

from apps.journal.models import TopicProgress


class TopicProgressListSerializer(serializers.ModelSerializer):
    """Краткое представление прогресса темы."""

    course_title = serializers.CharField(source="course.title", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    is_behind = serializers.BooleanField(read_only=True)

    class Meta:
        model = TopicProgress
        fields = (
            "id",
            "course",
            "course_title",
            "group",
            "group_name",
            "lesson",
            "lesson_title",
            "planned_date",
            "actual_date",
            "status",
            "days_behind",
            "is_behind",
        )


class TopicProgressDetailSerializer(serializers.ModelSerializer):
    """Детальное представление прогресса темы."""

    course_title = serializers.CharField(source="course.title", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    journal_lesson_date = serializers.DateField(
        source="journal_lesson.date",
        read_only=True,
    )
    is_behind = serializers.BooleanField(read_only=True)

    class Meta:
        model = TopicProgress
        fields = (
            "id",
            "course",
            "course_title",
            "group",
            "group_name",
            "lesson",
            "lesson_title",
            "journal_lesson",
            "journal_lesson_date",
            "planned_date",
            "actual_date",
            "status",
            "days_behind",
            "is_behind",
            "comment",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "days_behind",
            "is_behind",
            "created_at",
            "updated_at",
        )


class TopicProgressCreateSerializer(serializers.ModelSerializer):
    """Создание прогресса темы."""

    class Meta:
        model = TopicProgress
        fields = (
            "course",
            "group",
            "lesson",
            "journal_lesson",
            "planned_date",
            "actual_date",
            "status",
            "comment",
        )

    def validate(self, attrs: dict) -> dict:
        course = attrs.get("course")
        group = attrs.get("group")
        lesson = attrs.get("lesson")

        if course and group and lesson:
            exists = TopicProgress.objects.filter(
                course=course,
                group=group,
                lesson=lesson,
            ).exists()

            if exists:
                raise serializers.ValidationError(
                    {
                        "lesson": (
                            "Прогресс по этой теме для выбранного курса "
                            "и группы уже существует."
                        )
                    }
                )

        return attrs


class TopicProgressUpdateSerializer(serializers.ModelSerializer):
    """Обновление прогресса темы."""

    class Meta:
        model = TopicProgress
        fields = (
            "journal_lesson",
            "planned_date",
            "actual_date",
            "status",
            "comment",
        )
