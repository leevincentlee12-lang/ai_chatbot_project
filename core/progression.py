"""Student progression and adaptive learning helpers.

The public function names in this module are intentionally stable because
`homework_helper.py`, `app.py`, and older tests import them directly. The
implementation is now user-scoped and backed by `core.state_store`.
"""

import random
from fractions import Fraction

from core.adaptive import (
    build_learning_dashboard,
    build_recommendation,
    choose_adaptive_level,
    choose_focus_skill,
    format_skill_label,
    mastery_delta,
    personalise_hint,
)
from core.misconceptions import (
    ranked_misconceptions,
    targeted_recommendations,
)
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


def get_misconception_counts(user_id=None):
    """Return structured misconception counts for this user."""
    return state_store.get_misconception_counts(user_id)


def get_learning_events(user_id=None, limit=50):
    """Return recent learning events for this user."""
    return state_store.get_learning_events(user_id, limit=limit)


def get_mastery_history(user_id=None, limit=100):
    """Return recent mastery score snapshots for this user."""
    return state_store.get_mastery_history(user_id, limit=limit)


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


def record_misconception(misconception_id, user_id=None):
    """Increment a structured misconception count for future adaptation."""
    count = state_store.record_misconception(user_id, misconception_id)
    _refresh_legacy_state()
    return count


def record_learning_event(
    event_type,
    skill=None,
    topic=None,
    detail=None,
    user_id=None,
):
    """Record a lightweight learning event for history and analytics."""
    state_store.add_learning_event(
        user_id,
        event_type,
        skill=skill,
        topic=topic,
        detail=detail,
    )


def record_hint_used(skill=None, topic=None, detail=None, user_id=None):
    """Record hint usage without changing mastery by itself."""
    record_learning_event(
        "hint_used",
        skill=skill,
        topic=topic,
        detail=detail,
        user_id=user_id,
    )


def detect_math_skill(question):
    """Infer the targeted maths skill from a question string."""
    q_lower = (question or "").lower()

    if (
        "(" in q_lower
        and ")" in q_lower
        and any(
            keyword in q_lower
            for keyword in (
                "coordinate",
                "midpoint",
                "distance",
                "gradient",
                "slope",
                "equation of the line",
                "line through",
                "line passing",
            )
        )
    ):
        return "coordinate_geometry"

    if (
        "y =" in q_lower
        and any(
            keyword in q_lower
            for keyword in (
                "graph",
                "gradient",
                "intercept",
                "vertex",
                "axis of symmetry",
                "discriminant",
            )
        )
    ):
        return "function_graphs"

    if "(" in q_lower and ")" in q_lower and "x" in q_lower:
        return "expanding_brackets"

    if "x^2" in q_lower or "quadratic" in q_lower:
        return "quadratics"

    if "simplify" in q_lower or "like terms" in q_lower:
        return "simplifying_expressions"

    if "/" in q_lower and "x" in q_lower:
        return "rational_equations"

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
        score_delta=mastery_delta(correct),
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

    if correct_streak >= 5:
        difficulty = min(3, difficulty + 1)
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


def _signed_number(value):
    """Format a signed constant for readable algebra strings."""
    return f" + {value}" if value >= 0 else f" - {abs(value)}"


def _signed_term(coefficient, variable):
    """Format a signed variable or constant term after the first term."""
    absolute = abs(coefficient)
    if variable:
        body = variable if absolute == 1 else f"{absolute}{variable}"
    else:
        body = str(absolute)
    return f" + {body}" if coefficient >= 0 else f" - {body}"


def _first_linear_term(coefficient):
    """Format the leading x-term on one side of a linear equation."""
    if coefficient == 1:
        return "x"
    if coefficient == -1:
        return "-x"
    return f"{coefficient}x"


def _format_linear_side(x_coefficient, constant):
    """Format ax + b without awkward '+ (-b)' notation."""
    if x_coefficient == 0:
        return str(constant)

    side = _first_linear_term(x_coefficient)
    if constant:
        side += _signed_term(constant, "")
    return side


