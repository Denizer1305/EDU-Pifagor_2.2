from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class ScheduleTimeStampedModel(models.Model):
    created_at = models.DateTimeField(
        _("Дата создания"),
        auto_now_add=True,
        db_index=True,
    )
    updated_at = models.DateTimeField(
        _("Дата обновления"),
        auto_now=True,
    )

    class Meta:
        abstract = True
