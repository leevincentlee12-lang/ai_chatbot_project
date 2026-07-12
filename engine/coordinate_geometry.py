"""Coordinate geometry helpers for point, line, and distance questions."""

import re

from sympy import sqrt, simplify

from core.parser import parse_math_expression
from utils.formatting import _build_explanation, _format_expression, _format_value


POINT_PATTERN = re.compile(r"\(\s*([^,()]+)\s*,\s*([^()]+?)\s*\)")
COORDINATE_PARSE_ERROR = (
    "Enter two points in coordinate form, such as (2, 3) and (6, 11)."
)


def _parse_coordinate_value(value):
    """Parse one coordinate value into a simplified SymPy expression."""
    parsed = simplify(parse_math_expression(str(value).strip()))
    if getattr(parsed, "free_symbols", set()):
        raise ValueError(COORDINATE_PARSE_ERROR)
    return parsed


def extract_points(text):
    """Extract coordinate pairs from text."""
    points = []
    for x_value, y_value in POINT_PATTERN.findall(str(text or "")):
        points.append((
            _parse_coordinate_value(x_value),
            _parse_coordinate_value(y_value),
        ))
    return points


def _format_point(point):
    return f"({_format_value(point[0])}, {_format_value(point[1])})"


def midpoint_between_points(point_a, point_b):
    """Return the midpoint between two points."""
    return (
        simplify((point_a[0] + point_b[0]) / 2),
        simplify((point_a[1] + point_b[1]) / 2),
    )


def gradient_between_points(point_a, point_b):
    """Return the gradient between two points, or None for a vertical line."""
    dx = simplify(point_b[0] - point_a[0])
    if dx == 0:
        return None
    return simplify((point_b[1] - point_a[1]) / dx)


def distance_between_points(point_a, point_b):
    """Return the exact distance between two points."""
    dx = simplify(point_b[0] - point_a[0])
    dy = simplify(point_b[1] - point_a[1])
    return simplify(sqrt(dx**2 + dy**2))


def equation_of_line_through_points(point_a, point_b):
    """Return the equation of the line through two points."""
    gradient = gradient_between_points(point_a, point_b)
    if gradient is None:
        return f"x = {_format_value(point_a[0])}"

    if gradient == 0:
        return f"y = {_format_value(point_a[1])}"

    intercept = simplify(point_a[1] - gradient * point_a[0])
    gradient_text = _format_expression(gradient)

    if gradient == 1:
        x_term = "x"
    elif gradient == -1:
        x_term = "-x"
    elif "/" in gradient_text:
        x_term = f"({gradient_text})x"
    else:
        x_term = f"{gradient_text}x"

    if intercept == 0:
        return f"y = {x_term}"
    if intercept > 0:
        return f"y = {x_term} + {_format_value(intercept)}"
    return f"y = {x_term} - {_format_value(abs(intercept))}"


def _operation_from_question(question):
    lowered = str(question or "").lower()
    if (
        "equation of" in lowered
        or "equation for" in lowered
        or "line through" in lowered
        or "line passing" in lowered
        or "straight line" in lowered
    ):
        return "line"
    if "midpoint" in lowered or "middle point" in lowered:
        return "midpoint"
    if "distance" in lowered or "length" in lowered:
        return "distance"
    if "gradient" in lowered or "slope" in lowered:
        return "gradient"
    return None


def _two_points_from_question(question):
    points = extract_points(question)
    if len(points) < 2:
        raise ValueError(COORDINATE_PARSE_ERROR)
    return points[0], points[1]


def _handle_midpoint(question):
    point_a, point_b = _two_points_from_question(question)
    midpoint = midpoint_between_points(point_a, point_b)
    return _build_explanation(
        answer=f"The midpoint is {_format_point(midpoint)}.",
        method=(
            "Use the midpoint formula:\n"
            f"x-coordinate = ({_format_value(point_a[0])} + {_format_value(point_b[0])}) / 2\n"
            f"y-coordinate = ({_format_value(point_a[1])} + {_format_value(point_b[1])}) / 2"
        ),
        why="The midpoint averages the x-values and the y-values separately.",
        check=(
            f"The point {_format_point(midpoint)} is halfway from "
            f"{_format_point(point_a)} to {_format_point(point_b)}."
        ),
        next_step="Try finding the gradient between the same two points.",
    )


