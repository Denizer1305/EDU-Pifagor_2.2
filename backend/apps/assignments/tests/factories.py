from __future__ import annotations

import uuid
from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from apps.assignments.models import (
    Appeal,
    Assignment,
    AssignmentAttachment,
    AssignmentOfficialFormat,
    AssignmentPolicy,
    AssignmentPublication,
    AssignmentAudience,
    AssignmentQuestion,
    AssignmentSection,
    AssignmentVariant,
    GradeRecord,
    ReviewComment,
    Rubric,
    RubricCriterion,
    Submission,
    SubmissionAnswer,
    SubmissionAttachment,
    SubmissionAttempt,
    SubmissionReview,
)

from apps.course.tests.factories import (
    create_course as base_create_course,
    create_course_enrollment as base_create_course_enrollment,
    create_course_lesson as base_create_course_lesson,
)
from apps.education.tests.factories import (
    create_student_group_enrollment as base_create_student_group_enrollment,
)
from apps.users.tests.factories import (
    create_admin_user as base_create_admin_user,
    create_student_user as base_create_student_user,
    create_teacher_user as base_create_teacher_user,
)


def _uuid() -> str:
    return uuid.uuid4().hex[:8]


def _extract_user(created):
    if isinstance(created, tuple):
        return created[0]
    return created


def unique_email(prefix: str) -> str:
    return f"{prefix}_{_uuid()}@example.com"


def create_teacher_user(email: str | None = None):
    created = base_create_teacher_user(
        email=email or unique_email("assignments_teacher")
    )
    return _extract_user(created)


def create_student_user(email: str | None = None):
    created = base_create_student_user(
        email=email or unique_email("assignments_student")
    )
    return _extract_user(created)


def create_admin_user(email: str | None = None):
    created = base_create_admin_user(
        email=email or unique_email("assignments_admin")
    )
    return _extract_user(created)


def create_course(author=None, **kwargs):
    author = author or create_teacher_user()
    return base_create_course(author=author, **kwargs)


def create_course_lesson(course=None, **kwargs):
    course = course or create_course()
    return base_create_course_lesson(course=course, **kwargs)


def create_course_enrollment(course=None, student=None, **kwargs):
    course = course or create_course()
    student = student or create_student_user()
    return base_create_course_enrollment(course=course, student=student, **kwargs)


def create_group_with_enrollment(student=None, **kwargs):
    student = student or create_student_user()
    enrollment = base_create_student_group_enrollment(student=student, **kwargs)
    return enrollment.group, enrollment


def create_assignment(
    author=None,
    course=None,
    lesson=None,
    subject=None,
    organization=None,
    title: str | None = None,
    **kwargs,
):
    author = author or create_teacher_user()

    assignment = Assignment.objects.create(
        author=author,
        course=course,
        lesson=lesson,
        subject=subject,
        organization=organization,
        title=title or f"Работа {_uuid()}",
        subtitle=kwargs.pop("subtitle", ""),
        description=kwargs.pop("description", ""),
        instructions=kwargs.pop("instructions", ""),
        assignment_kind=kwargs.pop(
            "assignment_kind",
            Assignment.AssignmentKindChoices.HOMEWORK,
        ),
        control_scope=kwargs.pop(
            "control_scope",
            Assignment.ControlScopeChoices.LEARNING_ACTIVITY,
        ),
        status=kwargs.pop("status", Assignment.StatusChoices.DRAFT),
        visibility=kwargs.pop(
            "visibility",
            Assignment.VisibilityChoices.ASSIGNED_ONLY,
        ),
        education_level=kwargs.pop(
            "education_level",
            Assignment.EducationLevelChoices.SCHOOL,
        ),
        is_template=kwargs.pop("is_template", False),
        is_active=kwargs.pop("is_active", True),
        **kwargs,
    )

    AssignmentPolicy.objects.get_or_create(
        assignment=assignment,
        defaults={
            "check_mode": AssignmentPolicy.CheckModeChoices.MANUAL,
            "grading_mode": AssignmentPolicy.GradingModeChoices.RAW_SCORE,
            "max_score": Decimal("0"),
            "passing_score": Decimal("0"),
            "attempts_limit": 1,
            "allow_text_answer": True,
        },
    )
    return assignment