def _random_signed(low, high):
    """Return a random non-zero integer from +/- the given positive range."""
    value = random.randint(abs(low), abs(high))
    if value == 0:
        value = 1
    return -value if random.randint(0, 1) == 0 else value


def _random_nonzero(low, high):
    """Return a random non-zero integer from an inclusive range."""
    value = 0
    while value == 0:
        value = random.randint(low, high)
    return value


def _generate_basic_linear_problem(ranges):
    """Generate the original one-variable linear-equation template."""
    a_value = random.randint(*ranges["a_range"])
    b_value = random.randint(*ranges["b_range"])
    solution = random.randint(*ranges["x_range"])
    c_value = a_value * solution + b_value

    return {
        "skill": "linear_equations",
        "problem": f"{a_value}x + ({b_value}) = {c_value}",
        "solution": solution,
        "difficulty": ranges["label"],
    }


def _generate_two_sided_linear_problem(ranges):
    """Generate ax + b = cx + d with an integer solution."""
    solution = random.randint(*ranges["x_range"])
    left_coefficient = _random_signed(*ranges["a_range"])
    right_coefficient = left_coefficient
    while right_coefficient == left_coefficient:
        right_coefficient = _random_signed(*ranges["a_range"])

    left_constant = random.randint(*ranges["b_range"])
    right_constant = (
        left_coefficient * solution
        + left_constant
        - right_coefficient * solution
    )

    return {
        "skill": "linear_equations",
        "problem": (
            f"{_format_linear_side(left_coefficient, left_constant)} = "
            f"{_format_linear_side(right_coefficient, right_constant)}"
        ),
        "solution": solution,
        "difficulty": ranges["label"],
    }


def _generate_parentheses_linear_problem(ranges):
    """Generate a distributive-property linear equation."""
    solution = random.randint(*ranges["x_range"])
    multiplier = random.randint(*ranges["a_range"])
    shift = _random_nonzero(-6, 6)
    outside_constant = random.randint(*ranges["b_range"])
    result = multiplier * (solution + shift) + outside_constant
    outside_term = _signed_number(outside_constant) if outside_constant else ""

    return {
        "skill": "expanding_brackets",
        "problem": (
            f"{multiplier}(x{_signed_number(shift)})"
            f"{outside_term} = {result}"
        ),
        "solution": solution,
        "difficulty": ranges["label"],
    }


def _format_quadratic_expression(b_coefficient, constant):
    """Format x^2 + bx + c in readable school notation."""
    expression = "x^2"
    if b_coefficient:
        expression += _signed_term(b_coefficient, "x")
    if constant:
        expression += _signed_term(constant, "")
    return expression


def _format_quadratic_expression_with_a(a_coefficient, b_coefficient, constant):
    """Format ax^2 + bx + c in readable school notation."""
    if a_coefficient == 1:
        expression = "x^2"
    elif a_coefficient == -1:
        expression = "-x^2"
    else:
        expression = f"{a_coefficient}x^2"

    if b_coefficient:
        expression += _signed_term(b_coefficient, "x")
    if constant:
        expression += _signed_term(constant, "")
    return expression


def _generate_quadratic_problem(ranges):
    """Generate a factorable quadratic with two integer roots."""
    root_a = _random_nonzero(*ranges["x_range"])
    root_b = root_a
    while root_b == root_a:
        root_b = _random_nonzero(*ranges["x_range"])

    b_coefficient = -(root_a + root_b)
    constant = root_a * root_b

    return {
        "skill": "quadratics",
        "problem": f"{_format_quadratic_expression(b_coefficient, constant)} = 0",
        "solution": sorted([root_a, root_b]),
        "difficulty": ranges["label"],
    }


