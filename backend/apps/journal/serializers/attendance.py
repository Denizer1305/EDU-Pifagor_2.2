from __future__ import annotations

from rest_framework import serializers

from apps.journal.models import AttendanceRecord


class AttendanceRecordListSerializer(serializers.ModelSerializer):
    """Краткое представление посещаемости."""

    lesson_date = serializers.DateField(source="lesson.date", read_only=True)
    lesson_topic = serializers.CharField(source="lesson.topic", read_only=True)
    student_email = serializers.EmailField(source="student.email", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = (
            "id",
            "lesson",
            "lesson_date",
            "lesson_topic",
            "student",
            "student_email",
            "status",
            "comment",
            "created_at",
        )


class AttendanceRecordDetailSerializer(serializers.ModelSerializer):
    """Детальное представление посещаемости."""

    lesson_date = serializers.DateField(source="lesson.date", read_only=True)
    lesson_topic = serializers.CharField(source="lesson.topic", read_only=True)
    course = serializers.PrimaryKeyRelatedField(source="lesson.course", read_only=True)
    group = serializers.PrimaryKeyRelatedField(source="lesson.group", read_only=True)
    student_email = serializers.EmailField(source="student.email", read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = (
            "id",
            "lesson",
            "lesson_date",
            "lesson_topic",
            "course",
            "group",
            "student",
            "student_email",
            "status",
            "comment",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class AttendanceRecordCreateSerializer(serializers.ModelSerializer):
    """Создание записи посещаемости."""

    class Meta:
        model = AttendanceRecord
        fields = (
            "lesson",
            "student",
            "status",
            "comment",
        )

    def validate(self, attrs: dict) -> dict:
        lesson = attrs.get("lesson")
        student = attrs.get("student")

        if lesson and student:
            exists = AttendanceRecord.objects.filter(
                lesson=lesson,
                student=student,
            ).exists()

            if exists:
                raise serializers.ValidationError(
                    {
                        "student": (
                            "Запись посещаемости для этого студента "
                            "на данном занятии уже существует."
                        )
                    }
                )

        return attrs


class AttendanceRecordUpdateSerializer(serializers.ModelSerializer):
    """Обновление записи посещаемости."""

    class Meta:
        model = AttendanceRecord
        fields = (
            "status",
            "comment",
        )
