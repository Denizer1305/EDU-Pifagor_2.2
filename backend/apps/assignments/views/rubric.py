from __future__ import annotations

import logging

from django.apps import apps
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import CanManageAssignmentObject, IsTeacherOrAdmin
from apps.assignments.selectors import (
    get_rubric_by_id,
    get_rubric_criteria_queryset,
    get_rubrics_queryset,
)
from apps.assignments.serializers import (
    RubricCreateSerializer,
    RubricCriterionSerializer,
    RubricCriterionWriteSerializer,
    RubricDetailSerializer,
    RubricListSerializer,
    RubricUpdateSerializer,
)
from apps.assignments.services import (
    create_rubric,
    create_rubric_criterion,
    delete_rubric_criterion,
    reorder_rubric_criteria,
    update_rubric,
    update_rubric_criterion,
)

logger = logging.getLogger(__name__)


def _validation_error_response(exc):
    if hasattr(exc, "message_dict"):
        payload = exc.message_dict
    elif hasattr(exc, "messages"):
        payload = {"detail": exc.messages}
    else:
        payload = {"detail": [str(exc)]}
    return Response(payload, status=status.HTTP_400_BAD_REQUEST)


def _resolve_organization(organization_id):
    if not organization_id:
        return None

    try:
        model = apps.get_model("organizations", "Organization")
    except LookupError:
        return None

    return model.objects.filter(pk=organization_id).first()


class RubricListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def get(self, request, *args, **kwargs):
        queryset = get_rubrics_queryset(
            search=request.query_params.get("search", ""),
            assignment_kind=request.query_params.get("assignment_kind", ""),
            organization_id=request.query_params.get("organization_id") or None,
            author_id=request.query_params.get("author_id") or None,
        )

        if not request.user.is_superuser:
            queryset = queryset.filter(author=request.user)

        serializer = RubricListSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = RubricCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        organization = _resolve_organization(serializer.validated_data.get("organization_id"))

        try:
            rubric = create_rubric(
                title=serializer.validated_data["title"],
                description=serializer.validated_data.get("description", ""),
                assignment_kind=serializer.validated_data.get("assignment_kind", ""),
                organization=organization,
                author=request.user,
                is_template=serializer.validated_data.get("is_template", True),
                is_active=serializer.validated_data.get("is_active", True),
            )
        except (DjangoValidationError, ValueError) as exc:
            return _validation_error_response(exc)

        output = RubricDetailSerializer(rubric, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class RubricDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin, CanManageAssignmentObject)

    def get_object(self, request, pk: int):
        rubric = get_rubric_by_id(rubric_id=pk)
        if rubric is None:
            return None
        self.check_object_permissions(request, rubric)
        return rubric

    def get(self, request, pk: int, *args, **kwargs):
        rubric = self.get_object(request, pk)
        if rubric is None:
            return Response({"detail": "Рубрика не найдена."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RubricDetailSerializer(rubric, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk: int, *args, **kwargs):
        rubric = self.get_object(request, pk)
        if rubric is None:
            return Response({"detail": "Рубрика не найдена."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RubricUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data
        if "organization_id" in validated:
            validated["organization"] = _resolve_organization(validated.pop("organization_id"))

        try:
            rubric = update_rubric(rubric, **validated)
        except (DjangoValidationError, ValueError) as exc:
            return _validation_error_response(exc)

        output = RubricDetailSerializer(rubric, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)


class RubricCriterionListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin, CanManageAssignmentObject)

    def get_object(self, request, rubric_id: int):
        rubric = get_rubric_by_id(rubric_id=rubric_id)
        if rubric is None:
            return None
        self.check_object_permissions(request, rubric)
        return rubric

    def get(self, request, rubric_id: int, *args, **kwargs):
        rubric = self.get_object(request, rubric_id)
        if rubric is None:
            return Response({"detail": "Рубрика не найдена."}, status=status.HTTP_404_NOT_FOUND)

        queryset = get_rubric_criteria_queryset(rubric_id=rubric.id)
        serializer = RubricCriterionSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, rubric_id: int, *args, **kwargs):
        rubric = self.get_object(request, rubric_id)
        if rubric is None:
            return Response({"detail": "Рубрика не найдена."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RubricCriterionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            criterion = create_rubric_criterion(
                rubric=rubric,
                **serializer.validated_data,
            )
        except (DjangoValidationError, ValueError) as exc:
            return _validation_error_response(exc)

        output = RubricCriterionSerializer(criterion, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class RubricCriterionDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def _get_criterion(self, pk: int):
        return get_rubric_criteria_queryset().filter(id=pk).first()

    def get(self, request, pk: int, *args, **kwargs):
        criterion = self._get_criterion(pk)
        if criterion is None:
            return Response({"detail": "Критерий не найден."}, status=status.HTTP_404_NOT_FOUND)

        checker = CanManageAssignmentObject()
        if not checker.has_object_permission(request, self, criterion.rubric):
            self.permission_denied(request, message=checker.message)

        serializer = RubricCriterionSerializer(criterion, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk: int, *args, **kwargs):
        criterion = self._get_criterion(pk)
        if criterion is None:
            return Response({"detail": "Критерий не найден."}, status=status.HTTP_404_NOT_FOUND)

        checker = CanManageAssignmentObject()
        if not checker.has_object_permission(request, self, criterion.rubric):
            self.permission_denied(request, message=checker.message)

        serializer = RubricCriterionWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            criterion = update_rubric_criterion(criterion, **serializer.validated_data)
        except (DjangoValidationError, ValueError) as exc:
            return _validation_error_response(exc)

        output = RubricCriterionSerializer(criterion, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)

    def delete(self, request, pk: int, *args, **kwargs):
        criterion = self._get_criterion(pk)
        if criterion is None:
            return Response({"detail": "Критерий не найден."}, status=status.HTTP_404_NOT_FOUND)

        checker = CanManageAssignmentObject()
        if not checker.has_object_permission(request, self, criterion.rubric):
            self.permission_denied(request, message=checker.message)

        delete_rubric_criterion(criterion)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RubricCriteriaReorderAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin, CanManageAssignmentObject)

    def post(self, request, rubric_id: int, *args, **kwargs):
        rubric = get_rubric_by_id(rubric_id=rubric_id)
        if rubric is None:
            return Response({"detail": "Рубрика не найдена."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, rubric)

        ids = request.data.get("criterion_ids", [])
        if not isinstance(ids, list):
            return Response(
                {"criterion_ids": ["Ожидается список id критериев."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        criteria = reorder_rubric_criteria(rubric=rubric, criterion_ids_in_order=ids)
        serializer = RubricCriterionSerializer(criteria, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
