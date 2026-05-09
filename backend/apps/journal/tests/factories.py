from __future__ import annotations

from uuid import uuid4

from django.utils import timezone

from apps.course.models import Course, CourseLesson, CourseModule
from apps.journal.models import AttendanceRecord, JournalGrade, JournalLesson
from apps.journal.models.choices import (
    AttendanceStatus,
    GradeScale,
    GradeType,
    JournalLessonStatus,
)
from apps.organizations.models import Group, Organization, OrganizationType
from apps.users.models import User


def unique(value: str) -> str:
    return f"{value}-{uuid4().hex[:8]}"


def create_user(*, email: str | None = None) -> User:
    return User.objects.create_user(
        email=email or f"{unique('user')}@example.com",
        password="test-password-123",
    )


def create_teacher_user() -> User:
    return create_user(email=f"{unique('teacher')}@example.com")


def create_student_user() -> User:
    return create_user(email=f"{unique('student')}@example.com")


def create_organization_type() -> OrganizationType:
    return OrganizationType.objects.create(
        code=unique("school"),
        name=unique("Школа"),
        description="",
        is_active=True,
    )


def create_organization() -> Organization:
    return Organization.objects.create(
        type=create_organization_type(),
        name=unique("Тестовая организация"),
        short_name=unique("ТО"),
        description="",
        city="Москва",
        address="Тестовый адрес",
        phone="+70000000000",
        email=f"{unique('org')}@example.com",
        website="https://example.com",
        is_active=True,
    )


def create_group(*, organization: Organization | None = None) -> Group:
    return Group.objects.create(
        organization=organization or create_organization(),
        name=unique("10А"),
        code=unique("10a"),
        study_form="full_time",
        course_number=1,
        admission_year=2024,
        graduation_year=2025,
        academic_year="2024/2025",
        status="active",
        description="",
        is_active=True,
    )


def create_course(
    *,
    author: User | None = None,
    organization: Organization | None = None,
) -> Course:
    return Course.objects.create(
        author=author or create_teacher_user(),
        organization=organization,
        code=unique("course"),
        slug=unique("course"),
        title=unique("Тестовый курс"),
        subtitle="",
        description="",
        course_type="standard",
        origin="manual",
        status="draft",
        visibility="private",
        level="basic",
        language="ru",
        is_template=False,
        is_active=True,
        allow_self_enrollment=False,
        estimated_minutes=0,
    )


def create_course_module(
    *,
    course: Course | None = None,
    order: int | None = None,
) -> CourseModule:
    if course is None:
        course = create_course()

    if order is None:
        last_order = (
            CourseModule.objects.filter(course=course)
            .order_by("-order")
            .values_list("order", flat=True)
            .first()
        )
        order = (last_order or 0) + 1

    return CourseModule.objects.create(
        course=course,
        order=order,
        title=unique("Модуль"),
        description="",
        is_required=True,
        is_published=True,
        estimated_minutes=0,
    )


def create_course_lesson(
    *,
    course: Course | None = None,
    module: CourseModule | None = None,
    order: int | None = None,
    title: str | None = None,
) -> CourseLesson:
    if course is None:
        course = create_course()

    if module is None:
        module = create_course_module(course=course)

    if order is None:
        last_order = (
            CourseLesson.objects.filter(module=module)
            .order_by("-order")
            .values_list("order", flat=True)
            .first()
        )
        order = (last_order or 0) + 1

    return CourseLesson.objects.create(
        course=course,
        module=module,
        order=order,
        title=title or unique("Тема"),
        subtitle="",
        description="",
        content="",
        lesson_type="lesson",
        estimated_minutes=45,
        is_required=True,
        is_preview=False,
        is_published=True,
        video_url="",
        external_url="",
    )


def create_journal_lesson(
    *,
    course: Course | None = None,
    group: Group | None = None,
    teacher: User | None = None,
    course_lesson: CourseLesson | None = None,
    date_value=None,
    lesson_number: int | None = 1,
    status: str = JournalLessonStatus.CONDUCTED,
    planned_topic: str = "Плановая тема",
    actual_topic: str = "Фактическая тема",
) -> JournalLesson:
    if course is None:
        course = create_course()

    if group is None:
        group = create_group(organization=course.organization)

    if course_lesson is None:
        course_lesson = create_course_lesson(course=course)

    return JournalLesson.objects.create(
        course=course,
        group=group,
        teacher=teacher or create_teacher_user(),
        course_lesson=course_lesson,
        date=date_value or timezone.localdate(),
        started_at=None,
        ended_at=None,
        planned_topic=planned_topic,
        actual_topic=actual_topic,
        homework="",
        status=status,
        teacher_comment="",
        lesson_number=lesson_number,
    )


def create_attendance_record(
    *,
    lesson: JournalLesson | None = None,
    student: User | None = None,
    status: str = AttendanceStatus.PRESENT,
) -> AttendanceRecord:
    return AttendanceRecord.objects.create(
        lesson=lesson or create_journal_lesson(),
        student=student or create_student_user(),
        status=status,
        comment="",
    )


def create_five_point_grade(
    *,
    lesson: JournalLesson | None = None,
    student: User | None = None,
    score: int = 5,
    grade_type: str = GradeType.CLASSWORK,
    weight: int = 1,
    is_auto: bool = False,
) -> JournalGrade:
    return JournalGrade.objects.create(
        lesson=lesson or create_journal_lesson(),
        student=student or create_student_user(),
        grade_type=grade_type,
        scale=GradeScale.FIVE_POINT,
        score_five=score,
        is_passed=None,
        weight=weight,
        comment="",
        is_auto=is_auto,
    )


def create_pass_fail_grade(
    *,
    lesson: JournalLesson | None = None,
    student: User | None = None,
    is_passed: bool = True,
    grade_type: str = GradeType.CREDIT,
    weight: int = 1,
    is_auto: bool = False,
) -> JournalGrade:
    return JournalGrade.objects.create(
        lesson=lesson or create_journal_lesson(),
        student=student or create_student_user(),
        grade_type=grade_type,
        scale=GradeScale.PASS_FAIL,
        score_five=None,
        is_passed=is_passed,
        weight=weight,
        comment="",
        is_auto=is_auto,
    )
