from apps.schedule.services.conflict_services.lesson import detect_conflicts_for_lesson
from apps.schedule.services.conflict_services.pattern import (
    detect_conflicts_for_pattern,
)
from apps.schedule.services.conflict_services.period import detect_conflicts_for_period
from apps.schedule.services.conflict_services.resolution import (
    ignore_conflict,
    resolve_conflict,
)

__all__ = [
    "detect_conflicts_for_lesson",
    "detect_conflicts_for_pattern",
    "detect_conflicts_for_period",
    "ignore_conflict",
    "resolve_conflict",
]
