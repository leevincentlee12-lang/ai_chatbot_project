"""Answer checking and diagnostic feedback for math practice."""

import re

from sympy import simplify

from core.parser import (
    MATH_PARSE_ERROR_MESSAGE,
    _extract_numeric_answer,
    has_obvious_malformed_math_input,
    parse_math_expression,
)
from core.misconceptions import detect_misconception, get_misconception_definition
from core.progression import (
    adjust_skill,
    detect_math_skill,
    get_personalised_recommendation,
    record_learning_event,
    record_misconception,
    record_mistake,
    record_correct_answer,
    record_problem_attempt,
    update_progression,
)
from core.adaptive import mastery_delta
from core.validator import equations_equivalent
from engine.algebra_solver import _parse_linear_equation, solve_values
from engine.coordinate_geometry import (
    distance_between_points,
    equation_of_line_through_points,
    extract_points,
    gradient_between_points,
    midpoint_between_points,
)
from engine.graph_engine import graph_function_data
from utils.formatting import (
    _compose_message,
    _format_expression,
    _format_skill_label,
    _format_value,
    _section,
)


def _extract_numeric_answers(answer):
    """Parse one or more numeric answers from student input."""
    text = str(answer or "").strip()
    if not text:
        return None

    cleaned = text.replace("{", "").replace("}", "")
    cleaned = cleaned.replace("[", "").replace("]", "")
    cleaned = re.sub(r"\b(?:or|and)\b", ",", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.replace(";", ",")
    parts = [part.strip() for part in cleaned.split(",") if part.strip()]

    values = []
    for part in parts or [cleaned]:
        value = _extract_numeric_answer(part)
        if value is None:
            return None
        if not any(abs(value - existing) < 1e-9 for existing in values):
            values.append(value)

    return sorted(values)


def _format_solution_set(values):
    """Format one or more x-values for display."""
    return " or ".join(f"x = {_format_value(value)}" for value in values)


def _values_match(expected, submitted):
    """Return whether two numeric solution sets match within tolerance."""
    if len(expected) != len(submitted):
        return False
    return all(abs(a - b) < 1e-9 for a, b in zip(expected, submitted))


def _diagnose_solution_set_answer(expected_values, submitted_values):
    """Explain common mistakes for equations with more than one solution."""
    expected_text = _format_solution_set(expected_values)

    if len(submitted_values) < len(expected_values):
        return {
            "issue": "You found only part of the solution set.",
            "fix": (
                "For a quadratic, each factor can produce a separate x-value. "
                "List every value that makes the equation true."
            ),
            "next_step": f"Check both roots: {expected_text}.",
        }

    if len(submitted_values) > len(expected_values):
        return {
            "issue": "You included an extra value that does not satisfy the equation.",
            "fix": "Substitute each listed value back into the original equation and remove any that fail.",
            "next_step": f"The complete solution set is {expected_text}.",
        }

    return {
        "issue": "At least one value in your solution set is incorrect.",
        "fix": "Factor the quadratic or solve it again, then check each root by substitution.",
        "next_step": f"The complete solution set is {expected_text}.",
    }


def _diagnose_linear_answer(eq, student_value, correct):
    """Infer the most likely reason a linear-equation answer is wrong."""
    analysis = _parse_linear_equation(eq)
    if not analysis or analysis["solution"] is None:
        return {
            "issue": "The answer does not match the equation.",
            "fix": "Go back to isolating x one inverse operation at a time.",
            "next_step": "First get the equation into the form ax = b, then divide by a.",
        }

    a_total = analysis["a_total"]
    b_total = analysis["b_total"]

    candidates = []
    if abs(student_value - b_total) < 1e-9:
        candidates.append({
            "issue": "You isolated the x-term but did not divide by its coefficient.",
            "fix": f"After reaching {a_total}x = {b_total}, divide both sides by {a_total}.",
            "next_step": f"Finish with x = {b_total}/{a_total}.",
            "priority": 4,
        })
    if b_total != 0 and abs(student_value - (a_total / b_total)) < 1e-9:
        candidates.append({
            "issue": "You appear to have reversed the division step.",
            "fix": f"Use x = {b_total}/{a_total}, not x = {a_total}/{b_total}.",
            "next_step": "Keep the constant side on top and the x-coefficient on the bottom.",
            "priority": 3,
        })
    if abs(student_value + correct) < 1e-9:
        candidates.append({
            "issue": "This looks like a sign error while moving terms across the equals sign.",
            "fix": "When a term crosses the equals sign, its operation changes.",
            "next_step": "Rebuild the line where you moved the constant or variable term.",
            "priority": 5,
        })
    if abs(student_value - round(correct)) <= 1 and abs(student_value - correct) <= 1:
        candidates.append({
            "issue": "You are close, so this is likely an arithmetic slip rather than a method error.",
            "fix": "Recheck the subtraction and final division carefully.",
            "next_step": f"Work from {a_total}x = {b_total} and compute the division one more time.",
            "priority": 2,
        })

    if candidates:
        best = max(candidates, key=lambda item: item["priority"])
        return {
            "issue": best["issue"],
            "fix": best["fix"],
            "next_step": best["next_step"],
        }

    if student_value > correct:
        return {
            "issue": "Your answer is larger than the correct value.",
            "fix": "Check whether you added instead of subtracting, or divided by the wrong number.",
            "next_step": f"Reduce the equation to {a_total}x = {b_total} and solve again.",
        }

    return {
        "issue": "Your answer is smaller than the correct value.",
        "fix": "Check sign handling and the final division step.",
        "next_step": f"Reduce the equation to {a_total}x = {b_total} and solve again.",
    }


def _numeric_answer_value(answer):
    """Return a numeric value from a submitted feature answer."""
    parsed = _extract_numeric_answer(answer)
    if parsed is not None:
        return parsed

    text = str(answer or "").strip()
    if not text:
        return None

    try:
        value = simplify(parse_math_expression(text))
    except Exception:
        return None

    if getattr(value, "free_symbols", set()):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _values_close(left, right, tolerance=1e-6):
    return abs(float(left) - float(right)) <= tolerance


def _extract_point_answer(answer):
    """Return a submitted point as two numeric values."""
    try:
        points = extract_points(answer)
    except Exception:
        points = []

    if points:
        try:
            return tuple(float(value) for value in points[0])
        except (TypeError, ValueError):
            return None

    text = str(answer or "").strip().strip("()")
    if "," not in text:
        return None

    parts = [part.strip() for part in text.split(",", 1)]
    values = [_numeric_answer_value(part) for part in parts]
    if any(value is None for value in values):
        return None
    return tuple(values)


def _points_close(left, right):
    return (
        left is not None
        and right is not None
        and len(left) == len(right) == 2
        and _values_close(left[0], right[0])
        and _values_close(left[1], right[1])
    )


def _format_point_value(point):
    return f"({_format_value(point[0])}, {_format_value(point[1])})"


def _two_points_from_problem(problem):
    points = extract_points(problem)
    if len(points) < 2:
        return None
    return points[0], points[1]


def _line_answer_matches(student_answer, expected_equation):
    submitted = str(student_answer or "").strip()
    if "=" not in submitted:
        return False
    return equations_equivalent(submitted, expected_equation)


def _record_misconception_section(misconception_id, user_id=None):
    """Record a structured misconception and return display metadata."""
    if not misconception_id:
        return None

    misconception = get_misconception_definition(misconception_id)
    if misconception is None:
        return None

    misconception["count"] = record_misconception(misconception_id, user_id=user_id)
    return misconception


def _finalise_practice_feedback(
    problem,
    student_answer,
    skill,
    correct,
    correct_text,
    issue=None,
    fix=None,
    next_step=None,
    misconception_id=None,
    user_id=None,
):
    """Update progression and build feedback for non-equation practice."""
    record_problem_attempt(user_id=user_id)
    topic = _format_skill_label(skill)
    record_learning_event(
        "problem_attempted",
        skill=skill,
        topic=topic,
        detail=problem,
        user_id=user_id,
    )

    if correct:
        skill_data = adjust_skill(
            skill,
            score_delta=mastery_delta(True),
            attempt_delta=1,
            user_id=user_id,
        )
        record_correct_answer(user_id=user_id)
        record_learning_event(
            "answer_correct",
            skill=skill,
            topic=topic,
            detail=problem,
            user_id=user_id,
        )
        level_message = update_progression(True, user_id=user_id)
        recommendation = get_personalised_recommendation(user_id)
        details = _compose_message(
            _section("Result", f"Correct. {correct_text}"),
            _section("Why It Works", "Your answer matches the targeted graph or coordinate feature."),
            _section("Mastery", f"{topic}: {skill_data['score']}/100"),
            _section("Next Step", level_message or "Try another problem from the same topic."),
            _section(
                "Recommended Practice",
                f"{recommendation['title']}\nReason: {recommendation['reason']}",
            ),
        )
        return {
            "status": "correct",
            "headline": "Correct",
            "result": f"Correct. {correct_text}",
            "details": details,
            "recommendation": recommendation,
            "next_steps": [
                recommendation["title"],
                "Try another coordinate geometry problem",
                "Explain a related graph feature",
            ],
        }

    misconception = _record_misconception_section(
        misconception_id,
        user_id=user_id,
    )
    misconception_count = misconception.get("count", 0) if misconception else 0
    skill_data = adjust_skill(
        skill,
        score_delta=mastery_delta(False, misconception_count=misconception_count),
        attempt_delta=1,
        user_id=user_id,
    )
    record_learning_event(
        "answer_incorrect",
        skill=skill,
        topic=topic,
        detail=misconception_id or problem,
        user_id=user_id,
    )
    update_progression(False, user_id=user_id)
    recommendation = get_personalised_recommendation(user_id)
    record_mistake(
        skill=skill,
        question=problem,
        submitted_answer=student_answer,
        correct_answer=correct_text,
        issue=issue,
        user_id=user_id,
    )

    misconception_section = None
    if misconception:
        misconception_text = (
            f"{misconception['label']}: {misconception['explanation']}\n"
            f"Recommendation: {misconception['recommendation']}"
        )
        if misconception_count >= 2:
            misconception_text += (
                f"\nThis has appeared {misconception_count} times, so targeted "
                f"practice on {misconception['practice_area'].lower()} would be useful."
            )
        misconception_section = _section("Misconception Detected", misconception_text)

    details = _compose_message(
        _section("Result", f"Not correct yet. The expected answer is {correct_text}"),
        _section("Likely Issue", issue or "The submitted answer does not match the requested feature."),
        _section("How To Fix It", fix or "Recalculate the requested feature and check the formula used."),
        misconception_section,
        _section("Mastery", f"{topic}: {skill_data['score']}/100"),
        _section("Next Step", next_step or "Try the same problem again using the formula."),
        _section(
            "Recommended Practice",
            f"{recommendation['title']}\nReason: {recommendation['reason']}",
        ),
    )
    next_steps = [
        recommendation["title"],
        "Try a similar graph or coordinate problem",
        "Review the worked method before retrying",
    ]
    if misconception and misconception_count >= 2:
        next_steps.insert(0, f"Practise {misconception['practice_area'].lower()}")

    return {
        "status": "incorrect",
        "headline": "Not Yet",
        "result": f"Incorrect. Expected answer: {correct_text}",
        "details": details,
        "next_steps": next_steps,
        "misconception": misconception,
        "recommendation": recommendation,
    }


def _evaluate_coordinate_geometry_problem(problem, student_answer, user_id=None):
    """Evaluate supported coordinate-geometry practice problems."""
    q_lower = str(problem or "").lower()
    points = _two_points_from_problem(problem)
    if points is None:
        return None

    point_a, point_b = points

    if "gradient" in q_lower or "slope" in q_lower:
        expected = gradient_between_points(point_a, point_b)
        expected_text = "undefined" if expected is None else _format_expression(expected)
        submitted = _numeric_answer_value(student_answer)
        if expected is None:
            correct = "undefined" in str(student_answer or "").lower()
            return _finalise_practice_feedback(
                problem,
                student_answer,
                "coordinate_geometry",
                correct,
                expected_text,
                issue="A vertical line has undefined gradient.",
                fix="Check whether the x-coordinates are the same.",
                next_step="Write undefined instead of a number for a vertical-line gradient.",
                user_id=user_id,
            )

        correct = submitted is not None and _values_close(submitted, float(expected))
        misconception_id = None
        if submitted is not None and expected != 0:
            reversed_gradient = 1 / float(expected)
            if _values_close(submitted, reversed_gradient):
                misconception_id = "GRADIENT_RUN_OVER_RISE"

        return _finalise_practice_feedback(
            problem,
            student_answer,
            "coordinate_geometry",
            correct,
            expected_text,
            issue="The gradient should be change in y divided by change in x.",
            fix="Use (y2 - y1) / (x2 - x1), not the reverse.",
            next_step="Recalculate rise over run from the two points.",
            misconception_id=misconception_id,
            user_id=user_id,
        )

    if "midpoint" in q_lower or "middle point" in q_lower:
        expected = midpoint_between_points(point_a, point_b)
        expected_point = tuple(float(value) for value in expected)
        submitted_point = _extract_point_answer(student_answer)
        correct = _points_close(submitted_point, expected_point)
        misconception_id = None
        if submitted_point is not None and not correct:
            if (
                _values_close(submitted_point[0], expected_point[0])
                or _values_close(submitted_point[1], expected_point[1])
            ):
                misconception_id = "MIDPOINT_ONE_COORDINATE"

        return _finalise_practice_feedback(
            problem,
            student_answer,
            "coordinate_geometry",
            correct,
            _format_point_value(expected),
            issue="The midpoint needs both coordinates averaged separately.",
            fix="Average the x-values, then average the y-values.",
            next_step="Write the answer as an ordered pair, for example (4, 7).",
            misconception_id=misconception_id,
            user_id=user_id,
        )

    if "distance" in q_lower or "length" in q_lower:
        expected = distance_between_points(point_a, point_b)
        submitted = _numeric_answer_value(student_answer)
        expected_float = float(expected.evalf())
        correct = submitted is not None and _values_close(submitted, expected_float)
        dx = float(point_b[0] - point_a[0])
        dy = float(point_b[1] - point_a[1])
        squared_distance = dx * dx + dy * dy
        misconception_id = None
        if submitted is not None and _values_close(submitted, squared_distance):
            misconception_id = "DISTANCE_MISSING_SQUARE_ROOT"

        return _finalise_practice_feedback(
            problem,
            student_answer,
            "coordinate_geometry",
            correct,
            _format_expression(expected),
            issue="The distance formula needs the final square root.",
            fix="Calculate sqrt((x2 - x1)^2 + (y2 - y1)^2).",
            next_step="Check the squared changes, add them, then take the square root.",
            misconception_id=misconception_id,
            user_id=user_id,
        )

    if "equation of the line" in q_lower or "line through" in q_lower or "line passing" in q_lower:
        expected = equation_of_line_through_points(point_a, point_b)
        correct = _line_answer_matches(student_answer, expected)
        return _finalise_practice_feedback(
            problem,
            student_answer,
            "coordinate_geometry",
            correct,
            expected,
            issue="The line equation must pass through both given points.",
            fix="Find the gradient first, then substitute one point into y = mx + c.",
            next_step="Substitute both coordinates into your equation to check it.",
            user_id=user_id,
        )

    return None


def _extract_graph_equation(problem):
    match = re.search(
        r"(?i)\bfor\s+(?P<equation>y\s*=.+?),\s*(?:find|identify|calculate)",
        str(problem or ""),
    )
    return match.group("equation").strip() if match else None


def _evaluate_graph_feature_problem(problem, student_answer, user_id=None):
    """Evaluate supported graph-feature practice problems."""
    q_lower = str(problem or "").lower()
    equation = _extract_graph_equation(problem)
    if not equation:
        return None

    try:
        data = graph_function_data(equation)
    except ValueError:
        return None

    features = data["features"]
    skill = "function_graphs"

    if "gradient" in q_lower:
        expected = _numeric_answer_value(features["gradient"])
        submitted = _numeric_answer_value(student_answer)
        correct = submitted is not None and _values_close(submitted, expected)
        misconception_id = None
        y_intercept = _numeric_answer_value(features.get("y_intercept"))
        if submitted is not None and y_intercept is not None and _values_close(submitted, y_intercept):
            misconception_id = "GRAPH_INTERCEPT_CONFUSION"
        return _finalise_practice_feedback(
            problem,
            student_answer,
            skill,
            correct,
            features["gradient"],
            issue="The gradient is the coefficient of x in y = mx + c.",
            fix="Identify m, not the intercept.",
            next_step="Compare the answer with the number multiplying x.",
            misconception_id=misconception_id,
            user_id=user_id,
        )

    if "y-intercept" in q_lower or "y intercept" in q_lower:
        expected = _numeric_answer_value(features["y_intercept"])
        submitted = _numeric_answer_value(student_answer)
        correct = submitted is not None and _values_close(submitted, expected)
        misconception_id = None
        gradient = _numeric_answer_value(features.get("gradient"))
        if submitted is not None and gradient is not None and _values_close(submitted, gradient):
            misconception_id = "GRAPH_INTERCEPT_CONFUSION"
        return _finalise_practice_feedback(
            problem,
            student_answer,
            skill,
            correct,
            features["y_intercept"],
            issue="The y-intercept is where x = 0.",
            fix="In y = mx + c, c is the y-intercept.",
            next_step="Substitute x = 0 into the equation to check.",
            misconception_id=misconception_id,
            user_id=user_id,
        )

    if "x-intercept" in q_lower or "x intercept" in q_lower:
        intercepts = features.get("x_intercepts", [])
        if not intercepts:
            submitted_text = str(student_answer or "").lower()
            correct = "none" in submitted_text or "no real" in submitted_text
            expected_text = "no real x-intercepts"
        else:
            expected = _numeric_answer_value(intercepts[0])
            submitted = _numeric_answer_value(student_answer)
            correct = submitted is not None and _values_close(submitted, expected)
            expected_text = intercepts[0]
        return _finalise_practice_feedback(
            problem,
            student_answer,
            skill,
            correct,
            expected_text,
            issue="The x-intercept is where y = 0.",
            fix="Set the function equal to 0 and solve for x.",
            next_step="Substitute the x-intercept back in and check y becomes 0.",
            user_id=user_id,
        )

    if "vertex" in q_lower:
        vertex = features.get("vertex")
        if not vertex:
            return None
        expected_point = (
            _numeric_answer_value(vertex["x"]),
            _numeric_answer_value(vertex["y"]),
        )
        submitted_point = _extract_point_answer(student_answer)
        correct = _points_close(submitted_point, expected_point)
        return _finalise_practice_feedback(
            problem,
            student_answer,
            skill,
            correct,
            _format_point_value(expected_point),
            issue="The vertex is the turning point of the parabola.",
            fix="Use x = -b/(2a) or read the vertex from vertex form.",
            next_step="Check that the axis of symmetry passes through the vertex.",
            user_id=user_id,
        )

    if "axis of symmetry" in q_lower:
        expected = _numeric_answer_value(features.get("axis_of_symmetry"))
        submitted = _numeric_answer_value(student_answer)
        correct = submitted is not None and _values_close(submitted, expected)
        return _finalise_practice_feedback(
            problem,
            student_answer,
            skill,
            correct,
            f"x = {_format_value(expected)}",
            issue="The axis of symmetry is a vertical line through the vertex.",
            fix="Use the x-coordinate of the vertex.",
            next_step="Write the answer as x = value.",
            user_id=user_id,
        )

    return None


def _evaluate_non_equation_practice(problem, student_answer, user_id=None):
    """Evaluate graph and coordinate practice before equation solving fallback."""
    skill = detect_math_skill(problem)
    if skill == "coordinate_geometry":
        return _evaluate_coordinate_geometry_problem(
            problem,
            student_answer,
            user_id=user_id,
        )
    if skill == "function_graphs":
        return _evaluate_graph_feature_problem(
            problem,
            student_answer,
            user_id=user_id,
        )
    return None


def evaluate_answer_details(eq, student_answer, user_id=None):
    """Evaluate a student's answer and return structured coaching feedback."""
    non_equation_result = _evaluate_non_equation_practice(
        eq,
        student_answer,
        user_id=user_id,
    )
    if non_equation_result is not None:
        return non_equation_result

    if has_obvious_malformed_math_input(eq):
        return {
            "status": "error",
            "headline": "Invalid Equation",
            "result": MATH_PARSE_ERROR_MESSAGE,
            "details": MATH_PARSE_ERROR_MESSAGE,
            "next_steps": [
                "Check that both sides of the equation are complete.",
                "Use one equals sign, for example 2x + 4 = 10.",
            ],
        }

    correct_values = solve_values(eq)
    if correct_values is None:
        return {
            "status": "error",
            "headline": "Unsupported Problem",
            "result": "This answer checker currently supports equations with real numeric solutions.",
            "details": "This answer checker currently supports equations with real numeric solutions.",
            "next_steps": ["Try a linear equation or a factorable quadratic equation."],
        }

    student_values = _extract_numeric_answers(student_answer)
    if student_values is None:
        if len(correct_values) == 1:
            message = "Enter a numeric answer such as 5, -2, or x = 3/2."
            next_step = "Use a single numeric value or x = value."
        else:
            message = "Enter all solutions, for example x = 2 or x = 3."
            next_step = "Separate multiple solutions with 'or' or commas."
        return {
            "status": "error",
            "headline": "Invalid Answer Format",
            "result": message,
            "details": message,
            "next_steps": [next_step],
        }

    record_problem_attempt(user_id=user_id)

    skill = detect_math_skill(eq) or "linear_equations"
    correct_text = _format_solution_set(correct_values)
    record_learning_event(
        "problem_attempted",
        skill=skill,
        topic=_format_skill_label(skill),
        detail=eq,
        user_id=user_id,
    )

    if _values_match(correct_values, student_values):
        skill_data = adjust_skill(
            skill,
            score_delta=mastery_delta(True),
            attempt_delta=1,
            user_id=user_id,
        )
        record_correct_answer(user_id=user_id)
        record_learning_event(
            "answer_correct",
            skill=skill,
            topic=_format_skill_label(skill),
            detail=eq,
            user_id=user_id,
        )
        level_message = update_progression(True, user_id=user_id)
        recommendation = get_personalised_recommendation(user_id)

        details = _compose_message(
            _section("Result", f"Correct. {correct_text}"),
            _section(
                "Why It Works",
                "Your value or solution set satisfies the original equation.",
            ),
            _section(
                "Mastery",
                f"{_format_skill_label(skill)}: {skill_data['score']}/100",
            ),
            _section(
                "Next Step",
                level_message or "Try the next problem without checking the method first.",
            ),
            _section(
                "Recommended Practice",
                f"{recommendation['title']}\nReason: {recommendation['reason']}",
            ),
        )
        return {
            "status": "correct",
            "headline": "Correct",
            "result": f"Correct. {correct_text}",
            "details": details,
            "recommendation": recommendation,
            "next_steps": [
                recommendation["title"],
                f"Give me a harder equation like {eq}",
                f"Show the full working for {eq}",
            ],
        }

    if len(correct_values) == 1 and len(student_values) == 1:
        diagnosis = _diagnose_linear_answer(eq, student_values[0], correct_values[0])
    else:
        diagnosis = _diagnose_solution_set_answer(correct_values, student_values)

    misconception = detect_misconception(
        eq,
        student_answer,
        correct_values,
    )
    misconception_section = None
    if misconception is not None:
        misconception_count = record_misconception(
            misconception["id"],
            user_id=user_id,
        )
        misconception["count"] = misconception_count

        misconception_text = (
            f"{misconception['label']}: {misconception['explanation']}\n"
            f"Recommendation: {misconception['recommendation']}"
        )
        if misconception_count >= 2:
            misconception_text += (
                f"\nThis has appeared {misconception_count} times, so targeted "
                f"practice on {misconception['practice_area'].lower()} would be useful."
            )
        misconception_section = _section(
            "Misconception Detected",
            misconception_text,
        )

    skill_data = adjust_skill(
        skill,
        score_delta=mastery_delta(
            False,
            misconception_count=misconception.get("count", 0) if misconception else 0,
        ),
        attempt_delta=1,
        user_id=user_id,
    )
    record_learning_event(
        "answer_incorrect",
        skill=skill,
        topic=_format_skill_label(skill),
        detail=misconception["id"] if misconception else eq,
        user_id=user_id,
    )
    update_progression(False, user_id=user_id)
    recommendation = get_personalised_recommendation(user_id)

    record_mistake(
        skill=skill,
        question=eq,
        submitted_answer=student_answer,
        correct_answer=correct_text,
        issue=diagnosis["issue"],
        user_id=user_id,
    )
    sections = [
        _section("Result", f"Not correct yet. The correct answer is {correct_text}"),
        _section("Likely Issue", diagnosis["issue"]),
        _section("How To Fix It", diagnosis["fix"]),
    ]
    if misconception_section:
        sections.append(misconception_section)
    sections.extend([
        _section(
            "Mastery",
            f"{_format_skill_label(skill)}: {skill_data['score']}/100",
        ),
        _section("Next Step", diagnosis["next_step"]),
        _section(
            "Recommended Practice",
            f"{recommendation['title']}\nReason: {recommendation['reason']}",
        ),
    ])
    details = _compose_message(*sections)
    next_steps = [
        recommendation["title"],
        f"Give me a similar problem to {eq}",
        f"Show the full working for {eq}",
    ]
    if misconception is not None and misconception.get("count", 0) >= 2:
        next_steps.insert(
            0,
            f"Practise {misconception['practice_area'].lower()}",
        )

    return {
        "status": "incorrect",
        "headline": "Not Yet",
        "result": f"Incorrect. Correct answer: {correct_text}",
        "details": details,
        "next_steps": next_steps,
        "misconception": misconception,
        "recommendation": recommendation,
    }


def evaluate_answer(eq, student_answer, user_id=None):
    """Return the text-only version of structured answer feedback."""
    return evaluate_answer_details(eq, student_answer, user_id=user_id)["details"]
