"""Fallback tutoring responses when no specialised subject handler applies."""

from utils.formatting import _build_explanation


def general_explainer(question):
    """Return a generic study-skills style explanation."""
    q_lower = (question or "").lower()

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
