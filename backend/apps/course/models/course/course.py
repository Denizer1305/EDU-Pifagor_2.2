from __future__ import annotations

from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.course.models.base import (
    TimeStampedModel,
    build_unique_slug,
    generate_code,
    normalize_text,
)


def course_cover_upload_to(instance, filename: str) -> str:
    """Формирует путь загрузки обложки курса."""

    ext = filename.split(".")[-1].lower() if "." in filename else "jpg"
    return f"course/covers/{uuid4().hex}.{ext}"


course_cover_upload_to.__module__ = "apps.course.models.course"


class Course(TimeStampedModel):
    class CourseTypeChoices(models.TextChoices):
        ACADEMIC = "academic", "Учебный курс"
        AUTHOR = "author", "Авторский курс"
        EXAM_PREP = "exam_prep", "Подготовка к экзамену"
        INTENSIVE = "intensive", "Интенсив"
        CLUB = "club", "Клуб / факультатив"

    class OriginChoices(models.TextChoices):
        MANUAL = "manual", "Создан вручную"
        GROUP_SUBJECT = "group_subject", "На основе учебного контура"
        TEMPLATE = "template", "На основе шаблона"
        IMPORT = "import", "Импорт"

    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Черновик"
        PUBLISHED = "published", "Опубликован"
        ARCHIVED = "archived", "Архив"

    class VisibilityChoices(models.TextChoices):
        PRIVATE = "private", "Приватный"
        ASSIGNED_ONLY = "assigned_only", "Только по назначению"
        ORGANIZATION = "organization", "Внутри организации"
        PUBLIC_LINK = "public_link", "По публичной ссылке"

    class LevelChoices(models.TextChoices):
        BEGINNER = "beginner", "Начальный"
        BASIC = "basic", "Базовый"
        ADVANCED = "advanced", "Продвинутый"
        EXAM = "exam", "Экзаменационный"

    class Meta:
        db_table = "course"
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("status",)),
            models.Index(fields=("visibility",)),
            models.Index(fields=("course_type",)),
            models.Index(fields=("author",)),
            models.Index(fields=("organization",)),
            models.Index(fields=("subject",)),
            models.Index(fields=("academic_year",)),
        ]

    uid = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False,
        verbose_name="UUID",
    )
    code = models.CharField(
        max_length=32,
        unique=True,
        blank=True,
        verbose_name="Код курса",
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name="Slug",
    )

    title = models.CharField(
        max_length=255,
        verbose_name="Название",
    )
    subtitle = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Подзаголовок",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )

    course_type = models.CharField(
        max_length=32,
        choices=CourseTypeChoices.choices,
        default=CourseTypeChoices.AUTHOR,
        verbose_name="Тип курса",
    )
    origin = models.CharField(
        max_length=32,
        choices=OriginChoices.choices,
        default=OriginChoices.MANUAL,
        verbose_name="Источник",
    )
    status = models.CharField(
        max_length=32,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        verbose_name="Статус",
    )
    visibility = models.CharField(
        max_length=32,
        choices=VisibilityChoices.choices,
        default=VisibilityChoices.ASSIGNED_ONLY,
        verbose_name="Видимость",
    )
    level = models.CharField(
        max_length=32,
        choices=LevelChoices.choices,
        default=LevelChoices.BASIC,
        verbose_name="Уровень",
    )
    language = models.CharField(
        max_length=12,
        default="ru",
        verbose_name="Язык",
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="authored_courses",
        verbose_name="Автор",
    )
    teachers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="course.CourseTeacher",
        related_name="teaching_courses",
        blank=True,
        verbose_name="Преподаватели",
    )

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="course",
        verbose_name="Организация",
    )
    subject = models.ForeignKey(
        "organizations.Subject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="course",
        verbose_name="Предмет",
    )
    academic_year = models.ForeignKey(
        "education.AcademicYear",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="course",
        verbose_name="Учебный год",
    )
    period = models.ForeignKey(
        "education.EducationPeriod",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="course",
        verbose_name="Учебный период",
    )
    group_subject = models.ForeignKey(
        "education.GroupSubject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="course",
        verbose_name="Связь с учебным предметом группы",
    )

    cover_image = models.ImageField(
        upload_to=course_cover_upload_to,
        null=True,
        blank=True,
        verbose_name="Обложка",
    )

    is_template = models.BooleanField(
        default=False,
        verbose_name="Шаблон",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
    )
    allow_self_enrollment = models.BooleanField(
        default=False,
        verbose_name="Разрешить самостоятельную запись",
    )
    enrollment_code = models.CharField(
        max_length=32,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Код записи",
    )

    estimated_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Плановая длительность (мин)",
    )

    starts_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата начала",
    )
    ends_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата окончания",
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата публикации",
    )
    archived_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Дата архивации",
    )

    def clean(self):
        errors = {}

        self.title = normalize_text(self.title)
        self.subtitle = normalize_text(self.subtitle)
        self.description = normalize_text(self.description)

        if self.starts_at and self.ends_at and self.ends_at < self.starts_at:
            errors["ends_at"] = "Дата окончания не может быть раньше даты начала."

        if self.group_subject:
            if self.subject_id and self.subject_id != self.group_subject.subject_id:
                errors["subject"] = (
                    "Предмет курса не совпадает с предметом group_subject."
                )

            if (
                self.academic_year_id
                and self.academic_year_id != self.group_subject.academic_year_id
            ):
                errors["academic_year"] = (
                    "Учебный год курса не совпадает с group_subject."
                )

            group = getattr(self.group_subject, "group", None)
            if (
                group
                and self.organization_id
                and self.organization_id != group.organization_id
            ):
                errors["organization"] = (
                    "Организация курса не совпадает с организацией группы."
                )

        if self.status == self.StatusChoices.PUBLISHED and not self.title:
            errors["title"] = "Нельзя публиковать курс без названия."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.title = normalize_text(self.title)
        self.subtitle = normalize_text(self.subtitle)
        self.description = normalize_text(self.description)

        if not self.code:
            self.code = generate_code("CRS")

        if not self.slug:
            self.slug = build_unique_slug(
                self.__class__,
                self.title or self.code,
                instance=self,
            )

        if self.status == self.StatusChoices.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()

        if self.status == self.StatusChoices.ARCHIVED and self.archived_at is None:
            self.archived_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title
