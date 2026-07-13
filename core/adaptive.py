"""Deterministic adaptive-learning rules.

This module answers the core Phase 2 question: what should the student
practise next? The rules are deliberately simple and explainable.
"""

from datetime import datetime


MIN_MASTERY = 0
MAX_MASTERY = 100

LOW_MASTERY_THRESHOLD = 50
HIGH_MASTERY_THRESHOLD = 80
REPEATED_MISCONCEPTION_THRESHOLD = 2

SKILL_LABELS = {
    "linear_equations": "Linear Equations",
    "quadratics": "Quadratics",
    "factoring": "Factorisation",
    "expanding_brackets": "Expanding Brackets",
    "simplifying_expressions": "Simplifying Expressions",
    "fractions": "Fractions",
    "indices": "Indices",
    "rational_equations": "Rational Equations",
    "coordinate_geometry": "Coordinate Geometry",
    "function_graphs": "Function Graphs",
}

MISCONCEPTION_SKILL_MAP = {
    "SIGN_ERROR": "linear_equations",
    "FORGOT_TO_DIVIDE": "linear_equations",
    "REVERSED_DIVISION": "linear_equations",
    "DISTRIBUTIVE_ERROR": "expanding_brackets",
    "COMBINING_UNLIKE_TERMS": "simplifying_expressions",
    "ARITHMETIC_ERROR": "linear_equations",
    "GRADIENT_RUN_OVER_RISE": "coordinate_geometry",
    "MIDPOINT_ONE_COORDINATE": "coordinate_geometry",
    "DISTANCE_MISSING_SQUARE_ROOT": "coordinate_geometry",
    "GRAPH_INTERCEPT_CONFUSION": "function_graphs",
}


def clamp_mastery(score):
    """Clamp a mastery score to the supported 0-100 range."""
    return max(MIN_MASTERY, min(MAX_MASTERY, int(score)))


def format_skill_label(skill):
    """Return a readable topic name for a skill key."""
    return SKILL_LABELS.get(
        skill,
        str(skill or "unknown").replace("_", " ").title(),
    )


def mastery_delta(correct, misconception_count=0):
    """Return the mastery score change for one completed question."""
    if correct:
        return 5

    if misconception_count >= REPEATED_MISCONCEPTION_THRESHOLD:
        return -7

    return -3


def overall_mastery(skills):
    """Return the average mastery score across supported topics."""
    if not skills:
        return 0

    scores = [
        clamp_mastery(data.get("score", 0))
        for data in skills.values()
        if isinstance(data, dict)
    ]
    if not scores:
        return 0

    return round(sum(scores) / len(scores), 2)


def strongest_skill(skills):
    """Return the skill with the highest mastery score."""
    entries = _skill_entries(skills)
    return max(entries, key=lambda item: item["score"]) if entries else None


def weakest_skill(skills):
    """Return the skill with the lowest mastery score."""
    entries = _skill_entries(skills)
    return min(entries, key=lambda item: item["score"]) if entries else None


def _skill_entries(skills):
    entries = []
    for skill, data in (skills or {}).items():
        if not isinstance(data, dict):
            continue
        entries.append({
            "skill": skill,
            "label": format_skill_label(skill),
            "score": clamp_mastery(data.get("score", 0)),
            "attempts": int(data.get("attempts", 0)),
        })
    return entries


def misconception_focus(misconception_summary):
    """Return the highest-priority repeated misconception focus."""
    for item in misconception_summary or []:
        count = int(item.get("count", 0))
        if count < REPEATED_MISCONCEPTION_THRESHOLD:
            continue

        skill = MISCONCEPTION_SKILL_MAP.get(item.get("id"))
        if not skill:
            continue

        return {
            "skill": skill,
            "topic": format_skill_label(skill),
            "misconception": item,
            "reason": f"Repeated {item.get('label', 'mistake pattern').lower()} detected.",
        }

    return None


def choose_focus_skill(skills, misconception_summary):
    """Choose the next topic focus from misconceptions first, then mastery."""
    focus = misconception_focus(misconception_summary)
    if focus:
        return focus

    entries = _skill_entries(skills)
    if entries and all(item["score"] == 0 and item["attempts"] == 0 for item in entries):
        return {
            "skill": "linear_equations",
            "topic": "Linear Equations",
            "misconception": None,
            "reason": "Linear equations are the safest starting point for algebra practice.",
        }

    weakest = weakest_skill(skills)
    if weakest:
        return {
            "skill": weakest["skill"],
            "topic": weakest["label"],
            "misconception": None,
            "reason": f"Current mastery is {weakest['score']}%, below stronger topics.",
        }

    return {
        "skill": "linear_equations",
        "topic": "Linear Equations",
        "misconception": None,
        "reason": "Linear equations are the safest starting point for algebra practice.",
    }


def mastery_level(score):
    """Convert a mastery score into a suggested difficulty level."""
    score = clamp_mastery(score)
    if score < LOW_MASTERY_THRESHOLD:
        return 1
    if score <= HIGH_MASTERY_THRESHOLD:
        return 2
    return 3


