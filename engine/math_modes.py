"""Mode-specific algebra responses for direct, step-by-step, and hint modes."""

import math
import re

from sympy import Poly, expand, factor as sympy_factor, simplify, solve

from core.classifier import classify_algebra_intent
from core.parser import _equation_to_expression, parse_math_expression, x, y
from engine.algebra_solver import _parse_linear_equation, solve_value
from utils.formatting import (
    _build_explanation,
    _format_expression,
    _format_raw_expression,
    _format_value,
)


def _is_gradient_question(question):
    """Return whether the question asks for a line gradient."""
    q_lower = (question or "").lower().strip()
    gradient_keywords = [
        r"\bgradient\b",
        r"\bslope\b",
        r"\brate\s+of\s+change\b",
    ]
    return any(re.search(keyword, q_lower) for keyword in gradient_keywords)


def _extract_gradient(question):
    """Extract m from a line equation in y = mx + b form."""
    patterns = [
        r"y\s*=\s*([+-]?\d*\.?\d*)\s*x",
        r"y\s*=\s*([+-]?\d*\.?\d*)x",
    ]

    for pattern in patterns:
        match = re.search(pattern, question, re.IGNORECASE)
        if match:
            coefficient = match.group(1)
            try:
                if coefficient in ("", "+"):
                    return 1
                if coefficient == "-":
                    return -1
                return float(coefficient)
            except (ValueError, IndexError):
                continue

    return None


def _answer_gradient_question(question, mode):
    """Answer a gradient question in the requested experiment mode."""
    gradient = _extract_gradient(question)

    if gradient is None:
        return None

    if isinstance(gradient, float) and gradient == int(gradient):
        gradient_text = str(int(gradient))
    else:
        gradient_text = str(gradient)

    answer = f"The gradient is {gradient_text}."

    if mode == "direct":
        return answer

    if mode == "hint":
        return "The gradient is the coefficient of x in the equation y = mx + b."

    return (
        "The equation is in the form y = mx + b, where m is the gradient.\n"
        f"In this case, m = {gradient_text}\n"
        f"So the gradient is {gradient_text}."
    )


def _ratio_parts(question):
    """Extract integer ratio parts from text."""
    match = re.search(r"(-?\d+)\s*:\s*(-?\d+)", str(question or ""))
    if not match:
        return None

    left_value = int(match.group(1))
    right_value = int(match.group(2))

    if left_value == 0 and right_value == 0:
        return None

    return left_value, right_value


def _answer_ratio_question(question, mode):
    """Simplify a ratio in the requested experiment mode."""
    parts = _ratio_parts(question)
    if parts is None:
        return None

    left_value, right_value = parts
    divisor = math.gcd(abs(left_value), abs(right_value)) or 1
    simplified_left = left_value // divisor
    simplified_right = right_value // divisor
    answer = f"{simplified_left}:{simplified_right}"

    if mode == "direct":
        return answer

    if mode == "hint":
        return (
            "Find the greatest common factor of both parts of the ratio, "
            "then divide each part by it."
        )

    return (
        f"1. Find the greatest common factor of {left_value} and {right_value}, "
        f"which is {divisor}.\n"
        f"2. Divide both parts of the ratio by {divisor}.\n"
        f"3. The simplified ratio is {answer}."
    )


def _answer_factor_question(question, mode):
    """Factor an expression in the requested experiment mode."""
    if "factor" not in str(question or "").lower():
        return None

    expression = re.sub(r"(?i)^.*\bfactor\b\s*", "", str(question or "")).strip()
    if not expression:
        return "Provide an algebra equation or expression to work with."

    try:
        parsed = simplify(parse_math_expression(expression))
        factored = sympy_factor(parsed)
    except Exception:
        return "Provide an algebra equation or expression to work with."

    answer = _format_raw_expression(factored)

    if mode == "direct":
        return answer

    if mode == "hint":
        return (
            "Look first for a common factor or a standard pattern such as "
            "a difference of squares."
        )

    return (
        "1. Look for a common factor or a standard factorisation pattern.\n"
        "2. Rewrite the expression as a product of simpler factors.\n"
        f"3. The factorised form is {answer}."
    )


def _answer_expand_question(question, mode):
    """Expand an algebraic expression in the requested experiment mode."""
    if "expand" not in str(question or "").lower():
        return None

    expression = re.sub(r"(?i)^.*\bexpand\b\s*", "", str(question or "")).strip()
    if not expression:
        return "Provide an algebra equation or expression to work with."

    try:
        expanded = expand(parse_math_expression(expression))
    except Exception:
        return "Provide an algebra equation or expression to work with."

    answer = _format_expression(expanded)

    if mode == "direct":
        return answer

    if mode == "hint":
        return (
            "Expand one bracket term at a time, then combine like terms only "
            "after everything has been multiplied out."
        )

    return (
        "1. Multiply each term in the brackets by the relevant term outside or "
        "in the other bracket.\n"
        "2. Combine any like terms that appear.\n"
        f"3. The expanded expression is {answer}."
    )