def _generate_fractional_linear_problem(ranges):
    """Generate a linear equation with algebraic fractions and an integer root."""
    solution = random.randint(*ranges["x_range"])
    first_denominator = random.randint(2, 5)
    second_denominator = random.randint(3, 7)
    first_coefficient = _random_nonzero(-9, 9)
    second_coefficient = _random_nonzero(-9, 9)
    while (
        first_coefficient * second_denominator
        + second_coefficient * first_denominator
    ) == 0:
        second_coefficient = _random_nonzero(-9, 9)
    first_value = _random_nonzero(-8, 8)
    second_value = _random_nonzero(-8, 8)

    first_constant = first_denominator * first_value - first_coefficient * solution
    second_constant = second_denominator * second_value - second_coefficient * solution
    right_value = first_value + second_value

    first_numerator = _format_linear_side(first_coefficient, first_constant)
    second_numerator = _format_linear_side(second_coefficient, second_constant)

    return {
        "skill": "linear_equations",
        "problem": (
            f"({first_numerator})/{first_denominator} + "
            f"({second_numerator})/{second_denominator} = {right_value}"
        ),
        "solution": solution,
        "difficulty": ranges["label"],
    }


def _generate_non_monic_quadratic_problem(ranges):
    """Generate ax^2 + bx + c = 0 where a is not 1."""
    a_factor = random.randint(2, 5)
    first_factor_root = _random_nonzero(-8, 8)
    second_factor_root = first_factor_root
    while (
        second_factor_root == first_factor_root
        or abs((first_factor_root / a_factor) - second_factor_root) < 1e-9
    ):
        second_factor_root = _random_nonzero(-8, 8)

    # (a_factor*x - first_factor_root)(x - second_factor_root) = 0
    a_coefficient = a_factor
    b_coefficient = -(a_factor * second_factor_root + first_factor_root)
    constant = first_factor_root * second_factor_root
    roots = sorted([first_factor_root / a_factor, second_factor_root])

    return {
        "skill": "quadratics",
        "problem": (
            f"{_format_quadratic_expression_with_a(a_coefficient, b_coefficient, constant)} = 0"
        ),
        "solution": roots,
        "difficulty": ranges["label"],
    }


def _generate_rational_equation_problem(ranges):
    """Generate a rational equation with one valid numeric solution."""
    solution = _random_nonzero(-9, 9)
    excluded_value = solution
    while excluded_value == solution:
        excluded_value = _random_nonzero(-6, 6)

    ratio_value = random.randint(2, 6)
    x_coefficient = ratio_value
    while x_coefficient == ratio_value:
        x_coefficient = random.randint(2, 8)
    constant = ratio_value * (solution - excluded_value) - x_coefficient * solution
    numerator = _format_linear_side(x_coefficient, constant)

    return {
        "skill": "rational_equations",
        "problem": f"({numerator})/(x{_signed_number(-excluded_value)}) = {ratio_value}",
        "solution": solution,
        "difficulty": ranges["label"],
    }


def _point_pair(ranges, avoid_vertical=False, avoid_horizontal=False):
    """Return two classroom-friendly points for coordinate geometry."""
    x1 = random.randint(*ranges["x_range"])
    y1 = random.randint(*ranges["x_range"])
    x2 = x1
    y2 = y1

    while (
        (x2 == x1 and y2 == y1)
        or (avoid_vertical and x2 == x1)
        or (avoid_horizontal and y2 == y1)
    ):
        x2 = random.randint(*ranges["x_range"])
        y2 = random.randint(*ranges["x_range"])

    return (x1, y1), (x2, y2)


def _format_point(point):
    return f"({point[0]}, {point[1]})"


def _format_fraction(value):
    """Format an integer or simple rational value without decimal noise."""
    fraction = Fraction(value).limit_denominator()
    if fraction.denominator == 1:
        return str(fraction.numerator)
    return f"{fraction.numerator}/{fraction.denominator}"


def _format_fraction_x_term(value):
    """Format mx for a line equation."""
    fraction = Fraction(value).limit_denominator()
    if fraction == 1:
        return "x"
    if fraction == -1:
        return "-x"
    text = _format_fraction(fraction)
    return f"({text})x" if fraction.denominator != 1 else f"{text}x"


