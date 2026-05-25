"""Algebra parsing, solving, and symbolic manipulation helpers."""

import re

from sympy import Poly, factor as sympy_factor, simplify, solve

from core.parser import (
    MATH_PARSE_ERROR_MESSAGE,
    _equation_to_expression,
    has_obvious_malformed_math_input,
    parse_math_expression,
    x,
    y,
)
from utils.formatting import (
    _build_explanation,
    _format_expression,
    _format_raw_expression,
    _format_value,
)


def _parse_linear_equation(eq):
    """Analyse a plain linear equation into coefficient totals and solution data."""
    equation = (eq or "").replace(" ", "")

    if (
        equation.count("=") != 1
        or has_obvious_malformed_math_input(equation)
        or "y" in equation
        or "^" in equation
    ):
        return None

    if "/" in equation or re.search(r"\d\(", equation):
        return None

    left, right = equation.split("=", 1)

    def parse_side(side):
        if not side:
            raise ValueError("Empty equation side.")

        normalized = side if side[0] in "+-" else f"+{side}"
        terms = re.findall(r"[+-](?:\d*x|\d+)", normalized)

        if not terms or "".join(terms) != normalized:
            raise ValueError("Unsupported linear equation side.")

        a_value = 0
        b_value = 0

        for term in terms:
            if "x" in term:
                coefficient = term.replace("x", "")
                if coefficient in ("", "+"):
                    coefficient = 1
                elif coefficient == "-":
                    coefficient = -1
                else:
                    coefficient = int(coefficient)
                a_value += coefficient
            else:
                b_value += int(term)

        return a_value, b_value

    try:
        a1, b1 = parse_side(left)
        a2, b2 = parse_side(right)
    except ValueError:
        return None

    a_total = a1 - a2
    b_total = b2 - b1

    if a_total == 0:
        solution = None
    else:
        solution = b_total / a_total

    return {
        "a_total": a_total,
        "b_total": b_total,
        "left": left,
        "right": right,
        "solution": solution,
    }


def solve_linear(eq):
    """Solve a plain linear equation and explain the process."""
    analysis = _parse_linear_equation(eq)
    if analysis is None:
        return None

    a_total = analysis["a_total"]
    b_total = analysis["b_total"]

    if a_total == 0 and b_total == 0:
        return "Infinite solutions."

    if a_total == 0:
        return "No solution."

    solution = analysis["solution"]
    reduced_step = f"{a_total}x = {b_total}"

    if b_total % a_total == 0:
        division_step = f"x = {b_total // a_total}"
    else:
        division_step = f"x = {b_total}/{a_total} = {_format_value(solution)}"

    return _build_explanation(
        answer=f"x = {_format_value(solution)}",
        method=(
            "1. Move the x terms to one side and constants to the other.\n"
            f"   {reduced_step}\n"
            "2. Divide both sides by the coefficient of x.\n"
            f"   {division_step}"
        ),
        why=(
            "Each step keeps the equation balanced while isolating x, "
            "so the final value still satisfies the original equation."
        ),
        check=(
            f"Substitute x = {_format_value(solution)} back into the equation "
            "and both sides will match."
        ),
        next_step="Try solving the next one without looking at the method first.",
    )


