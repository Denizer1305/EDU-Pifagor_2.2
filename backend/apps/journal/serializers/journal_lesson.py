from __future__ import annotations

from rest_framework import serializers

from apps.journal.models import AttendanceRecord, JournalGrade, JournalLesson
from apps.journal.serializers.attendance import AttendanceRecordListSerializer
from apps.journal.serializers.grade import JournalGradeListSerializer


class JournalLessonListSerializer(serializers.ModelSerializer):
    """Краткое представление занятия журнала."""

    course_title = serializers.CharField(source="course.title", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)
    teacher_email = serializers.EmailField(source="teacher.email", read_only=True)
    topic = serializers.CharField(read_only=True)

    class Meta:
        model = JournalLesson
        fields = (
            "id",
            "date",
            "lesson_number",
            "course",
            "course_title",
            "group",
            "group_name",
            "teacher",
            "teacher_email",
            "status",
            "topic",
            "planned_topic",
            "actual_topic",
            "homework",
            "created_at",
        )


class JournalLessonDetailSerializer(serializers.ModelSerializer):
    """Детальное представление занятия журнала."""

    course_title = serializers.CharField(source="course.title", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)
    teacher_email = serializers.EmailField(source="teacher.email", read_only=True)
    course_lesson_title = serializers.CharField(
        source="course_lesson.title",
        read_only=True,
    )
    topic = serializers.CharField(read_only=True)
    attendance = serializers.SerializerMethodField()
    grades = serializers.SerializerMethodField()

    class Meta:
        model = JournalLesson
        fields = (
            "id",
            "course",
            "course_title",
            "group",
            "group_name",
            "teacher",
            "teacher_email",
            "course_lesson",
            "course_lesson_title",
            "date",
            "started_at",
            "ended_at",
            "lesson_number",
            "planned_topic",
            "actual_topic",
            "topic",
            "homework",
            "status",
            "teacher_comment",
            "attendance",
            "grades",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "topic",
            "attendance",
            "grades",
            "created_at",
            "updated_at",
        )

    def get_attendance(self, obj: JournalLesson) -> list[dict]:
        queryset = AttendanceRecord.objects.select_related(
            "student",
            "lesson",
        ).filter(lesson=obj)

        return AttendanceRecordListSerializer(queryset, many=True).data

    def get_grades(self, obj: JournalLesson) -> list[dict]:
        queryset = JournalGrade.objects.select_related(
            "student",
            "graded_by",
            "lesson",
        ).filter(lesson=obj)

        return JournalGradeListSerializer(queryset, many=True).data


class JournalLessonCreateSerializer(serializers.ModelSerializer):
    """Создание занятия журнала."""

    class Meta:
        model = JournalLesson
        fields = (
            "course",
            "group",
            "teacher",
            "course_lesson",
            "date",
            "started_at",
            "ended_at",
            "lesson_number",
            "planned_topic",
            "actual_topic",
            "homework",
            "status",
            "teacher_comment",
        )

    def validate(self, attrs: dict) -> dict:
        course = attrs.get("course")
        group = attrs.get("group")
        lesson_date = attrs.get("date")
        lesson_number = attrs.get("lesson_number")

        if course and group and lesson_date and lesson_number is not None:
            exists = JournalLesson.objects.filter(
                course=course,
                group=group,
                date=lesson_date,
                lesson_number=lesson_number,
            ).exists()

            if exists:
                raise serializers.ValidationError(
                    {
                        "lesson_number": (
                            "Занятие с таким курсом, группой, датой "
                            "и номером пары уже существует."
                        )
                    }
                )

        started_at = attrs.get("started_at")
        ended_at = attrs.get("ended_at")

        if started_at and ended_at and ended_at <= started_at:
            raise serializers.ValidationError(
                {"ended_at": "Время окончания должно быть позже времени начала."}
            )

        return attrs


class JournalLessonUpdateSerializer(serializers.ModelSerializer):
    """Обновление занятия журнала."""

    class Meta:
        model = JournalLesson
        fields = (
            "teacher",
            "course_lesson",
            "date",
            "started_at",
            "ended_at",
            "lesson_number",
            "planned_topic",
            "actual_topic",
            "homework",
            "status",
            "teacher_comment",
        )

    def validate(self, attrs: dict) -> dict:
        instance = self.instance

        started_at = attrs.get(
            "started_at",
            instance.started_at if instance else None,
        )
        ended_at = attrs.get(
            "ended_at",
            instance.ended_at if instance else None,
        )

        if started_at and ended_at and ended_at <= started_at:
            raise serializers.ValidationError(
                {"ended_at": "Время окончания должно быть позже времени начала."}
            )

        return attrs