def create_assignment_policy(assignment=None, **kwargs):
    assignment = assignment or create_assignment()
    policy, _ = AssignmentPolicy.objects.update_or_create(
        assignment=assignment,
        defaults={
            "check_mode": kwargs.pop(
                "check_mode",
                AssignmentPolicy.CheckModeChoices.MANUAL,
            ),
            "grading_mode": kwargs.pop(
                "grading_mode",
                AssignmentPolicy.GradingModeChoices.RAW_SCORE,
            ),
            "max_score": kwargs.pop("max_score", Decimal("100")),
            "passing_score": kwargs.pop("passing_score", Decimal("40")),
            "attempts_limit": kwargs.pop("attempts_limit", 1),
            "allow_text_answer": kwargs.pop("allow_text_answer", True),
            **kwargs,
        },
    )
    return policy


def create_assignment_official_format(assignment=None, **kwargs):
    assignment = assignment or create_assignment()
    official_format, _ = AssignmentOfficialFormat.objects.update_or_create(
        assignment=assignment,
        defaults={
            "official_family": kwargs.pop("official_family", "vpr"),
            "assessment_year": kwargs.pop("assessment_year", 2024),
            "grade_level": kwargs.pop("grade_level", "8"),
            "exam_subject_name": kwargs.pop("exam_subject_name", "Математика"),
            "source_kind": kwargs.pop("source_kind", "official_demo"),
            "source_title": kwargs.pop("source_title", "ВПР 2024"),
            "source_url": kwargs.pop("source_url", ""),
            "format_version": kwargs.pop("format_version", "1.0"),
            "is_preparation_only": kwargs.pop("is_preparation_only", True),
            "has_answer_key": kwargs.pop("has_answer_key", True),
            "has_scoring_criteria": kwargs.pop("has_scoring_criteria", True),
            "has_official_demo_source": kwargs.pop("has_official_demo_source", True),
            **kwargs,
        },
    )
    return official_format


def create_assignment_variant(assignment=None, **kwargs):
    assignment = assignment or create_assignment()

    last_variant = assignment.variants.order_by("-variant_number", "-order").first()
    next_variant_number = 1 if last_variant is None else last_variant.variant_number + 1
    next_order = 1 if last_variant is None else last_variant.order + 1

    return AssignmentVariant.objects.create(
        assignment=assignment,
        title=kwargs.pop("title", f"Вариант {_uuid()}"),
        code=kwargs.pop("code", f"VAR-{_uuid()}"),
        description=kwargs.pop("description", ""),
        variant_number=kwargs.pop("variant_number", next_variant_number),
        order=kwargs.pop("order", next_order),
        is_default=kwargs.pop("is_default", last_variant is None),
        max_score=kwargs.pop("max_score", Decimal("0")),
        is_active=kwargs.pop("is_active", True),
        **kwargs,
    )


def create_assignment_section(assignment=None, variant=None, **kwargs):
    assignment = assignment or (variant.assignment if variant else create_assignment())

    section_type_default = AssignmentSection.SectionTypeChoices.choices[0][0]

    return AssignmentSection.objects.create(
        assignment=assignment,
        variant=variant,
        title=kwargs.pop("title", f"Секция {_uuid()}"),
        description=kwargs.pop("description", ""),
        section_type=kwargs.pop("section_type", section_type_default),
        order=kwargs.pop("order", 1),
        max_score=kwargs.pop("max_score", Decimal("0")),
        is_required=kwargs.pop("is_required", True),
        **kwargs,
    )


