"""Rule-based misconception detection for algebra answer checking."""

import re

from sympy import Poly, simplify

from core.parser import _equation_to_expression, _extract_numeric_answer, parse_math_expression, x


MISCONCEPTIONS = {
    "SIGN_ERROR": {
        "label": "Sign error",
        "explanation": (
            "You may have changed a positive value to a negative value, or "
            "moved a term across the equals sign with the wrong sign."
        ),
        "recommendation": (
            "Practise linear equations with negative values and check each "
            "sign when moving terms."
        ),
        "practice_area": "Linear equations with negative values",
    },
    "FORGOT_TO_DIVIDE": {
        "label": "Forgot to divide",
        "explanation": (
            "You may have reached the ax = b step but used b as the answer "
            "instead of dividing by the coefficient of x."
        ),
        "recommendation": (
            "Practise one-step and two-step equations where the final step is "
            "dividing both sides by the coefficient."
        ),
        "practice_area": "One-step and two-step equations",
    },
    "REVERSED_DIVISION": {
        "label": "Reversed division",
        "explanation": (
            "You may have divided the coefficient by the constant instead of "
            "dividing the constant by the coefficient."
        ),
        "recommendation": (
            "Practise writing the final step as x = constant divided by "
            "coefficient."
        ),
        "practice_area": "Final division in linear equations",
    },
    "DISTRIBUTIVE_ERROR": {
        "label": "Distributive law error",
        "explanation": (
            "You may have multiplied only the x term and not every term inside "
            "the brackets."
        ),
        "recommendation": (
            "Practise expanding brackets and checking that every inside term "
            "is multiplied."
        ),
        "practice_area": "Expanding brackets",
    },
    "COMBINING_UNLIKE_TERMS": {
        "label": "Combining unlike terms",
        "explanation": (
            "You may have combined x terms and constants even though they are "
            "not like terms."
        ),
        "recommendation": (
            "Practise simplifying expressions by grouping only like terms."
        ),
        "practice_area": "Simplifying expressions",
    },
    "ARITHMETIC_ERROR": {
        "label": "Arithmetic error",
        "explanation": (
            "Your method may be close, but a final addition, subtraction, "
            "multiplication, or division appears to be incorrect."
        ),
        "recommendation": (
            "Practise checking the final calculation by substituting the value "
            "back into the original equation."
        ),
        "practice_area": "Checking solutions by substitution",
    },
    "GRADIENT_RUN_OVER_RISE": {
        "label": "Gradient formula reversed",
        "explanation": (
            "You may have used run over rise instead of rise over run when "
            "calculating the gradient between two points."
        ),
        "recommendation": (
            "Practise using gradient = change in y divided by change in x."
        ),
        "practice_area": "Coordinate geometry gradients",
    },
    "MIDPOINT_ONE_COORDINATE": {
        "label": "Incomplete midpoint averaging",
        "explanation": (
            "You may have averaged one coordinate correctly but not the other."
        ),
        "recommendation": (
            "Practise applying the midpoint formula to x-values and y-values separately."
        ),
        "practice_area": "Coordinate geometry midpoints",
    },
    "DISTANCE_MISSING_SQUARE_ROOT": {
        "label": "Missing square root in distance formula",
        "explanation": (
            "You may have added the squared changes but forgotten the final square root."
        ),
        "recommendation": (
            "Practise the full distance formula: square, add, then take the square root."
        ),
        "practice_area": "Coordinate geometry distance",
    },
    "GRAPH_INTERCEPT_CONFUSION": {
        "label": "Gradient and intercept confusion",
        "explanation": (
            "You may have confused the gradient with an intercept when reading "
            "a function equation."
        ),
        "recommendation": (
            "Practise identifying m and c in y = mx + c and reading graph features separately."
        ),
        "practice_area": "Function graph features",
    },
}


def _is_close(left, right, tolerance=1e-9):
    return abs(float(left) - float(right)) <= tolerance


