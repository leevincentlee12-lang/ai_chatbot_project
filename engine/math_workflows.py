"""General math command workflows and legacy chat-style math handling."""

import random
import re

from sympy import Poly, expand, simplify

from core.parser import _equation_to_expression, parse_math_expression, x
from core.progression import generate_problem, student_profile, student_steps
from core.validator import check_student_answer, generate_hint, validate_steps
from engine.algebra_solver import (
    _parse_linear_equation,
    factor_expression,
    solve_linear,
    solve_quadratic,
    solve_simultaneous,
    sympy_solve_equation,
)
from engine.lesson_engine import _is_lesson_request, find_lesson_topic, generate_lesson
from engine.math_practice import guided_response, start_guided_problem
from utils.formatting import _build_explanation, _format_expression


def handle_math(question):
    """Handle mathematics questions across lessons, solving, and practice workflows."""
    original = (question or "").strip()
    q_lower = original.lower()
    lesson_topic = find_lesson_topic(original)

    if lesson_topic and _is_lesson_request(original):
        return generate_lesson(lesson_topic)["display_text"]

    if "show the full working for" in q_lower:
        eq = re.sub(r"(?i)^.*show the full working for\s*", "", original).strip()
        if "=" in eq and "x" in eq:
            linear = solve_linear(eq)
            if linear:
                return linear
            quadratic = solve_quadratic(eq)
            if quadratic:
                return quadratic
            sym_solution = sympy_solve_equation(eq)
            if sym_solution:
                return sym_solution

    if "give me a hint for" in q_lower:
        eq = re.sub(r"(?i)^.*give me a hint for\s*", "", original).strip()
        analysis = _parse_linear_equation(eq)
        if analysis and analysis["solution"] is not None:
            return _build_explanation(
                answer=f"Hint for {eq}",
                method=(
                    f"First move everything until you get {analysis['a_total']}x = {analysis['b_total']}."
                ),
                why="The goal is to isolate x before doing the final division.",
                next_step=f"After that, divide both sides by {analysis['a_total']}.",
            )

    if "give me a harder equation like" in q_lower:
        level = min(student_profile.get("difficulty", 1) + 1, 3)
        problem = generate_problem(level=level)
        return _build_explanation(
            answer=problem["problem"],
            why="This keeps the same skill area but raises the difficulty slightly.",
            next_step="Solve it and submit your answer in the practice panel.",
        )

    if "give me a similar problem to" in q_lower:
        problem = generate_problem(level=student_profile.get("difficulty", 1))
        return _build_explanation(
            answer=problem["problem"],
            why="This keeps you on the same skill without increasing difficulty yet.",
            next_step="Try solving it on your own, then check your answer.",
        )

    if "give me another factoring problem like" in q_lower:
        new_problem = random.choice([
            "factor x^2 - 16",
            "factor x^2 + 7x + 12",
            "factor x^2 + 9x + 20",
        ])
        return _build_explanation(
            answer=new_problem,
            why="This keeps you focused on the same factoring skill.",
            next_step="Try factoring it first, then ask me to check or explain it.",
        )

    if "explain the discriminant in" in q_lower:
        eq = re.sub(r"(?i)^.*explain the discriminant in\s*", "", original).strip()
        try:
            expr = _equation_to_expression(eq)
            poly = Poly(expr, x)
        except Exception:
            poly = None
        if poly and poly.degree() == 2:
            a_coeff, b_coeff, c_coeff = poly.all_coeffs()
            discriminant = simplify(b_coeff**2 - 4 * a_coeff * c_coeff)
            return _build_explanation(
                answer=f"The discriminant is {_format_expression(discriminant)}.",
                method=(
                    "For a quadratic ax^2 + bx + c = 0, compute b^2 - 4ac.\n"
                    f"Here that gives {_format_expression(discriminant)}."
                ),
                why=(
                    "The discriminant tells you whether the quadratic has two real roots, "
                    "one repeated real root, or no real roots."
                ),
                next_step="Ask me to connect that to the graph if you want a visual interpretation.",
            )

    if q_lower.startswith("expand "):
        expr = original[7:].strip()
        try:
            expanded = expand(parse_math_expression(expr))
        except Exception:
            expanded = None
        if expanded is not None:
            return _build_explanation(
                answer=_format_expression(expanded),
                method=f"Multiply the brackets term by term in {expr}.",
                why="Expanding checks whether a factored form really rebuilds the original expression.",
                next_step="If you want, I can also show the reverse factoring process.",
            )

    if "multiplies back to" in q_lower and "explain why" in q_lower:
        return _build_explanation(
            answer="Because factoring and expanding are inverse processes.",
            method="When you expand the brackets term by term, the combined terms rebuild the original expression.",
            why="A correct factorisation must expand exactly to the starting expression.",
            next_step="Ask me to expand the brackets line by line if you want the proof shown.",
        )

    if "show steps" in q_lower:
        if not student_steps:
            return "No steps recorded."
        return "\n".join(
            f"Step {index + 1}: {step}"
            for index, step in enumerate(student_steps)
        )

    if "validate steps" in q_lower:
        return validate_steps(student_steps)

    if "clear steps" in q_lower:
        student_steps.clear()
        return "Steps cleared."

    if q_lower.startswith("step"):
        step_expr = original[4:].strip().lower()
        if not step_expr:
            return "No step provided."
        student_steps.append(step_expr)
        return f"Step {len(student_steps)} recorded."

    if "hint" in q_lower:
        if len(student_steps) >= 2:
            return generate_hint(student_steps[-2], student_steps[-1])
        return "Record at least two steps first."

    if q_lower.startswith("check "):
        parts = original[6:].split(",", 1)
        if len(parts) == 2:
            return check_student_answer(parts[0].strip(), parts[1].strip())
        return "Use: check first_expression, second_expression"

    if "check my answer for" in q_lower:
        return (
            "Use the practice answer box or type your value like "
            "'answer x = 3' after starting a guided problem."
        )

    if "guided problem" in q_lower:
        return start_guided_problem()

    if q_lower.startswith("answer"):
        return guided_response(original[6:].strip())

    if q_lower == "problem" or "practice problem" in q_lower:
        problem = generate_problem()
        return f"Practice problem: {problem['problem']}"

    if "factor" in q_lower:
        expr = re.sub(r"(?i)^factor\s*", "", original).strip()
        return factor_expression(expr)

    if " and " in q_lower and "=" in q_lower and "y" in q_lower:
        parts = re.split(r"(?i)\sand\s", original, maxsplit=1)
        if len(parts) == 2:
            return solve_simultaneous(parts[0].strip(), parts[1].strip())

    if "=" in q_lower and ("x^2" in q_lower or "quadratic" in q_lower):
        eq = re.sub(r"(?i)^\s*solve\s*", "", original).strip()
        solution = solve_quadratic(eq)
        if solution:
            return solution

    if "=" in q_lower and "x" in q_lower:
        eq = re.sub(r"(?i)^\s*solve\s*", "", original).strip()
        linear = solve_linear(eq)
        if linear:
            return linear

        sym_solution = sympy_solve_equation(eq)
        if sym_solution:
            return sym_solution

    return "Provide a valid maths question or equation."
