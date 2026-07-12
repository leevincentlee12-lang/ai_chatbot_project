"""Supported function graphing helpers for coordinate-geometry visuals."""

import math
import re

from sympy import Poly, solve, simplify

from core.parser import MATH_PARSE_ERROR_MESSAGE, parse_math_expression, x, y
from utils.formatting import _build_explanation, _format_expression, _format_value


GRAPH_PARSE_ERROR = (
    "Enter a supported function such as y = 2x + 3 or y = x^2 - 4x + 3."
)
GRAPH_UNSUPPORTED_ERROR = (
    "Graphing currently supports linear and quadratic functions in x."
)


def _strip_graph_prompt(text):
    """Remove natural-language graphing prefixes from a user prompt."""
    cleaned = str(text or "").strip()
    cleaned = re.sub(
        r"(?i)^\s*(?:graph|plot|sketch|draw|interpret|"
        r"explain\s+the\s+graph\s+of|explain\s+graph\s+of|"
        r"show\s+the\s+graph\s+of|show\s+graph\s+of)\s*",
        "",
        cleaned,
    )
    cleaned = re.sub(r"(?i)^\s*(?:the\s+function|function)\s*", "", cleaned)
    return cleaned.strip()


def _extract_function_expression(text):
    """Return the right-side expression from y = f(x), f(x) = ..., or f(x)."""
    cleaned = _strip_graph_prompt(text)
    if not cleaned:
        raise ValueError(GRAPH_PARSE_ERROR)

    cleaned = cleaned.replace("−", "-")

    if "=" not in cleaned:
        return parse_math_expression(cleaned)

    if cleaned.count("=") != 1:
        raise ValueError(MATH_PARSE_ERROR_MESSAGE)

    left, right = [part.strip() for part in cleaned.split("=", 1)]
    if not left or not right:
        raise ValueError(GRAPH_PARSE_ERROR)

    left_normalized = left.lower().replace(" ", "")
    right_normalized = right.lower().replace(" ", "")

    if left_normalized in {"y", "f(x)"}:
        return parse_math_expression(right)

    if right_normalized in {"y", "f(x)"}:
        return parse_math_expression(left)

    raise ValueError(GRAPH_PARSE_ERROR)


def _safe_float(value):
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None

    return numeric if math.isfinite(numeric) else None


def _sample_points(expr, x_min=-5, x_max=5, steps=40):
    """Sample graph points over a small classroom-friendly x-window."""
    points = []
    for index in range(steps + 1):
        x_value = x_min + (x_max - x_min) * index / steps
        y_value = _safe_float(expr.subs(x, x_value).evalf())
        if y_value is None:
            continue
        points.append({
            "x": round(x_value, 4),
            "y": round(y_value, 4),
        })
    return points


def _padded_bounds(values, default_min=-10, default_max=10):
    if not values:
        return [default_min, default_max]

    lower = min(min(values), 0)
    upper = max(max(values), 0)
    if abs(upper - lower) < 1e-9:
        lower -= 5
        upper += 5

    padding = max(1, (upper - lower) * 0.12)
    return [
        round(lower - padding, 2),
        round(upper + padding, 2),
    ]


def _real_roots(expr):
    roots = []
    for root in solve(expr, x):
        numeric = _safe_float(simplify(root))
        if numeric is None:
            continue
        if not any(abs(numeric - existing) < 1e-9 for existing in roots):
            roots.append(numeric)
    return sorted(roots)


def _linear_features(poly, expr):
    gradient = simplify(poly.nth(1))
    intercept = simplify(poly.nth(0))
    root_values = _real_roots(expr)
    return {
        "gradient": _format_value(gradient),
        "y_intercept": _format_value(intercept),
        "x_intercepts": [_format_value(root) for root in root_values],
        "summary": (
            f"Gradient {_format_value(gradient)} and y-intercept {_format_value(intercept)}."
        ),
    }


def _quadratic_features(poly, expr):
    a_coeff = simplify(poly.nth(2))
    b_coeff = simplify(poly.nth(1))
    c_coeff = simplify(poly.nth(0))
    vertex_x = simplify(-b_coeff / (2 * a_coeff))
    vertex_y = simplify(expr.subs(x, vertex_x))
    discriminant = simplify(b_coeff**2 - 4 * a_coeff * c_coeff)
    root_values = _real_roots(expr)
    a_float = _safe_float(a_coeff)
    direction = "opens upward" if a_float is None or a_float > 0 else "opens downward"
    return {
        "a": _format_value(a_coeff),
        "b": _format_value(b_coeff),
        "c": _format_value(c_coeff),
        "y_intercept": _format_value(c_coeff),
        "x_intercepts": [_format_value(root) for root in root_values],
        "axis_of_symmetry": _format_value(vertex_x),
        "direction": direction,
        "discriminant": _format_value(discriminant),
        "vertex": {
            "x": _format_value(vertex_x),
            "y": _format_value(vertex_y),
        },
        "summary": (
            f"The parabola {direction} with vertex "
            f"({_format_value(vertex_x)}, {_format_value(vertex_y)})."
        ),
    }


def graph_function_data(text):
    """Return JSON-serialisable graph data for a supported function."""
    try:
        expr = simplify(_extract_function_expression(text))
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(GRAPH_PARSE_ERROR) from exc

    if getattr(expr, "free_symbols", set()) - {x}:
        raise ValueError(GRAPH_UNSUPPORTED_ERROR)

    try:
        poly = Poly(expr, x)
    except Exception as exc:
        raise ValueError(GRAPH_UNSUPPORTED_ERROR) from exc

    degree = poly.degree()
    if degree not in {1, 2}:
        raise ValueError(GRAPH_UNSUPPORTED_ERROR)

    points = _sample_points(expr)
    if not points:
        raise ValueError(GRAPH_UNSUPPORTED_ERROR)

    y_values = [point["y"] for point in points]
    kind = "linear" if degree == 1 else "quadratic"
    features = (
        _linear_features(poly, expr)
        if degree == 1
        else _quadratic_features(poly, expr)
    )

    return {
        "kind": kind,
        "input": str(text or "").strip(),
        "equation": f"y = {_format_expression(expr)}",
        "expression": _format_expression(expr),
        "points": points,
        "x_range": [-5, 5],
        "y_range": _padded_bounds(y_values),
        "features": features,
    }


def _format_intercepts(intercepts):
    """Return a readable intercept list for explanation text."""
    if not intercepts:
        return "no real x-intercepts"
    if len(intercepts) == 1:
        return f"x = {intercepts[0]}"
    return "x = " + " or x = ".join(intercepts)


def _linear_interpretation(data):
    """Build a structured explanation for a supported linear graph."""
    features = data["features"]
    gradient = features["gradient"]
    y_intercept = features["y_intercept"]
    x_intercepts = _format_intercepts(features["x_intercepts"])
    x_intercept_phrase = (
        x_intercepts
        if x_intercepts.startswith("no")
        else f"x-intercept is {x_intercepts}"
    )

    return _build_explanation(
        answer=(
            f"{data['equation']} is a linear function. Its gradient is {gradient}, "
            f"its y-intercept is {y_intercept}, and its {x_intercept_phrase}."
        ),
        method=(
            f"1. Start at the y-intercept: (0, {y_intercept}).\n"
            f"2. Use the gradient {gradient} as rise over run to find another point.\n"
            "3. Draw the straight line through those points.\n"
            "4. The x-intercept is where the line crosses y = 0."
        ),
        why=(
            "For y = mx + c, m controls the steepness and direction of the line, "
            "while c controls where the line crosses the y-axis."
        ),
        check=(
            f"Substitute x = 0 into {data['equation']}; the output should be "
            f"{y_intercept}, matching the y-intercept."
        ),
        next_step=(
            "Use the Function Graph Explorer, then compare the plotted line with "
            "the gradient and intercepts above."
        ),
    )


def _quadratic_interpretation(data):
    """Build a structured explanation for a supported quadratic graph."""
    features = data["features"]
    vertex = features["vertex"]
    x_intercepts = _format_intercepts(features["x_intercepts"])
    x_intercept_phrase = (
        x_intercepts
        if x_intercepts.startswith("no")
        else f"x-intercepts are {x_intercepts}"
    )
    root_count = len(features["x_intercepts"])
    if root_count == 2:
        discriminant_meaning = "two real x-intercepts"
    elif root_count == 1:
        discriminant_meaning = "one repeated real x-intercept"
    else:
        discriminant_meaning = "no real x-intercepts"

    return _build_explanation(
        answer=(
            f"{data['equation']} is a quadratic function. The parabola "
            f"{features['direction']}, has vertex ({vertex['x']}, {vertex['y']}), "
            f"axis of symmetry x = {features['axis_of_symmetry']}, y-intercept "
            f"{features['y_intercept']}, and its {x_intercept_phrase}."
        ),
        method=(
            f"1. Write the quadratic as ax^2 + bx + c with a = {features['a']}, "
            f"b = {features['b']}, c = {features['c']}.\n"
            f"2. Find the vertex using x = -b/(2a), giving ({vertex['x']}, {vertex['y']}).\n"
            f"3. Use the axis of symmetry x = {features['axis_of_symmetry']} to mirror points.\n"
            "4. Mark the intercepts and sketch the parabola."
        ),
        why=(
            f"The discriminant is {features['discriminant']}, which gives "
            f"{discriminant_meaning}. The vertex shows the turning point, and "
            "the sign of a decides whether the graph opens upward or downward."
        ),
        check=(
            f"Substitute x = 0 into {data['equation']}; the output should be "
            f"{features['y_intercept']}, matching the y-intercept."
        ),
        next_step=(
            "Compare the equation, vertex, intercepts, and graph in the Function "
            "Graph Explorer."
        ),
    )


def graph_function_interpretation(text):
    """Return an educational explanation for a supported function graph."""
    data = graph_function_data(text)
    if data["kind"] == "linear":
        return _linear_interpretation(data)
    return _quadratic_interpretation(data)