def _format_line_equation(gradient, intercept):
    """Format y = mx + c using readable school notation."""
    equation = f"y = {_format_fraction_x_term(gradient)}"
    intercept_fraction = Fraction(intercept).limit_denominator()
    if intercept_fraction == 0:
        return equation
    sign = " + " if intercept_fraction > 0 else " - "
    return f"{equation}{sign}{_format_fraction(abs(intercept_fraction))}"


def _generate_coordinate_midpoint_problem(ranges):
    """Generate a midpoint problem from two points."""
    point_a, point_b = _point_pair(ranges)
    midpoint = (
        Fraction(point_a[0] + point_b[0], 2),
        Fraction(point_a[1] + point_b[1], 2),
    )
    return {
        "skill": "coordinate_geometry",
        "problem": f"Find the midpoint of {_format_point(point_a)} and {_format_point(point_b)}.",
        "solution": _format_point((
            _format_fraction(midpoint[0]),
            _format_fraction(midpoint[1]),
        )),
        "difficulty": ranges["label"],
    }


def _generate_coordinate_gradient_problem(ranges):
    """Generate a gradient-between-two-points problem."""
    point_a, point_b = _point_pair(ranges, avoid_vertical=True)
    gradient = Fraction(point_b[1] - point_a[1], point_b[0] - point_a[0])
    return {
        "skill": "coordinate_geometry",
        "problem": f"Find the gradient between {_format_point(point_a)} and {_format_point(point_b)}.",
        "solution": _format_fraction(gradient),
        "difficulty": ranges["label"],
    }


def _generate_coordinate_distance_problem(ranges):
    """Generate a distance-between-two-points problem."""
    point_a, point_b = _point_pair(ranges)
    dx = point_b[0] - point_a[0]
    dy = point_b[1] - point_a[1]
    squared_distance = dx * dx + dy * dy
    return {
        "skill": "coordinate_geometry",
        "problem": f"Find the distance between {_format_point(point_a)} and {_format_point(point_b)}.",
        "solution": f"sqrt({squared_distance})",
        "difficulty": ranges["label"],
    }


def _generate_coordinate_line_problem(ranges):
    """Generate an equation-of-a-line problem from two points."""
    point_a, point_b = _point_pair(ranges, avoid_vertical=True)
    gradient = Fraction(point_b[1] - point_a[1], point_b[0] - point_a[0])
    intercept = point_a[1] - gradient * point_a[0]
    return {
        "skill": "coordinate_geometry",
        "problem": f"Find the equation of the line through {_format_point(point_a)} and {_format_point(point_b)}.",
        "solution": _format_line_equation(gradient, intercept),
        "difficulty": ranges["label"],
    }


def _generate_linear_graph_feature_problem(ranges):
    """Generate a graph-feature question for a straight line."""
    gradient = _random_nonzero(-6, 6)
    intercept = random.randint(*ranges["b_range"])
    question_type = random.choice(("gradient", "y_intercept", "x_intercept"))
    equation = f"y = {_format_linear_side(gradient, intercept)}"

    if question_type == "gradient":
        prompt = "Find the gradient"
        solution = str(gradient)
    elif question_type == "y_intercept":
        prompt = "Find the y-intercept"
        solution = str(intercept)
    else:
        prompt = "Find the x-intercept"
        solution = _format_fraction(Fraction(-intercept, gradient))

    return {
        "skill": "function_graphs",
        "problem": f"For {equation}, {prompt}.",
        "solution": solution,
        "difficulty": ranges["label"],
    }


def _generate_quadratic_graph_vertex_problem(ranges):
    """Generate a graph-feature question for a quadratic in vertex form."""
    h_value = random.randint(-5, 5)
    k_value = random.randint(*ranges["b_range"])
    a_value = random.choice((-1, 1))
    equation = f"y = {'' if a_value == 1 else '-'}(x{_signed_number(-h_value)})^2{_signed_number(k_value)}"
    return {
        "skill": "function_graphs",
        "problem": f"For {equation}, find the vertex.",
        "solution": _format_point((h_value, k_value)),
        "difficulty": ranges["label"],
    }


