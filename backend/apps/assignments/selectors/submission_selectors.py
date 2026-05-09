from __future__ import annotations

from django.db.models import Prefetch, Q, QuerySet

from apps.assignments.models import (
    Submission,
    SubmissionAnswer,
    SubmissionAttachment,
    SubmissionAttempt,
)


def get_submission_base_queryset() -> QuerySet[Submission]:
    return Submission.objects.select_related(
        "publication",
        "assignment",
        "variant",
        "student",
        "checked_by",
        "publication__course",
        "publication__lesson",
    ).order_by("-created_at")


def get_submission_detail_queryset() -> QuerySet[Submission]:
    return get_submission_base_queryset().prefetch_related(
        Prefetch(
            "answers",
            queryset=SubmissionAnswer.objects.select_related("question").order_by(
                "question__order", "id"
            ),
        ),
        Prefetch(
            "attachments",
            queryset=SubmissionAttachment.objects.select_related("question").order_by(
                "-created_at"
            ),
        ),
        Prefetch(
            "attempts",
            queryset=SubmissionAttempt.objects.order_by("attempt_number", "id"),
        ),
        "review__reviewer",
        "review__comments__question",
        "review__comments__submission_answer",
        "review__comments__created_by",
    )


def get_submissions_queryset(
    *,
    search: str = "",
    status: str = "",
    assignment_id: int | None = None,
    publication_id: int | None = None,
    student_id: int | None = None,
    checked_by_id: int | None = None,
    is_late: bool | None = None,
    passed: bool | None = None,
) -> QuerySet[Submission]:
    queryset = get_submission_base_queryset()

    if search:
        queryset = queryset.filter(
            Q(assignment__title__icontains=search)
            | Q(student__email__icontains=search)
            | Q(student__profile__last_name__icontains=search)
            | Q(student__profile__first_name__icontains=search)
            | Q(publication__assignment__title__icontains=search)
        )

    if status:
        queryset = queryset.filter(status=status)

    if assignment_id:
        queryset = queryset.filter(assignment_id=assignment_id)

    if publication_id:
        queryset = queryset.filter(publication_id=publication_id)

    if student_id:
        queryset = queryset.filter(student_id=student_id)

    if checked_by_id:
        queryset = queryset.filter(checked_by_id=checked_by_id)

    if is_late is not None:
        queryset = queryset.filter(is_late=is_late)

    if passed is not None:
        queryset = queryset.filter(passed=passed)

    return queryset


def get_student_submissions_queryset(
    *,
    student,
    search: str = "",
    status: str = "",
    course_id: int | None = None,
    lesson_id: int | None = None,
) -> QuerySet[Submission]:
    queryset = get_submissions_queryset(
        search=search,
        status=status,
        student_id=student.id,
    )

    if course_id:
        queryset = queryset.filter(publication__course_id=course_id)

    if lesson_id:
        queryset = queryset.filter(publication__lesson_id=lesson_id)

    return queryset


def get_submission_by_id(*, submission_id: int) -> Submission | None:
    return get_submission_detail_queryset().filter(id=submission_id).first()


def get_submission_answers_queryset(
    *,
    submission_id: int | None = None,
    question_id: int | None = None,
    review_status: str = "",
) -> QuerySet[SubmissionAnswer]:
    queryset = SubmissionAnswer.objects.select_related(
        "submission",
        "question",
    ).order_by("question__order", "id")

    if submission_id:
        queryset = queryset.filter(submission_id=submission_id)

    if question_id:
        queryset = queryset.filter(question_id=question_id)

    if review_status:
        queryset = queryset.filter(review_status=review_status)

    return queryset


def get_submission_attachments_queryset(
    *,
    submission_id: int | None = None,
    question_id: int | None = None,
) -> QuerySet[SubmissionAttachment]:
    queryset = SubmissionAttachment.objects.select_related(
        "submission",
        "question",
    ).order_by("-created_at")

    if submission_id:
        queryset = queryset.filter(submission_id=submission_id)

    if question_id:
        queryset = queryset.filter(question_id=question_id)

    return queryset


def get_submission_attempts_queryset(
    *,
    submission_id: int | None = None,
    status: str = "",
) -> QuerySet[SubmissionAttempt]:
    queryset = SubmissionAttempt.objects.select_related("submission").order_by(
        "attempt_number", "id"
    )

    if submission_id:
        queryset = queryset.filter(submission_id=submission_id)

    if status:
        queryset = queryset.filter(status=status)

    return queryset
