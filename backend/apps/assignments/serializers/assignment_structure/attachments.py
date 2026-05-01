from __future__ import annotations

from rest_framework import serializers

from apps.assignments.models import AssignmentAttachment, AssignmentVariant
from apps.assignments.serializers.assignment_structure.common import (
    build_file_url,
    validate_variant_belongs_to_assignment,
)
from apps.assignments.serializers.assignment_structure.variants import (
    AssignmentVariantSerializer,
)


class AssignmentAttachmentSerializer(serializers.ModelSerializer):
    variant = AssignmentVariantSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = AssignmentAttachment
        fields = (
            "id",
            "title",
            "attachment_type",
            "file",
            "file_url",
            "external_url",
            "is_visible_to_students",
            "order",
            "variant",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "file_url",
            "created_at",
            "updated_at",
        )

    def get_file_url(self, obj):
        return build_file_url(obj.file, self.context)


class AssignmentAttachmentWriteSerializer(serializers.ModelSerializer):
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=AssignmentVariant.objects.all(),
        source="variant",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = AssignmentAttachment
        fields = (
            "title",
            "attachment_type",
            "file",
            "external_url",
            "is_visible_to_students",
            "order",
            "variant_id",
        )

    def validate(self, attrs):
        assignment = self.context.get("assignment")
        variant = attrs.get("variant")
        file_value = attrs.get("file")
        external_url = attrs.get("external_url", "")

        validate_variant_belongs_to_assignment(
            assignment=assignment,
            variant=variant,
        )

        if not file_value and not external_url:
            raise serializers.ValidationError(
                {"file": "Нужно прикрепить файл или указать ссылку."}
            )

        return attrs
