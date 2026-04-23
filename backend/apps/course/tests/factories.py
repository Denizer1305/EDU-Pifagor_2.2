from __future__ import annotations

from itertools import count
from uuid import uuid4

from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from apps.course.models import (
    Course,
    CourseAssignment,
    CourseEnrollment,
    CourseLesson,
    CourseMaterial,
    CourseModule,
    CourseProgress,
    CourseTeacher,
    LessonProgress,
)
from apps.education.tests.factories import (
    create_academic_year as base_create_academic_year,
    create_education_period as base_create_education_period,
    create_group_subject as base_create_group_subject,
)
from apps.organizations.tests.factories import (
    create_group as base_create_group,
    create_organization as base_create_organization,
    create_subject as base_create_subject,
)
from apps.users.tests.factories import (
    create_admin_user as base_create_admin_user,
    create_student_user as base_create_student_user,
    create_teacher_user as base_create_teacher_user,
)

course_counter = count(1)
module_counter = count(1)
lesson_counter = count(1)
material_counter = count(1)
assignment_counter = count(1)
enrollment_counter = count(1)


def _unwrap_factory_result(value):
    if isinstance(value, tuple):
        return value[0]
    return value


def create_course_file(
    *,
    name: str | None = None,
    content: bytes | None = None,
    content_type: str = "application/pdf",
):
    index = next(material_counter)

    if name is None:
        name = f"course-file-{index}.pdf"
    if content is None:
        content = b"test file content"

    return SimpleUploadedFile(
        name=name,
        content=content,
        content_type=content_type,
    )


def create_course_author(*, email: str | None = None):
    if email is None:
        email = f"course_teacher_{uuid4().hex[:8]}@example.com"
    return _unwrap_factory_result(base_create_teacher_user(email=email))


def create_course_student(*, email: str | None = None):
    if email is None:
        email = f"course_student_{uuid4().hex[:8]}@example.com"
    return _unwrap_factory_result(base_create_student_user(email=email))


def create_course_admin(*, email: str | None = None):
    if email is None:
        email = f"course_admin_{uuid4().hex[:8]}@example.com"
    return _unwrap_factory_result(base_create_admin_user(email=email))


def create_organization():
    return _unwrap_factory_result(base_create_organization())


def create_subject():
    return _unwrap_factory_result(base_create_subject())


def create_group(*, organization=None):
    return _unwrap_factory_result(base_create_group(organization=organization))


def create_academic_year():
    return _unwrap_factory_result(base_create_academic_year())


def create_education_period(*, academic_year=None):
    return _unwrap_factory_result(
        base_create_education_period(academic_year=academic_year)
    )


def create_group_subject(*, group=None, subject=None, academic_year=None, period=None):
    return _unwrap_factory_result(
        base_create_group_subject(
            group=group,
            subject=subject,
            academic_year=academic_year,
            period=period,
        )
    )


def create_course(
    *,
    author=None,
    title: str | None = None,
    subtitle: str = "",
    description: str = "",
    course_type: str = Course.CourseTypeChoices.AUTHOR,
    origin: str = Course.OriginChoices.MANUAL,
    status: str = Course.StatusChoices.DRAFT,
    visibility: str = Course.VisibilityChoices.ASSIGNED_ONLY,
    level: str = Course.LevelChoices.BASIC,
    language: str = "ru",
    organization=None,
    subject=None,
    academic_year=None,
    period=None,
    group_subject=None,
    cover_image=None,
    is_template: bool = False,
    is_active: bool = True,
    allow_self_enrollment: bool = False,
    enrollment_code: str | None = None,
    estimated_minutes: int = 0,
    starts_at=None,
    ends_at=None,
    create_owner_link: bool = True,
):
    index = next(course_counter)

    if author is None:
        author = create_course_author()
    author = _unwrap_factory_result(author)

    if title is None:
        title = f"Курс {index}"

    course = Course(
        title=title,
        subtitle=subtitle,
        description=description,
        course_type=course_type,
        origin=origin,
        status=status,
        visibility=visibility,
        level=level,
        language=language,
        author=author,
        organization=organization,
        subject=subject,
        academic_year=academic_year,
        period=period,
        group_subject=group_subject,
        cover_image=cover_image,
        is_template=is_template,
        is_active=is_active,
        allow_self_enrollment=allow_self_enrollment,
        enrollment_code=enrollment_code,
        estimated_minutes=estimated_minutes,
        starts_at=starts_at,
        ends_at=ends_at,
    )
    course.full_clean()
    course.save()

    if create_owner_link:
        CourseTeacher.objects.create(
            course=course,
            teacher=author,
            role=CourseTeacher.RoleChoices.OWNER,
            is_active=True,
            can_edit=True,
            can_manage_structure=True,
            can_manage_assignments=True,
            can_view_analytics=True,
        )

    return course


