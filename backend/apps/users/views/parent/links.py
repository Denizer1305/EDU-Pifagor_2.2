from __future__ import annotations

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.filters import ParentStudentFilter
from apps.users.models import ParentStudent
from apps.users.permissions import CanManageUserRoles
from apps.users.selectors import get_parent_student_links_for_user
from apps.users.serializers.parent import (
    ParentStudentRequestSerializer,
    ParentStudentReviewSerializer,
    ParentStudentSerializer,
)
from apps.users.services.parent_services import create_parent_student_link_request
from apps.users.views.parent.common import (
    apply_parent_student_review_action,
    django_validation_error_to_drf,
    user_is_admin,
)

User = get_user_model()


class ParentStudentRequestAPIView(APIView):
    """Создание заявки на связь родитель-студент."""

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
            raise django_validation_error_to_drf(exc) from exc

        return Response(
            ParentStudentSerializer(link).data,
            status=status.HTTP_201_CREATED,
        )


class MyParentStudentLinksAPIView(APIView):
    """Список связей родитель-студент для текущего пользователя."""

    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        queryset = get_parent_student_links_for_user(request.user)
        serializer = ParentStudentSerializer(
            queryset,
            many=True,
        )
        return Response(serializer.data)


class ParentStudentViewSet(viewsets.ModelViewSet):
    """ViewSet связей родитель-студент."""

    filterset_class = ParentStudentFilter
    ordering_fields = (
        "created_at",
        "updated_at",
        "approved_at",
    )
    ordering = ("-created_at",)

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

        if user_is_admin(user):
            return queryset

        return queryset.filter(
            Q(parent=user) | Q(student=user),
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

        if parent_user_id and user_is_admin(request.user):
            parent_user = User.objects.filter(
                id=parent_user_id,
                is_active=True,
            ).first()

            if not parent_user:
                raise ValidationError(
                    {"parent_user_id": "Пользователь-родитель не найден."}
                )

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
            raise django_validation_error_to_drf(exc) from exc

        return Response(
            ParentStudentSerializer(
                link,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        if not user_is_admin(request.user):
            raise PermissionDenied(
                "Недостаточно прав для изменения статуса родительской связи."
            )

        instance = self.get_object()

        serializer = self.get_serializer(
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)

        status_value = serializer.validated_data["status"]
        comment = serializer.validated_data.get("comment", "")

        try:
            instance = apply_parent_student_review_action(
                link=instance,
                reviewer=request.user,
                status_value=status_value,
                comment=comment,
            )
        except DjangoValidationError as exc:
            raise django_validation_error_to_drf(exc) from exc

        return Response(
            ParentStudentSerializer(instance).data,
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
