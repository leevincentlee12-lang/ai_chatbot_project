"""Answer checking and diagnostic feedback for math practice."""

from core.parser import _extract_numeric_answer
from core.progression import (
    detect_math_skill,
    get_or_create_skill,
    record_correct_answer,
    record_problem_attempt,
    update_progression,
)
from engine.algebra_solver import _parse_linear_equation, solve_value
from utils.formatting import (
    _compose_message,
    _format_skill_label,
    _format_value,
    _section,
)


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


def evaluate_answer_details(eq, student_answer):
    """Evaluate a student's answer and return structured coaching feedback."""
    correct = solve_value(eq)
    if correct is None:
        return {
            "status": "error",
            "headline": "Unsupported Problem",
            "result": "This answer checker currently supports equations with one numeric solution.",
            "details": "This answer checker currently supports equations with one numeric solution.",
            "next_steps": ["Try a linear equation with one answer."],
        }

    student_value = _extract_numeric_answer(student_answer)
    if student_value is None:
        message = "Enter a numeric answer such as 5, -2, or x = 3/2."
        return {
            "status": "error",
            "headline": "Invalid Answer Format",
            "result": message,
            "details": message,
            "next_steps": ["Use a single numeric value or x = value."],
        }

    record_problem_attempt()

    skill = detect_math_skill(eq) or "linear_equations"
    skill_data = get_or_create_skill(skill)
    skill_data["attempts"] += 1

    if abs(correct - student_value) < 1e-9:
        skill_data["score"] = min(100, max(0, skill_data["score"] + 5))
        record_correct_answer()
        level_message = update_progression(True)

        details = _compose_message(
            _section("Result", f"Correct. x = {_format_value(correct)}"),
            _section(
                "Why It Works",
                "Your value satisfies the original equation, so the balance is preserved.",
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
            "result": f"Correct. x = {_format_value(correct)}",
            "details": details,
            "next_steps": [
                f"Give me a harder equation like {eq}",
                f"Show the full working for {eq}",
            ],
        }

    skill_data["score"] = min(100, max(0, skill_data["score"] - 3))
    update_progression(False)
    diagnosis = _diagnose_linear_answer(eq, student_value, correct)
    details = _compose_message(
        _section("Result", f"Not correct yet. The correct answer is x = {_format_value(correct)}"),
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
        "result": f"Incorrect. Correct answer: x = {_format_value(correct)}",
        "details": details,
        "next_steps": [
            f"Give me a similar problem to {eq}",
            f"Show the full working for {eq}",
        ],
    }


def evaluate_answer(eq, student_answer):
    """Return the text-only version of structured answer feedback."""
    return evaluate_answer_details(eq, student_answer)["details"]