def create_course_with_context(*, author=None, title: str | None = None):
    organization = create_organization()
    subject = create_subject()
    academic_year = create_academic_year()
    period = create_education_period(academic_year=academic_year)
    group = create_group(organization=organization)
    group_subject = create_group_subject(
        group=group,
        subject=subject,
        academic_year=academic_year,
        period=period,
    )

    course = create_course(
        author=author,
        title=title,
        organization=organization,
        subject=subject,
        academic_year=academic_year,
        period=period,
        group_subject=group_subject,
    )
    return {
        "course": course,
        "organization": organization,
        "subject": subject,
        "academic_year": academic_year,
        "period": period,
        "group": group,
        "group_subject": group_subject,
    }


def create_course_module(
    *,
    course=None,
    title: str | None = None,
    description: str = "",
    order: int | None = None,
    is_required: bool = True,
    is_published: bool = True,
    estimated_minutes: int = 0,
):
    index = next(module_counter)

    if course is None:
        course = create_course()

    if title is None:
        title = f"Модуль {index}"

    if order is None:
        last_module = course.modules.order_by("-order", "-id").first()
        order = (last_module.order if last_module else 0) + 1

    module = CourseModule(
        course=course,
        title=title,
        description=description,
        order=order,
        is_required=is_required,
        is_published=is_published,
        estimated_minutes=estimated_minutes,
    )
    module.full_clean()
    module.save()
    return module


def create_course_lesson(
    *,
    course=None,
    module=None,
    title: str | None = None,
    subtitle: str = "",
    description: str = "",
    content: str = "",
    lesson_type: str = CourseLesson.LessonTypeChoices.TEXT,
    order: int | None = None,
    estimated_minutes: int = 15,
    is_required: bool = True,
    is_preview: bool = False,
    is_published: bool = True,
    available_from=None,
    video_url: str = "",
    external_url: str = "",
):
    index = next(lesson_counter)

    if course is None and module is None:
        course = create_course()
        module = create_course_module(course=course)

    if course is None:
        course = module.course

    if module is None:
        module = create_course_module(course=course)

    if title is None:
        title = f"Урок {index}"

    if order is None:
        last_lesson = module.lessons.order_by("-order", "-id").first()
        order = (last_lesson.order if last_lesson else 0) + 1

    lesson = CourseLesson(
        course=course,
        module=module,
        title=title,
        subtitle=subtitle,
        description=description,
        content=content,
        lesson_type=lesson_type,
        order=order,
        estimated_minutes=estimated_minutes,
        is_required=is_required,
        is_preview=is_preview,
        is_published=is_published,
        available_from=available_from,
        video_url=video_url,
        external_url=external_url,
    )
    lesson.full_clean()
    lesson.save()
    return lesson


def create_course_material(
    *,
    course=None,
    lesson=None,
    title: str | None = None,
    description: str = "",
    material_type: str = CourseMaterial.MaterialTypeChoices.FILE,
    file=None,
    external_url: str = "",
    order: int | None = None,
    is_downloadable: bool = True,
    is_visible: bool = True,
):
    index = next(material_counter)

    if course is None and lesson is None:
        lesson = create_course_lesson()

    if lesson is not None and course is None:
        course = lesson.course

    if course is None:
        course = create_course()

    if title is None:
        title = f"Материал {index}"

    if order is None:
        last_item = CourseMaterial.objects.filter(
            course=course,
            lesson=lesson,
        ).order_by("-order", "-id").first()
        order = (last_item.order if last_item else 0) + 1

    if file is None and material_type != CourseMaterial.MaterialTypeChoices.LINK:
        file = create_course_file()

    material = CourseMaterial(
        course=course,
        lesson=lesson,
        title=title,
        description=description,
        material_type=material_type,
        file=file,
        external_url=external_url,
        order=order,
        is_downloadable=is_downloadable,
        is_visible=is_visible,
    )
    material.full_clean()
    material.save()
    return material


