from __future__ import annotations

from rest_framework import serializers

from apps.users.models import TeacherProfile


class TeacherProfileListSerializer(serializers.ModelSerializer):
    """Сериализатор teacher profile list."""
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.profile.full_name", read_only=True)
    short_name = serializers.CharField(source="user.profile.short_name", read_only=True)

    class Meta:
        model = TeacherProfile
        fields = (
            'id', 'user',
            'email', 'full_name',
            'short_name', 'public_title',
            'short_bio', 'is_public',
            'show_on_teachers_page',
        )
        read_only_fields = fields


class TeacherProfileDetailSerializer(serializers.ModelSerializer):
    """Сериализатор teacher profile detail."""
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.profile.full_name", read_only=True)
    short_name = serializers.CharField(source="user.profile.short_name", read_only=True)

    class Meta:
        model = TeacherProfile
        fields = (
            'id', 'user',
            'email', 'full_name',
            'short_name', 'public_title',
            'short_bio', 'bio',
            'education', 'experience',
            'achievements', 'cover_image',
            'is_public', 'show_on_teachers_page',
            'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'user',
            'email', 'full_name',
            'short_name', 'created_at',
            'updated_at',
        )


class TeacherProfileUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор teacher profile update."""
    class Meta:
        model = TeacherProfile
        fields = (
            'public_title', 'short_bio',
            'bio', 'education',
            'experience', 'achievements',
            'cover_image', 'is_public',
            'show_on_teachers_page',
        )
