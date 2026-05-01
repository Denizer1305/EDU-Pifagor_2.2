from __future__ import annotations

from rest_framework import serializers

from apps.assignments.models import AssignmentVariant


class AssignmentVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentVariant
        fields = (
            "id",
            "title",
            "code",
            "description",
            "variant_number",
            "order",
            "is_default",
            "max_score",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "max_score",
            "created_at",
            "updated_at",
        )


class AssignmentVariantWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentVariant
        exclude = (
            "id",
            "assignment",
            "created_at",
            "updated_at",
        )
