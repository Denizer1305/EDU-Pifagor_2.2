from __future__ import annotations

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from apps.assignments.models import (
    Appeal,
    Assignment,
    AssignmentAttachment,
    AssignmentAudience,
    AssignmentOfficialFormat,
    AssignmentPolicy,
    AssignmentPublication,
    AssignmentQuestion,
    AssignmentSection,
    AssignmentVariant,
    GradeRecord,
    PlagiarismCheck,
    ReviewComment,
    Rubric,
    RubricCriterion,
    Submission,
    SubmissionAnswer,
    SubmissionAttachment,
    SubmissionAttempt,
    SubmissionReview,
)


class AssignmentPolicyInline(admin.StackedInline):
    model = AssignmentPolicy
    extra = 0
    can_delete = False
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("Проверка и оценивание"), {
            "fields": (
                "check_mode",
                "grading_mode",
                "max_score",
                "passing_score",
                "requires_manual_review",
            )
        }),
        (_("Попытки и время"), {
            "fields": (
                "attempts_limit",
                "time_limit_minutes",
                "recommended_time_minutes",
                "auto_submit_on_timeout",
            )
        }),
        (_("Отображение и поведение"), {
            "fields": (
                "shuffle_questions",
                "shuffle_answers",
                "show_results_immediately",
                "show_correct_answers_after_submit",
            )
        }),
        (_("Сдача"), {
            "fields": (
                "allow_late_submission",
                "late_penalty_percent",
                "allow_file_upload",
                "allow_text_answer",
                "allow_photo_upload",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )


class AssignmentOfficialFormatInline(admin.StackedInline):
    model = AssignmentOfficialFormat
    extra = 0
    can_delete = False
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (_("Официальный формат"), {
            "fields": (
                "official_family",
                "assessment_year",
                "grade_level",
                "exam_subject_name",
                "is_preparation_only",
            )
        }),
        (_("Источник"), {
            "fields": (
                "source_kind",
                "source_title",
                "source_url",
                "format_version",
            )
        }),
        (_("Дополнительно"), {
            "fields": (
                "has_answer_key",
                "has_scoring_criteria",
                "has_official_demo_source",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )


class AssignmentVariantInline(admin.TabularInline):
    model = AssignmentVariant
    extra = 0
    fields = (
        "title",
        "code",
        "variant_number",
        "order",
        "is_default",
        "max_score",
        "is_active",
    )
    ordering = ("order", "variant_number", "id")


class AssignmentSectionInline(admin.TabularInline):
    model = AssignmentSection
    extra = 0
    fields = (
        "title",
        "variant",
        "section_type",
        "order",
        "max_score",
        "is_required",
    )
    autocomplete_fields = ("variant",)
    ordering = ("order", "id")


class AssignmentAttachmentInline(admin.TabularInline):
    model = AssignmentAttachment
    extra = 0
    fields = (
        "title",
        "variant",
        "attachment_type",
        "file",
        "external_url",
        "is_visible_to_students",
        "order",
    )
    autocomplete_fields = ("variant",)
    ordering = ("order", "id")


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "assignment_kind",
        "control_scope",
        "education_level",
        "status",
        "visibility",
        "course",
        "lesson",
        "author",
        "is_template",
        "is_active",
        "published_at",
        "created_at",
    )
    list_filter = (
        "assignment_kind",
        "control_scope",
        "education_level",
        "status",
        "visibility",
        "is_template",
        "is_active",
        "organization",
        "subject",
        "created_at",
    )
    search_fields = (
        "title",
        "subtitle",
        "description",
        "instructions",
        "author__email",
        "author__profile__last_name",
        "author__profile__first_name",
        "course__title",
        "lesson__title",
        "subject__name",
        "organization__name",
    )
    autocomplete_fields = (
        "course",
        "lesson",
        "subject",
        "organization",
        "author",
    )
    readonly_fields = (
        "uid",
        "published_at",
        "archived_at",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
    inlines = [
        AssignmentPolicyInline,
        AssignmentOfficialFormatInline,
        AssignmentVariantInline,
        AssignmentSectionInline,
        AssignmentAttachmentInline,
    ]

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "uid",
                "title",
                "subtitle",
                "description",
                "instructions",
            )
        }),
        (_("Связи"), {
            "fields": (
                "course",
                "lesson",
                "subject",
                "organization",
                "author",
            )
        }),
        (_("Классификация"), {
            "fields": (
                "assignment_kind",
                "control_scope",
                "education_level",
            )
        }),
        (_("Статус и видимость"), {
            "fields": (
                "status",
                "visibility",
                "is_template",
                "is_active",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "published_at",
                "archived_at",
                "created_at",
                "updated_at",
            )
        }),
    )


