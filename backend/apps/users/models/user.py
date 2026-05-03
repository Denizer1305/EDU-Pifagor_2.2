from __future__ import annotations

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Базовый класс для управления пользователем.

    Создание обычного пользователя, где поле email является его username и
    является уникальным.
    Создание superuser - администратора с абсолютными правами.
    """

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        """Создает пользователя с заданными атрибутами."""
        if not email:
            raise ValueError(_("Адрес эл.почты обязателен для регистрации."))

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Создает пользователя с заданными атрибутами."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValidationError(_("У админа is_staff должен быть True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValidationError(_("У админа is_superuser должен быть True."))

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Базовая модель управления пользователем платформы.

    В модели хранится толкьо данные для системы и аутентификации.
    Профильные и ролевые данные данные вынесены в отдельные модели.
    """

    class RegistrationTypeChoices(models.TextChoices):
        UNKNOWN = "unknown", _("Не указан")
        STUDENT = "student", _("Студент")
        PARENT = "parent", _("Родитель")
        TEACHER = "teacher", _("Преподаватель")

    class OnboardingStatusChoices(models.TextChoices):
        DRAFT = "draft", _("Черновик")
        PENDING = "pending", _("Ожидает подтверждения")
        ACTIVE = "active", _("Активирован")
        REJECTED = "rejected", _("Отклонен")
        BLOCKED = "blocked", _("Заблокирован")

    email = models.EmailField(
        _("Основная эл.почта"),
        unique=True,
        db_index=True,
    )
    reset_email = models.EmailField(
        _("Резервная почта для восстановления"),
        blank=True,
    )

    registration_type = models.CharField(
        _("Тип регистрации"),
        max_length=32,
        choices=RegistrationTypeChoices.choices,
        default=RegistrationTypeChoices.UNKNOWN,
    )

    onboarding_status = models.CharField(
        _("Статус онбординга"),
        max_length=32,
        choices=OnboardingStatusChoices.choices,
        default=OnboardingStatusChoices.DRAFT,
    )

    onboarding_completed_at = models.DateTimeField(
        _("Дата завершения онбординга"),
        blank=True,
        null=True,
    )

    reviewed_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="reviewed_users",
        verbose_name=_("Проверил"),
        blank=True,
        null=True,
    )

    reviewed_at = models.DateTimeField(
        _("Дата проверки"),
        blank=True,
        null=True,
    )

    review_comment = models.TextField(
        _("Комментарий проверки"),
        blank=True,
    )

    is_email_verified = models.BooleanField(
        _("Почта подтверждена"),
        default=False,
    )
    is_active = models.BooleanField(
        _("Активен"),
        default=True,
    )
    is_staff = models.BooleanField(
        _("Доступ в административную панель"),
        default=False,
    )
    created_at = models.DateTimeField(
        _("Дата создания"),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _("Дата обновления"),
        auto_now=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users_user"
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        ordering = ("-created_at",)

    def __str__(self):
        """Возвращает строковое представление объекта."""
        return self.email

    @property
    def full_name(self) -> str:
        """Возвращает полное имя пользователя из связанного профиля."""

        if not self.pk:
            return ""

        Profile = self._meta.apps.get_model("users", "Profile")
        profile = (
            Profile.objects.filter(user_id=self.pk)
            .only("last_name", "first_name", "patronymic")
            .first()
        )

        if profile is None:
            return ""

        return profile.full_name

    def clean(self) -> None:
        """Выполняет валидацию и нормализацию полей."""
        super().clean()

        if self.email:
            self.email = self.email.lower().strip()

        if self.reset_email:
            self.reset_email = self.reset_email.lower().strip()

        if self.reset_email and self.email and self.reset_email == self.email:
            raise ValidationError(
                {"reset_email": _("Резервная почта не может совпадать с основной.")}
            )

        if self.review_comment:
            self.review_comment = self.review_comment.strip()

    @property
    def is_fully_onboarded(self) -> bool:
        return self.onboarding_status == self.OnboardingStatusChoices.ACTIVE

    @property
    def requires_verification(self) -> bool:
        return self.onboarding_status == self.OnboardingStatusChoices.PENDING
