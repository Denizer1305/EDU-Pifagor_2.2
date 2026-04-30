from __future__ import annotations

import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import CanManageAssignmentObject, IsTeacherOrAdmin
from apps.assignments.selectors import (
    get_assignment_by_id,
    get_assignment_questions_queryset,
    get_assignment_sections_queryset,
    get_assignment_variants_queryset,
)
from apps.assignments.serializers import (
    AssignmentAttachmentSerializer,
    AssignmentAttachmentWriteSerializer,
    AssignmentQuestionSerializer,
    AssignmentQuestionWriteSerializer,
    AssignmentSectionSerializer,
    AssignmentSectionWriteSerializer,
    AssignmentVariantSerializer,
    AssignmentVariantWriteSerializer,
)
from apps.assignments.services import (
    create_assignment_attachment,
    create_assignment_question,
    create_assignment_section,
    create_assignment_variant,
    delete_assignment_attachment,
    delete_assignment_question,
    delete_assignment_section,
    delete_assignment_variant,
    reorder_assignment_questions,
    reorder_assignment_sections,
    reorder_assignment_variants,
    update_assignment_attachment,
    update_assignment_question,
    update_assignment_section,
    update_assignment_variant,
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


class AssignmentVariantListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin, CanManageAssignmentObject)

    def get_object(self, request, assignment_id: int):
        assignment = get_assignment_by_id(assignment_id=assignment_id)
        if assignment is None:
            return None
        self.check_object_permissions(request, assignment)
        return assignment

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
            return _validation_error_response(exc)

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

        checker = CanManageAssignmentObject()
        if not checker.has_object_permission(request, self, variant):
            self.permission_denied(request, message=checker.message)

        serializer = AssignmentVariantSerializer(variant, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk: int, *args, **kwargs):
        variant = self._get_variant(pk)
        if variant is None:
            return Response({"detail": "Вариант не найден."}, status=status.HTTP_404_NOT_FOUND)

        checker = CanManageAssignmentObject()
        if not checker.has_object_permission(request, self, variant):
            self.permission_denied(request, message=checker.message)

        serializer = AssignmentVariantWriteSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            variant = update_assignment_variant(variant, **serializer.validated_data)
        except (DjangoValidationError, ValueError) as exc:
            return _validation_error_response(exc)

        output = AssignmentVariantSerializer(variant, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)

    def delete(self, request, pk: int, *args, **kwargs):
        variant = self._get_variant(pk)
        if variant is None:
            return Response({"detail": "Вариант не найден."}, status=status.HTTP_404_NOT_FOUND)

        checker = CanManageAssignmentObject()
        if not checker.has_object_permission(request, self, variant):
            self.permission_denied(request, message=checker.message)

        delete_assignment_variant(variant)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignmentVariantReorderAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin, CanManageAssignmentObject)

    def post(self, request, assignment_id: int, *args, **kwargs):
        assignment = get_assignment_by_id(assignment_id=assignment_id)
        if assignment is None:
            return Response({"detail": "Работа не найдена."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, assignment)

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


class AssignmentSectionListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin, CanManageAssignmentObject)

    def get_object(self, request, assignment_id: int):
        assignment = get_assignment_by_id(assignment_id=assignment_id)
        if assignment is None:
            return None
        self.check_object_permissions(request, assignment)
        return assignment

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
            return _validation_error_response(exc)

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

        checker = CanManageAssignmentObject()
        if not checker.has_object_permission(request, self, section):
            self.permission_denied(request, message=checker.message)

        serializer = AssignmentSectionSerializer(section, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk: int, *args, **kwargs):
        section = self._get_section(pk)
        if section is None:
            return Response({"detail": "Секция не найдена."}, status=status.HTTP_404_NOT_FOUND)

        checker = CanManageAssignmentObject()
        if not checker.has_object_permission(request, self, section):
            self.permission_denied(request, message=checker.message)

        serializer = AssignmentSectionWriteSerializer(
            data=request.data,
            partial=True,
            context={"assignment": section.assignment},
        )
        serializer.is_valid(raise_exception=True)

        try:
            section = update_assignment_section(section, **serializer.validated_data)
        except (DjangoValidationError, ValueError) as exc:
            return _validation_error_response(exc)

        output = AssignmentSectionSerializer(section, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)

    def delete(self, request, pk: int, *args, **kwargs):
        section = self._get_section(pk)
        if section is None:
            return Response({"detail": "Секция не найдена."}, status=status.HTTP_404_NOT_FOUND)

        checker = CanManageAssignmentObject()
        if not checker.has_object_permission(request, self, section):
            self.permission_denied(request, message=checker.message)

        delete_assignment_section(section)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignmentSectionReorderAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin, CanManageAssignmentObject)

    def post(self, request, assignment_id: int, *args, **kwargs):
        assignment = get_assignment_by_id(assignment_id=assignment_id)
        if assignment is None:
            return Response({"detail": "Работа не найдена."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, assignment)

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


class AssignmentQuestionListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin, CanManageAssignmentObject)

    def get_object(self, request, assignment_id: int):
        assignment = get_assignment_by_id(assignment_id=assignment_id)
        if assignment is None:
            return None
        self.check_object_permissions(request, assignment)
        return assignment

    def get(self, request, assignment_id: int, *args, **kwargs):
        assignment = self.get_object(request, assignment_id)
        if assignment is None:
            return Response({"detail": "Работа не найдена."}, status=status.HTTP_404_NOT_FOUND)

        queryset = get_assignment_questions_queryset(assignment_id=assignment.id)
        serializer = AssignmentQuestionSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, assignment_id: int, *args, **kwargs):
        assignment = self.get_object(request, assignment_id)
        if assignment is None:
            return Response({"detail": "Работа не найдена."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AssignmentQuestionWriteSerializer(
            data=request.data,
            context={"assignment": assignment},
        )
        serializer.is_valid(raise_exception=True)

        try:
            question = create_assignment_question(
                assignment=assignment,
                **serializer.validated_data,
            )
        except (DjangoValidationError, ValueError) as exc:
            return _validation_error_response(exc)

        output = AssignmentQuestionSerializer(question, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class AssignmentQuestionDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def _get_question(self, pk: int):
        return get_assignment_questions_queryset().filter(id=pk).first()

    def get(self, request, pk: int, *args, **kwargs):
        question = self._get_question(pk)
        if question is None:
            return Response({"detail": "Вопрос не найден."}, status=status.HTTP_404_NOT_FOUND)

        checker = CanManageAssignmentObject()
        if not checker.has_object_permission(request, self, question):
            self.permission_denied(request, message=checker.message)

        serializer = AssignmentQuestionSerializer(question, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk: int, *args, **kwargs):
        question = self._get_question(pk)
        if question is None:
            return Response({"detail": "Вопрос не найден."}, status=status.HTTP_404_NOT_FOUND)

        checker = CanManageAssignmentObject()
        if not checker.has_object_permission(request, self, question):
            self.permission_denied(request, message=checker.message)

        serializer = AssignmentQuestionWriteSerializer(
            data=request.data,
            partial=True,
            context={"assignment": question.assignment},
        )
        serializer.is_valid(raise_exception=True)

        try:
            question = update_assignment_question(question, **serializer.validated_data)
        except (DjangoValidationError, ValueError) as exc:
            return _validation_error_response(exc)

        output = AssignmentQuestionSerializer(question, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)

    def delete(self, request, pk: int, *args, **kwargs):
        question = self._get_question(pk)
        if question is None:
            return Response({"detail": "Вопрос не найден."}, status=status.HTTP_404_NOT_FOUND)

        checker = CanManageAssignmentObject()
        if not checker.has_object_permission(request, self, question):
            self.permission_denied(request, message=checker.message)

        delete_assignment_question(question)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignmentQuestionReorderAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin, CanManageAssignmentObject)

    def post(self, request, assignment_id: int, *args, **kwargs):
        assignment = get_assignment_by_id(assignment_id=assignment_id)
        if assignment is None:
            return Response({"detail": "Работа не найдена."}, status=status.HTTP_404_NOT_FOUND)

        self.check_object_permissions(request, assignment)

        ids = request.data.get("question_ids", [])
        if not isinstance(ids, list):
            return Response(
                {"question_ids": ["Ожидается список id вопросов."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        questions = reorder_assignment_questions(
            assignment=assignment,
            question_ids_in_order=ids,
        )
        serializer = AssignmentQuestionSerializer(questions, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class AssignmentAttachmentListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin, CanManageAssignmentObject)
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_object(self, request, assignment_id: int):
        assignment = get_assignment_by_id(assignment_id=assignment_id)
        if assignment is None:
            return None
        self.check_object_permissions(request, assignment)
        return assignment

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
            return _validation_error_response(exc)

        output = AssignmentAttachmentSerializer(attachment, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class AssignmentAttachmentDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def _get_attachment(self, pk: int):
        from apps.assignments.models import AssignmentAttachment

        return AssignmentAttachment.objects.select_related("assignment", "variant").filter(id=pk).first()

    def get(self, request, pk: int, *args, **kwargs):
        attachment = self._get_attachment(pk)
        if attachment is None:
            return Response({"detail": "Вложение не найдено."}, status=status.HTTP_404_NOT_FOUND)

        checker = CanManageAssignmentObject()
        if not checker.has_object_permission(request, self, attachment):
            self.permission_denied(request, message=checker.message)

        serializer = AssignmentAttachmentSerializer(attachment, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk: int, *args, **kwargs):
        attachment = self._get_attachment(pk)
        if attachment is None:
            return Response({"detail": "Вложение не найдено."}, status=status.HTTP_404_NOT_FOUND)

        checker = CanManageAssignmentObject()
        if not checker.has_object_permission(request, self, attachment):
            self.permission_denied(request, message=checker.message)

        serializer = AssignmentAttachmentWriteSerializer(
            data=request.data,
            partial=True,
            context={"assignment": attachment.assignment},
        )
        serializer.is_valid(raise_exception=True)

        try:
            attachment = update_assignment_attachment(attachment, **serializer.validated_data)
        except (DjangoValidationError, ValueError) as exc:
            return _validation_error_response(exc)

        output = AssignmentAttachmentSerializer(attachment, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)

    def delete(self, request, pk: int, *args, **kwargs):
        attachment = self._get_attachment(pk)
        if attachment is None:
            return Response({"detail": "Вложение не найдено."}, status=status.HTTP_404_NOT_FOUND)

        checker = CanManageAssignmentObject()
        if not checker.has_object_permission(request, self, attachment):
            self.permission_denied(request, message=checker.message)

        delete_assignment_attachment(attachment)
        return Response(status=status.HTTP_204_NO_CONTENT)
