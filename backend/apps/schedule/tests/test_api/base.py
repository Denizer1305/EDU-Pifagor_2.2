from __future__ import annotations

from datetime import time

from rest_framework.test import APITestCase

from apps.schedule.tests.factories import (
    create_academic_year,
    create_admin,
    create_course,
    create_course_lesson,
    create_education_period,
    create_group,
    create_organization,
    create_schedule_room,
    create_schedule_time_slot,
    create_teacher,
)


def items(response):
    data = response.data

    if isinstance(data, dict) and "results" in data:
        return data["results"]

    return data


def ids(response) -> set[int]:
    return {item["id"] for item in items(response)}


class ScheduleAPIBaseTestCase(APITestCase):
    def setUp(self):
        self.user = create_admin()
        self.client.force_authenticate(self.user)

    def create_context(self):
        organization = create_organization()
        academic_year = create_academic_year()
        education_period = create_education_period(academic_year=academic_year)

        group = create_group(
            organization=organization,
            academic_year=academic_year.name,
        )

        course = create_course(
            organization=organization,
            academic_year=academic_year,
            period=education_period,
            group=group,
        )
        course_lesson = create_course_lesson(course=course)

        time_slot = create_schedule_time_slot(
            organization=organization,
            starts_at=time(9, 0),
            ends_at=time(10, 30),
            duration_minutes=90,
            is_pair=True,
        )

        room = create_schedule_room(
            organization=organization,
            name="Кабинет 305",
            number="305",
            building="Главный корпус",
            floor="3",
        )

        teacher = create_teacher()

        return {
            "organization": organization,
            "academic_year": academic_year,
            "education_period": education_period,
            "group": group,
            "course": course,
            "course_lesson": course_lesson,
            "group_subject": course.group_subject,
            "subject": course.subject,
            "time_slot": time_slot,
            "room": room,
            "teacher": teacher,
        }
