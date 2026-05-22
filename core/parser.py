"""Parsing and symbolic-normalisation helpers for mathematical input."""

from sympy import simplify, symbols
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

x, y = symbols("x y")

PARSE_LOCALS = {"x": x, "y": y}
TRANSFORMATIONS = standard_transformations + (
    convert_xor,
    implicit_multiplication_application,
)


def parse_math_expression(expr_str):
    """Parse a user-provided mathematical expression into a SymPy object."""
    expression = (expr_str or "").strip()
    if not expression:
        raise ValueError("Empty expression.")

    return parse_expr(
        expression,
        local_dict=PARSE_LOCALS,
        transformations=TRANSFORMATIONS,
    )


def _equation_to_expression(eq_str):
    """Convert an equation string into a single expression equal to zero."""
    if (eq_str or "").count("=") != 1:
        raise ValueError("Equation must contain exactly one '=' sign.")

    left, right = eq_str.split("=", 1)
    return simplify(
        parse_math_expression(left)
        - parse_math_expression(right)
    )


def _extract_numeric_answer(answer):
    """Parse a raw answer string and return its numeric value when valid."""
    text = str(answer or "").strip()
    if not text:
        return None

    if "=" in text:
        text = text.split("=", 1)[1].strip()

    try:
        parsed = simplify(parse_math_expression(text))
    except Exception:
        return None

    if getattr(parsed, "free_symbols", set()):
        return None

    return float(parsed)


def normalise_expression(expr_str):
    """Normalise an expression for symbolic comparison."""
    return simplify(parse_math_expression(expr_str))


def normalise_equation(eq_str):
    """Normalise an equation by moving both sides into one expression."""
    return _equation_to_expression(eq_str)