@admin.register(AssignmentVariant)
class AssignmentVariantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "assignment",
        "variant_number",
        "order",
        "is_default",
        "max_score",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_default",
        "is_active",
        "assignment__assignment_kind",
        "assignment__education_level",
    )
    search_fields = (
        "title",
        "code",
        "description",
        "assignment__title",
    )
    autocomplete_fields = ("assignment",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("assignment", "order", "variant_number", "id")


@admin.register(AssignmentSection)
class AssignmentSectionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "assignment",
        "variant",
        "section_type",
        "order",
        "max_score",
        "is_required",
        "created_at",
    )
    list_filter = (
        "section_type",
        "is_required",
        "assignment__assignment_kind",
    )
    search_fields = (
        "title",
        "description",
        "assignment__title",
        "variant__title",
    )
    autocomplete_fields = ("assignment", "variant")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("assignment", "order", "id")


@admin.register(AssignmentQuestion)
class AssignmentQuestionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assignment",
        "variant",
        "section",
        "question_type",
        "short_prompt",
        "order",
        "max_score",
        "is_required",
        "requires_manual_review",
        "created_at",
    )
    list_filter = (
        "question_type",
        "is_required",
        "requires_manual_review",
        "assignment__assignment_kind",
        "assignment__education_level",
    )
    search_fields = (
        "prompt",
        "description",
        "explanation",
        "assignment__title",
        "variant__title",
        "section__title",
    )
    autocomplete_fields = ("assignment", "variant", "section")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("assignment", "order", "id")

    @admin.display(description=_("Формулировка"))
    def short_prompt(self, obj):
        return (obj.prompt[:80] + "...") if len(obj.prompt) > 80 else obj.prompt


@admin.register(AssignmentAttachment)
class AssignmentAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "assignment",
        "variant",
        "attachment_type",
        "is_visible_to_students",
        "order",
        "created_at",
    )
    list_filter = (
        "attachment_type",
        "is_visible_to_students",
        "assignment__assignment_kind",
    )
    search_fields = (
        "title",
        "assignment__title",
        "variant__title",
    )
    autocomplete_fields = ("assignment", "variant")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("assignment", "order", "id")


class AssignmentAudienceInline(admin.TabularInline):
    model = AssignmentAudience
    extra = 0
    autocomplete_fields = (
        "group",
        "student",
        "course_enrollment",
    )
    fields = (
        "audience_type",
        "group",
        "student",
        "course_enrollment",
        "is_active",
    )


