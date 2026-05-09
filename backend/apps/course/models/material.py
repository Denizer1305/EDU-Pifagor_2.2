from __future__ import annotations

from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models

from apps.course.models.base import OrderedModel, TimeStampedModel, normalize_text


def course_material_upload_to(instance, filename):
    ext = filename.split(".")[-1].lower() if "." in filename else "bin"
    return f"course/materials/{uuid4().hex}.{ext}"


class CourseMaterial(TimeStampedModel, OrderedModel):
    class MaterialTypeChoices(models.TextChoices):
        FILE = "file", "Файл"
        LINK = "link", "Ссылка"
        IMAGE = "image", "Изображение"
        PRESENTATION = "presentation", "Презентация"
        DOCUMENT = "document", "Документ"
        ARCHIVE = "archive", "Архив"
        OTHER = "other", "Другое"

    class Meta:
        db_table = "course_material"
        verbose_name = "Материал курса"
        verbose_name_plural = "Материалы курса"
        ordering = ("course", "lesson", "order", "id")
        indexes = [
            models.Index(fields=("course",)),
            models.Index(fields=("lesson",)),
            models.Index(fields=("material_type",)),
        ]

    course = models.ForeignKey(
        "course.Course",
        on_delete=models.CASCADE,
        related_name="materials",
        null=True,
        blank=True,
        verbose_name="Курс",
    )
    lesson = models.ForeignKey(
        "course.CourseLesson",
        on_delete=models.CASCADE,
        related_name="materials",
        null=True,
        blank=True,
        verbose_name="Урок",
    )

    title = models.CharField(
        max_length=255,
        verbose_name="Название",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
    )
    material_type = models.CharField(
        max_length=32,
        choices=MaterialTypeChoices.choices,
        default=MaterialTypeChoices.FILE,
        verbose_name="Тип материала",
    )
    file = models.FileField(
        upload_to=course_material_upload_to,
        null=True,
        blank=True,
        verbose_name="Файл",
    )
    external_url = models.URLField(
        blank=True,
        verbose_name="Внешняя ссылка",
    )
    is_downloadable = models.BooleanField(
        default=True,
        verbose_name="Можно скачать",
    )
    is_visible = models.BooleanField(
        default=True,
        verbose_name="Виден пользователю",
    )

    def clean(self):
        errors = {}

        self.title = normalize_text(self.title)
        self.description = normalize_text(self.description)

        if not self.course and not self.lesson:
            errors["course"] = "Нужно указать курс или урок."

        if self.course and self.lesson and self.lesson.course_id != self.course_id:
            errors["lesson"] = "Урок должен принадлежать выбранному курсу."

        if self.lesson and not self.course:
            self.course = self.lesson.course

        if (
            self.material_type
            in {
                self.MaterialTypeChoices.FILE,
                self.MaterialTypeChoices.IMAGE,
                self.MaterialTypeChoices.PRESENTATION,
                self.MaterialTypeChoices.DOCUMENT,
                self.MaterialTypeChoices.ARCHIVE,
            }
            and not self.file
        ):
            errors["file"] = "Для выбранного типа материала нужно загрузить файл."

        if (
            self.material_type == self.MaterialTypeChoices.LINK
            and not self.external_url
        ):
            errors["external_url"] = "Для материала-ссылки нужно указать URL."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.lesson and not self.course:
            self.course = self.lesson.course

        self.title = normalize_text(self.title)
        self.description = normalize_text(self.description)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title
