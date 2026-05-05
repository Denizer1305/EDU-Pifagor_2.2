from __future__ import annotations

from datetime import date, time

from django.test import TestCase

from apps.schedule.services.import_services import (
    parse_uploaded_schedule,
    validate_import_rows,
)


class ParseUploadedScheduleTestCase(TestCase):
    def test_parse_uploaded_schedule_converts_date_and_time_values(self):
        rows = [
            {
                "date": "2025-09-01",
                "starts_at": "09:00",
                "ends_at": "10:30",
            }
        ]

        parsed_rows = parse_uploaded_schedule(rows=rows)

        self.assertEqual(len(parsed_rows), 1)

        parsed_row = parsed_rows[0]

        self.assertTrue(parsed_row.is_valid)
        self.assertEqual(parsed_row.row_number, 1)
        self.assertEqual(parsed_row.data["date"], date(2025, 9, 1))
        self.assertEqual(parsed_row.data["starts_at"], time(9, 0))
        self.assertEqual(parsed_row.data["ends_at"], time(10, 30))
        self.assertEqual(parsed_row.errors, [])

    def test_parse_uploaded_schedule_marks_invalid_rows(self):
        rows = [
            {
                "date": "wrong-date",
                "starts_at": "",
                "ends_at": "08:00",
            },
            {
                "date": "2025-09-01",
                "starts_at": "10:30",
                "ends_at": "09:00",
            },
        ]

        parsed_rows = parse_uploaded_schedule(rows=rows)

        self.assertEqual(len(parsed_rows), 2)

        self.assertFalse(parsed_rows[0].is_valid)
        self.assertIn(
            "Некорректная или пустая дата занятия.",
            parsed_rows[0].errors,
        )
        self.assertIn(
            "Некорректное или пустое время начала.",
            parsed_rows[0].errors,
        )

        self.assertFalse(parsed_rows[1].is_valid)
        self.assertIn(
            "Время окончания должно быть позже времени начала.",
            parsed_rows[1].errors,
        )

    def test_validate_import_rows_raises_value_error_for_invalid_rows(self):
        parsed_rows = parse_uploaded_schedule(
            rows=[
                {
                    "date": "",
                    "starts_at": "",
                    "ends_at": "",
                }
            ]
        )

        with self.assertRaises(ValueError) as context:
            validate_import_rows(parsed_rows)

        self.assertIn("Строка 1", str(context.exception))
        self.assertIn(
            "Некорректная или пустая дата занятия.",
            str(context.exception),
        )
