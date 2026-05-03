from __future__ import annotations

from rest_framework import serializers

from apps.journal.models import JournalGrade
from apps.journal.models.choices import GradeScale, GradeType


class JournalGradeListSerializer(serializers.ModelSerializer):
    """Краткое представление оценки журнала."""

    lesson_date = serializers.DateField(source="lesson.date", read_only=True)
    lesson_topic = serializers.CharField(source="lesson.topic", read_only=True)
    student_email = serializers.EmailField(source="student.email", read_only=True)
    graded_by_email = serializers.EmailField(source="graded_by.email", read_only=True)
    display_value = serializers.CharField(read_only=True)

    class Meta:
        model = JournalGrade
        fields = (
            "id",
            "lesson",
            "lesson_date",
            "lesson_topic",
            "student",
            "student_email",
            "grade_type",
            "scale",
            "score_five",
            "is_passed",
            "display_value",
            "weight",
            "is_auto",
            "graded_by",
            "graded_by_email",
            "created_at",
        )


class JournalGradeDetailSerializer(serializers.ModelSerializer):
    """Детальное представление оценки журнала."""

    lesson_date = serializers.DateField(source="lesson.date", read_only=True)
    lesson_topic = serializers.CharField(source="lesson.topic", read_only=True)
    course = serializers.PrimaryKeyRelatedField(source="lesson.course", read_only=True)
    group = serializers.PrimaryKeyRelatedField(source="lesson.group", read_only=True)
    student_email = serializers.EmailField(source="student.email", read_only=True)
    graded_by_email = serializers.EmailField(source="graded_by.email", read_only=True)
    display_value = serializers.CharField(read_only=True)

    class Meta:
        model = JournalGrade
        fields = (
            "id",
            "lesson",
            "lesson_date",
            "lesson_topic",
            "course",
            "group",
            "student",
            "student_email",
            "grade_type",
            "scale",
            "score_five",
            "is_passed",
            "display_value",
            "weight",
            "comment",
            "is_auto",
            "graded_by",
            "graded_by_email",
            "submission",
            "grade_record",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "display_value",
            "created_at",
            "updated_at",
        )


class JournalGradeCreateSerializer(serializers.ModelSerializer):
    """Создание оценки в журнале."""

    class Meta:
        model = JournalGrade
        fields = (
            "lesson",
            "student",
            "grade_type",
            "scale",
            "score_five",
            "is_passed",
            "weight",
            "comment",
            "is_auto",
            "graded_by",
            "submission",
            "grade_record",
        )

    def validate(self, attrs: dict) -> dict:
        attrs = self._validate_grade_value(attrs)
        self._validate_lesson_student_grade_limit(attrs)
        return attrs

    def _validate_grade_value(self, attrs: dict) -> dict:
        scale = attrs.get("scale")
        grade_type = attrs.get("grade_type")

        score_five = attrs.get("score_five")
        is_passed = attrs.get("is_passed")

        if scale == GradeScale.FIVE_POINT:
            if score_five is None:
                raise serializers.ValidationError(
                    {"score_five": "Для пятибалльной шкалы укажите оценку от 1 до 5."}
                )

            if score_five < 1 or score_five > 5:
                raise serializers.ValidationError(
                    {"score_five": "Оценка должна быть от 1 до 5."}
                )

            attrs["is_passed"] = None

        elif scale == GradeScale.PASS_FAIL:
            if is_passed is None:
                raise serializers.ValidationError(
                    {"is_passed": "Для зачёта/незачёта укажите результат."}
                )

            attrs["score_five"] = None

        else:
            raise serializers.ValidationError(
                {"scale": "Допустимы только шкалы: оценка 1–5 или зачёт/незачёт."}
            )

        if grade_type == GradeType.CREDIT and scale != GradeScale.PASS_FAIL:
            raise serializers.ValidationError(
                {"scale": "Тип оценки «Зачёт» должен использовать шкалу зачёт/незачёт."}
            )

        return attrs

    def _validate_lesson_student_grade_limit(self, attrs: dict) -> None:
        lesson = attrs.get("lesson")
        student = attrs.get("student")

        if not lesson or not student:
            return

        grades_count = JournalGrade.objects.filter(
            lesson=lesson,
            student=student,
        ).count()

        if grades_count >= 2:
            raise serializers.ValidationError(
                {
                    "student": (
                        "За одно занятие студенту можно поставить не более двух оценок."
                    )
                }
            )


class JournalGradeUpdateSerializer(serializers.ModelSerializer):
    """Обновление оценки в журнале."""

    class Meta:
        model = JournalGrade
        fields = (
            "grade_type",
            "scale",
            "score_five",
            "is_passed",
            "weight",
            "comment",
            "graded_by",
        )

    def validate(self, attrs: dict) -> dict:
        instance = self.instance

        if instance is None:
            return attrs

        merged_attrs = {
            "grade_type": attrs.get("grade_type", instance.grade_type),
            "scale": attrs.get("scale", instance.scale),
            "score_five": attrs.get("score_five", instance.score_five),
            "is_passed": attrs.get("is_passed", instance.is_passed),
        }

        validated = JournalGradeCreateSerializer()._validate_grade_value(merged_attrs)

        attrs["score_five"] = validated["score_five"]
        attrs["is_passed"] = validated["is_passed"]

        return attrs
