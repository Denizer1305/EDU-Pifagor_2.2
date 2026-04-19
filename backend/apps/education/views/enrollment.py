from __future__ import annotations

from rest_framework import generics, status
from rest_framework.response import Response

from apps.education.filters import StudentGroupEnrollmentFilter
from apps.education.permissions import IsAdminOrReadOnly
from apps.education.selectors import get_student_group_enrollments_queryset
from apps.education.serializers import StudentGroupEnrollmentSerializer
from apps.education.services import (
    create_student_group_enrollment,
    update_student_group_enrollment,
)


class StudentGroupEnrollmentListView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = StudentGroupEnrollmentSerializer
    filterset_class = StudentGroupEnrollmentFilter
    search_fields = (
        "student__email",
        "student__profile__last_name",
        "student__profile__first_name",
        "group__name",
        "group__code",
        "academic_year__name",
    )
    ordering_fields = (
        "enrollment_date", "completion_date",
        "journal_number", "created_at",
    )

    def get_queryset(self):
        return get_student_group_enrollments_queryset()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        enrollment = create_student_group_enrollment(
            student=serializer.validated_data["student"],
            group=serializer.validated_data["group"],
            academic_year=serializer.validated_data["academic_year"],
            enrollment_date=serializer.validated_data["enrollment_date"],
            completion_date=serializer.validated_data.get("completion_date"),
            status=serializer.validated_data.get("status"),
            is_primary=serializer.validated_data.get("is_primary", True),
            journal_number=serializer.validated_data.get("journal_number"),
            notes=serializer.validated_data.get("notes", ""),
        )

        output_serializer = self.get_serializer(enrollment)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class StudentGroupEnrollmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = StudentGroupEnrollmentSerializer

    def get_queryset(self):
        return get_student_group_enrollments_queryset()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        enrollment = update_student_group_enrollment(
            enrollment=instance,
            **serializer.validated_data,
        )

        output_serializer = self.get_serializer(enrollment)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)
