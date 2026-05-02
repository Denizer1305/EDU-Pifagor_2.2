from __future__ import annotations

from rest_framework import serializers

from apps.assignments.models import Appeal
from apps.assignments.serializers.common import (
    AssignmentBriefSerializer,
    AssignmentPublicationBriefSerializer,
    UserBriefSerializer,
)


class AppealListSerializer(serializers.ModelSerializer):
    student = UserBriefSerializer(read_only=True)
    resolved_by = UserBriefSerializer(read_only=True)
    assignment = serializers.SerializerMethodField()
    publication = serializers.SerializerMethodField()

    class Meta:
        model = Appeal
        fields = (
            "id",
            "submission_id",
            "student",
            "assignment",
            "publication",
            "status",
            "reason",
            "resolution",
            "resolved_by",
            "resolved_at",
            "created_at",
            "updated_at",
        )

    def get_assignment(self, obj):
        submission = getattr(obj, "submission", None)
        if submission is None or submission.assignment is None:
            return None
        return AssignmentBriefSerializer(submission.assignment).data

    def get_publication(self, obj):
        submission = getattr(obj, "submission", None)
        if submission is None or submission.publication is None:
            return None
        return AssignmentPublicationBriefSerializer(submission.publication).data


class AppealDetailSerializer(serializers.ModelSerializer):
    student = UserBriefSerializer(read_only=True)
    resolved_by = UserBriefSerializer(read_only=True)
    assignment = serializers.SerializerMethodField()
    publication = serializers.SerializerMethodField()

    class Meta:
        model = Appeal
        fields = (
            "id",
            "submission_id",
            "student",
            "assignment",
            "publication",
            "status",
            "reason",
            "resolution",
            "resolved_by",
            "resolved_at",
            "created_at",
            "updated_at",
        )

    def get_assignment(self, obj):
        submission = getattr(obj, "submission", None)
        if submission is None or submission.assignment is None:
            return None
        return AssignmentBriefSerializer(submission.assignment).data

    def get_publication(self, obj):
        submission = getattr(obj, "submission", None)
        if submission is None or submission.publication is None:
            return None
        return AssignmentPublicationBriefSerializer(submission.publication).data


class AppealCreateSerializer(serializers.Serializer):
    submission_id = serializers.IntegerField()
    reason = serializers.CharField()


class AppealResolveSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Appeal.StatusChoices.choices)
    resolution = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        status_value = attrs.get("status")
        resolution = attrs.get("resolution", "")

        if (
            status_value
            in {
                Appeal.StatusChoices.RESOLVED,
                Appeal.StatusChoices.REJECTED,
            }
            and not resolution.strip()
        ):
            raise serializers.ValidationError(
                {"resolution": "Для завершения апелляции нужно указать решение."}
            )

        return attrs
