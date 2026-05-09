from __future__ import annotations

from itertools import count

academic_year_counter = count(1)
education_period_counter = count(1)
curriculum_counter = count(1)
student_counter = count(1)
teacher_counter = count(1)


def unwrap_factory_result(value):
    """Возвращает объект из результата фабрики, если фабрика вернула tuple."""

    if isinstance(value, tuple):
        return value[0]

    return value