def _numeric_values(answer):
    """Return numeric values from a student or correct-answer payload."""
    if answer is None:
        return []

    if isinstance(answer, (list, tuple, set)):
        values = []
        for item in answer:
            try:
                values.append(float(item))
            except (TypeError, ValueError):
                parsed = _extract_numeric_answer(str(item))
                if parsed is not None:
                    values.append(parsed)
        return sorted(values)

    text = str(answer or "").strip()
    if not text:
        return []

    cleaned = text.replace("{", "").replace("}", "")
    cleaned = cleaned.replace("[", "").replace("]", "")
    cleaned = re.sub(r"\b(?:or|and)\b", ",", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.replace(";", ",")

    values = []
    for part in [part.strip() for part in cleaned.split(",") if part.strip()]:
        parsed = _extract_numeric_answer(part)
        if parsed is None:
            return []
        if not any(_is_close(parsed, existing) for existing in values):
            values.append(parsed)

    if not values:
        parsed = _extract_numeric_answer(cleaned)
        if parsed is not None:
            values.append(parsed)

    return sorted(values)


def _linear_reduction(question):
    """Return a and b for an equation reducible to ax = b."""
    try:
        expr = simplify(_equation_to_expression(question))
        poly = Poly(expr, x)
    except Exception:
        return None

    if poly.degree() != 1:
        return None

    a_value = float(poly.nth(1))
    constant = float(poly.nth(0))
    if _is_close(a_value, 0):
        return None

    return {
        "coefficient": a_value,
        "constant_side": -constant,
        "solution": -constant / a_value,
    }


def _equation_solution_values(equation):
    """Solve a single-variable equation into sorted numeric real values."""
    try:
        from sympy import solve

        solutions = solve(_equation_to_expression(equation), x)
    except Exception:
        return []

    values = []
    for solution in solutions:
        try:
            numeric = float(simplify(solution))
        except (TypeError, ValueError):
            continue
        if not any(_is_close(numeric, existing) for existing in values):
            values.append(numeric)
    return sorted(values)


def _student_matches_equation(student_values, equation):
    values = _equation_solution_values(equation)
    return (
        len(values) == len(student_values)
        and all(_is_close(left, right) for left, right in zip(values, student_values))
    )


def _wrong_distributive_equations(question):
    """Yield equations created by the common mistake a(x+b) -> ax+b."""
    text = str(question or "")
    if "=" not in text:
        return []

    pattern = re.compile(
        r"(?P<mult>[+-]?\d+)\s*\(\s*x\s*(?P<sign>[+-])\s*(?P<const>\d+)\s*\)"
    )
    equations = []

    for match in pattern.finditer(text):
        multiplier = int(match.group("mult"))
        sign = match.group("sign")
        constant = int(match.group("const"))
        signed_constant = constant if sign == "+" else -constant

        wrong_replacement = (
            f"{multiplier}x"
            f" + {signed_constant}" if signed_constant >= 0
            else f"{multiplier}x - {abs(signed_constant)}"
        )
        equations.append(
            text[:match.start()]
            + wrong_replacement
            + text[match.end():]
        )

    return equations


def _linear_expression_parts(expression_text):
    """Return x coefficient and constant for a linear expression."""
    try:
        expr = simplify(parse_math_expression(expression_text))
        poly = Poly(expr, x)
    except Exception:
        return None

    if poly.degree() > 1:
        return None

    return {
        "x_coefficient": float(poly.nth(1)),
        "constant": float(poly.nth(0)),
    }


def _detect_combining_unlike_terms(student_answer, correct_answer):
    student_parts = _linear_expression_parts(student_answer)
    correct_parts = _linear_expression_parts(correct_answer)

    if not student_parts or not correct_parts:
        return False

    correct_x = correct_parts["x_coefficient"]
    correct_constant = correct_parts["constant"]
    student_x = student_parts["x_coefficient"]
    student_constant = student_parts["constant"]

    if _is_close(correct_constant, 0):
        return False

    if _is_close(student_constant, 0) and _is_close(
        student_x,
        correct_x + correct_constant,
    ):
        return True

    if _is_close(student_x, 0) and _is_close(
        student_constant,
        correct_x + correct_constant,
    ):
        return True

    return False


def _build_result(misconception_id):
    data = MISCONCEPTIONS[misconception_id]
    return {
        "id": misconception_id,
        "label": data["label"],
        "explanation": data["explanation"],
        "recommendation": data["recommendation"],
        "practice_area": data["practice_area"],
    }


def get_misconception_definition(misconception_id, count=None):
    """Return display metadata for a misconception id."""
    if misconception_id not in MISCONCEPTIONS:
        return None

    result = _build_result(misconception_id)
    if count is not None:
        result["count"] = int(count)
    return result


def ranked_misconceptions(counts):
    """Return misconception metadata sorted by frequency."""
    items = []
    for misconception_id, count in (counts or {}).items():
        result = get_misconception_definition(misconception_id, count=count)
        if result is not None:
            items.append(result)

    return sorted(items, key=lambda item: (-item["count"], item["label"]))


def targeted_recommendations(counts, threshold=2):
    """Return practice recommendations for repeated misconceptions."""
    return [
        item
        for item in ranked_misconceptions(counts)
        if item["count"] >= threshold
    ]


def detect_misconception(question, student_answer, correct_answer, working_steps=None):
    """Detect a clear algebra misconception from an incorrect answer.

    This is deliberately rule-based. It returns None when the evidence is not
    strong enough for a useful diagnosis.
    """
    student_values = _numeric_values(student_answer)
    correct_values = _numeric_values(correct_answer)

    if len(student_values) == 1 and len(correct_values) == 1:
        student_value = student_values[0]
        correct_value = correct_values[0]
        reduction = _linear_reduction(question)

        if not _is_close(correct_value, 0) and _is_close(student_value, -correct_value):
            return _build_result("SIGN_ERROR")

        if reduction is not None:
            coefficient = reduction["coefficient"]
            constant_side = reduction["constant_side"]

            if not _is_close(coefficient, 1) and _is_close(student_value, constant_side):
                return _build_result("FORGOT_TO_DIVIDE")

            if not _is_close(constant_side, 0) and _is_close(
                student_value,
                coefficient / constant_side,
            ):
                return _build_result("REVERSED_DIVISION")

        for wrong_equation in _wrong_distributive_equations(question):
            if _student_matches_equation(student_values, wrong_equation):
                return _build_result("DISTRIBUTIVE_ERROR")

        if abs(student_value - correct_value) <= 1 and not _is_close(
            student_value,
            correct_value,
        ):
            return _build_result("ARITHMETIC_ERROR")

    if _detect_combining_unlike_terms(student_answer, correct_answer):
        return _build_result("COMBINING_UNLIKE_TERMS")

    for step in working_steps or []:
        if _detect_combining_unlike_terms(step, correct_answer):
            return _build_result("COMBINING_UNLIKE_TERMS")

    return None
