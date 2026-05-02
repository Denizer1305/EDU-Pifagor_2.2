from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import generics, status
from rest_framework.response import Response

from apps.users.models import ParentStudent
from apps.users.permissions import CanReviewParentStudentLink
from apps.users.serializers.parent import (
    ParentStudentReviewSerializer,
    ParentStudentSerializer,
)
from apps.users.views.parent.common import (
    apply_parent_student_review_action,
    django_validation_error_to_drf,
)


class ParentStudentReviewAPIView(generics.UpdateAPIView):
    """Отдельный endpoint проверки связи родитель-студент."""

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