def generate_problem(level=None, user_id=None):
    """Generate a practice problem at the requested adaptive difficulty."""
    if level is None:
        level = get_difficulty(user_id)

    level = max(1, int(level))
    ranges = _difficulty_ranges(level)

    if level <= 1:
        problem_data = _generate_basic_linear_problem(ranges)
    elif level == 2:
        generator = random.choice((
            _generate_basic_linear_problem,
            _generate_two_sided_linear_problem,
            _generate_coordinate_midpoint_problem,
            _generate_coordinate_gradient_problem,
            _generate_linear_graph_feature_problem,
        ))
        problem_data = generator(ranges)
    else:
        generator = random.choice((
            _generate_fractional_linear_problem,
            _generate_non_monic_quadratic_problem,
            _generate_rational_equation_problem,
            _generate_coordinate_line_problem,
            _generate_coordinate_distance_problem,
            _generate_quadratic_graph_vertex_problem,
        ))
        problem_data = generator(ranges)

    set_current_topic(problem_data["skill"], user_id=user_id)

    return problem_data


def _generate_combining_terms_linear_problem(ranges):
    """Generate a linear equation that requires combining like terms."""
    solution = random.randint(*ranges["x_range"])
    first_coefficient = _random_nonzero(-9, 9)
    second_coefficient = _random_nonzero(-9, 9)
    while first_coefficient + second_coefficient == 0:
        second_coefficient = _random_nonzero(-9, 9)
    constant = random.randint(*ranges["b_range"])
    result = (first_coefficient + second_coefficient) * solution + constant

    return {
        "skill": "simplifying_expressions",
        "problem": (
            f"{_first_linear_term(first_coefficient)}"
            f"{_signed_term(second_coefficient, 'x')}"
            f"{_signed_term(constant, '')} = {result}"
        ),
        "solution": solution,
        "difficulty": ranges["label"],
    }


def _generate_problem_for_skill(skill, level, ranges):
    """Generate a practice problem for a selected skill when supported."""
    if skill == "quadratics":
        if level >= 3:
            return _generate_non_monic_quadratic_problem(ranges)
        return _generate_quadratic_problem(ranges)

    if skill == "rational_equations":
        return _generate_rational_equation_problem(ranges)

    if skill == "coordinate_geometry":
        if level >= 3:
            return _generate_coordinate_line_problem(ranges)
        return _generate_coordinate_gradient_problem(ranges)

    if skill == "function_graphs":
        if level >= 3:
            return _generate_quadratic_graph_vertex_problem(ranges)
        return _generate_linear_graph_feature_problem(ranges)

    if skill == "expanding_brackets":
        return _generate_parentheses_linear_problem(ranges)

    if skill == "simplifying_expressions":
        return _generate_combining_terms_linear_problem(ranges)

    if skill == "factoring":
        return _generate_quadratic_problem(ranges)

    if skill == "linear_equations":
        if level <= 1:
            return _generate_basic_linear_problem(ranges)
        if level == 2:
            return _generate_two_sided_linear_problem(ranges)
        return _generate_fractional_linear_problem(ranges)

    return generate_problem(level=level)


def generate_problem_for_skill(skill, level=None, user_id=None):
    """Generate a practice problem for one requested skill."""
    if level is None:
        level = get_difficulty(user_id)

    level = max(1, int(level))
    ranges = _difficulty_ranges(level)
    problem_data = _generate_problem_for_skill(skill, level, ranges)
    set_current_topic(problem_data["skill"], user_id=user_id)
    return problem_data


def _recent_problem_texts(user_id=None):
    return {
        item.get("question")
        for item in get_recent_questions(user_id, limit=20)
        if item.get("mode") == "practice" and item.get("question")
    }


