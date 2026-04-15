from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from django.utils.translation import gettext_lazy as _

from users.models import User


class UserListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(
        method_name='full_name', read_only=True
    )

    class Meta:
        model = User
        fields = (
            'id', 'email', 'full_name',
            'is_active', 'is_staff', 'is_email_verified',
            'created_at',
        )
        read_only_fields = fields


class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(
        method_name='full_name', read_only=True
    )

    class Meta:
        model = User
        fields = (
            'id', 'email', 'reset_email', 'full_name',
            'is_active', 'is_staff', 'is_superuser', 'is_email_verified',
            'created_at', 'updated_at', 'last_login'
        )
        read_only_fields = (
            'id', 'full_name', 'is_staff',
            'is_superuser', 'created_at',
            'updated_at', 'last_login'
        )


class UserCurrentSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(
        method_name='full_name', read_only=True
    )

    class Meta:
        model = User
        fields = (
            'id', 'email', 'reset_email', 'full_name',
            'is_active', 'is_email_verified',
            'created_at',
        )
        read_only_fields = fields


class UserUpdateSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(
        method_name='full_name', read_only=True
    )

    class Meta:
        model = User
        fields = (
            'email', 'reset_email', 'is_active',
            'is_staff', 'is_email_verified',
        )
        read_only_fields = fields

    def validate_email(self, value):
        value = value.strip().lower()
        user = self.instance

        qs = User.objects.filter(email=value)
        if user is not None:
            qs = qs.exclude(pk=user.pk)

        if qs.exists():
            raise serializers.ValidationError(
                _('Пользователь с такой эл.почтой уже существует.')
            )

    def validate_reset_email(self, value):
        if not value:
            return None
        return value.strip().lower()

    def validate(self, attrs):
        email = attrs.get('email', getattr(attrs, 'email', None))
        reset_email = attrs.get('reset_email', getattr(attrs, 'reset_email', None))

        if email and reset_email and email == reset_email:
            raise serializers.ValidationError(
                {"reset_email": _("Резервная почта не может совпадать с основной.")}
            )
        return attrs
