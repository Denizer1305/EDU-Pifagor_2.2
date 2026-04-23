from __future__ import annotations

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, password_validation
from django.contrib.auth.hashers import check_password
from django.core import signing
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.users.constants import (
    ONBOARDING_STATUS_DRAFT,
    ONBOARDING_STATUS_PENDING,
    REGISTRATION_TYPE_STUDENT,
    REGISTRATION_TYPE_TEACHER,
    VERIFICATION_STATUS_NOT_FILLED,
    VERIFICATION_STATUS_PENDING,
)
from apps.users.services.profile_services import (
    ensure_role_profile,
    get_or_create_base_profile,
)
from apps.users.services.user_services import mark_user_email_verified
from apps.users.validators import validate_email, validate_phone

User = get_user_model()

VERIFY_EMAIL_SALT = "users.verify_email"
RESET_PASSWORD_SALT = "users.reset_password"


def _verify_teacher_registration_code(organization, code: str) -> None:
    """
    Проверяет код регистрации преподавателя.

    Работает в мягком режиме:
    если поля кодов ещё не добавлены в Organization, функция не ломает flow.
    """
    code = (code or "").strip()
    if not code:
        raise ValidationError(
            {"teacher_registration_code": _("Необходимо указать код регистрации преподавателя.")}
        )

    has_hash = hasattr(organization, "teacher_registration_code_hash")
    has_active = hasattr(organization, "teacher_registration_code_is_active")
    has_expires = hasattr(organization, "teacher_registration_code_expires_at")

    if not has_hash:
        return

    code_hash = getattr(organization, "teacher_registration_code_hash", "") or ""
    if not code_hash:
        raise ValidationError(
            {"teacher_registration_code": _("Для организации не настроен код регистрации преподавателя.")}
        )

    if has_active and not getattr(organization, "teacher_registration_code_is_active", False):
        raise ValidationError(
            {"teacher_registration_code": _("Код регистрации преподавателя для организации отключён.")}
        )

    if has_expires:
        expires_at = getattr(organization, "teacher_registration_code_expires_at", None)
        if expires_at and timezone.now() > expires_at:
            raise ValidationError(
                {"teacher_registration_code": _("Срок действия кода регистрации преподавателя истёк.")}
            )

    if not check_password(code, code_hash):
        raise ValidationError(
            {"teacher_registration_code": _("Неверный код регистрации преподавателя.")}
        )


@transaction.atomic
def register_user(
    *,
    email: str,
    password: str,
    password_repeat: str,
    registration_type: str,
    first_name: str,
    last_name: str,
    patronymic: str = "",
    phone: str = "",
    reset_email: str = "",
    requested_organization=None,
    requested_department=None,
    teacher_registration_code: str = "",
    position: str = "",
    employee_code: str = "",
    work_place: str = "",
    education_info: str = "",
    experience_years: int | None = None,
):
    """
    Регистрирует пользователя и подготавливает его профиль под нужный flow.
    """
    email = (email or "").strip().lower()
    reset_email = (reset_email or "").strip().lower()
    first_name = (first_name or "").strip()
    last_name = (last_name or "").strip()
    patronymic = (patronymic or "").strip()
    phone = (phone or "").strip()
    position = (position or "").strip()
    employee_code = (employee_code or "").strip()
    work_place = (work_place or "").strip()
    education_info = (education_info or "").strip()

    if not email:
        raise ValidationError({"email": _("Введите эл. почту.")})

    if User.objects.filter(email=email).exists():
        raise ValidationError({"email": _("Пользователь с такой эл. почтой уже существует.")})

    validate_email(email, reset_email)

    if phone:
        validate_phone(phone)

    if password != password_repeat:
        raise ValidationError({"password_repeat": _("Пароли не совпадают.")})

    password_validation.validate_password(password)

    if registration_type == REGISTRATION_TYPE_TEACHER:
        if not requested_organization:
            raise ValidationError(
                {"requested_organization": _("Для преподавателя необходимо указать образовательную организацию.")}
            )

        if (
            requested_department
            and requested_department.organization_id != requested_organization.id
        ):
            raise ValidationError(
                {"requested_department": _("Отделение должно принадлежать выбранной образовательной организации.")}
            )

        _verify_teacher_registration_code(
            organization=requested_organization,
            code=teacher_registration_code,
        )

    user = User.objects.create_user(
        email=email,
        password=password,
        reset_email=reset_email,
        registration_type=registration_type,
        onboarding_status=ONBOARDING_STATUS_DRAFT,
    )

    profile = get_or_create_base_profile(user)
    profile.first_name = first_name
    profile.last_name = last_name
    profile.patronymic = patronymic
    profile.phone = phone
    profile.full_clean()
    profile.save()

    role_profile = ensure_role_profile(user)

    if registration_type == REGISTRATION_TYPE_STUDENT and role_profile:
        role_profile.verification_status = VERIFICATION_STATUS_NOT_FILLED
        role_profile.full_clean()
        role_profile.save()

    if registration_type == REGISTRATION_TYPE_TEACHER and role_profile:
        if hasattr(role_profile, "requested_organization"):
            role_profile.requested_organization = requested_organization
        if hasattr(role_profile, "requested_department"):
            role_profile.requested_department = requested_department
        if hasattr(role_profile, "position"):
            role_profile.position = position
        if hasattr(role_profile, "employee_code"):
            role_profile.employee_code = employee_code
        if hasattr(role_profile, "education_info"):
            role_profile.education_info = education_info
        if hasattr(role_profile, "experience_years") and experience_years is not None:
            role_profile.experience_years = experience_years
        if hasattr(role_profile, "verification_status"):
            role_profile.verification_status = VERIFICATION_STATUS_PENDING
        if hasattr(role_profile, "code_verified_at"):
            role_profile.code_verified_at = timezone.now()

        role_profile.full_clean()
        role_profile.save()

    if registration_type not in {REGISTRATION_TYPE_STUDENT, REGISTRATION_TYPE_TEACHER} and role_profile:
        if hasattr(role_profile, "position"):
            role_profile.position = position
        if hasattr(role_profile, "work_place"):
            role_profile.work_place = work_place
        role_profile.full_clean()
        role_profile.save()

    return user


