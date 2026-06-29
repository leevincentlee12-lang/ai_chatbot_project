"""Preparation layer for a future teacher dashboard.

This does not implement authentication or a visible teacher page. It only
builds a read-only snapshot shape from the existing adaptive-learning state.
"""


def build_teacher_snapshot(user_id, learning_state):
    """Return the progress fields a future teacher view would need."""
    stats = learning_state.get("stats", {})
    dashboard = learning_state.get("dashboard", {})

    return {
        "user_id": user_id,
        "summary": {
            "overall_mastery": learning_state.get("overall_mastery", 0),
            "difficulty_level": learning_state.get("difficulty_level", 1),
            "questions_attempted": stats.get("problems_attempted", 0),
            "correct_answers": stats.get("correct_answers", 0),
            "incorrect_answers": dashboard.get("incorrect_answers", 0),
            "hint_usage": dashboard.get("hint_usage", 0),
            "current_focus_area": dashboard.get("current_focus_area"),
        },
        "mastery_by_topic": learning_state.get("mastery_by_topic", {}),
        "misconceptions": learning_state.get("misconception_summary", []),
        "recent_mistakes": learning_state.get("recent_mistakes", []),
        "recent_activity": learning_state.get("recent_questions", []),
        "recommendation": learning_state.get("recommendation"),
    }
