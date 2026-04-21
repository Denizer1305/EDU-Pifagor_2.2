from __future__ import annotations

from rest_framework import serializers

from apps.organizations.models import Subject, SubjectCategory


class SubjectCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectCategory
        fields = (
            "id", "code",
            "name", "description",
            "is_active", "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id", "created_at",
            "updated_at",
        )

    def validate_code(self, value):
        return value.strip()

    def validate_name(self, value):
        return value.strip()

    def validate_description(self, value):
        return value.strip()


class SubjectCategoryShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectCategory
        fields = (
            "id", "code",
            "name",
        )
        read_only_fields = fields


class SubjectSerializer(serializers.ModelSerializer):
    category = SubjectCategoryShortSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=SubjectCategory.objects.all(),
        source="category",
        write_only=True,
    )

    class Meta:
        model = Subject
        fields = (
            "id", "category",
            "category_id", "name",
            "short_name", "description",
            "is_active", "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id", "created_at",
            "updated_at",
        )

    def validate_name(self, value):
        return value.strip()

    def validate_short_name(self, value):
        return value.strip()

    def validate_description(self, value):
        return value.strip()
