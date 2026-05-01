from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import CanManageAssignmentObject, IsTeacherOrAdmin
from apps.assignments.selectors import get_assignment_questions_queryset
from apps.assignments.serializers import (
    AssignmentQuestionSerializer,
    AssignmentQuestionWriteSerializer,
)
from apps.assignments.services import (
    create_assignment_question,
    delete_assignment_question,
    reorder_assignment_questions,
    update_assignment_question,
)
from apps.assignments.views.assignment_structure.common import (
    check_assignment_object_permission,
    get_assignment_or_404,
    validation_error_response,
)


class AssignmentQuestionListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin, CanManageAssignmentObject)

    def get_object(self, request, assignment_id: int):
        return get_assignment_or_404(self, request, assignment_id)

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
            return validation_error_response(exc)

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

        check_assignment_object_permission(self, request, question)

        serializer = AssignmentQuestionSerializer(question, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk: int, *args, **kwargs):
        question = self._get_question(pk)
        if question is None:
            return Response({"detail": "Вопрос не найден."}, status=status.HTTP_404_NOT_FOUND)

        check_assignment_object_permission(self, request, question)

        serializer = AssignmentQuestionWriteSerializer(
            data=request.data,
            partial=True,
            context={"assignment": question.assignment},
        )
        serializer.is_valid(raise_exception=True)

        try:
            question = update_assignment_question(question, **serializer.validated_data)
        except (DjangoValidationError, ValueError) as exc:
            return validation_error_response(exc)

        output = AssignmentQuestionSerializer(question, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)

    def delete(self, request, pk: int, *args, **kwargs):
        question = self._get_question(pk)
        if question is None:
            return Response({"detail": "Вопрос не найден."}, status=status.HTTP_404_NOT_FOUND)

        check_assignment_object_permission(self, request, question)

        delete_assignment_question(question)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AssignmentQuestionReorderAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin, CanManageAssignmentObject)

    def post(self, request, assignment_id: int, *args, **kwargs):
        assignment = get_assignment_or_404(self, request, assignment_id)
        if assignment is None:
            return Response({"detail": "Работа не найдена."}, status=status.HTTP_404_NOT_FOUND)

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