def choose_adaptive_level(skill, skills, current_difficulty=1, requested_level=None):
    """Choose a difficulty level using mastery and current difficulty."""
    skill_score = clamp_mastery((skills or {}).get(skill, {}).get("score", 0))
    target = mastery_level(skill_score)

    try:
        current = max(1, min(3, int(current_difficulty)))
    except (TypeError, ValueError):
        current = 1

    if target > current:
        target = current + 1
    elif target < current:
        target = current - 1

    if requested_level is not None:
        try:
            requested = max(1, min(3, int(requested_level)))
            target = min(target, requested)
        except (TypeError, ValueError):
            pass

    return max(1, min(3, target))


def build_recommendation(skills, misconception_summary):
    """Return the next lesson/practice recommendation."""
    focus = misconception_focus(misconception_summary)
    if focus:
        return {
            "type": "lesson",
            "title": f"Recommended Next Lesson: {focus['topic']}",
            "topic": focus["topic"],
            "skill": focus["skill"],
            "reason": focus["reason"],
        }

    weakest = weakest_skill(skills)
    if weakest and weakest["score"] < 60:
        return {
            "type": "practice",
            "title": f"Recommended Practice: {weakest['label']}",
            "topic": weakest["label"],
            "skill": weakest["skill"],
            "reason": f"Current mastery is {weakest['score']}%, below the 60% review threshold.",
        }

    if weakest:
        return {
            "type": "challenge",
            "title": f"Recommended Challenge: {weakest['label']}",
            "topic": weakest["label"],
            "skill": weakest["skill"],
            "reason": "No repeated misconception is dominating, so continue building balanced mastery.",
        }

    return {
        "type": "practice",
        "title": "Recommended Practice: Linear Equations",
        "topic": "Linear Equations",
        "skill": "linear_equations",
        "reason": "Start with a core algebra topic before moving into harder questions.",
    }


def most_improved_topic(mastery_history):
    """Return the topic with the largest score increase in available history."""
    by_skill = {}
    for row in mastery_history or []:
        skill = row.get("skill")
        if not skill:
            continue
        by_skill.setdefault(skill, []).append(row)

    best = None
    for skill, rows in by_skill.items():
        if len(rows) < 2:
            continue
        first = int(rows[-1].get("score", 0))
        latest = int(rows[0].get("score", 0))
        change = latest - first
        if best is None or change > best["change"]:
            best = {
                "skill": skill,
                "topic": format_skill_label(skill),
                "change": change,
            }

    return best


def estimate_time_spent_minutes(events):
    """Estimate learning time from first and latest event timestamps."""
    parsed = []
    for event in events or []:
        timestamp = event.get("created_at")
        if not timestamp:
            continue
        try:
            parsed.append(datetime.fromisoformat(timestamp.replace("Z", "+00:00")))
        except ValueError:
            continue

    if len(parsed) < 2:
        return 0

    seconds = (max(parsed) - min(parsed)).total_seconds()
    return round(max(0, min(seconds, 3 * 60 * 60)) / 60, 2)


def build_learning_dashboard(
    profile,
    stats,
    recent_questions,
    mistakes,
    misconception_summary,
    mastery_history,
    events,
):
    """Build display-ready adaptive dashboard metrics."""
    skills = profile.get("skills", {})
    recommendation = build_recommendation(skills, misconception_summary)
    improved = most_improved_topic(mastery_history)
    strongest = strongest_skill(skills)
    weakest = weakest_skill(skills)

    attempted = int(stats.get("problems_attempted", 0))
    correct = int(stats.get("correct_answers", 0))
    incorrect = max(0, attempted - correct)
    hint_usage = sum(1 for event in events or [] if event.get("event_type") == "hint_used")

    return {
        "overall_mastery": overall_mastery(skills),
        "strongest_topic": strongest,
        "weakest_topic": weakest,
        "most_improved_topic": improved,
        "recent_improvement": improved["change"] if improved else 0,
        "recommended_next_topic": recommendation,
        "practice_streak": int(profile.get("correct_streak", 0)),
        "current_focus_area": recommendation["topic"],
        "recent_activity_count": len(recent_questions or []),
        "recent_mistake_count": len(mistakes or []),
        "incorrect_answers": incorrect,
        "hint_usage": hint_usage,
        "time_spent_minutes_estimate": estimate_time_spent_minutes(events),
    }


def personalise_hint(base_hint, misconception_summary):
    """Add a misconception-aware sentence to a hint when evidence is strong."""
    focus = misconception_focus(misconception_summary)
    if not focus:
        return base_hint

    misconception_id = focus["misconception"].get("id")
    if misconception_id == "SIGN_ERROR":
        prefix = (
            "You've recently made several sign errors when moving terms across "
            "the equals sign. Double-check whether each sign changes correctly."
        )
    elif misconception_id == "DISTRIBUTIVE_ERROR":
        prefix = (
            "You've recently made distributive law errors. Make sure every term "
            "inside the brackets is multiplied."
        )
    elif misconception_id == "FORGOT_TO_DIVIDE":
        prefix = (
            "You've recently stopped at the ax = b step. Remember that the last "
            "step is dividing both sides by the coefficient of x."
        )
    elif misconception_id == "COMBINING_UNLIKE_TERMS":
        prefix = (
            "You've recently combined unlike terms. Keep x terms and constants "
            "separate unless they are genuinely like terms."
        )
    else:
        prefix = (
            "Your recent mistakes show a pattern, so check the algebra rule "
            "before doing the next operation."
        )

    return f"{prefix}\n\n{base_hint}"
