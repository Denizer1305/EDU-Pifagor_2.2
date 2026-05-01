from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.models import AssignmentAttachment
from apps.assignments.permissions import CanManageAssignmentObject, IsTeacherOrAdmin
from apps.assignments.serializers import (
    AssignmentAttachmentSerializer,
    AssignmentAttachmentWriteSerializer,
)
from apps.assignments.services import (
    create_assignment_attachment,
    delete_assignment_attachment,
    update_assignment_attachment,
)
from apps.assignments.views.assignment_structure.common import (
    check_assignment_object_permission,
    get_assignment_or_404,
    validation_error_response,
)


class AssignmentAttachmentListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin, CanManageAssignmentObject)
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_object(self, request, assignment_id: int):
        return get_assignment_or_404(self, request, assignment_id)

    def get(self, request, assignment_id: int, *args, **kwargs):
        assignment = self.get_object(request, assignment_id)
        if assignment is None:
            return Response({"detail": "Работа не найдена."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AssignmentAttachmentSerializer(
            assignment.attachments.order_by("order", "id"),
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, assignment_id: int, *args, **kwargs):
        assignment = self.get_object(request, assignment_id)
        if assignment is None:
            return Response({"detail": "Работа не найдена."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AssignmentAttachmentWriteSerializer(
            data=request.data,
            context={"assignment": assignment},
        )
        serializer.is_valid(raise_exception=True)

        try:
            attachment = create_assignment_attachment(
                assignment=assignment,
                **serializer.validated_data,
            )
        except (DjangoValidationError, ValueError) as exc:
            return validation_error_response(exc)

        output = AssignmentAttachmentSerializer(attachment, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class AssignmentAttachmentDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def _get_attachment(self, pk: int):
        return AssignmentAttachment.objects.select_related(
            "assignment",
            "variant",
        ).filter(id=pk).first()

    def get(self, request, pk: int, *args, **kwargs):
        attachment = self._get_attachment(pk)
        if attachment is None:
            return Response({"detail": "Вложение не найдено."}, status=status.HTTP_404_NOT_FOUND)

        check_assignment_object_permission(self, request, attachment)

        serializer = AssignmentAttachmentSerializer(attachment, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk: int, *args, **kwargs):
        attachment = self._get_attachment(pk)
        if attachment is None:
            return Response({"detail": "Вложение не найдено."}, status=status.HTTP_404_NOT_FOUND)

        check_assignment_object_permission(self, request, attachment)

        serializer = AssignmentAttachmentWriteSerializer(
            data=request.data,
            partial=True,
            context={"assignment": attachment.assignment},
        )
        serializer.is_valid(raise_exception=True)

        try:
            attachment = update_assignment_attachment(attachment, **serializer.validated_data)
        except (DjangoValidationError, ValueError) as exc:
            return validation_error_response(exc)

        output = AssignmentAttachmentSerializer(attachment, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)

    def delete(self, request, pk: int, *args, **kwargs):
        attachment = self._get_attachment(pk)
        if attachment is None:
            return Response({"detail": "Вложение не найдено."}, status=status.HTTP_404_NOT_FOUND)

        check_assignment_object_permission(self, request, attachment)

        delete_assignment_attachment(attachment)
        return Response(status=status.HTTP_204_NO_CONTENT)
