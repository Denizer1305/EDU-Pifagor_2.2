from apps.schedule.serializers.audience import (
    ScheduledLessonAudienceCreateUpdateSerializer,
    ScheduledLessonAudienceSerializer,
    SchedulePatternAudienceCreateUpdateSerializer,
    SchedulePatternAudienceSerializer,
)
from apps.schedule.serializers.calendar import (
    ScheduleCalendarCreateUpdateSerializer,
    ScheduleCalendarSerializer,
    ScheduleCalendarShortSerializer,
    ScheduleWeekTemplateCreateUpdateSerializer,
    ScheduleWeekTemplateSerializer,
    ScheduleWeekTemplateShortSerializer,
)
from apps.schedule.serializers.change import (
    ScheduleChangeCreateSerializer,
    ScheduleChangeSerializer,
)
from apps.schedule.serializers.conflict import (
    ScheduleConflictCreateUpdateSerializer,
    ScheduleConflictIgnoreSerializer,
    ScheduleConflictResolveSerializer,
    ScheduleConflictSerializer,
    ScheduleConflictShortSerializer,
)
from apps.schedule.serializers.import_batch import (
    ScheduleGenerationBatchCreateSerializer,
    ScheduleGenerationBatchSerializer,
    ScheduleImportApplySerializer,
    ScheduleImportBatchSerializer,
    ScheduleImportCreateSerializer,
    ScheduleImportParseSerializer,
)
from apps.schedule.serializers.lesson import (
    ScheduledLessonChangeRoomSerializer,
    ScheduledLessonCreateUpdateSerializer,
    ScheduledLessonReplaceTeacherSerializer,
    ScheduledLessonRescheduleSerializer,
    ScheduledLessonSerializer,
    ScheduledLessonShortSerializer,
    ScheduledLessonStatusSerializer,
)
from apps.schedule.serializers.pattern import (
    SchedulePatternCopySerializer,
    SchedulePatternCreateUpdateSerializer,
    SchedulePatternSerializer,
    SchedulePatternShortSerializer,
)
from apps.schedule.serializers.reports import (
    DailyScheduleQuerySerializer,
    GroupScheduleQuerySerializer,
    RoomScheduleQuerySerializer,
    SchedulePeriodQuerySerializer,
    ScheduleReportSerializer,
    TeacherScheduleQuerySerializer,
)
from apps.schedule.serializers.room import (
    ScheduleRoomCreateUpdateSerializer,
    ScheduleRoomSerializer,
    ScheduleRoomShortSerializer,
)
from apps.schedule.serializers.time_slot import (
    ScheduleTimeSlotBulkCreateSerializer,
    ScheduleTimeSlotCreateUpdateSerializer,
    ScheduleTimeSlotSerializer,
    ScheduleTimeSlotShortSerializer,
)

__all__ = [
    "DailyScheduleQuerySerializer",
    "GroupScheduleQuerySerializer",
    "RoomScheduleQuerySerializer",
    "ScheduleCalendarCreateUpdateSerializer",
    "ScheduleCalendarSerializer",
    "ScheduleCalendarShortSerializer",
    "ScheduleChangeCreateSerializer",
    "ScheduleChangeSerializer",
    "ScheduleConflictCreateUpdateSerializer",
    "ScheduleConflictIgnoreSerializer",
    "ScheduleConflictResolveSerializer",
    "ScheduleConflictSerializer",
    "ScheduleConflictShortSerializer",
    "ScheduleGenerationBatchCreateSerializer",
    "ScheduleGenerationBatchSerializer",
    "ScheduleImportApplySerializer",
    "ScheduleImportBatchSerializer",
    "ScheduleImportCreateSerializer",
    "ScheduleImportParseSerializer",
    "SchedulePatternAudienceCreateUpdateSerializer",
    "SchedulePatternAudienceSerializer",
    "SchedulePatternCopySerializer",
    "SchedulePatternCreateUpdateSerializer",
    "SchedulePatternSerializer",
    "SchedulePatternShortSerializer",
    "SchedulePeriodQuerySerializer",
    "ScheduleReportSerializer",
    "ScheduleRoomCreateUpdateSerializer",
    "ScheduleRoomSerializer",
    "ScheduleRoomShortSerializer",
    "ScheduleTimeSlotBulkCreateSerializer",
    "ScheduleTimeSlotCreateUpdateSerializer",
    "ScheduleTimeSlotSerializer",
    "ScheduleTimeSlotShortSerializer",
    "ScheduleWeekTemplateCreateUpdateSerializer",
    "ScheduleWeekTemplateSerializer",
    "ScheduleWeekTemplateShortSerializer",
    "ScheduledLessonAudienceCreateUpdateSerializer",
    "ScheduledLessonAudienceSerializer",
    "ScheduledLessonChangeRoomSerializer",
    "ScheduledLessonCreateUpdateSerializer",
    "ScheduledLessonReplaceTeacherSerializer",
    "ScheduledLessonRescheduleSerializer",
    "ScheduledLessonSerializer",
    "ScheduledLessonShortSerializer",
    "ScheduledLessonStatusSerializer",
    "TeacherScheduleQuerySerializer",
]
