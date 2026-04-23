from __future__ import annotations

from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.users.filters import ProfileFilter
from apps.users.models import Profile
from apps.users.permissions import CanManageUserRoles
from apps.users.serializers.profile import (
    ProfileDetailSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
)
from apps.users.services.profile_services import get_or_create_base_profile


class MyProfileAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return get_or_create_base_profile(self.request.user)

    def get_serializer_class(self):
        if self.request.method in {"PUT", "PATCH"}:
            return ProfileUpdateSerializer
        return ProfileDetailSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.select_related(
        "user",
        "user__reviewed_by",
    )
    serializer_class = ProfileSerializer
    permission_classes = (CanManageUserRoles,)
    filterset_class = ProfileFilter
    ordering_fields = (
        "created_at",
        "updated_at",
        "last_name",
        "first_name",
    )
    ordering = (
        "last_name",
        "first_name",
        "patronymic",
    )
