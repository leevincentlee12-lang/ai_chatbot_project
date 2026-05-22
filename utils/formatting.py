"""Formatting helpers for algebra output, lesson rendering, and tutor messages."""

import math

from sympy import simplify


def _format_expression(expr):
    """Return a simplified symbolic expression in user-facing text form."""
    return str(simplify(expr)).replace("**", "^")


def _format_raw_expression(expr):
    """Return a symbolic expression without re-simplifying its structure."""
    return str(expr).replace("**", "^")


def _format_skill_label(skill_name):
    """Convert an internal skill key into a display label."""
    return skill_name.replace("_", " ").title()


def _format_value(value):
    """Format a numeric or symbolic value for user-facing output."""
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return _format_expression(value)

    if math.isfinite(numeric) and abs(numeric - round(numeric)) < 1e-9:
        return str(int(round(numeric)))

    return f"{numeric:.6g}"


def _section(title, body):
    """Build a titled section when the body contains content."""
    text = str(body or "").strip()
    if not text:
        return None
    return f"{title}\n{text}"


def _bullet_lines(items):
    """Render a list of strings as single-level bullet lines."""
    cleaned = [str(item).strip() for item in items if str(item).strip()]
    return "\n".join(f"- {item}" for item in cleaned)


def _compose_message(*sections):
    """Join non-empty sections into a readable multi-block message."""
    return "\n\n".join(section for section in sections if section)


def _build_explanation(answer, method=None, why=None, check=None, next_step=None):
    """Create a structured tutor explanation with consistent headings."""
    return _compose_message(
        _section("Answer", answer),
        _section("Method", method),
        _section("Why", why),
        _section("Check", check),
        _section("Next Step", next_step),
    )