@admin.register(AssignmentPublication)
class AssignmentPublicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assignment",
        "course",
        "lesson",
        "published_by",
        "status",
        "starts_at",
        "due_at",
        "available_until",
        "is_active",
        "created_at",
    )
    list_filter = (
        "status",
        "is_active",
        "assignment__assignment_kind",
        "assignment__education_level",
        "created_at",
    )
    search_fields = (
        "assignment__title",
        "title_override",
        "notes",
        "course__title",
        "lesson__title",
        "published_by__email",
    )
    autocomplete_fields = (
        "assignment",
        "course",
        "lesson",
        "published_by",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    inlines = [AssignmentAudienceInline]

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "assignment",
                "course",
                "lesson",
                "published_by",
                "title_override",
            )
        }),
        (_("Сроки"), {
            "fields": (
                "starts_at",
                "due_at",
                "available_until",
            )
        }),
        (_("Статус"), {
            "fields": (
                "status",
                "is_active",
                "notes",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )


@admin.register(AssignmentAudience)
class AssignmentAudienceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "publication",
        "audience_type",
        "group",
        "student",
        "course_enrollment",
        "is_active",
        "created_at",
    )
    list_filter = (
        "audience_type",
        "is_active",
        "publication__status",
    )
    search_fields = (
        "publication__assignment__title",
        "group__name",
        "group__code",
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
    )
    autocomplete_fields = (
        "publication",
        "group",
        "student",
        "course_enrollment",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


class SubmissionAnswerInline(admin.TabularInline):
    model = SubmissionAnswer
    extra = 0
    autocomplete_fields = ("question",)
    fields = (
        "question",
        "is_correct",
        "auto_score",
        "manual_score",
        "final_score",
        "review_status",
    )


class SubmissionAttachmentInline(admin.TabularInline):
    model = SubmissionAttachment
    extra = 0
    autocomplete_fields = ("question",)
    fields = (
        "question",
        "file",
        "attachment_type",
        "original_name",
        "file_size",
    )
    readonly_fields = ("original_name", "mime_type", "file_size")


class SubmissionAttemptInline(admin.TabularInline):
    model = SubmissionAttempt
    extra = 0
    fields = (
        "attempt_number",
        "status",
        "started_at",
        "submitted_at",
        "time_spent_minutes",
    )
    readonly_fields = ("started_at", "submitted_at")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assignment",
        "publication",
        "student",
        "variant",
        "status",
        "attempt_number",
        "final_score",
        "percentage",
        "passed",
        "is_late",
        "submitted_at",
        "checked_at",
    )
    list_filter = (
        "status",
        "passed",
        "is_late",
        "assignment__assignment_kind",
        "publication__status",
        "created_at",
    )
    search_fields = (
        "assignment__title",
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
        "publication__assignment__title",
    )
    autocomplete_fields = (
        "publication",
        "assignment",
        "variant",
        "student",
        "checked_by",
    )
    readonly_fields = (
        "submitted_at",
        "completed_at",
        "is_late",
        "late_minutes",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
    inlines = [
        SubmissionAnswerInline,
        SubmissionAttachmentInline,
        SubmissionAttemptInline,
    ]

    fieldsets = (
        (_("Основное"), {
            "fields": (
                "publication",
                "assignment",
                "variant",
                "student",
                "status",
                "attempt_number",
            )
        }),
        (_("Сроки и время"), {
            "fields": (
                "started_at",
                "submitted_at",
                "completed_at",
                "time_spent_minutes",
                "is_late",
                "late_minutes",
            )
        }),
        (_("Оценивание"), {
            "fields": (
                "auto_score",
                "manual_score",
                "final_score",
                "percentage",
                "passed",
            )
        }),
        (_("Проверка"), {
            "fields": (
                "checked_at",
                "checked_by",
            )
        }),
        (_("Служебное"), {
            "fields": (
                "created_at",
                "updated_at",
            )
        }),
    )


@admin.register(SubmissionAnswer)
class SubmissionAnswerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "submission",
        "question",
        "is_correct",
        "auto_score",
        "manual_score",
        "final_score",
        "review_status",
        "created_at",
    )
    list_filter = (
        "is_correct",
        "review_status",
        "question__question_type",
    )
    search_fields = (
        "submission__assignment__title",
        "submission__student__email",
        "question__prompt",
        "answer_text",
    )
    autocomplete_fields = ("submission", "question")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(SubmissionAttachment)
class SubmissionAttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "submission",
        "question",
        "attachment_type",
        "original_name",
        "file_size",
        "created_at",
    )
    list_filter = ("attachment_type",)
    search_fields = (
        "submission__assignment__title",
        "submission__student__email",
        "original_name",
    )
    autocomplete_fields = ("submission", "question")
    readonly_fields = (
        "original_name",
        "mime_type",
        "file_size",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)


