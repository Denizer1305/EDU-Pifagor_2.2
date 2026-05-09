from __future__ import annotations

import re

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from apps.organizations.models import Organization, TeacherOrganization

User = get_user_model()


class PublicOrganizationSerializer(serializers.ModelSerializer):
    """
    Публичный сериализатор образовательной организации
    для страницы преподавателей.
    """

    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = (
            "id",
            "name",
            "short_name",
            "description",
            "city",
            "logo_url",
        )
        read_only_fields = fields

    def get_logo_url(self, obj: Organization) -> str:
        return self._get_file_url(obj.logo)

    def _get_file_url(self, file_field) -> str:
        if not file_field:
            return ""

        try:
            url = file_field.url
        except ValueError:
            return ""

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(url)

        return url


class PublicTeacherSerializer(serializers.ModelSerializer):
    """
    Публичный сериализатор преподавателя для страницы /teachers.

    Возвращает данные сразу в удобной форме для frontend-карточки:
    ФИО, роль, направление, предметы, описание, достижения и изображение.
    """

    organization_id = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    organization_short_name = serializers.SerializerMethodField()

    name = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()
    direction = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    education = serializers.SerializerMethodField()
    experience = serializers.SerializerMethodField()
    awards = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "organization_id",
            "organization_name",
            "organization_short_name",
            "name",
            "role",
            "subject",
            "direction",
            "description",
            "education",
            "experience",
            "awards",
            "tags",
            "image",
            "avatar",
            "cover_image",
            "position",
        )
        read_only_fields = fields

    def get_organization_id(self, obj: User) -> int | None:
        link = self._get_current_organization_link(obj)
        return link.organization_id if link else None

    def get_organization_name(self, obj: User) -> str:
        link = self._get_current_organization_link(obj)
        if not link:
            return ""
        return link.organization.name

    def get_organization_short_name(self, obj: User) -> str:
        link = self._get_current_organization_link(obj)
        if not link:
            return ""
        return link.organization.short_name or link.organization.name

    def get_name(self, obj: User) -> str:
        profile = self._get_profile(obj)
        if profile and profile.full_name:
            return profile.full_name

        return obj.email

    def get_role(self, obj: User) -> str:
        teacher_profile = self._get_teacher_profile(obj)
        organization_link = self._get_current_organization_link(obj)

        if teacher_profile and teacher_profile.public_title:
            return teacher_profile.public_title

        if organization_link and organization_link.position:
            return organization_link.position

        return "Преподаватель"

    def get_subject(self, obj: User) -> str:
        subjects = self._get_subject_names(obj)

        if subjects:
            return subjects[0]

        teacher_profile = self._get_teacher_profile(obj)
        if teacher_profile and teacher_profile.public_title:
            return teacher_profile.public_title

        return "Преподаватель"

    def get_direction(self, obj: User) -> str:
        subjects = self._get_subject_names(obj)

        if subjects:
            return ", ".join(subjects)

        return self.get_role(obj)

    def get_description(self, obj: User) -> str:
        teacher_profile = self._get_teacher_profile(obj)
        profile = self._get_profile(obj)

        if teacher_profile and teacher_profile.bio:
            return teacher_profile.bio

        if teacher_profile and teacher_profile.short_bio:
            return teacher_profile.short_bio

        if profile and profile.about:
            return profile.about

        return ""

    def get_education(self, obj: User) -> str:
        teacher_profile = self._get_teacher_profile(obj)
        if not teacher_profile:
            return ""

        return teacher_profile.education

    def get_experience(self, obj: User) -> int | None:
        teacher_profile = self._get_teacher_profile(obj)
        if not teacher_profile:
            return None

        return teacher_profile.experience

    def get_awards(self, obj: User) -> list[str]:
        teacher_profile = self._get_teacher_profile(obj)

        if not teacher_profile or not teacher_profile.achievements:
            return []

        parts = re.split(r"[\n;]+", teacher_profile.achievements)

        return [part.strip(" -•\t") for part in parts if part.strip(" -•\t")]

    def get_tags(self, obj: User) -> list[str]:
        tags = self._get_subject_names(obj)

        organization_link = self._get_current_organization_link(obj)
        if organization_link and organization_link.position:
            tags.append(organization_link.position)

        teacher_profile = self._get_teacher_profile(obj)
        if teacher_profile and teacher_profile.experience:
            tags.append(f"{teacher_profile.experience} лет опыта")

        unique_tags = []
        for tag in tags:
            if tag and tag not in unique_tags:
                unique_tags.append(tag)

        return unique_tags[:5]

    def get_image(self, obj: User) -> str:
        teacher_profile = self._get_teacher_profile(obj)
        profile = self._get_profile(obj)

        if teacher_profile and teacher_profile.cover_image:
            return self._get_file_url(teacher_profile.cover_image)

        if profile and profile.avatar:
            return self._get_file_url(profile.avatar)

        return ""

    def get_avatar(self, obj: User) -> str:
        profile = self._get_profile(obj)

        if profile and profile.avatar:
            return self._get_file_url(profile.avatar)

        return ""

    def get_cover_image(self, obj: User) -> str:
        teacher_profile = self._get_teacher_profile(obj)

        if teacher_profile and teacher_profile.cover_image:
            return self._get_file_url(teacher_profile.cover_image)

        return ""

    def get_position(self, obj: User) -> str:
        organization_link = self._get_current_organization_link(obj)

        if organization_link:
            return organization_link.position

        return ""

    def _get_profile(self, obj: User):
        try:
            return obj.profile
        except ObjectDoesNotExist:
            return None

    def _get_teacher_profile(self, obj: User):
        try:
            return obj.teacher_profile
        except ObjectDoesNotExist:
            return None

    def _get_current_organization_link(self, obj: User) -> TeacherOrganization | None:
        organization = self.context.get("organization")
        organization_id = organization.id if organization else None

        links = list(obj.teacher_organizations.all())

        if organization_id:
            for link in links:
                if link.organization_id == organization_id and link.is_current:
                    return link

        for link in links:
            if link.is_current and link.is_primary:
                return link

        for link in links:
            if link.is_current:
                return link

        return None

    def _get_subject_names(self, obj: User) -> list[str]:
        subject_links = list(obj.teacher_subjects.all())

        sorted_links = sorted(
            subject_links,
            key=lambda link: (
                not link.is_primary,
                link.subject.name,
            ),
        )

        return [
            link.subject.short_name or link.subject.name
            for link in sorted_links
            if link.is_active and link.subject.is_active
        ]

    def _get_file_url(self, file_field) -> str:
        if not file_field:
            return ""

        try:
            url = file_field.url
        except ValueError:
            return ""

        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(url)

        return url
