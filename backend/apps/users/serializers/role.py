from __future__ import annotations

from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from users.models import Role, UserRole


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class UserRoleSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Role.objects.all(),
        source='role',
        read_only=True,
    )

    class Meta:
        model = UserRole
        fields = '__all__'
        read_only_fields = ('id', 'assigned_at')
