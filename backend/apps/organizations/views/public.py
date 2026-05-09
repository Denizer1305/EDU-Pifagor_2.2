from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from apps.organizations.models import Organization, TeacherOrganization, TeacherSubject
from apps.organizations.serializers.public import (
    PublicOrganizationSerializer,
    PublicTeacherSerializer,
)
from apps.users.models import TeacherProfile

User = get_user_model()


class PublicOrganizationListAPIView(ListAPIView):
    """
    Публичный список активных образовательных организаций.

    Используется на странице преподавателей для выбора организации.
    """

    serializer_class = PublicOrganizationSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        return (
            Organization.objects.filter(is_active=True)
            .select_related("type")
            .order_by("name")
        )


class PublicOrganizationTeacherListAPIView(ListAPIView):
    """
    Публичный список преподавателей выбранной образовательной организации.

    Отдаёт только активных, публичных и подтверждённых преподавателей.
    """

    serializer_class = PublicTeacherSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        organization = self.get_organization()
        today = timezone.localdate()

        current_teacher_links = (
            TeacherOrganization.objects.filter(
                organization=organization,
                is_active=True,
            )
            .filter(Q(starts_at__isnull=True) | Q(starts_at__lte=today))
            .filter(Q(ends_at__isnull=True) | Q(ends_at__gte=today))
            .select_related("organization")
        )

        teacher_subject_links = (
            TeacherSubject.objects.filter(is_active=True)
            .select_related("subject")
            .order_by("-is_primary", "subject__name")
        )

        return (
            User.objects.filter(
                registration_type=User.RegistrationTypeChoices.TEACHER,
                is_active=True,
                teacher_profile__is_public=True,
                teacher_profile__show_on_teachers_page=True,
                teacher_profile__verification_status=TeacherProfile.VerificationStatusChoices.APPROVED,
                teacher_organizations__organization=organization,
                teacher_organizations__is_active=True,
            )
            .filter(
                Q(teacher_organizations__starts_at__isnull=True)
                | Q(teacher_organizations__starts_at__lte=today)
            )
            .filter(
                Q(teacher_organizations__ends_at__isnull=True)
                | Q(teacher_organizations__ends_at__gte=today)
            )
            .select_related(
                "profile",
                "teacher_profile",
            )
            .prefetch_related(
                Prefetch(
                    "teacher_organizations",
                    queryset=current_teacher_links,
                ),
                Prefetch(
                    "teacher_subjects",
                    queryset=teacher_subject_links,
                ),
            )
            .distinct()
            .order_by(
                "profile__last_name",
                "profile__first_name",
                "profile__patronymic",
            )
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organization"] = self.get_organization()
        return context

    def get_organization(self) -> Organization:
        return get_object_or_404(
            Organization,
            pk=self.kwargs["organization_id"],
            is_active=True,
        )
