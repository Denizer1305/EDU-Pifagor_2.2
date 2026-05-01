from __future__ import annotations

from rest_framework import serializers

from apps.assignments.models import (
    AssignmentQuestion,
    AssignmentSection,
    AssignmentVariant,
)
from apps.assignments.serializers.assignment_structure.common import (
    validate_section_belongs_to_assignment,
    validate_section_belongs_to_variant,
    validate_variant_belongs_to_assignment,
)
from apps.assignments.serializers.assignment_structure.sections import (
    AssignmentSectionSerializer,
)
from apps.assignments.serializers.assignment_structure.variants import (
    AssignmentVariantSerializer,
)


class AssignmentQuestionSerializer(serializers.ModelSerializer):
    variant = AssignmentVariantSerializer(read_only=True)
    section = AssignmentSectionSerializer(read_only=True)

    class Meta:
        model = AssignmentQuestion
        fields = (
            "id",
            "question_type",
            "prompt",
            "description",
            "answer_options_json",
            "correct_answer_json",
            "validation_rules_json",
            "explanation",
            "max_score",
            "order",
            "is_required",
            "requires_manual_review",
            "variant",
            "section",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
        )


class AssignmentQuestionWriteSerializer(serializers.ModelSerializer):
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=AssignmentVariant.objects.all(),
        source="variant",
        required=False,
        allow_null=True,
    )
    section_id = serializers.PrimaryKeyRelatedField(
        queryset=AssignmentSection.objects.all(),
        source="section",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = AssignmentQuestion
        fields = (
            "question_type",
            "prompt",
            "description",
            "answer_options_json",
            "correct_answer_json",
            "validation_rules_json",
            "explanation",
            "max_score",
            "order",
            "is_required",
            "requires_manual_review",
            "variant_id",
            "section_id",
        )

    def validate(self, attrs):
        assignment = self.context.get("assignment")
        variant = attrs.get("variant")
        section = attrs.get("section")

        validate_variant_belongs_to_assignment(
            assignment=assignment,
            variant=variant,
        )
        validate_section_belongs_to_assignment(
            assignment=assignment,
            section=section,
        )
        validate_section_belongs_to_variant(
            section=section,
            variant=variant,
        )

        return attrs
