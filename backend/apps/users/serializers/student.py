from __future__ import annotations

from rest_framework import serializers

from apps.users.models import StudentProfile


class StudentProfileDetailSerializer(serializers.ModelSerializer):
    """Сериализатор student profile detail."""
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.profile.full_name", read_only=True)

    class Meta:
        model = StudentProfile
        fields = (
            'id', 'user',
            'email', 'full_name',
            'student_code', 'admission_year',
            'status', 'notes',
            'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'user',
            'email', 'full_name',
            'created_at', 'updated_at',
        )


class StudentProfileUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор student profile update."""
    class Meta:
        model = StudentProfile
        fields = (
            'student_code', 'admission_year',
            'status', 'notes',
        )
