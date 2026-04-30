from __future__ import annotations

from django.apps import apps
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.models import Assignment

from apps.assignments.permissions import IsTeacherOrAdmin, is_admin
from apps.assignments.selectors import (
    get_assignment_by_id,
    get_assignment_publication_by_id,
)
from apps.assignments.serializers import (
    AssignmentStatisticsSerializer,
    CourseAssignmentDashboardSerializer,
    PublicationStatisticsSerializer,
    StudentAssignmentProgressSerializer,
)
from apps.assignments.selectors.analytics_selectors import (
    get_assignment_statistics,
    get_course_assignment_dashboard,
    get_publication_statistics,
    get_student_assignment_progress,
)


class AssignmentStatisticsAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def get(self, request, assignment_id: int, *args, **kwargs):
        assignment = get_assignment_by_id(assignment_id=assignment_id)
        if assignment is None:
            return Response({"detail": "Работа не найдена."}, status=status.HTTP_404_NOT_FOUND)

        if not is_admin(request.user) and assignment.author_id != request.user.id:
            return Response({"detail": "Нет доступа."}, status=status.HTTP_403_FORBIDDEN)

        payload = get_assignment_statistics(assignment=assignment)
        serializer = AssignmentStatisticsSerializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PublicationStatisticsAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def get(self, request, publication_id: int, *args, **kwargs):
        publication = get_assignment_publication_by_id(publication_id=publication_id)
        if publication is None:
            return Response({"detail": "Публикация не найдена."}, status=status.HTTP_404_NOT_FOUND)

        if not is_admin(request.user) and publication.assignment.author_id != request.user.id:
            return Response({"detail": "Нет доступа."}, status=status.HTTP_403_FORBIDDEN)

        payload = get_publication_statistics(publication=publication)
        serializer = PublicationStatisticsSerializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)


class StudentAssignmentProgressAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def get(self, request, assignment_id: int, student_id: int, *args, **kwargs):
        assignment = get_assignment_by_id(assignment_id=assignment_id)
        if assignment is None:
            return Response({"detail": "Работа не найдена."}, status=status.HTTP_404_NOT_FOUND)

        if not is_admin(request.user) and assignment.author_id != request.user.id:
            return Response({"detail": "Нет доступа."}, status=status.HTTP_403_FORBIDDEN)

        User = apps.get_model("users", "User")
        student = User.objects.filter(id=student_id).first()
        if student is None:
            return Response({"detail": "Студент не найден."}, status=status.HTTP_404_NOT_FOUND)

        payload = get_student_assignment_progress(student=student, assignment=assignment)
        serializer = StudentAssignmentProgressSerializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseAssignmentDashboardAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def get(self, request, course_id: int, *args, **kwargs):
        Course = apps.get_model("course", "Course")
        course = Course.objects.filter(id=course_id).first()
        if course is None:
            return Response({"detail": "Курс не найден."}, status=status.HTTP_404_NOT_FOUND)

        if not is_admin(request.user):
            has_access = (
                getattr(course, "author_id", None) == request.user.id
                or Assignment.objects.filter(course=course, author=request.user).exists()
            )
            if not has_access:
                return Response({"detail": "Нет доступа."}, status=status.HTTP_403_FORBIDDEN)

        payload = get_course_assignment_dashboard(course=course)
        serializer = CourseAssignmentDashboardSerializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)
