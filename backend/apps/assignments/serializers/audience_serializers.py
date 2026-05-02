from __future__ import annotations

from rest_framework import serializers

from apps.assignments.models import AssignmentAudience


class AssignmentAudienceSerializer(serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    course_enrollment_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = AssignmentAudience
        fields = (
            "id",
            "audience_type",
            "student",
            "group",
            "course_enrollment_id",
            "is_active",
            "created_at",
            "updated_at",
        )

    def get_student(self, obj):
        if not obj.student:
            return None
        return {
            "id": obj.student.id,
            "email": getattr(obj.student, "email", ""),
        }

    def get_group(self, obj):
        if not obj.group:
            return None
        return {
            "id": obj.group.id,
            "title": getattr(obj.group, "title", str(obj.group)),
        }


class AssignmentAudienceCreateSerializer(serializers.Serializer):
    audience_type = serializers.CharField()
    student_id = serializers.IntegerField(required=False)
    group_id = serializers.IntegerField(required=False)
    course_enrollment_id = serializers.IntegerField(required=False)
    is_active = serializers.BooleanField(default=True, required=False)

    def validate(self, attrs):
        audience_type = (attrs.get("audience_type") or "").strip()
        student_id = attrs.get("student_id")
        group_id = attrs.get("group_id")
        course_enrollment_id = attrs.get("course_enrollment_id")

        if audience_type in {"student", "selected_students"} and not student_id:
            raise serializers.ValidationError({"student_id": "Нужно указать студента."})

        if audience_type == "group" and not group_id:
            raise serializers.ValidationError({"group_id": "Нужно указать группу."})

        if (
            audience_type in {"course_enrollment", "enrollment"}
            and not course_enrollment_id
        ):
            raise serializers.ValidationError(
                {"course_enrollment_id": "Нужно указать запись на курс."}
            )

        return attrs


class AssignmentAudienceUpdateSerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=False)


class AssignPublicationToAllCourseStudentsSerializer(serializers.Serializer):
    create_individual_audiences = serializers.BooleanField(
        required=False,
        default=False,
    )
