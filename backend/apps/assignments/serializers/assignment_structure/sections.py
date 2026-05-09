from __future__ import annotations

from rest_framework import serializers

from apps.assignments.models import AssignmentSection, AssignmentVariant
from apps.assignments.serializers.assignment_structure.common import (
    validate_variant_belongs_to_assignment,
)
from apps.assignments.serializers.assignment_structure.variants import (
    AssignmentVariantSerializer,
)


class AssignmentSectionSerializer(serializers.ModelSerializer):
    variant = AssignmentVariantSerializer(read_only=True)

    class Meta:
        model = AssignmentSection
        fields = (
            "id",
            "title",
            "description",
            "section_type",
            "order",
            "max_score",
            "is_required",
            "variant",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class AssignmentSectionWriteSerializer(serializers.ModelSerializer):
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=AssignmentVariant.objects.all(),
        source="variant",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = AssignmentSection
        fields = (
            "title",
            "description",
            "section_type",
            "order",
            "max_score",
            "is_required",
            "variant_id",
        )

    def validate(self, attrs):
        assignment = self.context.get("assignment")
        variant = attrs.get("variant")

        validate_variant_belongs_to_assignment(
            assignment=assignment,
            variant=variant,
        )

        return attrs
