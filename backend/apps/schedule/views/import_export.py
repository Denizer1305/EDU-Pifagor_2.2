from __future__ import annotations

from django.utils.dateparse import parse_date
from rest_framework import generics, status
from rest_framework.response import Response

from apps.organizations.models import Group
from apps.schedule.filters import (
    ScheduleGenerationBatchFilter,
    ScheduleImportBatchFilter,
)
from apps.schedule.models import (
    ScheduleGenerationBatch,
    ScheduleImportBatch,
    ScheduleRoom,
)
from apps.schedule.permissions import CanImportExportSchedule
from apps.schedule.serializers.import_batch import (
    ScheduleGenerationBatchCreateSerializer,
    ScheduleGenerationBatchSerializer,
    ScheduleImportApplySerializer,
    ScheduleImportBatchSerializer,
    ScheduleImportParseSerializer,
)
from apps.schedule.services.export_services import (
    export_group_schedule,
    export_period_schedule,
    export_room_schedule,
    export_teacher_schedule,
)
from apps.schedule.services.generation_services import generate_lessons_from_patterns
from apps.schedule.services.import_services import (
    apply_import_batch,
    parse_uploaded_schedule,
)
from apps.users.models import User


def _parse_query_date(value: str | None):
    if not value:
        return None

    return parse_date(value)


class ScheduleImportBatchListAPIView(generics.ListAPIView):
    queryset = ScheduleImportBatch.objects.select_related(
        "organization",
        "academic_year",
        "education_period",
        "imported_by",
    )
    serializer_class = ScheduleImportBatchSerializer
    permission_classes = [CanImportExportSchedule]
    filterset_class = ScheduleImportBatchFilter
    ordering = ("-created_at",)


class ScheduleImportBatchDetailAPIView(generics.RetrieveAPIView):
    queryset = ScheduleImportBatch.objects.select_related(
        "organization",
        "academic_year",
        "education_period",
        "imported_by",
    )
    serializer_class = ScheduleImportBatchSerializer
    permission_classes = [CanImportExportSchedule]


class ScheduleImportParseAPIView(generics.GenericAPIView):
    serializer_class = ScheduleImportParseSerializer
    permission_classes = [CanImportExportSchedule]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        batch = ScheduleImportBatch.objects.create(
            imported_by=request.user,
            **serializer.validated_data,
        )

        response_serializer = ScheduleImportBatchSerializer(batch)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ScheduleImportApplyAPIView(generics.GenericAPIView):
    queryset = ScheduleImportBatch.objects.select_related(
        "organization",
        "academic_year",
        "education_period",
        "imported_by",
    )
    serializer_class = ScheduleImportApplySerializer
    permission_classes = [CanImportExportSchedule]

    def post(self, request, *args, **kwargs):
        batch = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rows = parse_uploaded_schedule(rows=request.data.get("rows", []))

        batch = apply_import_batch(
            batch=batch,
            rows=rows,
            created_by=request.user,
            validate_conflicts=serializer.validated_data["validate_conflicts"],
        )

        response_serializer = ScheduleImportBatchSerializer(batch)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class ScheduleGenerationBatchListCreateAPIView(generics.ListCreateAPIView):
    queryset = ScheduleGenerationBatch.objects.select_related(
        "organization",
        "academic_year",
        "education_period",
        "generated_by",
    )
    permission_classes = [CanImportExportSchedule]
    filterset_class = ScheduleGenerationBatchFilter
    ordering = ("-created_at",)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ScheduleGenerationBatchCreateSerializer

        return ScheduleGenerationBatchSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        batch = ScheduleGenerationBatch.objects.create(
            generated_by=request.user,
            **serializer.validated_data,
        )

        batch = generate_lessons_from_patterns(batch=batch)

        response_serializer = ScheduleGenerationBatchSerializer(batch)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ScheduleGenerationBatchDetailAPIView(generics.RetrieveAPIView):
    queryset = ScheduleGenerationBatch.objects.select_related(
        "organization",
        "academic_year",
        "education_period",
        "generated_by",
    )
    serializer_class = ScheduleGenerationBatchSerializer
    permission_classes = [CanImportExportSchedule]


class ScheduleExportGroupAPIView(generics.GenericAPIView):
    permission_classes = [CanImportExportSchedule]

    def get(self, request, *args, **kwargs):
        group = generics.get_object_or_404(Group, pk=kwargs["group_id"])

        data = export_group_schedule(
            group,
            starts_on=_parse_query_date(request.query_params.get("starts_on")),
            ends_on=_parse_query_date(request.query_params.get("ends_on")),
        )

        return Response(data, status=status.HTTP_200_OK)


class ScheduleExportTeacherAPIView(generics.GenericAPIView):
    permission_classes = [CanImportExportSchedule]

    def get(self, request, *args, **kwargs):
        teacher = generics.get_object_or_404(User, pk=kwargs["teacher_id"])

        data = export_teacher_schedule(
            teacher,
            starts_on=_parse_query_date(request.query_params.get("starts_on")),
            ends_on=_parse_query_date(request.query_params.get("ends_on")),
        )

        return Response(data, status=status.HTTP_200_OK)


class ScheduleExportRoomAPIView(generics.GenericAPIView):
    permission_classes = [CanImportExportSchedule]

    def get(self, request, *args, **kwargs):
        room = generics.get_object_or_404(ScheduleRoom, pk=kwargs["room_id"])

        data = export_room_schedule(
            room,
            starts_on=_parse_query_date(request.query_params.get("starts_on")),
            ends_on=_parse_query_date(request.query_params.get("ends_on")),
        )

        return Response(data, status=status.HTTP_200_OK)


class ScheduleExportPeriodAPIView(generics.GenericAPIView):
    permission_classes = [CanImportExportSchedule]

    def get(self, request, *args, **kwargs):
        organization_id = request.query_params.get("organization_id")

        if not organization_id:
            return Response(
                {"organization_id": "Этот параметр обязателен."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = export_period_schedule(
            organization_id=int(organization_id),
            education_period_id=kwargs["education_period_id"],
            starts_on=_parse_query_date(request.query_params.get("starts_on")),
            ends_on=_parse_query_date(request.query_params.get("ends_on")),
        )

        return Response(data, status=status.HTTP_200_OK)
