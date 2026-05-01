from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import CanManageAssignmentObject, IsTeacherOrAdmin
from apps.assignments.selectors import get_assignment_variants_queryset
from apps.assignments.serializers import (
    AssignmentVariantSerializer,
    AssignmentVariantWriteSerializer,
)
from apps.assignments.services import (
    create_assignment_variant,
    delete_assignment_variant,
    reorder_assignment_variants,
    update_assignment_variant,
)
from apps.assignments.views.assignment_structure.common import (
    check_assignment_object_permission,
    get_assignment_or_404,
    validation_error_response,
)


class AssignmentVariantListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin, CanManageAssignmentObject)

    def get_object(self, request, assignment_id: int):
        return get_assignment_or_404(self, request, assignment_id)

    def get(self, request, assignment_id: int, *args, **kwargs):
        assignment = self.get_object(request, assignment_id)
        if assignment is None:
            return Response({"detail": "Работа не найдена."}, status=status.HTTP_404_NOT_FOUND)

        queryset = get_assignment_variants_queryset(assignment_id=assignment.id)
        serializer = AssignmentVariantSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, assignment_id: int, *args, **kwargs):
        assignment = self.get_object(request, assignment_id)
        if assignment is None:
            return Response({"detail": "Работа не найдена."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AssignmentVariantWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            variant = create_assignment_variant(
                assignment=assignment,
                **serializer.validated_data,
            )
        except (DjangoValidationError, ValueError) as exc:
            return validation_error_response(exc)

        output = AssignmentVariantSerializer(variant, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class AssignmentVariantDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def _get_variant(self, pk: int):
        return get_assignment_variants_queryset().filter(id=pk).first()

    def get(self, request, pk: int, *args, **kwargs):
        variant = self._get_variant(pk)
        if variant is None:
            return Response({"detail": "Вариант не найден."}, status=status.HTTP_404_NOT_FOUND)

        check_assignment_object_permission(self, request, variant)

        serializer = AssignmentVariantSerializer(variant, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk: int, *args, **kwargs):
        variant = self._get_variant(pk)
        if variant is None:
            return Response({"detail": "Вариант не найден."}, status=status.HTTP_404_NOT_FOUND)

        check_assignment_object_permission(self, request, variant)

        serializer = AssignmentVariantWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            variant = update_assignment_variant(variant, **serializer.validated_data)
        except (DjangoValidationError, ValueError) as exc:
            return validation_error_response(exc)

        output = AssignmentVariantSerializer(variant, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)

    def delete(self, request, pk: int, *args, **kwargs):
        variant = self._get_variant(pk)
        if variant is None:
            return Response({"detail": "Вариант не найден."}, status=status.HTTP_404_NOT_FOUND)

        check_assignment_object_permission(self, request, variant)

        delete_assignment_variant(variant)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignmentVariantReorderAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin, CanManageAssignmentObject)

    def post(self, request, assignment_id: int, *args, **kwargs):
        assignment = get_assignment_or_404(self, request, assignment_id)
        if assignment is None:
            return Response({"detail": "Работа не найдена."}, status=status.HTTP_404_NOT_FOUND)

        ids = request.data.get("variant_ids", [])
        if not isinstance(ids, list):
            return Response(
                {"variant_ids": ["Ожидается список id вариантов."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        variants = reorder_assignment_variants(
            assignment=assignment,
            variant_ids_in_order=ids,
        )
        serializer = AssignmentVariantSerializer(variants, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
