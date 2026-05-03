from __future__ import annotations

from .assignment_admin import (
    AssignmentAdmin,
    AssignmentOfficialFormatInline,
    AssignmentPolicyInline,
)
from .grading_admin import (
    AppealAdmin,
    GradeRecordAdmin,
    PlagiarismCheckAdmin,
)
from .publication_admin import (
    AssignmentAudienceAdmin,
    AssignmentAudienceInline,
    AssignmentPublicationAdmin,
)
from .review_admin import (
    ReviewCommentAdmin,
    ReviewCommentInline,
    SubmissionReviewAdmin,
)
from .rubric_admin import (
    RubricAdmin,
    RubricCriterionAdmin,
    RubricCriterionInline,
)
from .structure_admin import (
    AssignmentAttachmentAdmin,
    AssignmentAttachmentInline,
    AssignmentQuestionAdmin,
    AssignmentSectionAdmin,
    AssignmentSectionInline,
    AssignmentVariantAdmin,
    AssignmentVariantInline,
)
from .submission_admin import (
    SubmissionAdmin,
    SubmissionAnswerAdmin,
    SubmissionAnswerInline,
    SubmissionAttachmentAdmin,
    SubmissionAttachmentInline,
    SubmissionAttemptAdmin,
    SubmissionAttemptInline,
)

__all__ = [
    "AppealAdmin",
    "AssignmentAdmin",
    "AssignmentAttachmentAdmin",
    "AssignmentAttachmentInline",
    "AssignmentAudienceAdmin",
    "AssignmentAudienceInline",
    "AssignmentOfficialFormatInline",
    "AssignmentPolicyInline",
    "AssignmentPublicationAdmin",
    "AssignmentQuestionAdmin",
    "AssignmentSectionAdmin",
    "AssignmentSectionInline",
    "AssignmentVariantAdmin",
    "AssignmentVariantInline",
    "GradeRecordAdmin",
    "PlagiarismCheckAdmin",
    "ReviewCommentAdmin",
    "ReviewCommentInline",
    "RubricAdmin",
    "RubricCriterionAdmin",
    "RubricCriterionInline",
    "SubmissionAdmin",
    "SubmissionAnswerAdmin",
    "SubmissionAnswerInline",
    "SubmissionAttachmentAdmin",
    "SubmissionAttachmentInline",
    "SubmissionAttemptAdmin",
    "SubmissionAttemptInline",
    "SubmissionReviewAdmin",
]
