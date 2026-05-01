from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import CanManageAssignmentObject, IsTeacherOrAdmin
from apps.assignments.selectors import get_assignment_sections_queryset
from apps.assignments.serializers import (
    AssignmentSectionSerializer,
    AssignmentSectionWriteSerializer,
)
from apps.assignments.services import (
    create_assignment_section,
    delete_assignment_section,
    reorder_assignment_sections,
    update_assignment_section,
)
from apps.assignments.views.assignment_structure.common import (
    check_assignment_object_permission,
    get_assignment_or_404,
    validation_error_response,
)


class AssignmentSectionListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin, CanManageAssignmentObject)

    def get_object(self, request, assignment_id: int):
        return get_assignment_or_404(self, request, assignment_id)

    def get(self, request, assignment_id: int, *args, **kwargs):
        assignment = self.get_object(request, assignment_id)
        if assignment is None:
            return Response({"detail": "Работа не найдена."}, status=status.HTTP_404_NOT_FOUND)

        queryset = get_assignment_sections_queryset(assignment_id=assignment.id)
        serializer = AssignmentSectionSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, assignment_id: int, *args, **kwargs):
        assignment = self.get_object(request, assignment_id)
        if assignment is None:
            return Response({"detail": "Работа не найдена."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AssignmentSectionWriteSerializer(
            data=request.data,
            context={"assignment": assignment},
        )
        serializer.is_valid(raise_exception=True)

        try:
            section = create_assignment_section(
                assignment=assignment,
                **serializer.validated_data,
            )
        except (DjangoValidationError, ValueError) as exc:
            return validation_error_response(exc)

        output = AssignmentSectionSerializer(section, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class AssignmentSectionDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def _get_section(self, pk: int):
        return get_assignment_sections_queryset().filter(id=pk).first()

    def get(self, request, pk: int, *args, **kwargs):
        section = self._get_section(pk)
        if section is None:
            return Response({"detail": "Секция не найдена."}, status=status.HTTP_404_NOT_FOUND)

        check_assignment_object_permission(self, request, section)

        serializer = AssignmentSectionSerializer(section, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk: int, *args, **kwargs):
        section = self._get_section(pk)
        if section is None:
            return Response({"detail": "Секция не найдена."}, status=status.HTTP_404_NOT_FOUND)

        check_assignment_object_permission(self, request, section)

        serializer = AssignmentSectionWriteSerializer(
            data=request.data,
            partial=True,
            context={"assignment": section.assignment},
        )
        serializer.is_valid(raise_exception=True)

        try:
            section = update_assignment_section(section, **serializer.validated_data)
        except (DjangoValidationError, ValueError) as exc:
            return validation_error_response(exc)

        output = AssignmentSectionSerializer(section, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)

    def delete(self, request, pk: int, *args, **kwargs):
        section = self._get_section(pk)
        if section is None:
            return Response({"detail": "Секция не найдена."}, status=status.HTTP_404_NOT_FOUND)

        check_assignment_object_permission(self, request, section)

        delete_assignment_section(section)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignmentSectionReorderAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin, CanManageAssignmentObject)

    def post(self, request, assignment_id: int, *args, **kwargs):
        assignment = get_assignment_or_404(self, request, assignment_id)
        if assignment is None:
            return Response({"detail": "Работа не найдена."}, status=status.HTTP_404_NOT_FOUND)

        ids = request.data.get("section_ids", [])
        if not isinstance(ids, list):
            return Response(
                {"section_ids": ["Ожидается список id секций."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        sections = reorder_assignment_sections(
            assignment=assignment,
            section_ids_in_order=ids,
        )
        serializer = AssignmentSectionSerializer(sections, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
