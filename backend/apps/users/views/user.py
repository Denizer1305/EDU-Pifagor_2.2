from __future__ import annotations

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.filters import UserFilter
from apps.users.models import User
from apps.users.permissions import CanManageUserRoles
from apps.users.serializers.user import CurrentUserSerializer

try:
    from apps.users.serializers.user import UserSerializer
except ImportError:  # pragma: no cover
    UserSerializer = CurrentUserSerializer


class CurrentUserAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = CurrentUserSerializer(
            request.user,
            context={"request": request},
        )
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("profile").prefetch_related("user_roles__role")
    serializer_class = UserSerializer
    permission_classes = (CanManageUserRoles,)
    filterset_class = UserFilter
    ordering_fields = (
        "created_at",
        "updated_at",
        "email",
    )
    ordering = (
        "-created_at",
        "email",
    )

    def get_serializer_class(self):
        if self.action in {"retrieve"}:
            return CurrentUserSerializer
        return UserSerializer
