"""Answer checking and diagnostic feedback for math practice."""

import re

from core.parser import (
    MATH_PARSE_ERROR_MESSAGE,
    _extract_numeric_answer,
    has_obvious_malformed_math_input,
)
from core.progression import (
    adjust_skill,
    detect_math_skill,
    record_mistake,
    record_correct_answer,
    record_problem_attempt,
    update_progression,
)
from engine.algebra_solver import _parse_linear_equation, solve_values
from utils.formatting import (
    _compose_message,
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


def evaluate_answer_details(eq, student_answer, user_id=None):
    """Evaluate a student's answer and return structured coaching feedback."""
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

    if _values_match(correct_values, student_values):
        skill_data = adjust_skill(
            skill,
            score_delta=5,
            attempt_delta=1,
            user_id=user_id,
        )
        record_correct_answer(user_id=user_id)
        level_message = update_progression(True, user_id=user_id)

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
        )
        return {
            "status": "correct",
            "headline": "Correct",
            "result": f"Correct. {correct_text}",
            "details": details,
            "next_steps": [
                f"Give me a harder equation like {eq}",
                f"Show the full working for {eq}",
            ],
        }

    skill_data = adjust_skill(
        skill,
        score_delta=-3,
        attempt_delta=1,
        user_id=user_id,
    )
    update_progression(False, user_id=user_id)
    if len(correct_values) == 1 and len(student_values) == 1:
        diagnosis = _diagnose_linear_answer(eq, student_values[0], correct_values[0])
    else:
        diagnosis = _diagnose_solution_set_answer(correct_values, student_values)

    record_mistake(
        skill=skill,
        question=eq,
        submitted_answer=student_answer,
        correct_answer=correct_text,
        issue=diagnosis["issue"],
        user_id=user_id,
    )
    details = _compose_message(
        _section("Result", f"Not correct yet. The correct answer is {correct_text}"),
        _section("Likely Issue", diagnosis["issue"]),
        _section("How To Fix It", diagnosis["fix"]),
        _section(
            "Mastery",
            f"{_format_skill_label(skill)}: {skill_data['score']}/100",
        ),
        _section("Next Step", diagnosis["next_step"]),
    )
    return {
        "status": "incorrect",
        "headline": "Not Yet",
        "result": f"Incorrect. Correct answer: {correct_text}",
        "details": details,
        "next_steps": [
            f"Give me a similar problem to {eq}",
            f"Show the full working for {eq}",
        ],
    }


def evaluate_answer(eq, student_answer, user_id=None):
    """Return the text-only version of structured answer feedback."""
    return evaluate_answer_details(eq, student_answer, user_id=user_id)["details"]
