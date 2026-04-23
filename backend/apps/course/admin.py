from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

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


class CourseTeacherInline(admin.TabularInline):
    model = CourseTeacher
    extra = 0
    autocomplete_fields = ("teacher",)
    fields = (
        "teacher",
        "role",
        "is_active",
        "can_edit",
        "can_manage_structure",
        "can_manage_assignments",
        "can_view_analytics",
        "assigned_at",
    )
    readonly_fields = ("assigned_at",)


class CourseModuleInline(admin.TabularInline):
    model = CourseModule
    extra = 0
    fields = (
        "order",
        "title",
        "is_required",
        "is_published",
        "estimated_minutes",
    )


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "code",
        "course_type",
        "status",
        "visibility",
        "author",
        "organization",
        "subject",
        "is_template",
        "is_active",
        "published_at",
        "created_at",
    )
    list_filter = (
        "course_type",
        "origin",
        "status",
        "visibility",
        "level",
        "is_template",
        "is_active",
        "allow_self_enrollment",
        "organization",
        "subject",
        "academic_year",
        "period",
        "created_at",
    )
    search_fields = (
        "title",
        "subtitle",
        "description",
        "code",
        "slug",
        "author__email",
        "author__profile__last_name",
        "author__profile__first_name",
        "organization__name",
        "organization__short_name",
        "subject__name",
        "subject__short_name",
    )
    autocomplete_fields = (
        "author",
        "organization",
        "subject",
        "academic_year",
        "period",
        "group_subject",
    )
    readonly_fields = (
        "uid",
        "code",
        "slug",
        "published_at",
        "archived_at",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
    inlines = [CourseTeacherInline, CourseModuleInline]

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "uid",
                "code",
                "slug",
                "title",
                "subtitle",
                "description",
            )
        }),
        (_("Тип и публикация"), {
            "fields": (
                "course_type",
                "origin",
                "status",
                "visibility",
                "level",
                "language",
                "is_template",
                "is_active",
            )
        }),
        (_("Автор и преподаватели"), {
            "fields": (
                "author",
            )
        }),
        (_("Учебный контур"), {
            "fields": (
                "organization",
                "subject",
                "academic_year",
                "period",
                "group_subject",
            )
        }),
        (_("Доступ и оформление"), {
            "fields": (
                "cover_image",
                "allow_self_enrollment",
                "enrollment_code",
                "estimated_minutes",
            )
        }),
        (_("Даты"), {
            "fields": (
                "starts_at",
                "ends_at",
                "published_at",
                "archived_at",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )


@admin.register(CourseTeacher)
class CourseTeacherAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course",
        "teacher",
        "role",
        "is_active",
        "can_edit",
        "can_manage_structure",
        "can_manage_assignments",
        "assigned_at",
    )
    list_filter = (
        "role",
        "is_active",
        "can_edit",
        "can_manage_structure",
        "can_manage_assignments",
        "can_view_analytics",
        "assigned_at",
    )
    search_fields = (
        "course__title",
        "course__code",
        "teacher__email",
        "teacher__profile__last_name",
        "teacher__profile__first_name",
    )
    autocomplete_fields = (
        "course",
        "teacher",
    )
    ordering = ("course", "teacher")
    readonly_fields = (
        "assigned_at",
        "created_at",
        "updated_at",
    )


@admin.register(CourseModule)
class CourseModuleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "course",
        "order",
        "is_required",
        "is_published",
        "estimated_minutes",
        "created_at",
    )
    list_filter = (
        "is_required",
        "is_published",
        "course__organization",
        "course__subject",
        "created_at",
    )
    search_fields = (
        "title",
        "description",
        "course__title",
        "course__code",
    )
    autocomplete_fields = ("course",)
    ordering = ("course", "order")
    readonly_fields = ("created_at", "updated_at")


