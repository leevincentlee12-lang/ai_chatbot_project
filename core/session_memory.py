"""Lightweight Flask-session memory helpers.

The persistent adaptive-learning data lives in core.state_store. These helpers
store only small, short-lived browser-session context such as the active
practice problem and current lesson.
"""

from datetime import datetime, timezone


ACTIVE_PRACTICE_KEY = "active_practice_problem"
CURRENT_LESSON_KEY = "current_lesson"


def _now():
    return datetime.now(timezone.utc).isoformat()


def remember_active_practice_problem(session_obj, problem_data, level=None):
    """Store the active practice problem without exposing its solution."""
    if not isinstance(problem_data, dict):
        return None

    memory = {
        "problem": problem_data.get("problem"),
        "skill": problem_data.get("skill"),
        "difficulty": problem_data.get("difficulty"),
        "level": level,
        "started_at": _now(),
    }
    memory = {key: value for key, value in memory.items() if value is not None}

    if not memory.get("problem"):
        return None

    session_obj[ACTIVE_PRACTICE_KEY] = memory
    session_obj.modified = True
    return memory


def remember_current_lesson(session_obj, lesson_data):
    """Store a compact reference to the current lesson."""
    if not isinstance(lesson_data, dict):
        return None

    memory = {
        "topic": lesson_data.get("topic"),
        "title": lesson_data.get("title"),
        "strand": lesson_data.get("strand"),
        "level": lesson_data.get("level"),
        "summary": lesson_data.get("summary"),
        "opened_at": _now(),
    }
    memory = {key: value for key, value in memory.items() if value is not None}

    if not memory.get("topic"):
        return None

    session_obj[CURRENT_LESSON_KEY] = memory
    session_obj.modified = True
    return memory


def get_session_memory(session_obj):
    """Return the lightweight memory currently stored in the Flask session."""
    return {
        "active_practice_problem": session_obj.get(ACTIVE_PRACTICE_KEY),
        "current_lesson": session_obj.get(CURRENT_LESSON_KEY),
    }


def clear_active_practice_problem(session_obj):
    """Clear the active practice problem from the Flask session."""
    session_obj.pop(ACTIVE_PRACTICE_KEY, None)
    session_obj.modified = True


def clear_current_lesson(session_obj):
    """Clear the current lesson from the Flask session."""
    session_obj.pop(CURRENT_LESSON_KEY, None)
    session_obj.modified = True
