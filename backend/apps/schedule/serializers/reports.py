from __future__ import annotations

from rest_framework import serializers

from apps.organizations.models import Group
from apps.schedule.models import ScheduleRoom
from apps.schedule.serializers.lesson import ScheduledLessonShortSerializer
from apps.users.models import User


class SchedulePeriodQuerySerializer(serializers.Serializer):
    organization = serializers.IntegerField(required=False)
    academic_year = serializers.IntegerField(required=False)
    education_period = serializers.IntegerField(required=False)
    starts_on = serializers.DateField()
    ends_on = serializers.DateField()

    def validate(self, attrs: dict) -> dict:
        starts_on = attrs["starts_on"]
        ends_on = attrs["ends_on"]

        if ends_on < starts_on:
            raise serializers.ValidationError(
                {"ends_on": "Дата окончания не может быть раньше даты начала."}
            )

        return attrs


class GroupScheduleQuerySerializer(SchedulePeriodQuerySerializer):
    group = serializers.IntegerField()


class TeacherScheduleQuerySerializer(SchedulePeriodQuerySerializer):
    teacher = serializers.IntegerField()


class RoomScheduleQuerySerializer(SchedulePeriodQuerySerializer):
    room = serializers.IntegerField()


class DailyScheduleQuerySerializer(serializers.Serializer):
    organization = serializers.IntegerField()
    date = serializers.DateField()


class ScheduleReportSerializer(serializers.Serializer):
    lessons = ScheduledLessonShortSerializer(many=True)
    count = serializers.IntegerField()


class ScheduleReportPeriodSerializer(serializers.Serializer):
    starts_on = serializers.DateField()
    ends_on = serializers.DateField()


class ScheduleGroupReportSerializer(ScheduleReportPeriodSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())


class ScheduleTeacherReportSerializer(ScheduleReportPeriodSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())


class ScheduleRoomReportSerializer(ScheduleReportPeriodSerializer):
    room = serializers.PrimaryKeyRelatedField(queryset=ScheduleRoom.objects.all())
