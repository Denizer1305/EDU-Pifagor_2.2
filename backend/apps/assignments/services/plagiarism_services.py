from __future__ import annotations

from django.db import transaction
from django.utils import timezone

from apps.assignments.models import PlagiarismCheck


@transaction.atomic
def create_or_get_plagiarism_check(submission) -> PlagiarismCheck:
    check, _ = PlagiarismCheck.objects.get_or_create(submission=submission)
    return check


@transaction.atomic
def start_plagiarism_check(submission) -> PlagiarismCheck:
    check = create_or_get_plagiarism_check(submission)
    check.status = PlagiarismCheck.StatusChoices.IN_PROGRESS
    check.full_clean()
    check.save()
    return check


@transaction.atomic
def complete_plagiarism_check(
    *,
    submission,
    similarity_percent,
    report_url: str = "",
    raw_result_json: dict | None = None,
) -> PlagiarismCheck:
    check = create_or_get_plagiarism_check(submission)
    check.status = PlagiarismCheck.StatusChoices.COMPLETED
    check.similarity_percent = similarity_percent
    check.report_url = report_url
    check.raw_result_json = raw_result_json or {}
    check.checked_at = timezone.now()
    check.full_clean()
    check.save()
    return check


@transaction.atomic
def fail_plagiarism_check(
    *,
    submission,
    raw_result_json: dict | None = None,
) -> PlagiarismCheck:
    check = create_or_get_plagiarism_check(submission)
    check.status = PlagiarismCheck.StatusChoices.ERROR
    check.raw_result_json = raw_result_json or {}
    check.checked_at = timezone.now()
    check.full_clean()
    check.save()
    return check
