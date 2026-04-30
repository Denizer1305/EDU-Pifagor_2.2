from __future__ import annotations

from rest_framework import serializers

from apps.assignments.models import GradeRecord
from apps.assignments.serializers.common import (
    AssignmentBriefSerializer,
    AssignmentPublicationBriefSerializer,
    UserBriefSerializer,
)


class GradeRecordListSerializer(serializers.ModelSerializer):
    student = UserBriefSerializer(read_only=True)
    assignment = AssignmentBriefSerializer(read_only=True)
    publication = AssignmentPublicationBriefSerializer(read_only=True)
    graded_by = UserBriefSerializer(read_only=True)

    class Meta:
        model = GradeRecord
        fields = (
            "id",
            "student",
            "assignment",
            "publication",
            "submission_id",
            "grade_value",
            "grade_numeric",
            "grading_mode",
            "is_final",
            "graded_by",
            "graded_at",
            "created_at",
            "updated_at",
        )


class GradeRecordDetailSerializer(serializers.ModelSerializer):
    student = UserBriefSerializer(read_only=True)
    assignment = AssignmentBriefSerializer(read_only=True)
    publication = AssignmentPublicationBriefSerializer(read_only=True)
    graded_by = UserBriefSerializer(read_only=True)

    class Meta:
        model = GradeRecord
        fields = (
            "id",
            "student",
            "assignment",
            "publication",
            "submission_id",
            "grade_value",
            "grade_numeric",
            "grading_mode",
            "is_final",
            "graded_by",
            "graded_at",
            "created_at",
            "updated_at",
        )


class GradeRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeRecord
        fields = (
            "student",
            "assignment",
            "publication",
            "submission",
            "grade_value",
            "grade_numeric",
            "grading_mode",
            "is_final",
            "graded_by",
            "graded_at",
        )


class GradeRecordUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeRecord
        fields = (
            "grade_value",
            "grade_numeric",
            "grading_mode",
            "is_final",
            "graded_by",
            "graded_at",
        )
