from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.assignments.models.base import TimeStampedModel, generate_uid, normalize_text


class Assignment(TimeStampedModel):
    class AssignmentKindChoices(models.TextChoices):
        HOMEWORK = "homework", "Домашняя работа"
        INDEPENDENT_WORK = "independent_work", "Самостоятельная работа"
        CONTROL_WORK = "control_work", "Контрольная работа"
        VERIFICATION_WORK = "verification_work", "Проверочная работа"
        TEST = "test", "Тест"
        QUIZ = "quiz", "Квиз"
        PRACTICAL_WORK = "practical_work", "Практическая работа"
        LABORATORY_WORK = "laboratory_work", "Лабораторная работа"
        PROJECT = "project", "Проект"
        CREDIT = "credit", "Зачёт"
        DIFFERENTIATED_CREDIT = "differentiated_credit", "Дифференцированный зачёт"
        EXAM = "exam", "Экзамен"
        MOCK_EXAM = "mock_exam", "Пробный экзамен"
        DEMO_EXAM = "demo_exam", "Демоэкзамен"
        COURSEWORK = "coursework", "Курсовая работа"
        COURSE_PROJECT = "course_project", "Курсовой проект"
        PRACTICE_REPORT = "practice_report", "Отчёт по практике"
        PRACTICE_DEFENSE = "practice_defense", "Защита практики"

    class ControlScopeChoices(models.TextChoices):
        LEARNING_ACTIVITY = "learning_activity", "Учебная активность"
        CURRENT_CONTROL = "current_control", "Текущий контроль"
        INTERIM_ATTESTATION = "interim_attestation", "Промежуточная аттестация"
        FINAL_PREPARATION = "final_preparation", "Подготовка к итоговой аттестации"
        STATE_EXAM_PREPARATION = "state_exam_preparation", "Подготовка к госэкзаменам"
        QUALIFICATION_ASSESSMENT = "qualification_assessment", "Квалификационная оценка"

    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Черновик"
        PUBLISHED = "published", "Опубликовано"
        ARCHIVED = "archived", "Архив"

    class VisibilityChoices(models.TextChoices):
        PRIVATE = "private", "Приватная"
        COURSE_ONLY = "course_only", "Только в рамках курса"
        ASSIGNED_ONLY = "assigned_only", "Только назначенным"
        PUBLIC_LINK = "public_link", "По публичной ссылке"

    class EducationLevelChoices(models.TextChoices):
        SCHOOL = "school", "Школа"
        SPO = "spo", "СПО"
        HIGHER = "higher", "Высшее образование"

    uid = models.UUIDField(
        default=generate_uid,
        unique=True,
        editable=False,
        verbose_name="UID",
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
    instructions = models.TextField(
        blank=True,
        verbose_name="Инструкция",
    )

    course = models.ForeignKey(
        "course.Course",
        on_delete=models.CASCADE,
        related_name="educational_assignments",
        null=True,
        blank=True,
        verbose_name="Курс",
    )
    lesson = models.ForeignKey(
        "course.CourseLesson",
        on_delete=models.CASCADE,
        related_name="educational_assignments",
        null=True,
        blank=True,
        verbose_name="Урок",
    )
    subject = models.ForeignKey(
        "organizations.Subject",
        on_delete=models.SET_NULL,
        related_name="educational_assignments",
        null=True,
        blank=True,
        verbose_name="Предмет",
    )
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        related_name="educational_assignments",
        null=True,
        blank=True,
        verbose_name="Организация",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_educational_assignments",
        verbose_name="Автор",
    )

    assignment_kind = models.CharField(
        max_length=64,
        choices=AssignmentKindChoices.choices,
        default=AssignmentKindChoices.HOMEWORK,
        verbose_name="Тип работы",
    )
    control_scope = models.CharField(
        max_length=64,
        choices=ControlScopeChoices.choices,
        default=ControlScopeChoices.LEARNING_ACTIVITY,
        verbose_name="Контур контроля",
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
    education_level = models.CharField(
        max_length=32,
        choices=EducationLevelChoices.choices,
        default=EducationLevelChoices.SCHOOL,
        verbose_name="Уровень образования",
    )

    is_template = models.BooleanField(
        default=False,
        verbose_name="Шаблон",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активно",
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

    class Meta:
        db_table = "assignments_assignment"
        verbose_name = "Работа"
        verbose_name_plural = "Работы"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("status", "is_active")),
            models.Index(fields=("assignment_kind",)),
            models.Index(fields=("control_scope",)),
            models.Index(fields=("education_level",)),
            models.Index(fields=("course", "lesson")),
            models.Index(fields=("organization", "subject")),
            models.Index(fields=("author",)),
        ]

    def clean(self):
        errors: dict[str, str] = {}

        self.title = normalize_text(self.title)
        self.subtitle = normalize_text(self.subtitle)

        if not self.title:
            errors["title"] = "Название работы обязательно."

        if self.lesson_id and self.course_id and self.lesson.course_id != self.course_id:
            errors["lesson"] = "Урок должен принадлежать выбранному курсу."

        if self.lesson_id and not self.course_id:
            self.course = self.lesson.course

        if self.status == self.StatusChoices.ARCHIVED and self.is_active:
            errors["status"] = "Архивная работа не может быть активной."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.status == self.StatusChoices.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()

        if self.status == self.StatusChoices.ARCHIVED and self.archived_at is None:
            self.archived_at = timezone.now()
            self.is_active = False

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title
