"""Student progression and adaptive learning helpers.

The public function names in this module are intentionally stable because
`homework_helper.py`, `app.py`, and older tests import them directly. The
implementation is now user-scoped and backed by `core.state_store`.
"""

import random

from core import state_store


def _clamp_score(score):
    """Clamp a mastery score to the supported range."""
    return max(0, min(100, int(score)))


def _legacy_snapshot():
    """Return snapshots for older imports that expect module-level names."""
    profile = state_store.get_profile()
    return (
        state_store.get_stats(),
        profile,
        state_store.get_steps(),
        state_store.get_guided_session(),
    )


student_stats, student_profile, student_steps, guided_sessions = _legacy_snapshot()


def _refresh_legacy_state():
    """Keep compatibility globals close to the default user's persisted state."""
    global student_stats, student_profile, student_steps, guided_sessions
    student_stats, student_profile, student_steps, guided_sessions = _legacy_snapshot()


def get_student_profile(user_id=None):
    """Return the current learning profile for a user."""
    return state_store.get_profile(user_id)


def get_student_stats(user_id=None):
    """Return a copy of the current statistics snapshot."""
    return state_store.get_stats(user_id)


def get_student_skills(user_id=None):
    """Return a copy of the student's skill map."""
    return state_store.get_skills(user_id)


def get_recent_questions(user_id=None, limit=10):
    """Return the latest questions asked by this user."""
    return state_store.get_recent_questions(user_id, limit=limit)


def get_mistake_history(user_id=None, limit=10):
    """Return recent answer mistakes for this user."""
    return state_store.get_mistakes(user_id, limit=limit)


def get_student_steps(user_id=None):
    """Return the recorded algebra steps for this user."""
    return state_store.get_steps(user_id)


def append_student_step(step, user_id=None):
    """Append one algebra step and return the user's recorded step count."""
    count = state_store.append_step(user_id, step)
    _refresh_legacy_state()
    return count


def clear_student_steps(user_id=None):
    """Clear recorded algebra steps for this user."""
    state_store.clear_steps(user_id)
    _refresh_legacy_state()


def get_guided_session(user_id=None):
    """Return the active guided-practice session, if one exists."""
    return state_store.get_guided_session(user_id)


def set_guided_session(problem, step, solution, user_id=None):
    """Persist the active guided-practice session."""
    state_store.set_guided_session(user_id, problem, step, solution)
    _refresh_legacy_state()


def clear_guided_session(user_id=None):
    """Clear the active guided-practice session."""
    state_store.clear_guided_session(user_id)
    _refresh_legacy_state()


def record_question_asked(user_id=None):
    """Increment the count of asked questions."""
    state_store.increment_stat(user_id, "questions_asked")
    _refresh_legacy_state()


def record_question(question, subject=None, topic=None, mode=None, user_id=None):
    """Store a recent question and update the user's current topic."""
    record_question_asked(user_id=user_id)
    if topic:
        set_current_topic(topic, user_id=user_id)
    state_store.add_recent_question(
        user_id,
        question,
        subject=subject,
        topic=topic,
        mode=mode,
    )


def record_problem_attempt(user_id=None):
    """Increment the count of attempted problems."""
    state_store.increment_stat(user_id, "problems_attempted")
    _refresh_legacy_state()


def record_correct_answer(user_id=None):
    """Increment the count of correct problem answers."""
    state_store.increment_stat(user_id, "correct_answers")
    _refresh_legacy_state()


def record_lesson_completed(user_id=None):
    """Increment the count of opened lessons."""
    state_store.increment_stat(user_id, "lessons_completed")
    _refresh_legacy_state()


def record_mistake(
    skill=None,
    question=None,
    submitted_answer=None,
    correct_answer=None,
    issue=None,
    user_id=None,
):
    """Store a diagnostic mistake entry for future adaptation."""
    state_store.add_mistake(
        user_id,
        skill=skill,
        question=question,
        submitted_answer=submitted_answer,
        correct_answer=correct_answer,
        issue=issue,
    )


def detect_math_skill(question):
    """Infer the targeted maths skill from a question string."""
    q_lower = (question or "").lower()

    if "x^2" in q_lower or "quadratic" in q_lower:
        return "quadratics"

    if "factor" in q_lower:
        return "factoring"

    if "=" in q_lower and "x" in q_lower:
        return "linear_equations"

    return None


def get_or_create_skill(skill, user_id=None):
    """Return the skill record for a topic, creating it when needed."""
    return state_store.get_or_create_skill(user_id, skill)


