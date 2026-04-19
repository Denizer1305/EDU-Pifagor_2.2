from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserListSerializer(serializers.ModelSerializer):
    """Сериализатор user list."""
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email',
            'full_name', 'is_email_verified',
            'is_active', 'is_staff',
            'created_at',
        )
        read_only_fields = fields


class UserDetailSerializer(serializers.ModelSerializer):
    """Сериализатор user detail."""
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'email',
            'reset_email', 'full_name',
            'is_email_verified', 'is_active',
            'is_staff', 'is_superuser',
            'last_login', 'created_at',
            'updated_at',
        )
        read_only_fields = (
            'id', 'full_name',
            'is_staff', 'is_superuser',
            'last_login', 'created_at',
            'updated_at',
        )


class CurrentUserSerializer(serializers.ModelSerializer):
    """Сериализатор current user."""
    full_name = serializers.CharField(read_only=True)
    roles = serializers.SerializerMethodField()
    profile_id = serializers.SerializerMethodField()
    teacher_profile_id = serializers.SerializerMethodField()
    student_profile_id = serializers.SerializerMethodField()
    parent_profile_id = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email',
            'reset_email', 'full_name',
            'is_email_verified', 'is_active',
            'is_staff', 'is_superuser',
            'roles', 'profile_id',
            'teacher_profile_id', 'student_profile_id',
            'parent_profile_id', 'created_at',
        )
        read_only_fields = fields

    def get_roles(self, obj):
        """Вычисляет и возвращает значение поля."""
        if not hasattr(obj, "user_roles"):
            return []
        return list(obj.user_roles.values_list("role__code", flat=True))

    def get_profile_id(self, obj):
        """Вычисляет и возвращает значение поля."""
        return getattr(getattr(obj, "profile", None), "id", None)

    def get_teacher_profile_id(self, obj):
        """Вычисляет и возвращает значение поля."""
        return getattr(getattr(obj, "teacher_profile", None), "id", None)

    def get_student_profile_id(self, obj):
        """Вычисляет и возвращает значение поля."""
        return getattr(getattr(obj, "student_profile", None), "id", None)

    def get_parent_profile_id(self, obj):
        """Вычисляет и возвращает значение поля."""
        return getattr(getattr(obj, "parent_profile", None), "id", None)


class UserUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор user update."""
    class Meta:
        model = User
        fields = (
            'email', 'reset_email',
            'is_active', 'is_email_verified',
        )

    def validate_email(self, value: str) -> str:
        """Выполняет валидацию значения поля."""
        value = value.strip().lower()
        user = self.instance

        qs = User.objects.filter(email=value)
        if user is not None:
            qs = qs.exclude(pk=user.pk)

        if qs.exists():
            raise serializers.ValidationError("Пользователь с такой электронной почтой уже существует.")

        return value

    def validate_reset_email(self, value: str | None) -> str | None:
        """Выполняет валидацию значения поля."""
        if not value:
            return None
        return value.strip().lower()

    def validate(self, attrs):
        """Выполняет общую валидацию входных данных."""
        email = attrs.get("email", getattr(self.instance, "email", None))
        reset_email = attrs.get("reset_email", getattr(self.instance, "reset_email", None))

        if email and reset_email and email == reset_email:
            raise serializers.ValidationError(
                {"reset_email": "Резервная почта не может совпадать с основной."}
            )

        return attrs
