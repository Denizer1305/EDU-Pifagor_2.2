from __future__ import annotations

from rest_framework import serializers

from apps.assignments.models import Rubric, RubricCriterion
from apps.assignments.serializers.common import OrganizationBriefSerializer, UserBriefSerializer


class RubricCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RubricCriterion
        fields = (
            "id",
            "title",
            "description",
            "max_score",
            "order",
            "criterion_type",
            "created_at",
            "updated_at",
        )


class RubricCriterionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = RubricCriterion
        exclude = (
            "id",
            "rubric",
            "created_at",
            "updated_at",
        )


class RubricListSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()
    author = UserBriefSerializer(read_only=True)

    class Meta:
        model = Rubric
        fields = (
            "id",
            "title",
            "description",
            "assignment_kind",
            "organization",
            "author",
            "is_template",
            "is_active",
            "criteria_count",
            "created_at",
            "updated_at",
        )

    def get_organization(self, obj):
        if obj.organization is None:
            return None
        return OrganizationBriefSerializer(obj.organization).data


class RubricDetailSerializer(serializers.ModelSerializer):
    organization = serializers.SerializerMethodField()
    author = UserBriefSerializer(read_only=True)
    criteria = RubricCriterionSerializer(read_only=True, many=True)

    class Meta:
        model = Rubric
        fields = (
            "id",
            "title",
            "description",
            "assignment_kind",
            "organization",
            "author",
            "is_template",
            "is_active",
            "criteria",
            "created_at",
            "updated_at",
        )

    def get_organization(self, obj):
        if obj.organization is None:
            return None
        return OrganizationBriefSerializer(obj.organization).data


class RubricCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    assignment_kind = serializers.CharField(required=False, allow_blank=True)
    organization_id = serializers.IntegerField(required=False, allow_null=True)
    is_template = serializers.BooleanField(default=True, required=False)
    is_active = serializers.BooleanField(default=True, required=False)


class RubricUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True)
    assignment_kind = serializers.CharField(required=False, allow_blank=True)
    organization_id = serializers.IntegerField(required=False, allow_null=True)
    is_template = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