def authenticate_user(*, email: str, password: str, request=None):
    """
    Аутентифицирует пользователя по email и паролю.
    """
    email = (email or "").strip().lower()
    user = authenticate(
        request=request,
        email=email,
        password=password,
    )

    if not user:
        raise ValidationError({"detail": _("Неверная эл. почта или пароль.")})

    if not user.is_active:
        raise ValidationError({"detail": _("Учетная запись деактивирована.")})

    return user


def build_verify_email_token(user) -> str:
    """
    Создаёт токен подтверждения email.
    """
    payload = {
        "user_id": user.id,
        "email": user.email,
    }
    return signing.dumps(payload, salt=VERIFY_EMAIL_SALT)


def read_verify_email_token(token: str, max_age: int | None = None) -> dict:
    """
    Читает токен подтверждения email.
    """
    max_age = max_age or int(getattr(settings, "VERIFY_EMAIL_TOKEN_TTL", 60 * 60 * 24))
    try:
        return signing.loads(token, salt=VERIFY_EMAIL_SALT, max_age=max_age)
    except signing.SignatureExpired as exc:
        raise ValidationError({"token": _("Срок действия токена истёк.")}) from exc
    except signing.BadSignature as exc:
        raise ValidationError({"token": _("Некорректный токен.")}) from exc


def verify_user_email_by_token(token: str):
    """
    Подтверждает email пользователя по токену.
    """
    payload = read_verify_email_token(token)
    try:
        user = User.objects.get(
            id=payload["user_id"],
            email=payload["email"],
        )
    except User.DoesNotExist as exc:
        raise ValidationError({"token": _("Пользователь по токену не найден.")}) from exc

    mark_user_email_verified(user)

    if user.onboarding_status == ONBOARDING_STATUS_DRAFT:
        user.onboarding_status = ONBOARDING_STATUS_PENDING
        user.save(update_fields=["onboarding_status", "updated_at"])

    return user


def build_password_reset_token(user) -> str:
    """
    Создаёт токен сброса пароля.
    """
    payload = {
        "user_id": user.id,
        "email": user.email,
    }
    return signing.dumps(payload, salt=RESET_PASSWORD_SALT)


def read_password_reset_token(token: str, max_age: int | None = None) -> dict:
    """
    Читает токен сброса пароля.
    """
    max_age = max_age or int(getattr(settings, "RESET_PASSWORD_TOKEN_TTL", 60 * 60 * 3))
    try:
        return signing.loads(token, salt=RESET_PASSWORD_SALT, max_age=max_age)
    except signing.SignatureExpired as exc:
        raise ValidationError({"token": _("Срок действия токена истёк.")}) from exc
    except signing.BadSignature as exc:
        raise ValidationError({"token": _("Некорректный токен.")}) from exc


def reset_password_by_token(*, token: str, password: str, password_repeat: str):
    """
    Сбрасывает пароль пользователя по токену.
    """
    if password != password_repeat:
        raise ValidationError({"password_repeat": _("Пароли не совпадают.")})

    payload = read_password_reset_token(token)

    try:
        user = User.objects.get(
            id=payload["user_id"],
            email=payload["email"],
            is_active=True,
        )
    except User.DoesNotExist as exc:
        raise ValidationError({"token": _("Пользователь по токену не найден.")}) from exc

    password_validation.validate_password(password, user=user)
    user.set_password(password)
    user.save(update_fields=["password", "updated_at"])
    return user


def change_user_password(
    *,
    user,
    old_password: str,
    new_password: str,
    new_password_confirm: str,
):
    """
    Меняет пароль авторизованного пользователя.
    """
    if not user.check_password(old_password):
        raise ValidationError({"old_password": _("Текущий пароль указан неверно.")})

    if new_password != new_password_confirm:
        raise ValidationError({"new_password_confirm": _("Пароли не совпадают.")})

    if old_password == new_password:
        raise ValidationError(
            {"new_password": _("Новый пароль не может совпадать с текущим.")}
        )

    password_validation.validate_password(new_password, user=user)
    user.set_password(new_password)
    user.save(update_fields=["password", "updated_at"])
    return user