@admin.register(CourseLesson)
class CourseLessonAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "course",
        "module",
        "lesson_type",
        "order",
        "is_required",
        "is_preview",
        "is_published",
        "estimated_minutes",
    )
    list_filter = (
        "lesson_type",
        "is_required",
        "is_preview",
        "is_published",
        "course__organization",
        "course__subject",
    )
    search_fields = (
        "title",
        "subtitle",
        "description",
        "content",
        "course__title",
        "module__title",
    )
    autocomplete_fields = (
        "course",
        "module",
    )
    ordering = ("module", "order")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "course",
                "module",
                "order",
                "title",
                "subtitle",
                "description",
                "lesson_type",
            )
        }),
        (_("Контент"), {
            "fields": (
                "content",
                "video_url",
                "external_url",
            )
        }),
        (_("Доступ"), {
            "fields": (
                "estimated_minutes",
                "is_required",
                "is_preview",
                "is_published",
                "available_from",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "material_type",
        "course",
        "lesson",
        "order",
        "is_visible",
        "is_downloadable",
        "created_at",
    )
    list_filter = (
        "material_type",
        "is_visible",
        "is_downloadable",
        "course__organization",
        "course__subject",
    )
    search_fields = (
        "title",
        "description",
        "course__title",
        "lesson__title",
    )
    autocomplete_fields = (
        "course",
        "lesson",
    )
    ordering = ("course", "lesson", "order")
    readonly_fields = ("created_at", "updated_at")


@admin.register(CourseAssignment)
class CourseAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course",
        "assignment_type",
        "target_display",
        "assigned_by",
        "starts_at",
        "ends_at",
        "is_active",
        "auto_enroll",
        "created_at",
    )
    list_filter = (
        "assignment_type",
        "is_active",
        "auto_enroll",
        "course__organization",
        "course__subject",
        "created_at",
    )
    search_fields = (
        "course__title",
        "course__code",
        "group__name",
        "group__code",
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
        "assigned_by__email",
    )
    autocomplete_fields = (
        "course",
        "group",
        "student",
        "assigned_by",
    )
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Кому назначен")
    def target_display(self, obj):
        if obj.group_id:
            return obj.group
        if obj.student_id:
            return obj.student
        return "—"


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course",
        "student",
        "status",
        "progress_percent",
        "enrolled_at",
        "started_at",
        "completed_at",
        "last_activity_at",
    )
    list_filter = (
        "status",
        "course__organization",
        "course__subject",
        "enrolled_at",
    )
    search_fields = (
        "course__title",
        "course__code",
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
    )
    autocomplete_fields = (
        "course",
        "student",
        "assignment",
    )
    ordering = ("-enrolled_at",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "course_display",
        "student_display",
        "progress_percent",
        "completed_lessons_count",
        "total_lessons_count",
        "spent_minutes",
        "last_activity_at",
        "completed_at",
    )
    list_filter = (
        "enrollment__course__organization",
        "enrollment__course__subject",
        "completed_at",
    )
    search_fields = (
        "enrollment__course__title",
        "enrollment__course__code",
        "enrollment__student__email",
        "enrollment__student__profile__last_name",
        "enrollment__student__profile__first_name",
    )
    autocomplete_fields = (
        "enrollment",
        "last_lesson",
    )
    ordering = ("-updated_at",)
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Курс")
    def course_display(self, obj):
        return obj.enrollment.course

    @admin.display(description="Студент")
    def student_display(self, obj):
        return obj.enrollment.student


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "lesson",
        "student_display",
        "status",
        "attempts_count",
        "score",
        "spent_minutes",
        "last_viewed_at",
        "completed_at",
    )
    list_filter = (
        "status",
        "lesson__lesson_type",
        "lesson__course__organization",
        "lesson__course__subject",
    )
    search_fields = (
        "lesson__title",
        "lesson__module__title",
        "lesson__course__title",
        "enrollment__student__email",
        "enrollment__student__profile__last_name",
        "enrollment__student__profile__first_name",
    )
    autocomplete_fields = (
        "enrollment",
        "course_progress",
        "lesson",
    )
    ordering = ("lesson", "id")
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Студент")
    def student_display(self, obj):
        return obj.enrollment.student
