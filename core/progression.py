"""Mutable tutoring state and progression helpers."""

import random
from copy import deepcopy


student_stats = {
    "questions_asked": 0,
    "problems_attempted": 0,
    "correct_answers": 0,
    "lessons_completed": 0,
}

student_profile = {
    "skills": {
        "linear_equations": {"score": 0, "attempts": 0},
        "quadratics": {"score": 0, "attempts": 0},
        "factoring": {"score": 0, "attempts": 0},
        "fractions": {"score": 0, "attempts": 0},
        "indices": {"score": 0, "attempts": 0},
    },
    "current_topic": "linear_equations",
    "difficulty": 1,
    "attempts": 0,
    "correct_streak": 0,
}

student_steps = []
guided_sessions = {}


def _clamp_score(score):
    """Clamp a mastery score to the supported range."""
    return max(0, min(100, score))


def get_student_stats():
    """Return a copy of the current statistics snapshot."""
    return deepcopy(student_stats)


def get_student_skills():
    """Return a copy of the student's skill map."""
    return deepcopy(student_profile["skills"])


def record_question_asked():
    """Increment the count of asked questions."""
    student_stats["questions_asked"] += 1


def record_problem_attempt():
    """Increment the count of attempted problems."""
    student_stats["problems_attempted"] += 1


def record_correct_answer():
    """Increment the count of correct problem answers."""
    student_stats["correct_answers"] += 1


def record_lesson_completed():
    """Increment the count of opened lessons."""
    student_stats["lessons_completed"] += 1


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


def get_or_create_skill(skill):
    """Return the mutable skill record for a topic, creating it when needed."""
    return student_profile["skills"].setdefault(
        skill,
        {"score": 0, "attempts": 0},
    )


def update_skill(skill, correct):
    """Adjust a skill score and attempts based on an outcome."""
    if skill not in student_profile["skills"]:
        return

    skill_data = student_profile["skills"][skill]
    skill_data["attempts"] += 1
    skill_data["score"] = _clamp_score(
        skill_data["score"] + (10 if correct else -5)
    )


def update_progression(correct):
    """Update difficulty and streak state after an answer result."""
    if correct:
        student_profile["correct_streak"] += 1
    else:
        student_profile["correct_streak"] = 0
        student_profile["difficulty"] = max(
            1,
            student_profile["difficulty"] - 1,
        )
        return None

    if student_profile["correct_streak"] >= 3:
        student_profile["difficulty"] += 1
        student_profile["correct_streak"] = 0
        return f"Level up. Difficulty is now {student_profile['difficulty']}."

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


def generate_problem(level=None):
    """Generate a linear-equation practice problem."""
    if level is None:
        level = student_profile.get("difficulty", 1)

    ranges = _difficulty_ranges(max(1, int(level)))
    a_value = random.randint(*ranges["a_range"])
    b_value = random.randint(*ranges["b_range"])
    solution = random.randint(*ranges["x_range"])
    c_value = a_value * solution + b_value

    problem = f"{a_value}x + ({b_value}) = {c_value}"
    student_profile["current_topic"] = "linear_equations"

    return {
        "skill": "linear_equations",
        "problem": problem,
        "solution": solution,
        "difficulty": ranges["label"],
    }


def generate_adaptive_problem():
    """Generate a practice problem targeting the skill with the lowest mastery score."""
    skills = student_profile["skills"]
    if not skills:
        return generate_problem(student_profile.get("difficulty", 1))

    weakest_skill = min(
        skills.items(),
        key=lambda item: item[1]["score"],
    )[0]
    student_profile["current_topic"] = weakest_skill
    return generate_problem(student_profile.get("difficulty", 1))
