from __future__ import annotations

from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        return value.strip().lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(
        required=True,
        write_only=True,
        trim_whitespace=False,
    )
    password_repeat = serializers.CharField(
        required=True,
        write_only=True,
        trim_whitespace=False,
    )

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password_repeat"):
            raise serializers.ValidationError(
                {"password_repeat": _("Пароли не совпадают.")}
            )

        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        trim_whitespace=False,
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        trim_whitespace=False,
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        trim_whitespace=False,
    )

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                _("Текущий пароль указан неверно.")
            )
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs.get("old_password") == attrs.get("new_password"):
            raise serializers.ValidationError(
                {"new_password": _("Новый пароль не может совпадать с текущим.")}
            )

        if attrs.get("new_password") != attrs.get("new_password_confirm"):
            raise serializers.ValidationError(
                {"new_password_confirm": _("Пароли не совпадают.")}
            )

        return attrs