def create_assignment_question(assignment=None, variant=None, section=None, **kwargs):
    assignment = assignment or (
        variant.assignment if variant else section.assignment if section else create_assignment()
    )
    return AssignmentQuestion.objects.create(
        assignment=assignment,
        variant=variant,
        section=section,
        question_type=kwargs.pop("question_type", "single_choice"),
        prompt=kwargs.pop("prompt", f"Вопрос {_uuid()}"),
        description=kwargs.pop("description", ""),
        answer_options_json=kwargs.pop(
            "answer_options_json",
            [{"id": "a", "text": "1"}, {"id": "b", "text": "2"}],
        ),
        correct_answer_json=kwargs.pop("correct_answer_json", {"id": "a"}),
        validation_rules_json=kwargs.pop("validation_rules_json", {}),
        explanation=kwargs.pop("explanation", ""),
        max_score=kwargs.pop("max_score", Decimal("5")),
        order=kwargs.pop("order", 1),
        is_required=kwargs.pop("is_required", True),
        requires_manual_review=kwargs.pop("requires_manual_review", False),
        **kwargs,
    )


def create_assignment_attachment(assignment=None, variant=None, **kwargs):
    assignment = assignment or (variant.assignment if variant else create_assignment())
    file_obj = kwargs.pop(
        "file",
        SimpleUploadedFile(
            "assignment.pdf",
            b"%PDF-1.4 test file",
            content_type="application/pdf",
        ),
    )
    return AssignmentAttachment.objects.create(
        assignment=assignment,
        variant=variant,
        title=kwargs.pop("title", "Файл задания"),
        attachment_type=kwargs.pop("attachment_type", "file"),
        file=file_obj,
        external_url=kwargs.pop("external_url", ""),
        is_visible_to_students=kwargs.pop("is_visible_to_students", True),
        order=kwargs.pop("order", 1),
        **kwargs,
    )


def create_assignment_publication(
    assignment=None,
    course=None,
    lesson=None,
    published_by=None,
    **kwargs,
):
    assignment = assignment or create_assignment()

    if course is None:
        course = assignment.course
    if course is None:
        course = create_course(author=assignment.author)

    if lesson is None:
        lesson = assignment.lesson

    published_by = published_by or assignment.author

    return AssignmentPublication.objects.create(
        assignment=assignment,
        course=course,
        lesson=lesson,
        published_by=published_by,
        title_override=kwargs.pop("title_override", ""),
        starts_at=kwargs.pop("starts_at", timezone.now()),
        due_at=kwargs.pop("due_at", timezone.now() + timezone.timedelta(days=7)),
        available_until=kwargs.pop(
            "available_until",
            timezone.now() + timezone.timedelta(days=10),
        ),
        status=kwargs.pop("status", AssignmentPublication.StatusChoices.DRAFT),
        is_active=kwargs.pop("is_active", True),
        notes=kwargs.pop("notes", ""),
        **kwargs,
    )


def create_assignment_audience(
    publication=None,
    audience_type=None,
    student=None,
    group=None,
    course_enrollment=None,
    **kwargs,
):
    publication = publication or create_assignment_publication()

    if audience_type is None:
        audience_type = AssignmentAudience.AudienceTypeChoices.STUDENT

    if audience_type in {
        AssignmentAudience.AudienceTypeChoices.STUDENT,
        AssignmentAudience.AudienceTypeChoices.SELECTED_STUDENTS,
    } and student is None and course_enrollment is None:
        student = create_student_user()

    if audience_type == AssignmentAudience.AudienceTypeChoices.GROUP and group is None:
        group, _ = create_group_with_enrollment()

    if course_enrollment is not None and student is None:
        student = getattr(course_enrollment, "student", None)

    return AssignmentAudience.objects.create(
        publication=publication,
        audience_type=audience_type,
        group=group,
        student=student,
        course_enrollment=course_enrollment,
        is_active=kwargs.pop("is_active", True),
        **kwargs,
    )


