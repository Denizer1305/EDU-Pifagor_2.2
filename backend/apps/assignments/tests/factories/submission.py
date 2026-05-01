from __future__ import annotations

from decimal import Decimal

from django.utils import timezone

from apps.assignments.models import (
    Submission,
    SubmissionAnswer,
    SubmissionAttachment,
    SubmissionAttempt,
)
from apps.assignments.tests.factories.assignment_structure import (
    create_assignment_question,
)
from apps.assignments.tests.factories.common import create_test_pdf_file
from apps.assignments.tests.factories.publication import create_assignment_publication
from apps.assignments.tests.factories.users import create_student_user


def create_submission(
    publication=None,
    assignment=None,
    student=None,
    variant=None,
    **kwargs,
):
    """Создаёт сдачу работы студентом."""

    publication = publication or create_assignment_publication()
    assignment = assignment or publication.assignment
    student = student or create_student_user()
    variant = variant or assignment.variants.first()

    status_value = kwargs.pop("status", Submission.StatusChoices.IN_PROGRESS)

    submitted_at_default = None
    if status_value != Submission.StatusChoices.IN_PROGRESS:
        submitted_at_default = timezone.now()

    return Submission.objects.create(
        publication=publication,
        assignment=assignment,
        variant=variant,
        student=student,
        status=status_value,
        attempt_number=kwargs.pop("attempt_number", 1),
        started_at=kwargs.pop("started_at", timezone.now()),
        submitted_at=kwargs.pop("submitted_at", submitted_at_default),
        completed_at=kwargs.pop("completed_at", None),
        time_spent_minutes=kwargs.pop("time_spent_minutes", 0),
        is_late=kwargs.pop("is_late", False),
        late_minutes=kwargs.pop("late_minutes", 0),
        auto_score=kwargs.pop("auto_score", Decimal("0")),
        manual_score=kwargs.pop("manual_score", Decimal("0")),
        final_score=kwargs.pop("final_score", Decimal("0")),
        percentage=kwargs.pop("percentage", Decimal("0")),
        passed=kwargs.pop("passed", False),
        checked_at=kwargs.pop("checked_at", None),
        checked_by=kwargs.pop("checked_by", None),
        **kwargs,
    )


def create_submission_answer(submission=None, question=None, **kwargs):
    """Создаёт ответ студента."""

    submission = submission or create_submission()
    question = question or create_assignment_question(assignment=submission.assignment)

    return SubmissionAnswer.objects.create(
        submission=submission,
        question=question,
        answer_text=kwargs.pop("answer_text", "Ответ"),
        answer_json=kwargs.pop("answer_json", {}),
        selected_options_json=kwargs.pop("selected_options_json", []),
        numeric_answer=kwargs.pop("numeric_answer", None),
        is_correct=kwargs.pop("is_correct", None),
        auto_score=kwargs.pop("auto_score", Decimal("0")),
        manual_score=kwargs.pop("manual_score", Decimal("0")),
        final_score=kwargs.pop("final_score", Decimal("0")),
        review_status=kwargs.pop("review_status", "pending"),
        **kwargs,
    )


def create_submission_attachment(submission=None, question=None, **kwargs):
    """Создаёт вложение к сдаче студента."""

    submission = submission or create_submission()
    file_obj = kwargs.pop(
        "file",
        create_test_pdf_file(
            name="answer.pdf",
            content=b"%PDF-1.4 answer file",
        ),
    )

    return SubmissionAttachment.objects.create(
        submission=submission,
        question=question,
        file=file_obj,
        original_name=kwargs.pop("original_name", "answer.pdf"),
        mime_type=kwargs.pop("mime_type", "application/pdf"),
        file_size=kwargs.pop("file_size", 128),
        attachment_type=kwargs.pop("attachment_type", "other"),
        **kwargs,
    )


def create_submission_attempt(submission=None, **kwargs):
    """Создаёт запись попытки сдачи."""

    submission = submission or create_submission()

    return SubmissionAttempt.objects.create(
        submission=submission,
        attempt_number=kwargs.pop("attempt_number", submission.attempt_number),
        started_at=kwargs.pop("started_at", timezone.now()),
        submitted_at=kwargs.pop("submitted_at", None),
        time_spent_minutes=kwargs.pop("time_spent_minutes", 0),
        status=kwargs.pop("status", submission.status),
        snapshot_json=kwargs.pop("snapshot_json", {}),
        **kwargs,
    )
