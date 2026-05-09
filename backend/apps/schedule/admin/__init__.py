from apps.schedule.admin.calendar_admin import (
    ScheduleCalendarAdmin,
    ScheduleWeekTemplateAdmin,
)
from apps.schedule.admin.change_admin import ScheduleChangeAdmin
from apps.schedule.admin.conflict_admin import ScheduleConflictAdmin
from apps.schedule.admin.import_batch_admin import (
    ScheduleGenerationBatchAdmin,
    ScheduleImportBatchAdmin,
)
from apps.schedule.admin.lesson_admin import ScheduledLessonAdmin
from apps.schedule.admin.pattern_admin import SchedulePatternAdmin
from apps.schedule.admin.room_admin import ScheduleRoomAdmin
from apps.schedule.admin.time_slot_admin import ScheduleTimeSlotAdmin

__all__ = [
    "ScheduleCalendarAdmin",
    "ScheduleChangeAdmin",
    "ScheduleConflictAdmin",
    "ScheduleGenerationBatchAdmin",
    "ScheduleImportBatchAdmin",
    "SchedulePatternAdmin",
    "ScheduleRoomAdmin",
    "ScheduleTimeSlotAdmin",
    "ScheduleWeekTemplateAdmin",
    "ScheduledLessonAdmin",
]
