from __future__ import annotations

from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _


@admin.action(description=_("Отключить код регистрации преподавателя"))
def disable_teacher_registration_code(modeladmin, request, queryset):
    """Отключает активные коды регистрации преподавателя у выбранных организаций."""

    updated_count = 0

    for obj in queryset:
        if hasattr(obj, "disable_teacher_registration_code"):
            obj.disable_teacher_registration_code()
            obj.save(
                update_fields=(
                    "teacher_registration_code_is_active",
                    "updated_at",
                )
            )
            updated_count += 1

    modeladmin.message_user(
        request,
        _("Отключено кодов регистрации преподавателя: %(count)s")
        % {"count": updated_count},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Очистить код регистрации преподавателя"))
def clear_teacher_registration_code(modeladmin, request, queryset):
    """Полностью очищает коды регистрации преподавателя у выбранных организаций."""

    updated_count = 0

    for obj in queryset:
        if hasattr(obj, "clear_teacher_registration_code"):
            obj.clear_teacher_registration_code()
            obj.save(
                update_fields=(
                    "teacher_registration_code_hash",
                    "teacher_registration_code_is_active",
                    "teacher_registration_code_expires_at",
                    "updated_at",
                )
            )
            updated_count += 1

    modeladmin.message_user(
        request,
        _("Очищено кодов регистрации преподавателя: %(count)s")
        % {"count": updated_count},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Отключить код присоединения к группе"))
def disable_group_join_code(modeladmin, request, queryset):
    """Отключает активные коды присоединения у выбранных групп."""

    updated_count = 0

    for obj in queryset:
        if hasattr(obj, "disable_join_code"):
            obj.disable_join_code()
            obj.save(
                update_fields=(
                    "join_code_is_active",
                    "updated_at",
                )
            )
            updated_count += 1

    modeladmin.message_user(
        request,
        _("Отключено кодов группы: %(count)s") % {"count": updated_count},
        level=messages.SUCCESS,
    )


@admin.action(description=_("Очистить код присоединения к группе"))
def clear_group_join_code(modeladmin, request, queryset):
    """Полностью очищает коды присоединения у выбранных групп."""

    updated_count = 0

    for obj in queryset:
        if hasattr(obj, "clear_join_code"):
            obj.clear_join_code()
            obj.save(
                update_fields=(
                    "join_code_hash",
                    "join_code_is_active",
                    "join_code_expires_at",
                    "updated_at",
                )
            )
            updated_count += 1

    modeladmin.message_user(
        request,
        _("Очищено кодов группы: %(count)s") % {"count": updated_count},
        level=messages.SUCCESS,
    )
