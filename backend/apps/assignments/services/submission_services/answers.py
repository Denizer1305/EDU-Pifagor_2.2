from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.assignments.models import Submission, SubmissionAnswer


@transaction.atomic
def save_submission_answer(
    *,
    submission: Submission,
    question,
    answer_text: str = "",
    answer_json: dict | None = None,
    selected_options_json: list | None = None,
    numeric_answer=None,
) -> SubmissionAnswer:
    """Создаёт или обновляет ответ студента на вопрос."""

    if submission.status not in {
        Submission.StatusChoices.DRAFT,
        Submission.StatusChoices.IN_PROGRESS,
        Submission.StatusChoices.RETURNED_FOR_REVISION,
    }:
        raise ValidationError("Нельзя редактировать ответы после отправки работы.")

    answer, _ = SubmissionAnswer.objects.get_or_create(
        submission=submission,
        question=question,
    )
    answer.answer_text = answer_text
    answer.answer_json = answer_json or {}
    answer.selected_options_json = selected_options_json or []
    answer.numeric_answer = numeric_answer
    answer.full_clean()
    answer.save()

    return answer
