from __future__ import annotations

from rest_framework import serializers

from apps.feedback.models import FeedbackAttachment


class FeedbackAttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FeedbackAttachment
        fields = (
            "id",
            "original_name",
            "file_type",
            "file_size",
            "file",
            "file_url",
            "created_at",
        )
        read_only_fields = (
            "id",
            "original_name",
            "file_type",
            "file_size",
            "file_url",
            "created_at",
        )

    def get_file_url(self, obj: FeedbackAttachment) -> str:
        request = self.context.get("request")
        if not obj.file:
            return ""

        url = obj.file.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url
