from __future__ import annotations

from rest_framework import serializers

from apps.assignments.models import ReviewComment, SubmissionAnswer, SubmissionReview
from apps.assignments.serializers.common import UserBriefSerializer


class ReviewCommentSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(source="question.id", read_only=True)
    submission_answer_id = serializers.IntegerField(
        source="submission_answer.id", read_only=True
    )
    created_by = UserBriefSerializer(read_only=True)

    class Meta:
        model = ReviewComment
        fields = (
            "id",
            "comment_type",
            "message",
            "score_delta",
            "question_id",
            "submission_answer_id",
            "created_by",
            "created_at",
            "updated_at",
        )


class ReviewCommentCreateSerializer(serializers.Serializer):
    comment_type = serializers.ChoiceField(
        choices=ReviewComment.CommentTypeChoices.choices,
        default=ReviewComment.CommentTypeChoices.GENERAL,
        required=False,
    )
    message = serializers.CharField()
    question_id = serializers.IntegerField(required=False, allow_null=True)
    submission_answer_id = serializers.IntegerField(required=False, allow_null=True)
    score_delta = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        allow_null=True,
    )


class SubmissionReviewListSerializer(serializers.ModelSerializer):
    reviewer = UserBriefSerializer(read_only=True)
    comments = ReviewCommentSerializer(read_only=True, many=True)

    class Meta:
        model = SubmissionReview
        fields = (
            "id",
            "submission_id",
            "review_status",
            "feedback",
            "private_note",
            "score",
            "passed",
            "reviewed_at",
            "reviewer",
            "comments",
            "created_at",
            "updated_at",
        )


class SubmissionReviewDetailSerializer(serializers.ModelSerializer):
    reviewer = UserBriefSerializer(read_only=True)
    comments = ReviewCommentSerializer(read_only=True, many=True)

    class Meta:
        model = SubmissionReview
        fields = (
            "id",
            "submission_id",
            "review_status",
            "feedback",
            "private_note",
            "score",
            "passed",
            "reviewed_at",
            "reviewer",
            "comments",
            "created_at",
            "updated_at",
        )


class SubmissionReviewStartSerializer(serializers.Serializer):
    confirm = serializers.BooleanField(default=True, required=False)


class SubmissionAnswerReviewSerializer(serializers.Serializer):
    manual_score = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    is_correct = serializers.BooleanField(required=False, allow_null=True)
    review_status = serializers.ChoiceField(
        choices=SubmissionAnswer.ReviewStatusChoices.choices,
        default=SubmissionAnswer.ReviewStatusChoices.REVIEWED,
        required=False,
    )


class SubmissionReviewSubmitSerializer(serializers.Serializer):
    feedback = serializers.CharField(required=False, allow_blank=True)
    private_note = serializers.CharField(required=False, allow_blank=True)
    score = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    passed = serializers.BooleanField(required=False, allow_null=True)


class SubmissionReviewReturnForRevisionSerializer(serializers.Serializer):
    feedback = serializers.CharField(required=False, allow_blank=True)
    private_note = serializers.CharField(required=False, allow_blank=True)


class SubmissionReviewApproveSerializer(serializers.Serializer):
    score = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    feedback = serializers.CharField(required=False, allow_blank=True)


class SubmissionReviewRejectSerializer(serializers.Serializer):
    score = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        required=False,
        allow_null=True,
    )
    feedback = serializers.CharField(required=False, allow_blank=True)
