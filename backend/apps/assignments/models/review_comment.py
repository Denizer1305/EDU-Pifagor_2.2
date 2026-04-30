from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.assignments.models.base import TimeStampedModel


class ReviewComment(TimeStampedModel):
    class CommentTypeChoices(models.TextChoices):
        GENERAL = "general", "Общий комментарий"
        QUESTION_COMMENT = "question_comment", "Комментарий к вопросу"
        ERROR_NOTE = "error_note", "Замечание об ошибке"
        IMPROVEMENT_NOTE = "Рекомендация"
        SCORE_COMMENT = "Комментарий к баллу"

    review = models.ForeignKey(
        "assignments.SubmissionReview",
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Проверка",
    )
    question = models.ForeignKey(
        "assignments.AssignmentQuestion",
        on_delete=models.CASCADE,
        related_name="review_comments",
        null=True,
        blank=True,
        verbose_name="Вопрос",
    )
    submission_answer = models.ForeignKey(
        "assignments.SubmissionAnswer",
        on_delete=models.CASCADE,
        related_name="review_comments",
        null=True,
        blank=True,
        verbose_name="Ответ",
    )
    comment_type = models.CharField(
        max_length=32,
        choices=CommentTypeChoices.choices,
        default=CommentTypeChoices.GENERAL,
        verbose_name="Тип комментария",
    )
    message = models.TextField(
        verbose_name="Сообщение",
    )
    score_delta = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Корректировка балла",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_review_comments",
        null=True,
        blank=True,
        verbose_name="Создал",
    )

    class Meta:
        db_table = "assignments_review_comment"
        verbose_name = "Комментарий проверки"
        verbose_name_plural = "Комментарии проверки"

    def clean(self):
        errors: dict[str, str] = {}

        if self.submission_answer_id and self.submission_answer.submission_id != self.review.submission_id:
            errors["submission_answer"] = "Ответ должен относиться к сдаче выбранной проверки."

        if self.question_id and self.question.assignment_id != self.review.submission.assignment_id:
            errors["question"] = "Вопрос должен относиться к работе выбранной сдачи."

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return self.message[:80]
