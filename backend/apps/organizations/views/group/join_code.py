from __future__ import annotations

import logging

from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.organizations.selectors import get_groups_queryset
from apps.organizations.serializers import (
    GroupJoinCodeSerializer,
    GroupSerializer,
)
from apps.organizations.services import (
    clear_group_join_code,
    set_group_join_code,
)

logger = logging.getLogger(__name__)


class GroupJoinCodeView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk, *args, **kwargs):
        logger.info("GroupJoinCodeView.post called group_id=%s", pk)

        group = get_groups_queryset().filter(pk=pk).first()
        if group is None:
            return Response(
                {"detail": "Группа не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = GroupJoinCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = set_group_join_code(
            group=group,
            raw_code=serializer.validated_data["join_code"],
            expires_at=serializer.validated_data.get("join_code_expires_at"),
        )

        return Response(
            GroupSerializer(group).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk, *args, **kwargs):
        logger.info("GroupJoinCodeView.delete called group_id=%s", pk)

        group = get_groups_queryset().filter(pk=pk).first()
        if group is None:
            return Response(
                {"detail": "Группа не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        group = clear_group_join_code(group=group)
        return Response(
            GroupSerializer(group).data,
            status=status.HTTP_200_OK,
        )
