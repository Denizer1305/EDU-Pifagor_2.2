from __future__ import annotations

import django_filters

from apps.schedule.models import ScheduleGenerationBatch, ScheduleImportBatch


class ScheduleGenerationBatchFilter(django_filters.FilterSet):
    created_after = django_filters.DateTimeFilter("created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter("created_at", lookup_expr="lte")

    class Meta:
        model = ScheduleGenerationBatch
        fields = {
            "organization": ["exact"],
            "academic_year": ["exact"],
            "education_period": ["exact"],
            "source": ["exact"],
            "status": ["exact"],
            "generated_by": ["exact"],
            "dry_run": ["exact"],
        }


class ScheduleImportBatchFilter(django_filters.FilterSet):
    created_after = django_filters.DateTimeFilter("created_at", lookup_expr="gte")
    created_before = django_filters.DateTimeFilter("created_at", lookup_expr="lte")

    class Meta:
        model = ScheduleImportBatch
        fields = {
            "organization": ["exact"],
            "academic_year": ["exact"],
            "education_period": ["exact"],
            "source_type": ["exact"],
            "status": ["exact"],
            "imported_by": ["exact"],
        }
