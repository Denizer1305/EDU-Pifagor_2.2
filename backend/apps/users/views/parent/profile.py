from __future__ import annotations

from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.filters import ParentProfileFilter
from apps.users.models import ParentProfile
from apps.users.permissions import (
    CanManageUserRoles,
    IsParentProfileOwnerOrAdmin,
)
from apps.users.selectors import get_parent_profile_by_user_id
from apps.users.serializers.parent import (
    ParentProfileSerializer,
    ParentProfileUpdateSerializer,
)


class MyParentProfileAPIView(APIView):
    """Личный профиль родителя."""

    permission_classes = (IsAuthenticated,)

    def get_object(self, request):
        profile = get_parent_profile_by_user_id(request.user.id)

        if not profile:
            raise NotFound("Профиль родителя не найден.")

        return profile

    def get(self, request, *args, **kwargs):
        profile = self.get_object(request)
        return Response(
            ParentProfileSerializer(profile).data,
        )

    def patch(self, request, *args, **kwargs):
        profile = self.get_object(request)

        serializer = ParentProfileUpdateSerializer(
            profile,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            ParentProfileSerializer(profile).data,
        )


class ParentProfileViewSet(viewsets.ModelViewSet):
    """Административный ViewSet профилей родителей."""

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
    ordering = ("-created_at",)

    def get_permissions(self):
        if self.action in {"list", "create", "destroy"}:
            return [CanManageUserRoles()]

        return [IsParentProfileOwnerOrAdmin()]
