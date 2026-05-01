from __future__ import annotations

import logging

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import (
    IsSubmissionOwnerOrReviewerOrAdmin,
    is_admin,
    is_teacher,
)
from apps.assignments.selectors import (
    get_student_submissions_queryset,
    get_submission_by_id,
    get_submissions_queryset,
)
from apps.assignments.serializers import (
    SubmissionDetailSerializer,
    SubmissionListSerializer,
)

logger = logging.getLogger(__name__)


class SubmissionListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        logger.info("SubmissionListAPIView.get called user_id=%s", request.user.id)

        if is_teacher(request.user) or is_admin(request.user):
            queryset = get_submissions_queryset(
                search=request.query_params.get("search", ""),
                status=request.query_params.get("status", ""),
                assignment_id=request.query_params.get("assignment_id") or None,
                publication_id=request.query_params.get("publication_id") or None,
                student_id=request.query_params.get("student_id") or None,
                checked_by_id=request.query_params.get("checked_by_id") or None,
            )

            if not request.user.is_superuser:
                queryset = queryset.filter(assignment__author=request.user)
        else:
            queryset = get_student_submissions_queryset(
                student=request.user,
                search=request.query_params.get("search", ""),
                status=request.query_params.get("status", ""),
                course_id=request.query_params.get("course_id") or None,
                lesson_id=request.query_params.get("lesson_id") or None,
            )

        serializer = SubmissionListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubmissionDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsSubmissionOwnerOrReviewerOrAdmin)

    def get_object(self, request, pk: int):
        submission = get_submission_by_id(submission_id=pk)
        if submission is None:
            return None

        self.check_object_permissions(request, submission)
        return submission

    def get(self, request, pk: int, *args, **kwargs):
        submission = self.get_object(request, pk)
        if submission is None:
            return Response(
                {"detail": "Сдача не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = SubmissionDetailSerializer(
            submission,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
