from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.filters import StudentProfileFilter
from apps.users.models import StudentProfile
from apps.users.permissions import (
    CanManageUserRoles,
    CanReviewStudentVerification,
    IsStudentProfileOwnerOrAdmin,
)
from apps.users.selectors import get_student_profile_by_user_id
from apps.users.serializers.student import (
    StudentOnboardingSerializer,
    StudentProfileReviewSerializer,
    StudentProfileSerializer,
)
from apps.users.services.student_services import (
    approve_student_profile,
    reject_student_profile,
    submit_student_group_request,
)


class MyStudentProfileAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        profile = get_student_profile_by_user_id(request.user.id)
        if not profile:
            raise NotFound("Профиль студента не найден.")
        return Response(StudentProfileSerializer(profile).data)


class StudentOnboardingAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        profile = get_student_profile_by_user_id(request.user.id)
        if not profile:
            raise NotFound("Профиль студента не найден.")

        serializer = StudentOnboardingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            profile = submit_student_group_request(
                student_profile=profile,
                requested_organization=serializer.validated_data["requested_organization"],
                requested_department=serializer.validated_data.get("requested_department"),
                requested_group=serializer.validated_data["requested_group"],
                submitted_group_code=serializer.validated_data["submitted_group_code"],
                admission_year=serializer.validated_data.get("admission_year"),
                graduation_year=serializer.validated_data.get("graduation_year"),
                student_code=serializer.validated_data.get("student_code", ""),
                notes=serializer.validated_data.get("notes", ""),
            )
        except DjangoValidationError as exc:
            raise ValidationError(
                exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            )

        return Response(
            StudentProfileSerializer(profile).data,
            status=status.HTTP_200_OK,
        )


class StudentProfileViewSet(viewsets.ModelViewSet):
    queryset = StudentProfile.objects.select_related(
        "user",
        "user__profile",
        "requested_organization",
        "requested_department",
        "requested_group",
        "verified_by",
    )
    serializer_class = StudentProfileSerializer
    filterset_class = StudentProfileFilter
    ordering_fields = (
        "created_at",
        "updated_at",
        "admission_year",
        "graduation_year",
    )
    ordering = (
        "-created_at",
    )

    def get_permissions(self):
        if self.action in {"list", "create", "destroy"}:
            return [CanManageUserRoles()]
        return [IsStudentProfileOwnerOrAdmin()]


class StudentProfileReviewAPIView(generics.UpdateAPIView):
    queryset = StudentProfile.objects.select_related(
        "user",
        "requested_organization",
        "requested_department",
        "requested_group",
        "verified_by",
    )
    serializer_class = StudentProfileReviewSerializer
    permission_classes = (CanReviewStudentVerification,)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        status_value = serializer.validated_data["verification_status"]
        comment = serializer.validated_data.get("verification_comment", "")

        try:
            if status_value == StudentProfile.VerificationStatusChoices.APPROVED:
                instance = approve_student_profile(
                    student_profile=instance,
                    reviewer=request.user,
                    comment=comment,
                )
            elif status_value == StudentProfile.VerificationStatusChoices.REJECTED:
                instance = reject_student_profile(
                    student_profile=instance,
                    reviewer=request.user,
                    comment=comment,
                )
            else:
                raise ValidationError(
                    {"verification_status": "Допустимы только approved или rejected."}
                )
        except DjangoValidationError as exc:
            raise ValidationError(
                exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            )

        return Response(StudentProfileSerializer(instance).data, status=status.HTTP_200_OK)