def _answer_simplify_question(question, mode):
    """Simplify an algebraic expression in the requested experiment mode."""
    if "simplify" not in str(question or "").lower():
        return None

    expression = re.sub(r"(?i)^.*\bsimplify\b\s*", "", str(question or "")).strip()
    if not expression:
        return None

    if not re.search(r"(?<![a-z])(?:\d*)[xy](?:\^\d+)?\b", expression.lower()):
        return None

    try:
        simplified = simplify(parse_math_expression(expression))
    except Exception:
        return "Provide an algebra equation or expression to work with."

    answer = _format_expression(simplified)

    if mode == "direct":
        return answer

    if mode == "hint":
        return (
            "Look for like terms, then combine only the terms that have the "
            "same variable part."
        )

    return (
        "1. Identify any like terms or algebraic rules that apply.\n"
        "2. Combine those terms carefully while keeping the variable parts the same.\n"
        f"3. The simplified expression is {answer}."
    )


def _answer_quadratic_question(question, mode):
    """Solve a quadratic equation in the requested experiment mode."""
    equation = re.sub(r"(?i)^.*\bsolve\b\s*", "", str(question or "")).strip()

    try:
        expr = _equation_to_expression(equation)
        poly = Poly(expr, x)
    except Exception:
        return None

    if poly.degree() != 2:
        return None

    a_coeff, b_coeff, c_coeff = poly.all_coeffs()
    discriminant = simplify(b_coeff**2 - 4 * a_coeff * c_coeff)
    solutions = solve(expr, x)
    real_solutions = sorted(
        [sol for sol in solutions if sol.is_real is not False],
        key=lambda value: float(value.evalf()),
    )

    if not real_solutions:
        if mode == "hint":
            return (
                "Rewrite the equation in the form ax^2 + bx + c = 0, then "
                "check the discriminant to see how many real roots are possible."
            )
        if mode == "direct":
            return "No real solutions."
        return (
            f"1. Write the equation in standard form: {_format_expression(expr)} = 0.\n"
            f"2. Compute the discriminant: b^2 - 4ac = {_format_expression(discriminant)}.\n"
            "3. The discriminant is negative, so there are no real solutions."
        )

    answer = " or ".join(
        f"x = {_format_expression(solution)}"
        for solution in real_solutions
    )

    if mode == "direct":
        return answer

    if mode == "hint":
        return (
            "Rewrite the equation in the form ax^2 + bx + c = 0 first, then "
            "decide whether factoring or the quadratic formula is the better method."
        )

    return (
        f"1. Write the equation in standard form: {_format_expression(expr)} = 0.\n"
        f"2. Identify the coefficients: a = {_format_expression(a_coeff)}, "
        f"b = {_format_expression(b_coeff)}, c = {_format_expression(c_coeff)}.\n"
        f"3. Compute the discriminant: b^2 - 4ac = {_format_expression(discriminant)}.\n"
        f"4. Solve for x to get {answer}."
    )


def _answer_simultaneous_question(question, mode):
    """Solve a simultaneous-equations prompt in the requested experiment mode."""
    q = (question or "").strip()
    q = re.sub(
        r"(?i)^\s*(?:solve|find|show(?: the)?(?: elimination(?: method)?)?(?: for)?|show me|solve for|solve:)\s*",
        "",
        q,
    )

    if " and " not in q.lower() or "=" not in q or "y" not in q.lower():
        return None

    parts = re.split(r"(?i)\sand\s", q, maxsplit=1)
    if len(parts) != 2:
        return None

    try:
        expr1 = _equation_to_expression(parts[0].strip())
        expr2 = _equation_to_expression(parts[1].strip())
        solutions = solve((expr1, expr2), (x, y), dict=True)
    except Exception:
        return None

    if len(solutions) != 1 or x not in solutions[0] or y not in solutions[0]:
        return "No unique solution."

    solution = solutions[0]
    answer = (
        f"x = {_format_expression(solution[x])}, "
        f"y = {_format_expression(solution[y])}"
    )

    if mode == "direct":
        return answer

    if mode == "hint":
        return (
            "Choose one variable to eliminate or isolate first, so you can turn "
            "the system into a single-variable equation."
        )

    return (
        "1. Eliminate one variable or make one variable the subject in one equation.\n"
        "2. Solve the resulting single-variable equation.\n"
        "3. Substitute that value back into one original equation to find the second variable.\n"
        f"4. The solution is {answer}."
    )


def _answer_linear_question(question, mode):
    """Solve a linear equation in the requested experiment mode."""
    equation = re.sub(r"(?i)^.*\bsolve\b\s*", "", str(question or "")).strip()
    analysis = _parse_linear_equation(equation)

    if analysis is None:
        return None

    if analysis["a_total"] == 0 and analysis["b_total"] == 0:
        if mode == "hint":
            return (
                "Simplify both sides first and see whether they become the same expression."
            )
        return "Infinite solutions."

    if analysis["a_total"] == 0:
        if mode == "hint":
            return (
                "Move all variable terms to one side and constants to the other, "
                "then check whether any value of x can make the statement true."
            )
        return "No solution."

    solution = analysis["solution"]
    answer = f"x = {_format_value(solution)}"
    reduced_step = f"{analysis['a_total']}x = {analysis['b_total']}"

    if mode == "direct":
        return answer

    if mode == "hint":
        return (
            "Undo the addition or subtraction around x first, and make sure the "
            "same operation is applied to both sides."
        )

    return (
        "1. Move the x-terms to one side and the constants to the other, because "
        "the goal is to isolate x.\n"
        f"   {reduced_step}\n"
        f"2. Divide both sides by {analysis['a_total']}, because that is the coefficient of x.\n"
        f"   {answer}"
    )


