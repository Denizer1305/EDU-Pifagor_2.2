from __future__ import annotations

from datetime import date

from django.contrib.auth import get_user_model

from apps.course.models import Course, CourseLesson, CourseModule
from apps.education.models import AcademicYear, EducationPeriod, GroupSubject
from apps.organizations.models import (
    Group,
    Organization,
    OrganizationType,
    Subject,
    SubjectCategory,
)

from ._utils import next_number


def _clean_kwargs(model_class, values: dict) -> dict:
    model_fields = {field.name for field in model_class._meta.fields}
    return {key: value for key, value in values.items() if key in model_fields}


def create_user(**kwargs):
    user_model = get_user_model()
    number = next_number("user")

    email = kwargs.pop("email", f"user{number}@example.com")
    password = kwargs.pop("password", "test-password")

    defaults = {
        "registration_type": kwargs.pop(
            "registration_type",
            getattr(user_model.RegistrationTypeChoices, "TEACHER", "teacher"),
        ),
        "onboarding_status": kwargs.pop(
            "onboarding_status",
            getattr(user_model.OnboardingStatusChoices, "ACTIVE", "active"),
        ),
        "is_email_verified": kwargs.pop("is_email_verified", True),
        "is_active": kwargs.pop("is_active", True),
    }
    defaults.update(kwargs)

    return user_model.objects.create_user(
        email=email,
        password=password,
        **_clean_kwargs(user_model, defaults),
    )


def create_organization_type(**kwargs):
    number = next_number("organization_type")

    defaults = {
        "code": kwargs.pop("code", f"college-{number}"),
        "name": kwargs.pop("name", f"Колледж {number}"),
        "description": kwargs.pop("description", ""),
        "is_active": kwargs.pop("is_active", True),
    }
    defaults.update(kwargs)

    return OrganizationType.objects.create(**_clean_kwargs(OrganizationType, defaults))


def create_organization(**kwargs):
    number = next_number("organization")
    organization_type = kwargs.pop("type", None) or create_organization_type()

    defaults = {
        "type": organization_type,
        "name": kwargs.pop("name", f"Тестовая организация {number}"),
        "short_name": kwargs.pop("short_name", f"ТО-{number}"),
        "description": kwargs.pop("description", ""),
        "city": kwargs.pop("city", "Москва"),
        "address": kwargs.pop("address", ""),
        "phone": kwargs.pop("phone", ""),
        "email": kwargs.pop("email", f"org{number}@example.com"),
        "website": kwargs.pop("website", ""),
        "is_active": kwargs.pop("is_active", True),
    }
    defaults.update(kwargs)

    return Organization.objects.create(**_clean_kwargs(Organization, defaults))


def create_academic_year(**kwargs):
    number = next_number("academic_year")
    start_year = 2025 + number

    defaults = {
        "name": kwargs.pop("name", f"{start_year}/{start_year + 1}"),
        "start_date": kwargs.pop("start_date", date(start_year, 9, 1)),
        "end_date": kwargs.pop("end_date", date(start_year + 1, 8, 31)),
        "description": kwargs.pop("description", ""),
        "is_current": kwargs.pop("is_current", False),
        "is_active": kwargs.pop("is_active", True),
    }
    defaults.update(kwargs)

    return AcademicYear.objects.create(**_clean_kwargs(AcademicYear, defaults))


def create_education_period(**kwargs):
    academic_year = kwargs.pop("academic_year", None) or create_academic_year()
    number = next_number(f"education_period_{academic_year.pk or academic_year.name}")

    defaults = {
        "academic_year": academic_year,
        "name": kwargs.pop("name", f"{number} семестр"),
        "code": kwargs.pop("code", f"SEM-{number}"),
        "period_type": kwargs.pop(
            "period_type",
            EducationPeriod.PeriodTypeChoices.SEMESTER,
        ),
        "sequence": kwargs.pop("sequence", number),
        "start_date": kwargs.pop("start_date", academic_year.start_date),
        "end_date": kwargs.pop("end_date", academic_year.end_date),
        "description": kwargs.pop("description", ""),
        "is_current": kwargs.pop("is_current", False),
        "is_active": kwargs.pop("is_active", True),
    }
    defaults.update(kwargs)

    return EducationPeriod.objects.create(**_clean_kwargs(EducationPeriod, defaults))


