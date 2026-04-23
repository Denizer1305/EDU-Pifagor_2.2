from __future__ import annotations

from rest_framework import serializers

from apps.course.models import CourseProgress, LessonProgress


class CourseShortSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="enrollment.course.id", read_only=True)
    title = serializers.CharField(source="enrollment.course.title", read_only=True)
    code = serializers.CharField(source="enrollment.course.code", read_only=True)
    slug = serializers.CharField(source="enrollment.course.slug", read_only=True)


class StudentShortSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="enrollment.student.id", read_only=True)
    email = serializers.EmailField(source="enrollment.student.email", read_only=True)
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        student = obj.enrollment.student
        profile = getattr(student, "profile", None)
        if profile is not None and getattr(profile, "full_name", ""):
            return profile.full_name
        first_name = getattr(profile, "first_name", "") if profile else ""
        last_name = getattr(profile, "last_name", "") if profile else ""
        patronymic = getattr(profile, "patronymic", "") if profile else ""
        parts = [last_name, first_name, patronymic]
        return " ".join(part for part in parts if part).strip() or student.email


class LastLessonShortSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    order = serializers.IntegerField(read_only=True)


class LessonProgressListSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    module_title = serializers.CharField(source="lesson.module.title", read_only=True)

    class Meta:
        model = LessonProgress
        fields = (
            "id",
            "lesson",
            "lesson_title",
            "module_title",
            "status",
            "started_at",
            "completed_at",
            "last_viewed_at",
            "spent_minutes",
            "attempts_count",
            "score",
            "created_at",
            "updated_at",
        )


class LessonProgressDetailSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    module_title = serializers.CharField(source="lesson.module.title", read_only=True)
    course_title = serializers.CharField(source="enrollment.course.title", read_only=True)

    class Meta:
        model = LessonProgress
        fields = (
            "id",
            "lesson",
            "lesson_title",
            "module_title",
            "course_title",
            "status",
            "started_at",
            "completed_at",
            "last_viewed_at",
            "spent_minutes",
            "attempts_count",
            "score",
            "created_at",
            "updated_at",
        )


class CourseProgressListSerializer(serializers.ModelSerializer):
    course = CourseShortSerializer(source="*", read_only=True)
    student = StudentShortSerializer(source="*", read_only=True)

    class Meta:
        model = CourseProgress
        fields = (
            "id",
            "enrollment",
            "course",
            "student",
            "total_lessons_count",
            "completed_lessons_count",
            "required_lessons_count",
            "completed_required_lessons_count",
            "progress_percent",
            "spent_minutes",
            "started_at",
            "completed_at",
            "last_activity_at",
            "created_at",
            "updated_at",
        )


class CourseProgressDetailSerializer(serializers.ModelSerializer):
    course = CourseShortSerializer(source="*", read_only=True)
    student = StudentShortSerializer(source="*", read_only=True)
    last_lesson = serializers.SerializerMethodField()
    lesson_progresses = serializers.SerializerMethodField()

    class Meta:
        model = CourseProgress
        fields = (
            "id",
            "enrollment",
            "course",
            "student",
            "total_lessons_count",
            "completed_lessons_count",
            "required_lessons_count",
            "completed_required_lessons_count",
            "progress_percent",
            "spent_minutes",
            "started_at",
            "completed_at",
            "last_activity_at",
            "last_lesson",
            "lesson_progresses",
            "created_at",
            "updated_at",
        )

    def get_last_lesson(self, obj):
        if obj.last_lesson is None:
            return None

        return {
            "id": obj.last_lesson.id,
            "title": obj.last_lesson.title,
            "order": obj.last_lesson.order,
        }

    def get_lesson_progresses(self, obj):
        queryset = obj.lesson_progresses.select_related("lesson", "lesson__module").order_by(
            "lesson__module__order",
            "lesson__order",
            "id",
        )
        return LessonProgressListSerializer(
            queryset,
            many=True,
            context=self.context,
        ).data


class CourseProgressStartSerializer(serializers.Serializer):
    pass


class LessonProgressMarkInProgressSerializer(serializers.Serializer):
    pass


class LessonProgressCompleteSerializer(serializers.Serializer):
    spent_minutes = serializers.IntegerField(required=False, min_value=0)
    score = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    attempts_increment = serializers.BooleanField(required=False, default=True)
