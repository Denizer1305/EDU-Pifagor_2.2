from __future__ import annotations

from rest_framework import serializers

from apps.users.models import ParentProfile, ParentStudent


class ParentProfileDetailSerializer(serializers.ModelSerializer):
    """Сериализатор parent profile detail."""
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.profile.full_name", read_only=True)

    class Meta:
        model = ParentProfile
        fields = (
            'id', 'user',
            'email', 'full_name',
            'occupation', 'work_place',
            'emergency_contact_phone', 'notes',
            'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'user',
            'email', 'full_name',
            'created_at', 'updated_at',
        )


class ParentProfileUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор parent profile update."""
    class Meta:
        model = ParentProfile
        fields = (
            'occupation', 'work_place',
            'emergency_contact_phone', 'notes',
        )


class ParentStudentSerializer(serializers.ModelSerializer):
    """Сериализатор parent student."""
    parent_email = serializers.EmailField(source="parent.email", read_only=True)
    student_email = serializers.EmailField(source="student.email", read_only=True)

    class Meta:
        model = ParentStudent
        fields = (
            'id', 'parent',
            'parent_email', 'student',
            'student_email', 'relation_type',
            'is_primary', 'created_at',
        )
        read_only_fields = (
            'id', 'created_at',
        )
