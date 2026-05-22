"""English tutoring helpers for TEEL, themes, and essay structure."""

from utils.formatting import _build_explanation


def generate_teel(topic, idea):
    """Return a simple TEEL paragraph scaffold."""
    return (
        f"T: {idea} is evident in {topic}.\n"
        "E: This is shown through key events or language choices.\n"
        "E: Explain how that evidence supports the idea.\n"
        f"L: Therefore, {idea} shapes the meaning of {topic}."
    )


def handle_english(question):
    """Handle English questions with basic writing scaffolds."""
    q_lower = (question or "").lower()

    if "teel" in q_lower:
        return _build_explanation(
            answer=generate_teel("the text", "the central theme"),
            why="TEEL keeps your paragraph focused on one clear analytical point.",
            next_step="Give me the text and theme and I can turn this into a specific paragraph.",
        )

    if "essay" in q_lower:
        return _build_explanation(
            answer="A strong essay has an introduction, body paragraphs, and a conclusion.",
            method=(
                "Introduction: give context and state the thesis\n"
                "Body paragraphs: use TEEL structure\n"
                "Conclusion: reinforce the argument"
            ),
            why="That structure keeps the argument clear and easy to follow.",
            next_step="Send me your topic and I can build an essay plan.",
        )

    if "theme" in q_lower:
        return _build_explanation(
            answer=(
                "A theme is the underlying idea or message explored through "
                "characters, events, and conflict."
            ),
            method="State the theme, find evidence, then explain how the evidence develops that idea.",
            next_step="Name the text and I can help you analyse one theme in it.",
        )

    return "Specify whether you want essay, theme, paragraph, or TEEL help."
