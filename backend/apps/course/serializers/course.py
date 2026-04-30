from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.course.models import Course, CourseTeacher
from apps.course.validators import (
    validate_course_can_be_published,
    validate_course_dates,
    validate_course_teacher_user,
)
from apps.education.models import AcademicYear, EducationPeriod, GroupSubject
from apps.organizations.models import Organization, Subject

User = get_user_model()


def _build_absolute_media_url(request, file_field) -> str:
    if not file_field:
        return ""

    try:
        url = file_field.url
    except Exception:
        return ""

    if request is not None:
        return request.build_absolute_uri(url)
    return url


class UserShortSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "full_name")

    def get_full_name(self, obj):
        profile = getattr(obj, "profile", None)
        if profile is not None and getattr(profile, "full_name", ""):
            return profile.full_name

        first_name = getattr(profile, "first_name", "") if profile else ""
        last_name = getattr(profile, "last_name", "") if profile else ""
        patronymic = getattr(profile, "patronymic", "") if profile else ""
        parts = [last_name, first_name, patronymic]
        return " ".join(part for part in parts if part).strip() or obj.email


class OrganizationShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "short_name")


class SubjectShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ("id", "name", "short_name")


class AcademicYearShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = ("id", "name", "start_date", "end_date")


class EducationPeriodShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationPeriod
        fields = ("id", "name", "code", "period_type", "sequence")


class GroupSubjectShortSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source="group.name", read_only=True)
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)

    class Meta:
        model = GroupSubject
        fields = (
            "id",
            "group_name",
            "subject_name",
            "academic_year_name",
        )


class CourseTeacherSerializer(serializers.ModelSerializer):
    teacher = UserShortSerializer(read_only=True)

    class Meta:
        model = CourseTeacher
        fields = (
            "id",
            "teacher",
            "role",
            "is_active",
            "can_edit",
            "can_manage_structure",
            "can_manage_assignments",
            "can_view_analytics",
            "assigned_at",
            "created_at",
            "updated_at",
        )


class CourseTeacherCreateSerializer(serializers.Serializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    role = serializers.ChoiceField(
        choices=CourseTeacher.RoleChoices.choices,
        default=CourseTeacher.RoleChoices.TEACHER,
    )
    is_active = serializers.BooleanField(default=True)
    can_edit = serializers.BooleanField(default=True)
    can_manage_structure = serializers.BooleanField(default=True)
    can_manage_assignments = serializers.BooleanField(default=False)
    can_view_analytics = serializers.BooleanField(default=True)

    def validate_teacher(self, value):
        validate_course_teacher_user(user=value)
        return value


class CourseTeacherUpdateSerializer(serializers.Serializer):
    role = serializers.ChoiceField(
        choices=CourseTeacher.RoleChoices.choices,
        required=False,
    )
    is_active = serializers.BooleanField(required=False)
    can_edit = serializers.BooleanField(required=False)
    can_manage_structure = serializers.BooleanField(required=False)
    can_manage_assignments = serializers.BooleanField(required=False)
    can_view_analytics = serializers.BooleanField(required=False)


class CourseListSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)
    organization = OrganizationShortSerializer(read_only=True)
    subject = SubjectShortSerializer(read_only=True)
    academic_year = AcademicYearShortSerializer(read_only=True)
    period = EducationPeriodShortSerializer(read_only=True)
    cover_image_url = serializers.SerializerMethodField()
    teachers_count = serializers.SerializerMethodField()
    modules_count = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "uid",
            "code",
            "slug",
            "title",
            "subtitle",
            "course_type",
            "origin",
            "status",
            "visibility",
            "level",
            "language",
            "author",
            "organization",
            "subject",
            "academic_year",
            "period",
            "cover_image_url",
            "is_template",
            "is_active",
            "allow_self_enrollment",
            "estimated_minutes",
            "starts_at",
            "ends_at",
            "published_at",
            "teachers_count",
            "modules_count",
            "lessons_count",
            "created_at",
            "updated_at",
        )

    def get_cover_image_url(self, obj):
        return _build_absolute_media_url(self.context.get("request"), obj.cover_image)

    def get_teachers_count(self, obj):
        return obj.course_teachers.filter(is_active=True).count()

    def get_modules_count(self, obj):
        return obj.modules.count()

    def get_lessons_count(self, obj):
        return obj.lessons.count()


