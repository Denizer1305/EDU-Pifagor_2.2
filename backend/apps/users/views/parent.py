from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.constants import ROLE_ADMIN
from apps.users.filters import ParentProfileFilter, ParentStudentFilter
from apps.users.models import ParentProfile, ParentStudent
from apps.users.permissions import (
    CanManageUserRoles,
    CanReviewParentStudentLink,
    IsParentProfileOwnerOrAdmin,
)
from apps.users.selectors import (
    get_parent_profile_by_user_id,
    get_parent_student_links_for_user,
)
from apps.users.serializers.parent import (
    ParentProfileSerializer,
    ParentProfileUpdateSerializer,
    ParentStudentRequestSerializer,
    ParentStudentReviewSerializer,
    ParentStudentSerializer,
)
from apps.users.services.parent_services import (
    approve_parent_student_link,
    create_parent_student_link_request,
    reject_parent_student_link,
    revoke_parent_student_link,
)

User = get_user_model()


def _user_is_admin(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return user.user_roles.filter(
        role__code=ROLE_ADMIN,
        is_active=True,
    ).exists()


class MyParentProfileAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, request):
        profile = get_parent_profile_by_user_id(request.user.id)
        if not profile:
            raise NotFound("Профиль родителя не найден.")
        return profile

    def get(self, request, *args, **kwargs):
        profile = self.get_object(request)
        return Response(ParentProfileSerializer(profile).data)

    def patch(self, request, *args, **kwargs):
        profile = self.get_object(request)
        serializer = ParentProfileUpdateSerializer(
            profile,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ParentProfileSerializer(profile).data)


class ParentProfileViewSet(viewsets.ModelViewSet):
    queryset = ParentProfile.objects.select_related(
        "user",
        "user__profile",
    )
    serializer_class = ParentProfileSerializer
    filterset_class = ParentProfileFilter
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
        return [IsParentProfileOwnerOrAdmin()]


class ParentStudentRequestAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = ParentStudentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            link = create_parent_student_link_request(
                parent_user=request.user,
                student_user=serializer.validated_data["student_user"],
                relation_type=serializer.validated_data["relation_type"],
                requested_by=request.user,
                comment=serializer.validated_data.get("comment", ""),
                is_primary=serializer.validated_data.get("is_primary", False),
            )
        except DjangoValidationError as exc:
            raise ValidationError(
                exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            )

        return Response(
            ParentStudentSerializer(link).data,
            status=status.HTTP_201_CREATED,
        )


class MyParentStudentLinksAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        queryset = get_parent_student_links_for_user(request.user)
        serializer = ParentStudentSerializer(queryset, many=True)
        return Response(serializer.data)


class ParentStudentViewSet(viewsets.ModelViewSet):
    filterset_class = ParentStudentFilter
    ordering_fields = (
        "created_at",
        "updated_at",
        "approved_at",
    )
    ordering = (
        "-created_at",
    )

    def get_queryset(self):
        queryset = ParentStudent.objects.select_related(
            "parent",
            "parent__profile",
            "student",
            "student__profile",
            "requested_by",
            "approved_by",
        )

        user = self.request.user
        if _user_is_admin(user):
            return queryset

        return queryset.filter(
            Q(parent=user) | Q(student=user)
        ).distinct()

    def get_permissions(self):
        if self.action in {"update", "partial_update", "destroy"}:
            return [CanManageUserRoles()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return ParentStudentRequestSerializer
        if self.action in {"update", "partial_update"}:
            return ParentStudentReviewSerializer
        return ParentStudentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        parent_user = request.user
        parent_user_id = request.data.get("parent_user_id")

        if parent_user_id and _user_is_admin(request.user):
            parent_user = User.objects.filter(id=parent_user_id, is_active=True).first()
            if not parent_user:
                raise ValidationError({"parent_user_id": "Пользователь-родитель не найден."})

        try:
            link = create_parent_student_link_request(
                parent_user=parent_user,
                student_user=serializer.validated_data["student_user"],
                relation_type=serializer.validated_data["relation_type"],
                requested_by=request.user,
                comment=serializer.validated_data.get("comment", ""),
                is_primary=serializer.validated_data.get("is_primary", False),
            )
        except DjangoValidationError as exc:
            raise ValidationError(
                exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            )

        return Response(
            ParentStudentSerializer(link, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        if not _user_is_admin(request.user):
            raise PermissionDenied(
                "Недостаточно прав для изменения статуса родительской связи."
            )

        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        status_value = serializer.validated_data["status"]
        comment = serializer.validated_data.get("comment", "")

        try:
            if status_value == ParentStudent.LinkStatusChoices.APPROVED:
                instance = approve_parent_student_link(
                    link=instance,
                    reviewer=request.user,
                    comment=comment,
                )
            elif status_value == ParentStudent.LinkStatusChoices.REJECTED:
                instance = reject_parent_student_link(
                    link=instance,
                    reviewer=request.user,
                    comment=comment,
                )
            elif status_value == ParentStudent.LinkStatusChoices.REVOKED:
                instance = revoke_parent_student_link(
                    link=instance,
                    reviewer=request.user,
                    comment=comment,
                )
            else:
                raise ValidationError(
                    {"status": "Допустимы только approved, rejected или revoked."}
                )
        except DjangoValidationError as exc:
            raise ValidationError(
                exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            )

        return Response(ParentStudentSerializer(instance).data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ParentStudentReviewAPIView(generics.UpdateAPIView):
    queryset = ParentStudent.objects.select_related(
        "parent",
        "student",
        "requested_by",
        "approved_by",
    )
    serializer_class = ParentStudentReviewSerializer
    permission_classes = (CanReviewParentStudentLink,)

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        status_value = serializer.validated_data["status"]
        comment = serializer.validated_data.get("comment", "")

        try:
            if status_value == ParentStudent.LinkStatusChoices.APPROVED:
                instance = approve_parent_student_link(
                    link=instance,
                    reviewer=request.user,
                    comment=comment,
                )
            elif status_value == ParentStudent.LinkStatusChoices.REJECTED:
                instance = reject_parent_student_link(
                    link=instance,
                    reviewer=request.user,
                    comment=comment,
                )
            elif status_value == ParentStudent.LinkStatusChoices.REVOKED:
                instance = revoke_parent_student_link(
                    link=instance,
                    reviewer=request.user,
                    comment=comment,
                )
            else:
                raise ValidationError(
                    {"status": "Допустимы только approved, rejected или revoked."}
                )
        except DjangoValidationError as exc:
            raise ValidationError(
                exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            )

        return Response(ParentStudentSerializer(instance).data, status=status.HTTP_200_OK)
