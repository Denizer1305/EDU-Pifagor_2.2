from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import models

from apps.course.models.base import OrderedModel, TimeStampedModel, normalize_text


class CourseLesson(TimeStampedModel, OrderedModel):
    class LessonTypeChoices(models.TextChoices):
        VIDEO = "video", "Видео"
        TEXT = "text", "Текстовый урок"
        PRACTICE = "practice", "Практика"
        TEST = "test", "Тест"
        HOMEWORK = "homework", "Домашняя работа"
        WEBINAR = "webinar", "Вебинар / занятие"
        FILE = "file", "Файл / материал"
        LINK = "link", "Ссылка"

    class Meta:
        db_table = "course_lesson"
        verbose_name = "Урок курса"
        verbose_name_plural = "Уроки курса"
        ordering = ("module", "order", "id")
        constraints = [
            models.UniqueConstraint(
                fields=("module", "order"),
                name="unique_course_lesson_order",
            ),
        ]
        indexes = [
            models.Index(fields=("course", "lesson_type")),
            models.Index(fields=("module", "is_published")),
        ]

    course = models.ForeignKey(
        "course.Course",
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Курс",
    )
    module = models.ForeignKey(
        "course.CourseModule",
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Модуль",
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
    content = models.TextField(
        blank=True,
        verbose_name="Контент",
    )

    lesson_type = models.CharField(
        max_length=32,
        choices=LessonTypeChoices.choices,
        default=LessonTypeChoices.TEXT,
        verbose_name="Тип урока",
    )

    estimated_minutes = models.PositiveIntegerField(
        default=0,
        verbose_name="Плановая длительность (мин)",
    )
    is_required = models.BooleanField(
        default=True,
        verbose_name="Обязательный",
    )
    is_preview = models.BooleanField(
        default=False,
        verbose_name="Доступен в превью",
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликован",
    )

    available_from = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Доступен с",
    )
    video_url = models.URLField(
        blank=True,
        verbose_name="Ссылка на видео",
    )
    external_url = models.URLField(
        blank=True,
        verbose_name="Внешняя ссылка",
    )

    def clean(self):
        errors = {}

        self.title = normalize_text(self.title)
        self.subtitle = normalize_text(self.subtitle)
        self.description = normalize_text(self.description)

        if self.order < 1:
            errors["order"] = "Порядок урока должен быть больше нуля."

        if self.module_id and self.course_id and self.module.course_id != self.course_id:
            errors["module"] = "Модуль должен принадлежать тому же курсу, что и урок."

        if self.lesson_type == self.LessonTypeChoices.VIDEO and not self.video_url:
            errors["video_url"] = "Для видеоурока необходимо указать ссылку на видео."

        if self.lesson_type in {self.LessonTypeChoices.LINK, self.LessonTypeChoices.WEBINAR} and not self.external_url:
            errors["external_url"] = "Для этого типа урока нужна внешняя ссылка."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.title = normalize_text(self.title)
        self.subtitle = normalize_text(self.subtitle)
        self.description = normalize_text(self.description)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title
