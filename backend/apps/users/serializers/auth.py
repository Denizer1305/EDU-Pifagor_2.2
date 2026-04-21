from __future__ import annotations

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apps.organizations.models import Department, Organization
from apps.users.services.auth_services import register_user


User = get_user_model()


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


class BaseRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    reset_email = serializers.EmailField(
        required=False,
        allow_blank=True,
    )
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

    first_name = serializers.CharField(
        required=True,
        max_length=150,
        write_only=True,
    )
    last_name = serializers.CharField(
        required=True,
        max_length=150,
        write_only=True,
    )
    patronymic = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=150,
        write_only=True,
    )
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=32,
        write_only=True,
    )

    registration_type = User.RegistrationTypeChoices.UNKNOWN

    def validate_email(self, value):
        return value.strip().lower()

    def validate_reset_email(self, value):
        return value.strip().lower()

    def validate_password(self, value):
        validate_password(value)
        return value

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

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("password_repeat"):
            raise serializers.ValidationError(
                {"password_repeat": _("Пароли не совпадают.")}
            )
        return attrs

    def create(self, validated_data):
        return register_user(
            registration_type=self.registration_type,
            **validated_data,
        )


class StudentRegistrationSerializer(BaseRegistrationSerializer):
    registration_type = User.RegistrationTypeChoices.STUDENT


class ParentRegistrationSerializer(BaseRegistrationSerializer):
    registration_type = User.RegistrationTypeChoices.PARENT

    work_place = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
        write_only=True,
    )
    position = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
        write_only=True,
    )

    def validate_work_place(self, value):
        return value.strip()

    def validate_position(self, value):
        return value.strip()


class TeacherRegistrationSerializer(BaseRegistrationSerializer):
    registration_type = User.RegistrationTypeChoices.TEACHER

    requested_organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        source="requested_organization",
        write_only=True,
        required=True,
    )
    requested_department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(),
        source="requested_department",
        write_only=True,
        required=False,
        allow_null=True,
    )
    teacher_registration_code = serializers.CharField(
        required=True,
        write_only=True,
        trim_whitespace=True,
        max_length=128,
    )
    position = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=255,
        write_only=True,
    )
    employee_code = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=128,
        write_only=True,
    )
    education_info = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )
    experience_years = serializers.IntegerField(
        required=False,
        min_value=0,
        write_only=True,
    )

    def validate_teacher_registration_code(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                _("Введите регистрационный код преподавателя.")
            )
        return value

    def validate_position(self, value):
        return value.strip()

    def validate_employee_code(self, value):
        return value.strip()

    def validate_education_info(self, value):
        return value.strip()

    def validate(self, attrs):
        attrs = super().validate(attrs)

        requested_organization = attrs.get("requested_organization")
        requested_department = attrs.get("requested_department")

        if (
            requested_department
            and requested_organization
            and requested_department.organization_id != requested_organization.id
        ):
            raise serializers.ValidationError(
                {"requested_department_id": _("Подразделение должно принадлежать выбранной организации.")}
            )

        return attrs


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