@admin.register(SubmissionAttempt)
class SubmissionAttemptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "submission",
        "attempt_number",
        "status",
        "started_at",
        "submitted_at",
        "time_spent_minutes",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = (
        "submission__assignment__title",
        "submission__student__email",
    )
    autocomplete_fields = ("submission",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("submission", "attempt_number")


class ReviewCommentInline(admin.TabularInline):
    model = ReviewComment
    extra = 0
    autocomplete_fields = (
        "question",
        "submission_answer",
        "created_by",
    )
    fields = (
        "comment_type",
        "question",
        "submission_answer",
        "message",
        "score_delta",
        "created_by",
    )


@admin.register(SubmissionReview)
class SubmissionReviewAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "submission",
        "reviewer",
        "review_status",
        "score",
        "passed",
        "reviewed_at",
        "created_at",
    )
    list_filter = (
        "review_status",
        "passed",
    )
    search_fields = (
        "submission__assignment__title",
        "submission__student__email",
        "reviewer__email",
        "feedback",
        "private_note",
    )
    autocomplete_fields = ("submission", "reviewer")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    inlines = [ReviewCommentInline]


@admin.register(ReviewComment)
class ReviewCommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "review",
        "comment_type",
        "question",
        "submission_answer",
        "score_delta",
        "created_by",
        "created_at",
    )
    list_filter = ("comment_type",)
    search_fields = (
        "review__submission__assignment__title",
        "message",
        "question__prompt",
    )
    autocomplete_fields = (
        "review",
        "question",
        "submission_answer",
        "created_by",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


class RubricCriterionInline(admin.TabularInline):
    model = RubricCriterion
    extra = 0
    fields = (
        "title",
        "criterion_type",
        "max_score",
        "order",
        "description",
    )
    ordering = ("order", "id")


@admin.register(Rubric)
class RubricAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "assignment_kind",
        "organization",
        "author",
        "is_template",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_template",
        "is_active",
        "organization",
    )
    search_fields = (
        "title",
        "description",
        "assignment_kind",
        "author__email",
        "organization__name",
    )
    autocomplete_fields = ("organization", "author")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("title",)
    inlines = [RubricCriterionInline]


@admin.register(RubricCriterion)
class RubricCriterionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "rubric",
        "criterion_type",
        "max_score",
        "order",
        "created_at",
    )
    list_filter = ("criterion_type",)
    search_fields = (
        "title",
        "description",
        "rubric__title",
    )
    autocomplete_fields = ("rubric",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("rubric", "order", "id")


@admin.register(GradeRecord)
class GradeRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "assignment",
        "publication",
        "submission",
        "grade_value",
        "grade_numeric",
        "grading_mode",
        "is_final",
        "graded_by",
        "graded_at",
    )
    list_filter = (
        "grading_mode",
        "is_final",
        "graded_at",
    )
    search_fields = (
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
        "assignment__title",
        "grade_value",
    )
    autocomplete_fields = (
        "student",
        "assignment",
        "publication",
        "submission",
        "graded_by",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-graded_at", "-created_at")


@admin.register(PlagiarismCheck)
class PlagiarismCheckAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "submission",
        "status",
        "similarity_percent",
        "checked_at",
        "created_at",
    )
    list_filter = ("status",)
    search_fields = (
        "submission__assignment__title",
        "submission__student__email",
        "report_url",
    )
    autocomplete_fields = ("submission",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(Appeal)
class AppealAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "submission",
        "student",
        "status",
        "resolved_by",
        "resolved_at",
        "created_at",
    )
    list_filter = (
        "status",
        "resolved_at",
    )
    search_fields = (
        "submission__assignment__title",
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
        "reason",
        "resolution",
    )
    autocomplete_fields = (
        "submission",
        "student",
        "resolved_by",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
