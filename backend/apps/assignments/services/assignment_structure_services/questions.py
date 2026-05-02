from __future__ import annotations

from django.db import transaction

from apps.assignments.models import Assignment, AssignmentQuestion
from apps.assignments.services.assignment_structure_services.recalculation import (
    recalculate_assignment_policy_max_score,
    recalculate_assignment_variant_max_score,
)


@transaction.atomic
def create_assignment_question(
    *,
    assignment: Assignment,
    prompt: str,
    question_type: str = AssignmentQuestion.QuestionTypeChoices.SHORT_TEXT,
    description: str = "",
    answer_options_json=None,
    correct_answer_json=None,
    validation_rules_json=None,
    explanation: str = "",
    max_score=0,
    order: int = 1,
    is_required: bool = True,
    requires_manual_review: bool = False,
    variant=None,
    section=None,
) -> AssignmentQuestion:
    """Создаёт вопрос работы."""

    question = AssignmentQuestion(
        assignment=assignment,
        variant=variant,
        section=section,
        question_type=question_type,
        prompt=prompt,
        description=description,
        answer_options_json=answer_options_json or [],
        correct_answer_json=correct_answer_json or {},
        validation_rules_json=validation_rules_json or {},
        explanation=explanation,
        max_score=max_score,
        order=order,
        is_required=is_required,
        requires_manual_review=requires_manual_review,
    )
    question.full_clean()
    question.save()

    if variant:
        recalculate_assignment_variant_max_score(variant)

    recalculate_assignment_policy_max_score(assignment)
    return question


@transaction.atomic
def update_assignment_question(
    question: AssignmentQuestion, **fields
) -> AssignmentQuestion:
    """Обновляет вопрос работы."""

    old_variant = question.variant
    old_assignment = question.assignment

    for field_name, value in fields.items():
        setattr(question, field_name, value)

    question.full_clean()
    question.save()

    if old_variant:
        recalculate_assignment_variant_max_score(old_variant)

    if question.variant:
        recalculate_assignment_variant_max_score(question.variant)

    recalculate_assignment_policy_max_score(old_assignment)

    if question.assignment_id != old_assignment.id:
        recalculate_assignment_policy_max_score(question.assignment)

    return question


@transaction.atomic
def delete_assignment_question(question: AssignmentQuestion) -> None:
    """Удаляет вопрос работы."""

    assignment = question.assignment
    variant = question.variant
    question.delete()

    if variant:
        recalculate_assignment_variant_max_score(variant)

    recalculate_assignment_policy_max_score(assignment)


@transaction.atomic
def reorder_assignment_questions(
    *,
    assignment: Assignment,
    question_ids_in_order: list[int],
) -> list[AssignmentQuestion]:
    """Меняет порядок вопросов работы."""

    questions = list(assignment.questions.filter(id__in=question_ids_in_order))
    questions_map = {question.id: question for question in questions}

    ordered_questions: list[AssignmentQuestion] = []

    for index, question_id in enumerate(question_ids_in_order, start=1):
        question = questions_map.get(question_id)
        if question is None:
            continue

        question.order = index
        question.full_clean()
        question.save(update_fields=("order", "updated_at"))
        ordered_questions.append(question)

    recalculate_assignment_policy_max_score(assignment)
    return ordered_questions