def create_course_assignment(
    *,
    course=None,
    group=None,
    student=None,
    assignment_type: str | None = None,
    assigned_by=None,
    starts_at=None,
    ends_at=None,
    is_active: bool = True,
    auto_enroll: bool = True,
    notes: str = "",
):
    if course is None:
        course = create_course()

    if assigned_by is None:
        assigned_by = course.author
    assigned_by = _unwrap_factory_result(assigned_by)

    if student is not None:
        student = _unwrap_factory_result(student)

    if assignment_type is None:
        assignment_type = (
            CourseAssignment.AssignmentTypeChoices.GROUP
            if group is not None
            else CourseAssignment.AssignmentTypeChoices.STUDENT
        )

    if assignment_type == CourseAssignment.AssignmentTypeChoices.GROUP and group is None:
        context = create_course_with_context(author=course.author)
        course = context["course"]
        group = context["group"]

    if assignment_type == CourseAssignment.AssignmentTypeChoices.STUDENT and student is None:
        student = create_course_student()

    assignment = CourseAssignment(
        course=course,
        assignment_type=assignment_type,
        group=group,
        student=student,
        assigned_by=assigned_by,
        starts_at=starts_at,
        ends_at=ends_at,
        is_active=is_active,
        auto_enroll=auto_enroll,
        notes=notes or f"Назначение {next(assignment_counter)}",
    )
    assignment.full_clean()
    assignment.save()
    return assignment


def create_course_enrollment(
    *,
    course=None,
    student=None,
    assignment=None,
    status: str = CourseEnrollment.StatusChoices.ENROLLED,
    progress_percent: int = 0,
    enrolled_at=None,
    started_at=None,
    completed_at=None,
    last_activity_at=None,
):
    index = next(enrollment_counter)

    if course is None:
        course = create_course()

    if student is None:
        student = create_course_student(
            email=f"enrollment_student_{index}@example.com"
        )
    student = _unwrap_factory_result(student)

    if enrolled_at is None:
        enrolled_at = timezone.now()

    if status == CourseEnrollment.StatusChoices.IN_PROGRESS and started_at is None:
        started_at = timezone.now()

    if status == CourseEnrollment.StatusChoices.COMPLETED:
        if started_at is None:
            started_at = timezone.now()
        if completed_at is None:
            completed_at = timezone.now()
        progress_percent = 100

    enrollment = CourseEnrollment(
        course=course,
        student=student,
        assignment=assignment,
        status=status,
        progress_percent=progress_percent,
        enrolled_at=enrolled_at,
        started_at=started_at,
        completed_at=completed_at,
        last_activity_at=last_activity_at,
    )
    enrollment.full_clean()
    enrollment.save()
    return enrollment


def create_course_progress(
    *,
    enrollment=None,
    total_lessons_count: int = 0,
    completed_lessons_count: int = 0,
    required_lessons_count: int = 0,
    completed_required_lessons_count: int = 0,
    progress_percent: int = 0,
    spent_minutes: int = 0,
    started_at=None,
    completed_at=None,
    last_activity_at=None,
    last_lesson=None,
):
    if enrollment is None:
        enrollment = create_course_enrollment()

    progress = CourseProgress.objects.filter(enrollment=enrollment).first()
    if progress is None:
        progress = CourseProgress(enrollment=enrollment)

    progress.total_lessons_count = total_lessons_count
    progress.completed_lessons_count = completed_lessons_count
    progress.required_lessons_count = required_lessons_count
    progress.completed_required_lessons_count = completed_required_lessons_count
    progress.progress_percent = progress_percent
    progress.spent_minutes = spent_minutes
    progress.started_at = started_at
    progress.completed_at = completed_at
    progress.last_activity_at = last_activity_at
    progress.last_lesson = last_lesson
    progress.full_clean()
    progress.save()
    return progress


def create_lesson_progress(
    *,
    enrollment=None,
    lesson=None,
    course_progress=None,
    status: str = LessonProgress.StatusChoices.NOT_STARTED,
    started_at=None,
    completed_at=None,
    last_viewed_at=None,
    spent_minutes: int = 0,
    attempts_count: int = 0,
    score=None,
):
    if enrollment is None and lesson is None:
        lesson = create_course_lesson()
        enrollment = create_course_enrollment(course=lesson.course)

    if lesson is None:
        lesson = create_course_lesson(course=enrollment.course)

    if enrollment is None:
        enrollment = create_course_enrollment(course=lesson.course)

    if course_progress is None:
        course_progress = CourseProgress.objects.filter(enrollment=enrollment).first()
        if course_progress is None:
            course_progress = create_course_progress(enrollment=enrollment)

    lesson_progress = LessonProgress(
        enrollment=enrollment,
        course_progress=course_progress,
        lesson=lesson,
        status=status,
        started_at=started_at,
        completed_at=completed_at,
        last_viewed_at=last_viewed_at,
        spent_minutes=spent_minutes,
        attempts_count=attempts_count,
        score=score,
    )
    lesson_progress.full_clean()
    lesson_progress.save()
    return lesson_progress