def solve_quadratic(eq):
    """Solve a quadratic equation with a structured explanation."""
    try:
        expr = _equation_to_expression(eq)
        poly = Poly(expr, x)
    except Exception:
        return None

    if poly.degree() != 2:
        return None

    a_coeff, b_coeff, c_coeff = poly.all_coeffs()
    discriminant = simplify(b_coeff**2 - 4 * a_coeff * c_coeff)

    solutions = solve(expr, x)
    real_solutions = [sol for sol in solutions if sol.is_real is not False]

    if not real_solutions:
        return _build_explanation(
            answer="No real solutions.",
            method=(
                "1. Write the equation in standard form.\n"
                f"   {_format_expression(expr)} = 0\n"
                "2. Calculate the discriminant.\n"
                f"   D = {_format_expression(discriminant)}"
            ),
            why=(
                "A negative discriminant means the graph does not cross the "
                "x-axis, so there are no real roots."
            ),
            next_step="If you want, I can show the complex-number solutions.",
        )

    solution_lines = [
        f"x{i + 1} = {_format_expression(solution)}"
        for i, solution in enumerate(real_solutions)
    ]

    answer = " or ".join(
        f"x = {_format_expression(solution)}"
        for solution in real_solutions
    )

    return _build_explanation(
        answer=answer,
        method=(
            "1. Write the equation in standard form.\n"
            f"   {_format_expression(expr)} = 0\n"
            "2. Identify the coefficients.\n"
            f"   a = {_format_expression(a_coeff)}, "
            f"b = {_format_expression(b_coeff)}, "
            f"c = {_format_expression(c_coeff)}\n"
            "3. Calculate the discriminant.\n"
            f"   D = {_format_expression(discriminant)}\n"
            "4. Solve for x.\n"
            f"   " + "\n   ".join(solution_lines)
        ),
        why=(
            "The discriminant shows how many real solutions exist, and the "
            "quadratic formula isolates the x-values that make the equation zero."
        ),
        check="Substitute each root back into the original equation to confirm it equals zero.",
        next_step="Ask for factoring or graph interpretation if you want a second view of the same quadratic.",
    )


def solve_simultaneous(eq1, eq2):
    """Solve a pair of simultaneous equations."""
    try:
        expr1 = _equation_to_expression(eq1)
        expr2 = _equation_to_expression(eq2)
        solutions = solve((expr1, expr2), (x, y), dict=True)
    except Exception:
        return MATH_PARSE_ERROR_MESSAGE

    if len(solutions) != 1:
        return "No unique solution."

    solution = solutions[0]
    if x not in solution or y not in solution:
        return "No unique solution."

    return _build_explanation(
        answer=(
            f"x = {_format_expression(solution[x])}\n"
            f"y = {_format_expression(solution[y])}"
        ),
        method=(
            "Solve both equations together and find the ordered pair that satisfies both at the same time."
        ),
        why="A simultaneous solution must make equation 1 and equation 2 true together.",
        check=(
            f"Substitute x = {_format_expression(solution[x])} and "
            f"y = {_format_expression(solution[y])} into both equations."
        ),
        next_step="Ask for elimination or substitution method if you want the full working shown.",
    )


def factor_expression(expr):
    """Factor an expression over the integers when possible."""
    expression = (expr or "").strip()
    if not expression:
        return "Provide an expression to factor."

    try:
        parsed = simplify(parse_math_expression(expression))
        factored = sympy_factor(parsed)
    except Exception:
        return MATH_PARSE_ERROR_MESSAGE

    if simplify(factored - parsed) != 0:
        return "Unable to factor that expression safely."

    if _format_raw_expression(factored) == _format_raw_expression(parsed):
        return "This expression does not factor further over the integers."

    return _build_explanation(
        answer=_format_raw_expression(factored),
        method=(
            "Rewrite the expression as a product of simpler factors. "
            "Those factors multiply back to the original expression."
        ),
        why="Factoring helps reveal roots, intercepts, and useful algebra structure.",
        check=(
            f"Expand {_format_raw_expression(factored)} and you will recover "
            f"{_format_raw_expression(parsed)}."
        ),
        next_step="I can also show how to expand the factors back out if you want to verify it.",
    )


def solve_value(eq):
    """Solve an equation for a single numeric x-value when possible."""
    if has_obvious_malformed_math_input(eq):
        return None

    try:
        solution = solve(_equation_to_expression(eq), x)
    except Exception:
        return None

    if len(solution) != 1:
        return None

    try:
        return float(solution[0])
    except (TypeError, ValueError):
        return None


def sympy_solve_equation(eq):
    """Solve an equation symbolically when the manual linear solver does not apply."""
    if has_obvious_malformed_math_input(eq):
        return MATH_PARSE_ERROR_MESSAGE

    value = solve_value(eq)
    if value is None:
        return None

    return _build_explanation(
        answer=f"x = {_format_value(value)}",
        method="This was solved symbolically because it does not fit the simpler linear step template.",
        why="Symbolic solving isolates the value of x while preserving equivalence.",
        check=f"Substitute x = {_format_value(value)} back into the original equation.",
        next_step="If you want, I can still break this down into manual algebra steps where possible.",
    )