class CourseDetailSerializer(serializers.ModelSerializer):
    author = UserShortSerializer(read_only=True)
    organization = OrganizationShortSerializer(read_only=True)
    subject = SubjectShortSerializer(read_only=True)
    academic_year = AcademicYearShortSerializer(read_only=True)
    period = EducationPeriodShortSerializer(read_only=True)
    group_subject = GroupSubjectShortSerializer(read_only=True)
    cover_image_url = serializers.SerializerMethodField()
    teachers = serializers.SerializerMethodField()
    modules = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "uid",
            "code",
            "slug",
            "title",
            "subtitle",
            "description",
            "course_type",
            "origin",
            "status",
            "visibility",
            "level",
            "language",
            "author",
            "organization",
            "subject",
            "academic_year",
            "period",
            "group_subject",
            "cover_image_url",
            "is_template",
            "is_active",
            "allow_self_enrollment",
            "enrollment_code",
            "estimated_minutes",
            "starts_at",
            "ends_at",
            "published_at",
            "archived_at",
            "teachers",
            "modules",
            "materials",
            "created_at",
            "updated_at",
        )

    def get_cover_image_url(self, obj):
        return _build_absolute_media_url(self.context.get("request"), obj.cover_image)

    def get_teachers(self, obj):
        queryset = obj.course_teachers.select_related("teacher").order_by("created_at", "id")
        return CourseTeacherSerializer(
            queryset,
            many=True,
            context=self.context,
        ).data

    def get_modules(self, obj):
        from apps.course.serializers.module import CourseModuleDetailSerializer

        queryset = obj.modules.order_by("order", "id")
        return CourseModuleDetailSerializer(
            queryset,
            many=True,
            context=self.context,
        ).data

    def get_materials(self, obj):
        from apps.course.serializers.lesson import CourseMaterialListSerializer

        queryset = obj.materials.filter(lesson__isnull=True).order_by("order", "id")
        return CourseMaterialListSerializer(
            queryset,
            many=True,
            context=self.context,
        ).data


class CoursePublicListSerializer(serializers.ModelSerializer):
    organization = OrganizationShortSerializer(read_only=True)
    subject = SubjectShortSerializer(read_only=True)
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "code",
            "slug",
            "title",
            "subtitle",
            "course_type",
            "level",
            "organization",
            "subject",
            "cover_image_url",
            "estimated_minutes",
            "starts_at",
            "ends_at",
            "published_at",
        )

    def get_cover_image_url(self, obj):
        return _build_absolute_media_url(self.context.get("request"), obj.cover_image)


class CoursePublicDetailSerializer(serializers.ModelSerializer):
    organization = OrganizationShortSerializer(read_only=True)
    subject = SubjectShortSerializer(read_only=True)
    cover_image_url = serializers.SerializerMethodField()
    modules = serializers.SerializerMethodField()
    materials = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "code",
            "slug",
            "title",
            "subtitle",
            "description",
            "course_type",
            "level",
            "organization",
            "subject",
            "cover_image_url",
            "estimated_minutes",
            "starts_at",
            "ends_at",
            "published_at",
            "modules",
            "materials",
        )

    def get_cover_image_url(self, obj):
        return _build_absolute_media_url(self.context.get("request"), obj.cover_image)

    def get_modules(self, obj):
        from apps.course.serializers.module import CourseModuleDetailSerializer

        queryset = obj.modules.filter(is_published=True).order_by("order", "id")
        return CourseModuleDetailSerializer(
            queryset,
            many=True,
            context={**self.context, "public_only": True},
        ).data

    def get_materials(self, obj):
        from apps.course.serializers.lesson import CourseMaterialListSerializer

        queryset = obj.materials.filter(
            lesson__isnull=True,
            is_visible=True,
        ).order_by("order", "id")
        return CourseMaterialListSerializer(
            queryset,
            many=True,
            context=self.context,
        ).data


class CourseCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    subtitle = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    description = serializers.CharField(required=False, allow_blank=True, default="")

    course_type = serializers.ChoiceField(
        choices=Course.CourseTypeChoices.choices,
        default=Course.CourseTypeChoices.AUTHOR,
    )
    origin = serializers.ChoiceField(
        choices=Course.OriginChoices.choices,
        default=Course.OriginChoices.MANUAL,
    )
    status = serializers.ChoiceField(
        choices=Course.StatusChoices.choices,
        required=False,
        default=Course.StatusChoices.DRAFT,
    )
    visibility = serializers.ChoiceField(
        choices=Course.VisibilityChoices.choices,
        default=Course.VisibilityChoices.ASSIGNED_ONLY,
    )
    level = serializers.ChoiceField(
        choices=Course.LevelChoices.choices,
        default=Course.LevelChoices.BASIC,
    )
    language = serializers.CharField(max_length=12, required=False, allow_blank=True, default="ru")

    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    subject = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    period = serializers.PrimaryKeyRelatedField(
        queryset=EducationPeriod.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )
    group_subject = serializers.PrimaryKeyRelatedField(
        queryset=GroupSubject.objects.all(),
        required=False,
        allow_null=True,
        default=None,
    )

    cover_image = serializers.ImageField(required=False, allow_null=True, default=None)
    is_template = serializers.BooleanField(default=False)
    is_active = serializers.BooleanField(default=True)
    allow_self_enrollment = serializers.BooleanField(default=False)
    enrollment_code = serializers.CharField(
        max_length=32,
        required=False,
        allow_blank=True,
        allow_null=True,
        default=None,
    )
    estimated_minutes = serializers.IntegerField(required=False, min_value=0, default=0)

    starts_at = serializers.DateTimeField(required=False, allow_null=True, default=None)
    ends_at = serializers.DateTimeField(required=False, allow_null=True, default=None)

    def validate(self, attrs):
        validate_course_dates(
            starts_at=attrs.get("starts_at"),
            ends_at=attrs.get("ends_at"),
        )

        if attrs.get("status") == Course.StatusChoices.PUBLISHED:
            raise serializers.ValidationError(
                {"status": "Курс нельзя создать сразу опубликованным. Сначала добавьте структуру, затем опубликуйте его отдельным действием."}
            )

        return attrs


class CourseUpdateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False)
    subtitle = serializers.CharField(max_length=255, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)

    course_type = serializers.ChoiceField(
        choices=Course.CourseTypeChoices.choices,
        required=False,
    )
    origin = serializers.ChoiceField(
        choices=Course.OriginChoices.choices,
        required=False,
    )
    status = serializers.ChoiceField(
        choices=Course.StatusChoices.choices,
        required=False,
    )
    visibility = serializers.ChoiceField(
        choices=Course.VisibilityChoices.choices,
        required=False,
    )
    level = serializers.ChoiceField(
        choices=Course.LevelChoices.choices,
        required=False,
    )
    language = serializers.CharField(max_length=12, required=False, allow_blank=True)

    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=False,
        allow_null=True,
    )
    subject = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        required=False,
        allow_null=True,
    )
    academic_year = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(),
        required=False,
        allow_null=True,
    )
    period = serializers.PrimaryKeyRelatedField(
        queryset=EducationPeriod.objects.all(),
        required=False,
        allow_null=True,
    )
    group_subject = serializers.PrimaryKeyRelatedField(
        queryset=GroupSubject.objects.all(),
        required=False,
        allow_null=True,
    )

    cover_image = serializers.ImageField(required=False, allow_null=True)
    is_template = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    allow_self_enrollment = serializers.BooleanField(required=False)
    enrollment_code = serializers.CharField(
        max_length=32,
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    estimated_minutes = serializers.IntegerField(required=False, min_value=0)

    starts_at = serializers.DateTimeField(required=False, allow_null=True)
    ends_at = serializers.DateTimeField(required=False, allow_null=True)

    def validate(self, attrs):
        course = self.context.get("course")

        starts_at = attrs.get("starts_at", getattr(course, "starts_at", None))
        ends_at = attrs.get("ends_at", getattr(course, "ends_at", None))

        validate_course_dates(
            starts_at=starts_at,
            ends_at=ends_at,
        )

        status_value = attrs.get("status")
        if status_value == Course.StatusChoices.PUBLISHED:
            if course is not None:
                validate_course_can_be_published(course=course)
            else:
                raise serializers.ValidationError(
                    {"status": "Для публикации используйте отдельное действие."}
                )

        if status_value == Course.StatusChoices.ARCHIVED:
            raise serializers.ValidationError(
                {"status": "Для архивации используйте отдельное действие."}
            )

        return attrs


class CourseDuplicateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    duplicate_teachers = serializers.BooleanField(default=False)
    duplicate_materials = serializers.BooleanField(default=True)
