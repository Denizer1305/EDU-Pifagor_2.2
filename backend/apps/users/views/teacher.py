from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.filters import TeacherProfileFilter
from apps.users.models import TeacherProfile
from apps.users.permissions import (
    CanManageUserRoles,
    CanReviewTeacherVerification,
    IsTeacherProfileOwnerOrAdmin,
)
from apps.users.selectors import get_teacher_profile_by_user_id
from apps.users.serializers.teacher import (
    TeacherOnboardingSerializer,
    TeacherProfileReviewSerializer,
    TeacherProfileSerializer,
)
from apps.users.services.teacher_services import (
    approve_teacher_profile,
    reject_teacher_profile,
    submit_teacher_verification_request,
)


class MyTeacherProfileAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        profile = get_teacher_profile_by_user_id(request.user.id)
        if not profile:
            raise NotFound("Профиль преподавателя не найден.")
        return Response(TeacherProfileSerializer(profile).data)


class TeacherOnboardingAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        profile = get_teacher_profile_by_user_id(request.user.id)
        if not profile:
            raise NotFound("Профиль преподавателя не найден.")

        serializer = TeacherOnboardingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            profile = submit_teacher_verification_request(
                teacher_profile=profile,
                **serializer.validated_data,
            )
        except DjangoValidationError as exc:
            raise ValidationError(
                exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            )

        return Response(
            TeacherProfileSerializer(profile).data,
            status=status.HTTP_200_OK,
        )


class TeacherProfileViewSet(viewsets.ModelViewSet):
    queryset = TeacherProfile.objects.select_related(
        "user",
        "user__profile",
        "requested_organization",
        "requested_department",
        "verified_by",
    )
    serializer_class = TeacherProfileSerializer
    filterset_class = TeacherProfileFilter
    ordering_fields = (
        "created_at",
        "updated_at",
    )
    ordering = (
        "-created_at",
    )

    def get_permissions(self):
        if self.action in {"list", "create", "destroy"}:
            return [CanManageUserRoles()]
        return [IsTeacherProfileOwnerOrAdmin()]


class TeacherProfileReviewAPIView(generics.UpdateAPIView):
    queryset = TeacherProfile.objects.select_related(
        "user",
        "requested_organization",
        "requested_department",
        "verified_by",
    )
    serializer_class = TeacherProfileReviewSerializer
    permission_classes = (CanReviewTeacherVerification,)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        status_value = serializer.validated_data["verification_status"]
        comment = serializer.validated_data.get("verification_comment", "")

        try:
            if status_value == TeacherProfile.VerificationStatusChoices.APPROVED:
                instance = approve_teacher_profile(
                    teacher_profile=instance,
                    reviewer=request.user,
                    comment=comment,
                )
            elif status_value == TeacherProfile.VerificationStatusChoices.REJECTED:
                instance = reject_teacher_profile(
                    teacher_profile=instance,
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

        return Response(
            TeacherProfileSerializer(instance).data,
            status=status.HTTP_200_OK,
        )
