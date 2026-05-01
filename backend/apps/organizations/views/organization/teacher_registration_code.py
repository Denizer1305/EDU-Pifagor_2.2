from __future__ import annotations

import logging

from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.organizations.selectors import get_organizations_queryset
from apps.organizations.serializers import (
    OrganizationSerializer,
    OrganizationTeacherRegistrationCodeSerializer,
)
from apps.organizations.services import (
    clear_teacher_registration_code,
    disable_teacher_registration_code,
    set_teacher_registration_code,
)

logger = logging.getLogger(__name__)


def get_organization_or_response(pk):
    """Возвращает организацию или None."""

    return get_organizations_queryset().filter(pk=pk).first()


class OrganizationTeacherRegistrationCodeView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk, *args, **kwargs):
        logger.info(
            "OrganizationTeacherRegistrationCodeView.post called organization_id=%s",
            pk,
        )

        organization = get_organization_or_response(pk)
        if organization is None:
            return Response(
                {"detail": "Организация не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrganizationTeacherRegistrationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        organization = set_teacher_registration_code(
            organization=organization,
            raw_code=serializer.validated_data["teacher_registration_code"],
            expires_at=serializer.validated_data.get(
                "teacher_registration_code_expires_at"
            ),
        )

        return Response(
            OrganizationSerializer(organization).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk, *args, **kwargs):
        logger.info(
            "OrganizationTeacherRegistrationCodeView.delete called organization_id=%s",
            pk,
        )

        organization = get_organization_or_response(pk)
        if organization is None:
            return Response(
                {"detail": "Организация не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        organization = clear_teacher_registration_code(organization=organization)
        return Response(
            OrganizationSerializer(organization).data,
            status=status.HTTP_200_OK,
        )


class OrganizationTeacherRegistrationCodeDisableView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk, *args, **kwargs):
        logger.info(
            (
                "OrganizationTeacherRegistrationCodeDisableView.post called "
                "organization_id=%s"
            ),
            pk,
        )

        organization = get_organization_or_response(pk)
        if organization is None:
            return Response(
                {"detail": "Организация не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        organization = disable_teacher_registration_code(organization=organization)
        return Response(
            OrganizationSerializer(organization).data,
            status=status.HTTP_200_OK,
        )