def _answer_symbolic_equation(question, mode):
    """Solve a supported equation symbolically in the requested experiment mode."""
    equation = re.sub(r"(?i)^.*\bsolve\b\s*", "", str(question or "")).strip()
    value = solve_value(equation)
    if value is None:
        return None

    answer = f"x = {_format_value(value)}"

    if mode == "direct":
        return answer

    if mode == "hint":
        return (
            "Rearrange the equation so x is isolated, and keep each transformation "
            "equivalent on both sides."
        )

    return (
        "1. Rearrange the equation using equivalent algebraic steps.\n"
        "2. Isolate x by undoing the surrounding operations in reverse order.\n"
        f"3. The final answer is {answer}."
    )


def _answer_trig_question(question, mode):
    """Handle simple trig ratio questions like 'find x if sin 35 = x/12'."""
    q = (question or "").strip()
    if not q:
        return None

    q = re.sub(
        r"(?i)^\s*(?:find\s+x(?:\s*if)?\s*|find\s*if\s*|find\s*|solve\s*for\s+x(?:\s*if)?\s*|solve\s*if\s*|solve\s*|show\s.*for\s*)",
        "",
        q,
    )

    if "=" not in q or not re.search(r"(?i)\b(sin|cos|tan)\b", q):
        return None

    def _deg_to_rad(match):
        func = match.group(1).lower()
        number = match.group(2)
        return f"{func}({number}*pi/180)"

    converted = re.sub(
        r"(?i)\b(sin|cos|tan)\s*\(?\s*([0-9]+(?:\.[0-9]+)?)\s*\)?",
        _deg_to_rad,
        q,
    )

    try:
        expr = _equation_to_expression(converted)
        solutions = solve(expr, x)
    except Exception:
        return None

    if not solutions:
        return None

    solution = None
    for candidate in solutions:
        try:
            if candidate.is_real is not False:
                solution = candidate
                break
        except Exception:
            solution = candidate
            break

    if solution is None:
        solution = solutions[0]

    try:
        numeric = float(solution.evalf())
    except Exception:
        numeric = None

    if mode == "direct":
        if numeric is not None:
            return f"x = {_format_value(numeric)}"
        return f"x = {_format_expression(solution)}"

    if mode == "hint":
        return (
            "Isolate x first, then use the inverse trig function or multiply both sides. "
            "Remember to convert degree angles to radians when evaluating."
        )

    try:
        value_text = (
            _format_value(solution.evalf())
            if numeric is not None
            else _format_expression(solution)
        )
    except Exception:
        value_text = _format_expression(solution)

    method = (
        "1. Rearrange so x is the subject (multiply both sides if x is divided).\n"
        "2. Convert numeric angles from degrees to radians when evaluating trig.\n"
        f"3. Evaluate the trig value and compute x = {value_text}."
    )

    return _build_explanation(
        answer=f"x = {value_text}",
        method=method,
        why=(
            "Trig functions give ratios; numeric angle values are usually in degrees "
            "in school problems, so convert to radians for calculation."
        ),
        check="Substitute the computed value back into the original equation.",
        next_step="Try another trig equation or ask for the radian-based method.",
    )


def answer_experiment_algebra_question(question, mode):
    """Answer an algebra-scoped experiment question in the selected mode."""
    intent = classify_algebra_intent(question)
    intent_handlers = {
        "factoring": _answer_factor_question,
        "expand": _answer_expand_question,
        "expand_expression": _answer_expand_question,
        "simplify": _answer_simplify_question,
        "ratio": _answer_ratio_question,
        "simultaneous_equations": _answer_simultaneous_question,
        "simultaneous": _answer_simultaneous_question,
        "quadratic_equation": _answer_quadratic_question,
        "linear_equation": _answer_linear_question,
    }

    handler = intent_handlers.get(intent)
    if handler is not None:
        response = handler(question, mode)
        if response:
            return response

    if _is_gradient_question(question):
        response = _answer_gradient_question(question, mode)
        if response:
            return response

    ordered_handlers = [
        _answer_ratio_question,
        _answer_factor_question,
        _answer_expand_question,
        _answer_simplify_question,
        _answer_simultaneous_question,
        _answer_quadratic_question,
        _answer_linear_question,
        _answer_trig_question,
        _answer_symbolic_equation,
    ]

    for fallback_handler in ordered_handlers:
        response = fallback_handler(question, mode)
        if response:
            return response

    return "Provide an algebra equation, expression, or ratio to work with."
