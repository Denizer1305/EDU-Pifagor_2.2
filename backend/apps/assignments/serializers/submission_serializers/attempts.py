from __future__ import annotations

from rest_framework import serializers

from apps.assignments.models import SubmissionAttempt


class SubmissionAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmissionAttempt
        fields = (
            "id",
            "attempt_number",
            "started_at",
            "submitted_at",
            "time_spent_minutes",
            "status",
            "snapshot_json",
            "created_at",
            "updated_at",
        )
