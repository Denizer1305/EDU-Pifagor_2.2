from __future__ import annotations

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.users.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )
    full_name = serializers.CharField(
        read_only=True,
    )
    short_name = serializers.CharField(
        read_only=True,
    )

    class Meta:
        model = Profile
        fields = (
            "id", "user",
            "email", "full_name",
            "short_name", "city",
            "avatar",
        )
        read_only_fields = fields


class ProfileDetailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        source="user.email",
        read_only=True,
    )
    full_name = serializers.CharField(read_only=True)
    short_name = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        fields = (
            "id", "user",
            "email", "first_name",
            "last_name", "patronymic",
            "full_name", "short_name",
            "phone", "birth_date",
            "gender", "about",
            "city", "avatar",
            "timezone", "social_link_max",
            "social_link_vk", "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id", "user",
            "email", "full_name",
            "short_name", "created_at",
            "updated_at",
        )


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "first_name", "last_name",
            "patronymic", "phone",
            "birth_date", "gender",
            "about", "city",
            "avatar", "timezone",
            "social_link_max", "social_link_vk",
        )

    def validate_first_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(_("Имя обязательно."))
        return value

    def validate_last_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(_("Фамилия обязательна."))
        return value

    def validate_patronymic(self, value):
        return value.strip()

    def validate_phone(self, value):
        return value.strip()

    def validate_city(self, value):
        return value.strip()

    def validate_timezone(self, value):
        return value.strip()

    def validate_about(self, value):
        return value.strip()
