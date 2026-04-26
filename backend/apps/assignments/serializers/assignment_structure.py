from __future__ import annotations

from rest_framework import serializers

from apps.assignments.models import (
    AssignmentAttachment,
    AssignmentQuestion,
    AssignmentSection,
    AssignmentVariant,
)


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

        if assignment is not None and variant is not None and variant.assignment_id != assignment.id:
            raise serializers.ValidationError(
                {"variant_id": "Вариант должен принадлежать выбранной работе."}
            )

        return attrs


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

        if assignment is not None and variant is not None and variant.assignment_id != assignment.id:
            raise serializers.ValidationError(
                {"variant_id": "Вариант должен принадлежать выбранной работе."}
            )

        if assignment is not None and section is not None and section.assignment_id != assignment.id:
            raise serializers.ValidationError(
                {"section_id": "Секция должна принадлежать выбранной работе."}
            )

        if variant is not None and section is not None and section.variant_id and section.variant_id != variant.id:
            raise serializers.ValidationError(
                {"section_id": "Секция должна относиться к выбранному варианту."}
            )

        return attrs


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
        if not obj.file:
            return ""
        request = self.context.get("request")
        url = obj.file.url
        return request.build_absolute_uri(url) if request else url


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

        if assignment is not None and variant is not None and variant.assignment_id != assignment.id:
            raise serializers.ValidationError(
                {"variant_id": "Вариант должен принадлежать выбранной работе."}
            )

        if not file_value and not external_url:
            raise serializers.ValidationError(
                {"file": "Нужно прикрепить файл или указать ссылку."}
            )

        return attrs