def create_group(**kwargs):
    number = next_number("group")
    organization = kwargs.pop("organization", None) or create_organization()

    defaults = {
        "organization": organization,
        "department": kwargs.pop("department", None),
        "name": kwargs.pop("name", f"ИС-{number}"),
        "code": kwargs.pop("code", f"IS-{number}"),
        "study_form": kwargs.pop("study_form", Group.StudyFormChoices.FULL_TIME),
        "course_number": kwargs.pop("course_number", 1),
        "admission_year": kwargs.pop("admission_year", 2025),
        "graduation_year": kwargs.pop("graduation_year", 2029),
        "academic_year": kwargs.pop("academic_year", "2025/2026"),
        "status": kwargs.pop("status", Group.StatusChoices.ACTIVE),
        "description": kwargs.pop("description", ""),
        "join_code_hash": kwargs.pop("join_code_hash", ""),
        "join_code_is_active": kwargs.pop("join_code_is_active", False),
        "join_code_expires_at": kwargs.pop("join_code_expires_at", None),
        "is_active": kwargs.pop("is_active", True),
    }
    defaults.update(kwargs)

    return Group.objects.create(**_clean_kwargs(Group, defaults))


def create_subject_category(**kwargs):
    number = next_number("subject_category")

    defaults = {
        "code": kwargs.pop("code", f"SUB-CAT-{number}"),
        "name": kwargs.pop("name", f"Категория предметов {number}"),
        "description": kwargs.pop("description", ""),
        "is_active": kwargs.pop("is_active", True),
    }
    defaults.update(kwargs)

    return SubjectCategory.objects.create(**_clean_kwargs(SubjectCategory, defaults))


def create_subject(**kwargs):
    number = next_number("subject")
    category = kwargs.pop("category", None) or create_subject_category()

    defaults = {
        "category": category,
        "name": kwargs.pop("name", f"Математика {number}"),
        "short_name": kwargs.pop("short_name", f"Мат-{number}"),
        "description": kwargs.pop("description", ""),
        "is_active": kwargs.pop("is_active", True),
    }
    defaults.update(kwargs)

    return Subject.objects.create(**_clean_kwargs(Subject, defaults))


def create_group_subject(**kwargs):
    academic_year = kwargs.pop("academic_year", None) or create_academic_year()
    period = kwargs.pop("period", None) or create_education_period(
        academic_year=academic_year
    )

    organization = kwargs.pop("organization", None) or create_organization()
    group = kwargs.pop("group", None) or create_group(
        organization=organization,
        academic_year=academic_year.name,
    )
    subject = kwargs.pop("subject", None) or create_subject()

    defaults = {
        "group": group,
        "subject": subject,
        "academic_year": academic_year,
        "period": period,
        "planned_hours": kwargs.pop("planned_hours", 72),
        "contact_hours": kwargs.pop("contact_hours", 36),
        "independent_hours": kwargs.pop("independent_hours", 36),
        "assessment_type": kwargs.pop(
            "assessment_type",
            GroupSubject.AssessmentTypeChoices.NONE,
        ),
        "is_required": kwargs.pop("is_required", True),
        "is_active": kwargs.pop("is_active", True),
        "notes": kwargs.pop("notes", ""),
    }
    defaults.update(kwargs)

    return GroupSubject.objects.create(**_clean_kwargs(GroupSubject, defaults))


