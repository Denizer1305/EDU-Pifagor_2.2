from __future__ import annotations

from django.apps import apps

from apps.assignments.selectors.analytics_selectors import (
    get_assignment_statistics,
    get_publication_statistics,
)
from apps.assignments.services.grading_services import calculate_submission_scores
from apps.assignments.services.plagiarism_services import start_plagiarism_check


def recalculate_submission_scores_task(submission_id: int):
    Submission = apps.get_model("assignments", "Submission")
    submission = Submission.objects.filter(id=submission_id).first()
    if submission is None:
        return None
    return calculate_submission_scores(submission)


def run_plagiarism_check_task(submission_id: int):
    Submission = apps.get_model("assignments", "Submission")
    submission = Submission.objects.filter(id=submission_id).first()
    if submission is None:
        return None
    return start_plagiarism_check(submission)


def collect_assignment_statistics_task(assignment_id: int) -> dict | None:
    Assignment = apps.get_model("assignments", "Assignment")
    assignment = Assignment.objects.filter(id=assignment_id).first()
    if assignment is None:
        return None
    return get_assignment_statistics(assignment=assignment)


def collect_publication_statistics_task(publication_id: int) -> dict | None:
    AssignmentPublication = apps.get_model("assignments", "AssignmentPublication")
    publication = AssignmentPublication.objects.filter(id=publication_id).first()
    if publication is None:
        return None
    return get_publication_statistics(publication=publication)
