from __future__ import annotations

from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        email = attrs.get("email", "").strip().lower()
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )

        if not user:
            raise serializers.ValidationError(
                {"detail": _("Неверная эл.почта или пароль.")}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": _("Учетная запись деактивирована.")}
            )

        attrs["email"] = email
        attrs["user"] = user
        return attrs
