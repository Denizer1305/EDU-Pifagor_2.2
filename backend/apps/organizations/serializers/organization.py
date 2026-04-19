from __future__ import annotations

from rest_framework import serializers

from apps.organizations.models import Department, Organization, OrganizationType


class OrganizationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationType
        fields = (
            'id', 'code',
            'name', 'description',
            'is_active', 'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id', 'created_at',
            'updated_at',
        )


class OrganizationSerializer(serializers.ModelSerializer):
    type = OrganizationTypeSerializer(read_only=True)
    type_id = serializers.PrimaryKeyRelatedField(
        queryset=OrganizationType.objects.all(),
        source="type",
        write_only=True,
    )

    class Meta:
        model = Organization
        fields = (
            'id', 'type',
            'type_id', 'name',
            'short_name', 'description',
            'city', 'address',
            'phone', 'email',
            'website', 'logo',
            'is_active', 'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id', 'created_at',
            'updated_at',
        )


class DepartmentSerializer(serializers.ModelSerializer):
    organization = OrganizationSerializer(read_only=True)
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        source="organization",
        write_only=True,
    )

    class Meta:
        model = Department
        fields = (
            'id', 'organization',
            'organization_id', 'name',
            'short_name', 'description',
            'is_active', 'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id', 'created_at',
            'updated_at',
        )
