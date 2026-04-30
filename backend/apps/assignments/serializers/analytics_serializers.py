from __future__ import annotations

from rest_framework import serializers


class AssignmentStatisticsSerializer(serializers.Serializer):
    assignment_id = serializers.IntegerField()
    submissions_count = serializers.IntegerField()
    avg_score = serializers.DecimalField(max_digits=10, decimal_places=2)
    avg_percentage = serializers.DecimalField(max_digits=10, decimal_places=2)
    passed_count = serializers.IntegerField()
    failed_count = serializers.IntegerField()
    draft_publications_count = serializers.IntegerField()
    published_publications_count = serializers.IntegerField()


class PublicationStatisticsSerializer(serializers.Serializer):
    publication_id = serializers.IntegerField()
    assignment_id = serializers.IntegerField()
    submissions_count = serializers.IntegerField()
    avg_score = serializers.DecimalField(max_digits=10, decimal_places=2)
    avg_percentage = serializers.DecimalField(max_digits=10, decimal_places=2)
    passed_count = serializers.IntegerField()
    failed_count = serializers.IntegerField()
    in_progress_count = serializers.IntegerField()
    submitted_count = serializers.IntegerField()
    reviewed_count = serializers.IntegerField()


class StudentAssignmentProgressSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    assignment_id = serializers.IntegerField()
    attempts_count = serializers.IntegerField()
    last_submission_id = serializers.IntegerField(allow_null=True)
    last_submission_status = serializers.CharField(allow_blank=True)
    last_submission_attempt_number = serializers.IntegerField()
    last_submission_score = serializers.DecimalField(max_digits=10, decimal_places=2)
    last_submission_percentage = serializers.DecimalField(max_digits=10, decimal_places=2)
    passed = serializers.BooleanField()


class CourseAssignmentDashboardSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(allow_null=True)
    assignments_count = serializers.IntegerField()
    publications_count = serializers.IntegerField()
    submissions_count = serializers.IntegerField()
    avg_score = serializers.DecimalField(max_digits=10, decimal_places=2)
    avg_percentage = serializers.DecimalField(max_digits=10, decimal_places=2)
    published_assignments_count = serializers.IntegerField()
    draft_assignments_count = serializers.IntegerField()
