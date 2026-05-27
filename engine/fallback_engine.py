"""Fallback tutoring responses when no specialised subject handler applies."""

from utils.formatting import _build_explanation


def general_explainer(question):
    """Return a generic study-skills style explanation."""
    q_lower = (question or "").lower()

    is_platform_help = (
        "what can you do" in q_lower
        or "how can you help" in q_lower
        or "how do i use" in q_lower
        or "how to use" in q_lower
        or "tutorial" in q_lower
        or q_lower.strip() in {"help", "what is this", "how does this work"}
    )

    if is_platform_help:
        return _build_explanation(
            answer=(
                "This is a guided algebra learning platform. It can solve supported "
                "algebra questions, explain methods, give hints, generate practice, "
                "check answers, and track progress."
            ),
            method=(
                "Use Direct for a final answer, Step-by-step for worked solutions, "
                "Hint when you want help without the full solution, Practice for "
                "generated problems, and Progress to review skill growth."
            ),
            why=(
                "The platform is intentionally focused on algebra so the feedback, "
                "practice, and progress tracking stay specific rather than generic."
            ),
            next_step=(
                "Try 'solve 2x + 4 = 10', 'explain y = mx + c', or open Practice Mode."
            ),
        )

    if "what is" in q_lower:
        topic = q_lower.replace("what is", "", 1).strip()
        return _build_explanation(
            answer=f"{topic.capitalize()} is a concept studied in school subjects.",
            method="A strong explanation should define it, explain why it matters, and give examples.",
            next_step="Ask me to explain it in simple terms or with examples.",
        )

    if "why" in q_lower:
        return _build_explanation(
            answer="A strong why answer explains causes, mechanisms, and consequences.",
            next_step="Ask the full why question and I can structure the answer for you.",
        )

    if "how" in q_lower:
        return _build_explanation(
            answer="A strong how answer explains the process step by step.",
            next_step="Ask the full how question and I can break the process down.",
        )

    return "Try asking a maths, science, humanities, or English question."
