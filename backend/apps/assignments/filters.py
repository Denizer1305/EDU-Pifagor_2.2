from __future__ import annotations

from django.utils.dateparse import parse_date, parse_datetime


def parse_bool(value):
    if value is None or value == "":
        return None

    if isinstance(value, bool):
        return value

    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "y", "on"}:
        return True
    if normalized in {"false", "0", "no", "n", "off"}:
        return False

    return None


def parse_int(value):
    if value is None or value == "":
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_date_or_datetime(value):
    if value is None or value == "":
        return None

    dt = parse_datetime(value)
    if dt is not None:
        return dt

    d = parse_date(value)
    return d


def build_assignment_filters(query_params) -> dict:
    return {
        "search": query_params.get("search", "").strip(),
        "status": query_params.get("status", "").strip(),
        "assignment_kind": query_params.get("assignment_kind", "").strip(),
        "control_scope": query_params.get("control_scope", "").strip(),
        "education_level": query_params.get("education_level", "").strip(),
        "course_id": parse_int(query_params.get("course_id")),
        "lesson_id": parse_int(query_params.get("lesson_id")),
        "subject_id": parse_int(query_params.get("subject_id")),
        "organization_id": parse_int(query_params.get("organization_id")),
        "author_id": parse_int(query_params.get("author_id")),
        "is_template": parse_bool(query_params.get("is_template")),
        "is_active": parse_bool(query_params.get("is_active")),
    }


def build_publication_filters(query_params) -> dict:
    return {
        "search": query_params.get("search", "").strip(),
        "status": query_params.get("status", "").strip(),
        "assignment_id": parse_int(query_params.get("assignment_id")),
        "course_id": parse_int(query_params.get("course_id")),
        "lesson_id": parse_int(query_params.get("lesson_id")),
        "published_by_id": parse_int(query_params.get("published_by_id")),
        "is_active": parse_bool(query_params.get("is_active")),
        "starts_from": parse_date_or_datetime(query_params.get("starts_from")),
        "starts_to": parse_date_or_datetime(query_params.get("starts_to")),
        "due_from": parse_date_or_datetime(query_params.get("due_from")),
        "due_to": parse_date_or_datetime(query_params.get("due_to")),
    }


def build_audience_filters(query_params) -> dict:
    return {
        "search": query_params.get("search", "").strip(),
        "publication_id": parse_int(query_params.get("publication_id")),
        "audience_type": query_params.get("audience_type", "").strip(),
        "group_id": parse_int(query_params.get("group_id")),
        "student_id": parse_int(query_params.get("student_id")),
        "course_enrollment_id": parse_int(query_params.get("course_enrollment_id")),
        "is_active": parse_bool(query_params.get("is_active")),
    }


def build_submission_filters(query_params) -> dict:
    return {
        "search": query_params.get("search", "").strip(),
        "status": query_params.get("status", "").strip(),
        "assignment_id": parse_int(query_params.get("assignment_id")),
        "publication_id": parse_int(query_params.get("publication_id")),
        "student_id": parse_int(query_params.get("student_id")),
        "checked_by_id": parse_int(query_params.get("checked_by_id")),
        "is_late": parse_bool(query_params.get("is_late")),
        "passed": parse_bool(query_params.get("passed")),
    }


def build_review_filters(query_params) -> dict:
    return {
        "search": query_params.get("search", "").strip(),
        "review_status": query_params.get("review_status", "").strip(),
        "reviewer_id": parse_int(query_params.get("reviewer_id")),
        "submission_id": parse_int(query_params.get("submission_id")),
    }


def build_rubric_filters(query_params) -> dict:
    return {
        "search": query_params.get("search", "").strip(),
        "assignment_kind": query_params.get("assignment_kind", "").strip(),
        "organization_id": parse_int(query_params.get("organization_id")),
        "author_id": parse_int(query_params.get("author_id")),
        "is_template": parse_bool(query_params.get("is_template")),
        "is_active": parse_bool(query_params.get("is_active")),
    }
