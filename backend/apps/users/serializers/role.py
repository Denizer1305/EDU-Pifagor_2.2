from __future__ import annotations

from rest_framework import serializers

from apps.users.models import Role, UserRole


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = (
            "id",
            "code",
            "name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class UserRoleSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)

    class Meta:
        model = UserRole
        fields = (
            "id",
            "role",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields
