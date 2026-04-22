from __future__ import annotations

import django_filters
from django.db.models import Q

from apps.feedback.models import FeedbackRequest


class FeedbackRequestFilter(django_filters.FilterSet):
    q = django_filters.CharFilter(method="filter_q")

    type = django_filters.CharFilter(field_name="type")
    status = django_filters.CharFilter(field_name="status")
    source = django_filters.CharFilter(field_name="source")

    user_id = django_filters.NumberFilter(field_name="user_id")
    assigned_to_id = django_filters.NumberFilter(field_name="processing__assigned_to_id")
    processed_by_id = django_filters.NumberFilter(field_name="processing__processed_by_id")

    is_processed = django_filters.BooleanFilter(method="filter_is_processed")
    is_spam_suspected = django_filters.BooleanFilter(
        field_name="processing__is_spam_suspected"
    )
    is_personal_data_consent = django_filters.BooleanFilter(
        field_name="is_personal_data_consent"
    )

    created_at_from = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="gte",
    )
    created_at_to = django_filters.DateTimeFilter(
        field_name="created_at",
        lookup_expr="lte",
    )

    processed_at_from = django_filters.DateTimeFilter(
        field_name="processing__processed_at",
        lookup_expr="gte",
    )
    processed_at_to = django_filters.DateTimeFilter(
        field_name="processing__processed_at",
        lookup_expr="lte",
    )

    has_attachments = django_filters.BooleanFilter(method="filter_has_attachments")
    is_authenticated_sender = django_filters.BooleanFilter(
        method="filter_is_authenticated_sender"
    )

    class Meta:
        model = FeedbackRequest
        fields = (
            "type",
            "status",
            "source",
            "user_id",
            "assigned_to_id",
            "processed_by_id",
            "is_processed",
            "is_spam_suspected",
            "is_personal_data_consent",
            "created_at_from",
            "created_at_to",
            "processed_at_from",
            "processed_at_to",
            "has_attachments",
            "is_authenticated_sender",
        )

    def filter_q(self, queryset, name, value):
        value = (value or "").strip()
        if not value:
            return queryset

        return queryset.filter(
            Q(uid__icontains=value)
            | Q(subject__icontains=value)
            | Q(message__icontains=value)
            | Q(contact__full_name__icontains=value)
            | Q(contact__email__icontains=value)
            | Q(contact__phone__icontains=value)
            | Q(contact__organization_name__icontains=value)
            | Q(technical__error_code__icontains=value)
            | Q(technical__error_title__icontains=value)
            | Q(technical__error_details__icontains=value)
            | Q(technical__page_url__icontains=value)
            | Q(technical__frontend_route__icontains=value)
            | Q(technical__ip_address__icontains=value)
            | Q(user__email__icontains=value)
            | Q(user__profile__last_name__icontains=value)
            | Q(user__profile__first_name__icontains=value)
            | Q(user__profile__patronymic__icontains=value)
            | Q(processing__assigned_to__email__icontains=value)
            | Q(processing__assigned_to__profile__last_name__icontains=value)
            | Q(processing__assigned_to__profile__first_name__icontains=value)
            | Q(processing__processed_by__email__icontains=value)
            | Q(processing__processed_by__profile__last_name__icontains=value)
            | Q(processing__processed_by__profile__first_name__icontains=value)
            | Q(processing__reply_message__icontains=value)
            | Q(processing__internal_note__icontains=value)
        ).distinct()

    def filter_is_processed(self, queryset, name, value):
        if value is True:
            return queryset.filter(processing__processed_at__isnull=False)

        if value is False:
            return queryset.filter(processing__processed_at__isnull=True)

        return queryset

    def filter_has_attachments(self, queryset, name, value):
        if value is True:
            return queryset.filter(attachments__isnull=False).distinct()

        if value is False:
            return queryset.filter(attachments__isnull=True).distinct()

        return queryset

    def filter_is_authenticated_sender(self, queryset, name, value):
        if value is True:
            return queryset.filter(user__isnull=False)

        if value is False:
            return queryset.filter(user__isnull=True)

        return queryset
