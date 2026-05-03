from __future__ import annotations

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers, status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.journal.filters import JournalSummaryFilter
from apps.journal.models import JournalSummary
from apps.journal.serializers import JournalSummaryDetailSerializer
from apps.journal.services.summary_services import recalculate_journal_summary


class JournalSummaryListAPIView(ListAPIView):
    """Список рассчитанных сводок журнала."""

    permission_classes = (IsAuthenticated,)
    serializer_class = JournalSummaryDetailSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = JournalSummaryFilter
    ordering_fields = (
        "id",
        "attendance_percent",
        "avg_score",
        "progress_percent",
        "debt_count",
        "calculated_at",
    )
    ordering = ("-calculated_at", "-id")

    def get_queryset(self):
        return JournalSummary.objects.select_related(
            "course",
            "group",
            "student",
        ).order_by("-calculated_at", "-id")


class JournalSummaryRecalculateInputSerializer(serializers.Serializer):
    """Входные данные для ручного пересчёта сводки журнала."""

    course_id = serializers.IntegerField(min_value=1)
    group_id = serializers.IntegerField(min_value=1)
    student_id = serializers.IntegerField(min_value=1, required=False, allow_null=True)


class JournalSummaryRecalculateAPIView(APIView):
    """Ручной пересчёт сводки журнала.

    Если student_id не передан, пересчитывается групповая сводка.
    Если student_id передан, пересчитывается сводка конкретного студента.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        input_serializer = JournalSummaryRecalculateInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        summary = recalculate_journal_summary(
            course_id=input_serializer.validated_data["course_id"],
            group_id=input_serializer.validated_data["group_id"],
            student_id=input_serializer.validated_data.get("student_id"),
        )

        output_serializer = JournalSummaryDetailSerializer(
            summary,
            context={"request": request},
        )

        return Response(output_serializer.data, status=status.HTTP_200_OK)
