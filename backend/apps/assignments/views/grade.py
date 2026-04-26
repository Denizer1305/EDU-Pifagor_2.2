from __future__ import annotations

from django.db.models import QuerySet
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.models import GradeRecord
from apps.assignments.permissions import IsSubmissionOwnerOrReviewerOrAdmin, IsTeacherOrAdmin, is_admin, is_teacher
from apps.assignments.selectors import get_submission_by_id
from apps.assignments.serializers import (
    GradeRecordDetailSerializer,
    GradeRecordListSerializer,
)
from apps.assignments.services import create_grade_record_from_submission


def _get_grade_queryset() -> QuerySet[GradeRecord]:
    return GradeRecord.objects.select_related(
        "student",
        "assignment",
        "publication",
        "submission",
        "graded_by",
    ).order_by("-created_at")


class GradeRecordListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        queryset = _get_grade_queryset()

        if is_teacher(request.user) or is_admin(request.user):
            if not request.user.is_superuser:
                queryset = queryset.filter(assignment__author=request.user)
        else:
            queryset = queryset.filter(student=request.user)

        if request.query_params.get("assignment_id"):
            queryset = queryset.filter(assignment_id=request.query_params.get("assignment_id"))

        if request.query_params.get("publication_id"):
            queryset = queryset.filter(publication_id=request.query_params.get("publication_id"))

        if request.query_params.get("student_id") and (is_teacher(request.user) or is_admin(request.user)):
            queryset = queryset.filter(student_id=request.query_params.get("student_id"))

        serializer = GradeRecordListSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class GradeRecordDetailAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk: int, *args, **kwargs):
        grade = _get_grade_queryset().filter(id=pk).first()
        if grade is None:
            return Response({"detail": "Оценка не найдена."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_superuser:
            if is_teacher(request.user) and grade.assignment.author_id != request.user.id:
                return Response({"detail": "Нет доступа."}, status=status.HTTP_403_FORBIDDEN)
            if not is_teacher(request.user) and grade.student_id != request.user.id:
                return Response({"detail": "Нет доступа."}, status=status.HTTP_403_FORBIDDEN)

        serializer = GradeRecordDetailSerializer(grade, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class GradeRecordCreateFromSubmissionAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, submission_id: int, *args, **kwargs):
        submission = get_submission_by_id(submission_id=submission_id)
        if submission is None:
            return Response({"detail": "Сдача не найдена."}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_superuser and submission.assignment.author_id != request.user.id:
            return Response({"detail": "Нет доступа."}, status=status.HTTP_403_FORBIDDEN)

        grade = create_grade_record_from_submission(
            submission=submission,
            graded_by=request.user,
            is_final=bool(request.data.get("is_final", True)),
        )
        serializer = GradeRecordDetailSerializer(grade, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
