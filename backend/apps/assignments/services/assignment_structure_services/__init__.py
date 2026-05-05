from __future__ import annotations

from .attachments import (
    create_assignment_attachment,
    delete_assignment_attachment,
    update_assignment_attachment,
)
from .questions import (
    create_assignment_question,
    delete_assignment_question,
    reorder_assignment_questions,
    update_assignment_question,
)
from .recalculation import (
    recalculate_assignment_policy_max_score,
    recalculate_assignment_variant_max_score,
)
from .sections import (
    create_assignment_section,
    delete_assignment_section,
    reorder_assignment_sections,
    update_assignment_section,
)
from .variants import (
    create_assignment_variant,
    delete_assignment_variant,
    reorder_assignment_variants,
    update_assignment_variant,
)

__all__ = [
    "create_assignment_attachment",
    "create_assignment_question",
    "create_assignment_section",
    "create_assignment_variant",
    "delete_assignment_attachment",
    "delete_assignment_question",
    "delete_assignment_section",
    "delete_assignment_variant",
    "recalculate_assignment_policy_max_score",
    "recalculate_assignment_variant_max_score",
    "reorder_assignment_questions",
    "reorder_assignment_sections",
    "reorder_assignment_variants",
    "update_assignment_attachment",
    "update_assignment_question",
    "update_assignment_section",
    "update_assignment_variant",
]