def create_submission(
    publication=None,
    assignment=None,
    student=None,
    variant=None,
    **kwargs,
):
    publication = publication or create_assignment_publication()
    assignment = assignment or publication.assignment
    student = student or create_student_user()
    variant = variant or assignment.variants.first()

    status_value = kwargs.pop("status", Submission.StatusChoices.IN_PROGRESS)

    return Submission.objects.create(
        publication=publication,
        assignment=assignment,
        variant=variant,
        student=student,
        status=status_value,
        attempt_number=kwargs.pop("attempt_number", 1),
        started_at=kwargs.pop("started_at", timezone.now()),
        submitted_at=kwargs.pop(
            "submitted_at",
            timezone.now() if status_value != Submission.StatusChoices.IN_PROGRESS else None,
        ),
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
    submission = submission or create_submission()
    file_obj = kwargs.pop(
        "file",
        SimpleUploadedFile(
            "answer.pdf",
            b"%PDF-1.4 answer file",
            content_type="application/pdf",
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


def create_submission_review(submission=None, reviewer=None, **kwargs):
    submission = submission or create_submission()
    reviewer = reviewer or submission.assignment.author
    review, _ = SubmissionReview.objects.get_or_create(
        submission=submission,
        defaults={
            "reviewer": reviewer,
            "review_status": kwargs.pop("review_status", "in_progress"),
            "feedback": kwargs.pop("feedback", ""),
            "private_note": kwargs.pop("private_note", ""),
            "score": kwargs.pop("score", Decimal("0")),
            "passed": kwargs.pop("passed", False),
            "reviewed_at": kwargs.pop("reviewed_at", None),
            **kwargs,
        },
    )
    return review


def create_review_comment(review=None, created_by=None, **kwargs):
    review = review or create_submission_review()
    created_by = created_by or review.reviewer
    return ReviewComment.objects.create(
        review=review,
        question=kwargs.pop("question", None),
        submission_answer=kwargs.pop("submission_answer", None),
        created_by=created_by,
        comment_type=kwargs.pop("comment_type", "general"),
        message=kwargs.pop("message", "Комментарий"),
        score_delta=kwargs.pop("score_delta", None),
        **kwargs,
    )


def create_rubric(author=None, organization=None, **kwargs):
    author = author or create_teacher_user()
    return Rubric.objects.create(
        title=kwargs.pop("title", f"Рубрика {_uuid()}"),
        description=kwargs.pop("description", ""),
        assignment_kind=kwargs.pop("assignment_kind", "homework"),
        organization=organization,
        author=author,
        is_template=kwargs.pop("is_template", True),
        is_active=kwargs.pop("is_active", True),
        **kwargs,
    )


def create_rubric_criterion(rubric=None, **kwargs):
    rubric = rubric or create_rubric()
    return RubricCriterion.objects.create(
        rubric=rubric,
        title=kwargs.pop("title", f"Критерий {_uuid()}"),
        description=kwargs.pop("description", ""),
        max_score=kwargs.pop("max_score", Decimal("5")),
        order=kwargs.pop("order", 1),
        criterion_type=kwargs.pop("criterion_type", "score"),
        **kwargs,
    )


def create_grade_record(submission=None, graded_by=None, **kwargs):
    submission = submission or create_submission()
    graded_by = graded_by or submission.assignment.author
    return GradeRecord.objects.create(
        student=submission.student,
        assignment=submission.assignment,
        publication=submission.publication,
        submission=submission,
        grade_value=kwargs.pop("grade_value", "5"),
        grade_numeric=kwargs.pop("grade_numeric", Decimal("5")),
        grading_mode=kwargs.pop("grading_mode", "five_point"),
        is_final=kwargs.pop("is_final", True),
        graded_by=graded_by,
        graded_at=kwargs.pop("graded_at", timezone.now()),
        **kwargs,
    )


def create_appeal(submission=None, student=None, **kwargs):
    submission = submission or create_submission()
    student = student or submission.student
    return Appeal.objects.create(
        submission=submission,
        student=student,
        status=kwargs.pop("status", "pending"),
        reason=kwargs.pop("reason", "Не согласен с оценкой"),
        resolution=kwargs.pop("resolution", ""),
        resolved_by=kwargs.pop("resolved_by", None),
        resolved_at=kwargs.pop("resolved_at", None),
        **kwargs,
    )