def adjust_skill(skill, score_delta=0, attempt_delta=0, user_id=None):
    """Adjust a persisted skill score and attempts counter."""
    updated = state_store.adjust_skill(
        user_id,
        skill,
        score_delta=score_delta,
        attempt_delta=attempt_delta,
    )
    _refresh_legacy_state()
    return updated


def update_skill(skill, correct, user_id=None):
    """Adjust a skill score and attempts based on an outcome."""
    if not skill:
        return None

    return adjust_skill(
        skill,
        score_delta=10 if correct else -5,
        attempt_delta=1,
        user_id=user_id,
    )


def get_difficulty(user_id=None):
    """Return the user's current adaptive difficulty level."""
    return int(get_student_profile(user_id).get("difficulty", 1))


def set_current_topic(topic, user_id=None):
    """Persist the current learning topic for a user."""
    if not topic:
        return get_student_profile(user_id)
    profile = state_store.update_profile(user_id, current_topic=str(topic))
    _refresh_legacy_state()
    return profile


def update_last_question_time(timestamp, user_id=None):
    """Persist the latest question timestamp for activity tracking."""
    profile = state_store.update_profile(user_id, last_question_ts=timestamp)
    _refresh_legacy_state()
    return profile


def update_progression(correct, user_id=None):
    """Update difficulty and streak state after an answer result."""
    profile = get_student_profile(user_id)
    difficulty = int(profile.get("difficulty", 1))
    correct_streak = int(profile.get("correct_streak", 0))

    if correct:
        correct_streak += 1
    else:
        state_store.update_profile(
            user_id,
            correct_streak=0,
            difficulty=max(1, difficulty - 1),
        )
        _refresh_legacy_state()
        return None

    if correct_streak >= 3:
        difficulty += 1
        correct_streak = 0
        state_store.update_profile(
            user_id,
            correct_streak=correct_streak,
            difficulty=difficulty,
        )
        _refresh_legacy_state()
        return f"Level up. Difficulty is now {difficulty}."

    state_store.update_profile(user_id, correct_streak=correct_streak)
    _refresh_legacy_state()
    return None


def _difficulty_ranges(level):
    """Return coefficient and solution ranges for a difficulty level."""
    if level <= 1:
        return {
            "label": "Easy",
            "a_range": (1, 4),
            "b_range": (-6, 6),
            "x_range": (-5, 5),
        }

    if level == 2:
        return {
            "label": "Medium",
            "a_range": (2, 8),
            "b_range": (-12, 12),
            "x_range": (-8, 8),
        }

    return {
        "label": "Hard",
        "a_range": (3, 12),
        "b_range": (-20, 20),
        "x_range": (-10, 10),
    }


def generate_problem(level=None, user_id=None):
    """Generate a linear-equation practice problem."""
    if level is None:
        level = get_difficulty(user_id)

    ranges = _difficulty_ranges(max(1, int(level)))
    a_value = random.randint(*ranges["a_range"])
    b_value = random.randint(*ranges["b_range"])
    solution = random.randint(*ranges["x_range"])
    c_value = a_value * solution + b_value

    problem = f"{a_value}x + ({b_value}) = {c_value}"
    set_current_topic("linear_equations", user_id=user_id)

    return {
        "skill": "linear_equations",
        "problem": problem,
        "solution": solution,
        "difficulty": ranges["label"],
    }


def generate_adaptive_problem(user_id=None):
    """Generate a practice problem targeting the weakest mastery score."""
    skills = get_student_skills(user_id)
    if not skills:
        return generate_problem(get_difficulty(user_id), user_id=user_id)

    weakest_skill = min(
        skills.items(),
        key=lambda item: item[1]["score"],
    )[0]
    set_current_topic(weakest_skill, user_id=user_id)
    return generate_problem(get_difficulty(user_id), user_id=user_id)


def get_learning_state(user_id=None):
    """Return the adaptive-learning state displayed by the app/API."""
    profile = get_student_profile(user_id)
    stats = get_student_stats(user_id)
    recent_questions = get_recent_questions(user_id, limit=10)
    mistakes = get_mistake_history(user_id, limit=10)
    return {
        "current_topic": profile["current_topic"],
        "recent_question": recent_questions[0] if recent_questions else None,
        "recent_questions": recent_questions,
        "skill_progression": profile["skills"],
        "difficulty_level": profile["difficulty"],
        "correct_streak": profile["correct_streak"],
        "recent_mistakes": mistakes,
        "mistake_history": mistakes,
        "stats": stats,
    }
