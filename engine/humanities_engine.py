"""Humanities tutoring helpers for history and geography topics."""

from utils.formatting import _build_explanation, _bullet_lines


def handle_humanities(question):
    """Handle history and geography questions with structured notes."""
    q_lower = (question or "").lower()

    if "ww2" in q_lower or "world war 2" in q_lower or "world war ii" in q_lower:
        return _build_explanation(
            answer="WW2 was caused by a mix of political instability, aggression, and failed international responses.",
            method=_bullet_lines([
                "Treaty of Versailles resentment",
                "Rise of fascist leaders",
                "Expansionist aggression in Europe and Asia",
                "Failure of the League of Nations",
                "Appeasement policy",
            ]),
            check="Immediate trigger: Germany invaded Poland in 1939.",
            next_step="Ask for short notes or a paragraph version if you need this for homework.",
        )

    if "ww1" in q_lower or "world war 1" in q_lower or "world war i" in q_lower:
        return _build_explanation(
            answer="WW1 grew from long-term tensions between European powers.",
            method=_bullet_lines([
                "Militarism",
                "Alliances",
                "Imperialism",
                "Nationalism",
            ]),
            check="Immediate trigger: the assassination of Archduke Franz Ferdinand.",
            next_step="Ask me to turn this into a paragraph or study cards.",
        )

    if "significance" in q_lower:
        return _build_explanation(
            answer="To explain significance, show why an event mattered beyond the moment it happened.",
            method=(
                "1. Describe the immediate impact.\n"
                "2. Explain the long-term consequences.\n"
                "3. Show how it changed people, systems, or history."
            ),
            next_step="Give me the event and I can model a significance paragraph.",
        )

    if "climate" in q_lower:
        return _build_explanation(
            answer="Climate is shaped by several major physical factors.",
            method=_bullet_lines([
                "Latitude",
                "Ocean currents",
                "Altitude",
                "Prevailing winds",
            ]),
            next_step="Ask for examples of how each factor changes temperature or rainfall.",
        )

    return "Specify the historical or geographical topic."