def _handle_gradient(question):
    point_a, point_b = _two_points_from_question(question)
    gradient = gradient_between_points(point_a, point_b)
    if gradient is None:
        return _build_explanation(
            answer="The gradient is undefined.",
            method="Both points have the same x-coordinate, so the line is vertical.",
            why="Gradient is rise divided by run. A vertical line has run = 0, so division by zero is undefined.",
            check=f"The line through {_format_point(point_a)} and {_format_point(point_b)} is x = {_format_value(point_a[0])}.",
            next_step="Try two points with different x-coordinates to calculate a numerical gradient.",
        )

    return _build_explanation(
        answer=f"The gradient is {_format_expression(gradient)}.",
        method=(
            "Use gradient = change in y / change in x:\n"
            f"({_format_value(point_b[1])} - {_format_value(point_a[1])}) / "
            f"({_format_value(point_b[0])} - {_format_value(point_a[0])}) = "
            f"{_format_expression(gradient)}"
        ),
        why="Gradient measures how much y changes for each 1-unit increase in x.",
        check=(
            f"From {_format_point(point_a)} to {_format_point(point_b)}, "
            "the rise and run have the same ratio as the gradient."
        ),
        next_step="Use this gradient to form the equation of the line.",
    )


def _handle_distance(question):
    point_a, point_b = _two_points_from_question(question)
    distance = distance_between_points(point_a, point_b)
    return _build_explanation(
        answer=f"The distance is {_format_expression(distance)}.",
        method=(
            "Use the distance formula:\n"
            f"sqrt(({_format_value(point_b[0])} - {_format_value(point_a[0])})^2 + "
            f"({_format_value(point_b[1])} - {_format_value(point_a[1])})^2)"
        ),
        why="The distance formula comes from Pythagoras' theorem on the horizontal and vertical changes.",
        check=f"The distance between {_format_point(point_a)} and {_format_point(point_b)} must be positive.",
        next_step="Try finding the midpoint to locate the halfway point on the same segment.",
    )


def _handle_line_equation(question):
    point_a, point_b = _two_points_from_question(question)
    gradient = gradient_between_points(point_a, point_b)
    equation = equation_of_line_through_points(point_a, point_b)

    if gradient is None:
        method = (
            "Both points share the same x-coordinate, so every point on the "
            f"line has x = {_format_value(point_a[0])}."
        )
    else:
        method = (
            f"1. Find the gradient: m = {_format_expression(gradient)}.\n"
            f"2. Substitute {_format_point(point_a)} into y = mx + c.\n"
            "3. Solve for c, then write the line in y = mx + c form."
        )

    return _build_explanation(
        answer=equation,
        method=method,
        why="Two different points determine exactly one straight line.",
        check=(
            f"Substitute {_format_point(point_a)} and {_format_point(point_b)} "
            "into the equation to confirm both points lie on the line."
        ),
        next_step="Graph the line and check that it passes through both points.",
    )


def handle_coordinate_geometry(question):
    """Handle supported coordinate-geometry requests."""
    operation = _operation_from_question(question)
    if operation is None:
        return _build_explanation(
            answer="I can handle midpoint, gradient, distance, and line-equation questions from two points.",
            method="Write two points like (2, 3) and (6, 11), then ask for the calculation you need.",
            next_step="Try: find the equation of the line through (2, 3) and (6, 11).",
        )

    try:
        if operation == "midpoint":
            return _handle_midpoint(question)
        if operation == "gradient":
            return _handle_gradient(question)
        if operation == "distance":
            return _handle_distance(question)
        return _handle_line_equation(question)
    except ValueError as error:
        return str(error)