def create_course(**kwargs):
    group_subject = kwargs.pop("group_subject", None)

    if group_subject is None:
        academic_year = kwargs.pop("academic_year", None) or create_academic_year()
        period = kwargs.pop("period", None) or create_education_period(
            academic_year=academic_year
        )
        organization = kwargs.pop("organization", None) or create_organization()
        subject = kwargs.pop("subject", None) or create_subject()
        group = kwargs.pop("group", None) or create_group(
            organization=organization,
            academic_year=academic_year.name,
        )
        group_subject = create_group_subject(
            group=group,
            subject=subject,
            academic_year=academic_year,
            period=period,
        )
    else:
        assert group_subject is not None

        academic_year = kwargs.pop("academic_year", group_subject.academic_year)
        period = kwargs.pop("period", group_subject.period)
        subject = kwargs.pop("subject", group_subject.subject)
        organization = kwargs.pop(
            "organization",
            getattr(group_subject.group, "organization", None),
        )

    number = next_number("course")
    author = kwargs.pop("author", None) or create_user()

    defaults = {
        "title": kwargs.pop("title", f"Тестовый курс {number}"),
        "subtitle": kwargs.pop("subtitle", ""),
        "description": kwargs.pop("description", ""),
        "course_type": kwargs.pop("course_type", Course.CourseTypeChoices.ACADEMIC),
        "origin": kwargs.pop("origin", Course.OriginChoices.GROUP_SUBJECT),
        "status": kwargs.pop("status", Course.StatusChoices.DRAFT),
        "visibility": kwargs.pop(
            "visibility",
            Course.VisibilityChoices.ASSIGNED_ONLY,
        ),
        "level": kwargs.pop("level", Course.LevelChoices.BASIC),
        "language": kwargs.pop("language", "ru"),
        "author": author,
        "organization": organization,
        "subject": subject,
        "academic_year": academic_year,
        "period": period,
        "group_subject": group_subject,
        "is_template": kwargs.pop("is_template", False),
        "is_active": kwargs.pop("is_active", True),
        "allow_self_enrollment": kwargs.pop("allow_self_enrollment", False),
        "estimated_minutes": kwargs.pop("estimated_minutes", 1440),
    }
    defaults.update(kwargs)

    return Course.objects.create(**_clean_kwargs(Course, defaults))


def create_course_module(**kwargs):
    course = kwargs.pop("course", None) or create_course()
    number = next_number(f"course_module_{course.pk or 'new'}")

    defaults = {
        "course": course,
        "title": kwargs.pop("title", f"Модуль {number}"),
        "description": kwargs.pop("description", ""),
        "order": kwargs.pop("order", number),
        "is_required": kwargs.pop("is_required", True),
        "is_published": kwargs.pop("is_published", True),
        "estimated_minutes": kwargs.pop("estimated_minutes", 90),
    }
    defaults.update(kwargs)

    return CourseModule.objects.create(**_clean_kwargs(CourseModule, defaults))


def create_course_lesson(**kwargs):
    course = kwargs.pop("course", None) or create_course()
    module = kwargs.pop("module", None) or create_course_module(course=course)
    number = next_number(f"course_lesson_{module.pk or 'new'}")

    defaults = {
        "course": course,
        "module": module,
        "title": kwargs.pop("title", f"Урок курса {number}"),
        "subtitle": kwargs.pop("subtitle", ""),
        "description": kwargs.pop("description", ""),
        "content": kwargs.pop("content", ""),
        "lesson_type": kwargs.pop(
            "lesson_type",
            CourseLesson.LessonTypeChoices.TEXT,
        ),
        "estimated_minutes": kwargs.pop("estimated_minutes", 45),
        "order": kwargs.pop("order", number),
        "is_required": kwargs.pop("is_required", True),
        "is_preview": kwargs.pop("is_preview", False),
        "is_published": kwargs.pop("is_published", True),
        "available_from": kwargs.pop("available_from", None),
        "video_url": kwargs.pop("video_url", ""),
        "external_url": kwargs.pop("external_url", ""),
    }
    defaults.update(kwargs)

    return CourseLesson.objects.create(**_clean_kwargs(CourseLesson, defaults))