def _record_generated_problem(problem_data, reason, user_id=None):
    state_store.add_recent_question(
        user_id,
        problem_data["problem"],
        subject="Math",
        topic=format_skill_label(problem_data["skill"]),
        mode="practice",
    )
    record_learning_event(
        "problem_generated",
        skill=problem_data["skill"],
        topic=format_skill_label(problem_data["skill"]),
        detail=reason,
        user_id=user_id,
    )


def generate_adaptive_problem(user_id=None, requested_level=None):
    """Generate a practice problem based on mastery and misconception history."""
    profile = get_student_profile(user_id)
    skills = profile.get("skills", {})
    misconception_summary = ranked_misconceptions(get_misconception_counts(user_id))
    focus = choose_focus_skill(skills, misconception_summary)
    level = choose_adaptive_level(
        focus["skill"],
        skills,
        current_difficulty=profile.get("difficulty", 1),
        requested_level=requested_level,
    )
    ranges = _difficulty_ranges(level)
    recent_problems = _recent_problem_texts(user_id)

    problem_data = None
    for _ in range(12):
        candidate = _generate_problem_for_skill(focus["skill"], level, ranges)
        if candidate["problem"] not in recent_problems:
            problem_data = candidate
            break

    if problem_data is None:
        problem_data = _generate_problem_for_skill(focus["skill"], level, ranges)

    problem_data["adaptive_focus"] = focus["topic"]
    problem_data["adaptive_reason"] = focus["reason"]
    set_current_topic(problem_data["skill"], user_id=user_id)
    _record_generated_problem(problem_data, focus["reason"], user_id=user_id)
    return problem_data


def get_personalised_recommendation(user_id=None):
    """Return the current recommendation for what the student should do next."""
    skills = get_student_skills(user_id)
    misconception_summary = ranked_misconceptions(get_misconception_counts(user_id))
    return build_recommendation(skills, misconception_summary)


def personalise_hint_for_user(base_hint, user_id=None):
    """Add adaptive context to a hint when repeated mistakes justify it."""
    misconception_summary = ranked_misconceptions(get_misconception_counts(user_id))
    return personalise_hint(base_hint, misconception_summary)


def get_learning_state(user_id=None):
    """Return the adaptive-learning state displayed by the app/API."""
    profile = get_student_profile(user_id)
    stats = get_student_stats(user_id)
    recent_questions = get_recent_questions(user_id, limit=10)
    mistakes = get_mistake_history(user_id, limit=10)
    misconception_counts = get_misconception_counts(user_id)
    misconception_summary = ranked_misconceptions(misconception_counts)
    repeated_recommendations = targeted_recommendations(misconception_counts)
    mastery_history = get_mastery_history(user_id, limit=100)
    learning_events = get_learning_events(user_id, limit=100)
    recommendation = build_recommendation(profile["skills"], misconception_summary)
    dashboard = build_learning_dashboard(
        profile,
        stats,
        recent_questions,
        mistakes,
        misconception_summary,
        mastery_history,
        learning_events,
    )
    return {
        "current_topic": profile["current_topic"],
        "recent_question": recent_questions[0] if recent_questions else None,
        "recent_questions": recent_questions,
        "skill_progression": profile["skills"],
        "mastery_by_topic": profile["skills"],
        "overall_mastery": dashboard["overall_mastery"],
        "difficulty_level": profile["difficulty"],
        "correct_streak": profile["correct_streak"],
        "recent_mistakes": mistakes,
        "mistake_history": mistakes,
        "mastery_history": mastery_history,
        "learning_events": learning_events,
        "misconceptions": misconception_counts,
        "misconception_summary": misconception_summary,
        "most_common_misconception": (
            misconception_summary[0] if misconception_summary else None
        ),
        "misconception_recommendations": repeated_recommendations,
        "recommendation": recommendation,
        "dashboard": dashboard,
        "stats": stats,
    }
