from __future__ import annotations

from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from apps.users.models import Profile


User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """Сериализатор login."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        """Выполняет общую валидацию входных данных."""
        email = attrs.get('email').strip().lower()
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password)

        if not user:
            raise serializers.ValidationError(
                {'detail': _('Неверная эл.почта или пароль.')}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {'detail': _('Учетная запись деактивирована.')}
            )

        attrs['user'] = user
        return attrs


class RegisterSerializer(serializers.Serializer):
    """Сериализатор register."""
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True, write_only=True, trim_whitespace=False
    )
    password_repeat = serializers.CharField(
        required=True, write_only=True, trim_whitespace=False
    )

    first_name = serializers.CharField(required=True, max_length=150, write_only=True)
    last_name = serializers.CharField(required=True, max_length=150, write_only=True)
    patronymic = serializers.CharField(required=False, max_length=150, write_only=True)

    def validate_email(self, value):
        """Выполняет валидацию значения поля."""
        value = value.strip().lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                _("Пользователь с такой эл.почтой уже существует.")
            )
        return value

    def validate(self, attrs):
        """Выполняет общую валидацию входных данных."""
        password = attrs.get('password')
        password_repeat = attrs.get('password_repeat')
        email = attrs.get('email')
        phone = attrs.get('phone')

        if password != password_repeat:
            raise serializers.ValidationError(
                {"password_repeat": _("Пароли не совпадают.")}
            )

        if email == '' or phone == '':
            raise serializers.ValidationError({
                "email": _("Введите эл.почту."),
                "phone": _("Введите номер телефона."),
            })
        return attrs

    def create(self, validated_data):
        """Создает и возвращает новый объект."""
        email = validated_data.pop('email', None)

        profile_data = {
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'patronymic': validated_data.pop('patronymic', ''),
            'phone': validated_data.pop('phone'),
        }

        password = validated_data.pop('password', None)
        user = User.objects.create_user(email=email, password=password, **profile_data)
        Profile.objects.create(user=user, **profile_data)
        return user


class PasswordResetSerializer(serializers.Serializer):
    """Сериализатор password reset."""
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Выполняет валидацию значения поля."""
        return value.strip().lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Сериализатор password reset confirm."""
    password = serializers.CharField(
        required=True, write_only=True, trim_whitespace=False
    )
    password_repeat = serializers.CharField(
        required=True, write_only=True, trim_whitespace=False
    )

    def validate(self, attrs):
        """Выполняет общую валидацию входных данных."""
        if attrs.get('password') != attrs.get('password_repeat'):
            raise serializers.ValidationError(
                {"password_repeat": _("Пароли не совпадают.")}
            )
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор change password."""
    old_password = serializers.CharField(
        required=True, write_only=True, trim_whitespace=False
    )
    new_password = serializers.CharField(
        required=True, write_only=True, trim_whitespace=False
    )
    new_password_confirm = serializers.CharField(
        required=True, write_only=True, trim_whitespace=False
    )

    def validate_old_password(self, value):
        """Выполняет валидацию значения поля."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                _("Текущий пароль указан неверно.")
            )
        return value

    def validate(self, attrs):
        """Выполняет общую валидацию входных данных."""
        if attrs.get('old_password') == attrs.get('new_password'):
            raise serializers.ValidationError(
                {"new_password": _("Новый пароль не может совпадать с текущим.")}
            )

        if attrs.get('new_password') != attrs.get('new_password_confirm'):
            raise serializers.ValidationError(
                {"new_password_confirm": _("Пароли не совпадают.")}
            )
        return attrs
