from __future__ import annotations

from django.db.models import Avg, Count

from apps.assignments.models import Assignment, AssignmentPublication, Submission


def _num(value):
    return value if value is not None else 0


def get_assignment_statistics(*, assignment):
    submissions = Submission.objects.filter(assignment=assignment)

    aggregate = submissions.aggregate(
        submissions_count=Count("id"),
        avg_score=Avg("final_score"),
        avg_percentage=Avg("percentage"),
    )

    return {
        "assignment_id": assignment.id,
        "submissions_count": aggregate["submissions_count"] or 0,
        "avg_score": _num(aggregate["avg_score"]),
        "avg_percentage": _num(aggregate["avg_percentage"]),
        "passed_count": submissions.filter(passed=True).count(),
        "failed_count": submissions.filter(passed=False)
        .exclude(status=Submission.StatusChoices.IN_PROGRESS)
        .count(),
        "draft_publications_count": AssignmentPublication.objects.filter(
            assignment=assignment,
            status=AssignmentPublication.StatusChoices.DRAFT,
        ).count(),
        "published_publications_count": AssignmentPublication.objects.filter(
            assignment=assignment,
            status=AssignmentPublication.StatusChoices.PUBLISHED,
        ).count(),
    }


def get_publication_statistics(*, publication):
    submissions = Submission.objects.filter(publication=publication)

    aggregate = submissions.aggregate(
        submissions_count=Count("id"),
        avg_score=Avg("final_score"),
        avg_percentage=Avg("percentage"),
    )

    return {
        "publication_id": publication.id,
        "assignment_id": publication.assignment_id,
        "submissions_count": aggregate["submissions_count"] or 0,
        "avg_score": _num(aggregate["avg_score"]),
        "avg_percentage": _num(aggregate["avg_percentage"]),
        "passed_count": submissions.filter(passed=True).count(),
        "failed_count": submissions.filter(passed=False)
        .exclude(status=Submission.StatusChoices.IN_PROGRESS)
        .count(),
        "in_progress_count": submissions.filter(
            status=Submission.StatusChoices.IN_PROGRESS
        ).count(),
        "submitted_count": submissions.filter(
            status=Submission.StatusChoices.SUBMITTED
        ).count(),
        "reviewed_count": submissions.filter(
            status=Submission.StatusChoices.REVIEWED
        ).count(),
    }


def get_student_assignment_progress(*, student, assignment):
    submissions = Submission.objects.filter(
        student=student,
        assignment=assignment,
    ).order_by("-attempt_number", "-created_at")

    last_submission = submissions.first()

    return {
        "student_id": student.id,
        "assignment_id": assignment.id,
        "attempts_count": submissions.count(),
        "last_submission_id": last_submission.id if last_submission else None,
        "last_submission_status": last_submission.status if last_submission else "",
        "last_submission_attempt_number": last_submission.attempt_number
        if last_submission
        else 0,
        "last_submission_score": _num(last_submission.final_score)
        if last_submission
        else 0,
        "last_submission_percentage": _num(last_submission.percentage)
        if last_submission
        else 0,
        "passed": bool(last_submission.passed) if last_submission else False,
    }


def get_course_assignment_dashboard(*, course):
    if course is None:
        return {
            "course_id": None,
            "assignments_count": 0,
            "publications_count": 0,
            "submissions_count": 0,
            "avg_score": 0,
            "avg_percentage": 0,
            "published_assignments_count": 0,
            "draft_assignments_count": 0,
        }

    assignments = Assignment.objects.filter(course=course)
    publications = AssignmentPublication.objects.filter(course=course)
    submissions = Submission.objects.filter(publication__course=course)

    aggregate = submissions.aggregate(
        submissions_count=Count("id"),
        avg_score=Avg("final_score"),
        avg_percentage=Avg("percentage"),
    )

    return {
        "course_id": course.id,
        "assignments_count": assignments.count(),
        "publications_count": publications.count(),
        "submissions_count": aggregate["submissions_count"] or 0,
        "avg_score": _num(aggregate["avg_score"]),
        "avg_percentage": _num(aggregate["avg_percentage"]),
        "published_assignments_count": assignments.filter(
            status=Assignment.StatusChoices.PUBLISHED
        ).count(),
        "draft_assignments_count": assignments.filter(
            status=Assignment.StatusChoices.DRAFT
        ).count(),
    }
