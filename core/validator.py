"""Validation logic for mathematical equivalence and algebraic step checking."""

from sympy import simplify, solve

from core.parser import (
    _equation_to_expression,
    normalise_equation,
    normalise_expression,
    parse_math_expression,
    x,
)


def expressions_equivalent(expr1_str, expr2_str):
    """Return whether two expressions simplify to the same value."""
    try:
        expr1 = normalise_expression(expr1_str)
        expr2 = normalise_expression(expr2_str)
        return simplify(expr1 - expr2) == 0
    except Exception:
        return False


def equations_equivalent(eq1_str, eq2_str):
    """Return whether two equations describe the same relationship."""
    try:
        expr1 = normalise_equation(eq1_str)
        expr2 = normalise_equation(eq2_str)

        if simplify(expr1 - expr2) == 0:
            return True

        if expr1 == 0 or expr2 == 0:
            return expr1 == expr2

        ratio = simplify(expr1 / expr2)
        if getattr(ratio, "is_number", False) and ratio != 0:
            return True

        return set(solve(expr1, x)) == set(solve(expr2, x))
    except Exception:
        return False


def step_complexity(step):
    """Estimate structural complexity for an algebra step."""
    return (
        len(step)
        + step.count("^") * 3
        + step.count("(") * 2
        + step.count(")") * 2
    )


def classify_transformation(prev_step, current_step):
    """Classify the mathematical validity of a transformation."""
    if prev_step == current_step:
        return "redundant"

    if "=" in prev_step and "=" in current_step:
        if equations_equivalent(prev_step, current_step):
            return "valid_equation_transform"
        return "invalid"

    if expressions_equivalent(prev_step, current_step):
        return "valid_expression_transform"

    return "invalid"


def diagnose_error(prev_step, current_step):
    """Explain why a proposed algebra transformation appears invalid."""
    try:
        prev_left, prev_right = prev_step.split("=", 1)
        curr_left, curr_right = current_step.split("=", 1)

        prev_left_expr = parse_math_expression(prev_left)
        prev_right_expr = parse_math_expression(prev_right)
        curr_left_expr = parse_math_expression(curr_left)
        curr_right_expr = parse_math_expression(curr_right)

        prev_balance = simplify(prev_left_expr - prev_right_expr)
        curr_balance = simplify(curr_left_expr - curr_right_expr)

        if prev_balance != curr_balance:
            return (
                "The equation became unbalanced.\n\n"
                "Apply the same operation to both sides."
            )

        if "x" in prev_step and "x" in current_step:
            prev_coef = prev_left_expr.coeff(x)
            curr_coef = curr_left_expr.coeff(x)

            if prev_coef != curr_coef:
                return (
                    "The coefficient of x changed incorrectly.\n"
                    "Check whether you only divided or multiplied one side."
                )

        return "The transformation changed the equation structure unexpectedly."
    except Exception:
        return "Unable to analyse this transformation."


def generate_hint(prev_step, current_step):
    """Return a next-step hint based on a student's recent transformation."""
    if "+" in prev_step:
        return "Hint: Remove constants by subtracting the same value from both sides."

    if "-" in prev_step:
        return "Hint: Try adding the same value to both sides."

    if "x" in prev_step and "=" in prev_step:
        return "Hint: Once the constant is isolated, divide both sides by the coefficient of x."

    return "Hint: Apply the same operation to both sides of the equation."


def check_student_answer(expr1, expr2):
    """Compare two expressions or equations for equivalence."""
    if "=" in expr1 and "=" in expr2:
        return "Equivalent" if equations_equivalent(expr1, expr2) else "Not equivalent"

    return "Equivalent" if expressions_equivalent(expr1, expr2) else "Not equivalent"


def validate_steps(steps):
    """Validate a sequence of recorded algebra steps."""
    if len(steps) < 2:
        return "Not enough steps to validate."

    report = []

    for index in range(1, len(steps)):
        prev_step = steps[index - 1].strip()
        current_step = steps[index].strip()
        transformation_type = classify_transformation(prev_step, current_step)

        if transformation_type == "redundant":
            return (
                f"Redundant step detected at step {index + 1}. "
                "No transformation occurred."
            )

        if transformation_type == "invalid":
            diagnosis = diagnose_error(prev_step, current_step)
            hint = generate_hint(prev_step, current_step)
            return (
                f"Transformation error at step {index + 1}.\n\n"
                f"{diagnosis}\n\n"
                f"{hint}"
            )

        prev_complexity = step_complexity(prev_step)
        current_complexity = step_complexity(current_step)
        if current_complexity > prev_complexity + 5:
            report.append(
                f"Warning at step {index + 1}: equation complexity increased."
            )

        if index >= 2 and current_step == steps[index - 2].strip():
            return (
                f"Reversal detected at step {index + 1}. "
                "You returned to a previous state."
            )

    if report:
        return "All transformations are valid.\n" + "\n".join(report)

    return "All transformations are mathematically valid."
