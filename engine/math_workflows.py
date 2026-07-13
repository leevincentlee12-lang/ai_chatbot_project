"""General math command workflows and legacy chat-style math handling."""

import random
import re
from dataclasses import dataclass
from typing import Callable, Optional, Tuple

from sympy import Poly, expand, simplify

from core.parser import (
    MATH_PARSE_ERROR_MESSAGE,
    UNSUPPORTED_MATH_OPERATION_MESSAGE,
    _equation_to_expression,
    has_obvious_malformed_math_input,
    parse_math_expression,
    x,
)
from core.progression import (
    append_student_step,
    clear_student_steps,
    generate_adaptive_problem,
    generate_problem,
    generate_problem_for_skill,
    get_difficulty,
    get_student_steps,
)
from core.validator import check_student_answer, generate_hint, validate_steps
from engine.algebra_solver import (
    _parse_linear_equation,
    factor_expression,
    solve_linear,
    solve_quadratic,
    solve_simultaneous,
    sympy_solve_equation,
)
from engine.coordinate_geometry import handle_coordinate_geometry
from engine.graph_engine import graph_function_interpretation
from engine.math_answer_checker import evaluate_answer_details
from engine.lesson_engine import _is_lesson_request, find_lesson_topic, generate_lesson
from engine.math_practice import guided_response, start_guided_problem
from utils.formatting import _build_explanation, _format_expression


@dataclass(frozen=True)
class MathRequestContext:
    """Normalized request data shared by math intent handlers."""

    original: str
    q_lower: str
    user_id: object = None
    lesson_topic: Optional[str] = None


@dataclass(frozen=True)
class MathIntentMatch:
    """Public classification result for math workflow intents."""

    name: str
    confidence: float
    topic: str


Matcher = Callable[[MathRequestContext], bool]
Handler = Callable[[MathRequestContext], Optional[str]]


@dataclass(frozen=True)
class MathIntent:
    """One deterministic math workflow intent and its handler."""

    name: str
    topic: str
    handler: Handler
    patterns: Tuple[str, ...] = ()
    matcher: Optional[Matcher] = None
    confidence: float = 0.95

    def matches(self, context):
        """Return whether this intent should handle the request."""
        if self.matcher is not None:
            return self.matcher(context)
        return any(re.search(pattern, context.q_lower) for pattern in self.patterns)


def _build_context(question, user_id=None):
    """Build normalized request context once for all intent matchers."""
    original = (question or "").strip()
    return MathRequestContext(
        original=original,
        q_lower=original.lower(),
        user_id=user_id,
        lesson_topic=find_lesson_topic(original),
    )


def _contains(text):
    """Create a simple substring matcher for ordered intent definitions."""
    return lambda context: text in context.q_lower


def _starts_with(text):
    """Create a lowercase prefix matcher for ordered intent definitions."""
    return lambda context: context.q_lower.startswith(text)


def _strip_equation_prompt(text):
    """Remove common natural-language wrappers around an equation."""
    cleaned = str(text or "").strip()
    cleaned = re.sub(
        r"(?i)^\s*(?:solve(?:\s+for\s+x)?|find\s+x(?:\s+(?:in|if|when))?|"
        r"what\s+is\s+x(?:\s+(?:if|in|when))?|calculate\s+x(?:\s+(?:if|in|when))?|"
        r"determine\s+x(?:\s+(?:if|in|when))?|work\s+out\s+x(?:\s+(?:if|in|when))?|"
        r"show\s+me|solve:)\s*[:,]?\s*",
        "",
        cleaned,
    )
    return cleaned.strip()


def _handle_lesson_request(context):
    return generate_lesson(context.lesson_topic)["display_text"]


def _handle_full_working(context):
    original = context.original
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
    return None


def _handle_linear_hint(context):
    original = context.original
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

    if "=" in eq and "x" in eq.lower():
        if "/" in eq:
            method = "First clear the fractions by multiplying every term by the lowest common denominator."
            next_step = "After the fractions are removed, collect x terms on one side and constants on the other."
        elif "x^2" in eq.lower():
            method = "Move everything to one side so the equation equals zero, then look for factoring or the quadratic formula."
            next_step = "Check whether the quadratic factorises before using a formula."
        else:
            method = "First simplify both sides, then move x terms to one side and constants to the other."
            next_step = "Keep the same operation on both sides at each step."

        return _build_explanation(
            answer=f"Hint for {eq}",
            method=method,
            why="The goal is to make the equation simpler without changing its solution.",
            next_step=next_step,
        )

    return None


def _handle_harder_problem(context):
    level = min(get_difficulty(context.user_id) + 1, 3)
    problem = generate_problem(level=level, user_id=context.user_id)
    return _build_explanation(
        answer=problem["problem"],
        why="This keeps the same skill area but raises the difficulty slightly.",
        next_step="Solve it and submit your answer in the practice panel.",
    )


def _handle_linear_problem(context):
    problem = generate_problem_for_skill(
        "linear_equations",
        level=2,
        user_id=context.user_id,
    )
    return _build_explanation(
        answer=problem["problem"],
        why="This keeps the practice focused on linear equations.",
        next_step="Solve it in Practice Mode or ask for a hint if you get stuck.",
    )


def _handle_quadratic_problem(context):
    problem = None
    for _ in range(12):
        candidate = generate_problem(level=3, user_id=context.user_id)
        if candidate["skill"] == "quadratics":
            problem = candidate
            break

    if problem is None:
        problem = {
            "problem": random.choice([
                "2x^2 - 7x + 3 = 0",
                "3x^2 + 2x - 8 = 0",
                "4x^2 - 21x + 5 = 0",
            ]),
        }

    return _build_explanation(
        answer=problem["problem"],
        why="This gives you another factorable quadratic rather than repeating the same solved example.",
        next_step="Solve for all real roots, then check both values in the original equation.",
    )


def _handle_similar_problem(context):
    problem = generate_problem(
        level=get_difficulty(context.user_id),
        user_id=context.user_id,
    )
    return _build_explanation(
        answer=problem["problem"],
        why="This keeps you on the same skill without increasing difficulty yet.",
        next_step="Try solving it on your own, then check your answer.",
    )


def _handle_factoring_problem(context):
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


def _handle_discriminant_explanation(context):
    original = context.original
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
    return None


def _handle_expand_expression(context):
    expr = context.original[7:].strip()
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
    return None


def _handle_simplify_expression(context):
    expression = re.sub(
        r"(?i)^.*\bsimplify\b\s*",
        "",
        context.original,
    ).strip()

    if not expression or ":" in expression:
        return None

    if not re.search(r"(?<![a-z])(?:\d*)[xy](?:\^\d+)?\b", expression.lower()):
        return None

    try:
        simplified = simplify(parse_math_expression(expression))
    except Exception:
        return "Provide an algebra equation or expression to work with."

    return _build_explanation(
        answer=_format_expression(simplified),
        method="Identify like terms or algebraic rules, then combine only compatible terms.",
        why="Simplifying preserves the value of the expression while writing it in a cleaner form.",
        check=f"Substitute a value for x into both {expression} and {_format_expression(simplified)}.",
        next_step="Try a similar expression and check that each variable term is combined correctly.",
    )


def _handle_factor_inverse(context):
    return _build_explanation(
        answer="Because factoring and expanding are inverse processes.",
        method="When you expand the brackets term by term, the combined terms rebuild the original expression.",
        why="A correct factorisation must expand exactly to the starting expression.",
        next_step="Ask me to expand the brackets line by line if you want the proof shown.",
    )


def _handle_balance_explanation(context):
    return _build_explanation(
        answer="Each algebra step must preserve the same solution set.",
        method=(
            "When solving an equation, apply the same operation to both sides. "
            "That keeps the two sides balanced while gradually isolating the variable."
        ),
        why=(
            "If you change only one side, the new equation may no longer describe "
            "the same x-value as the original."
        ),
        check="Substitute the final value back into the original equation, not only the last line.",
        next_step="Use the working space in Practice Mode to check each line of your method.",
    )


def _handle_show_steps(context):
    steps = get_student_steps(context.user_id)
    if not steps:
        return "No steps recorded."
    return "\n".join(
        f"Step {index + 1}: {step}"
        for index, step in enumerate(steps)
    )


def _handle_validate_steps(context):
    return validate_steps(get_student_steps(context.user_id))


def _handle_clear_steps(context):
    clear_student_steps(context.user_id)
    return "Steps cleared."


def _handle_record_step(context):
    step_expr = context.original[4:].strip().lower()
    if not step_expr:
        return "No step provided."
    count = append_student_step(step_expr, user_id=context.user_id)
    return f"Step {count} recorded."


def _handle_recorded_step_hint(context):
    steps = get_student_steps(context.user_id)
    if len(steps) >= 2:
        return generate_hint(steps[-2], steps[-1])
    return "Record at least two steps first."


def _handle_check_expressions(context):
    parts = context.original[6:].split(",", 1)
    if len(parts) == 2:
        return check_student_answer(parts[0].strip(), parts[1].strip())
    return "Use: check first_expression, second_expression"


def _handle_check_answer_guidance(context):
    return (
        "Use the practice answer box or type your value like "
        "'answer x = 3' after starting a guided problem."
    )


def _handle_guided_problem(context):
    return start_guided_problem(user_id=context.user_id)


def _handle_guided_answer(context):
    return guided_response(context.original[6:].strip(), user_id=context.user_id)


def _handle_generate_problem(context):
    problem = generate_adaptive_problem(user_id=context.user_id)
    return _build_explanation(
        answer=problem["problem"],
        why=problem.get("adaptive_reason", "This problem matches your current practice profile."),
        next_step="Solve it in Practice Mode or submit your answer for checking.",
    )


def _handle_factor_expression(context):
    expr = re.sub(r"(?i)^factor\s*", "", context.original).strip()
    return factor_expression(expr)


def _handle_linear_graph_form(context):
    return _build_explanation(
        answer=(
            "y = mx + c is the straight-line form. m is the gradient and c is "
            "the y-intercept."
        ),
        method=(
            "1. y is the output value on the vertical axis.\n"
            "2. x is the input value on the horizontal axis.\n"
            "3. m tells you the gradient, or steepness.\n"
            "4. c tells you where the line crosses the y-axis."
        ),
        why="The form is useful because it shows the line's steepness and y-axis crossing directly.",
        check="For y = 2x + 3, the gradient is 2 and the y-intercept is 3.",
        next_step="Try identifying m and c in y = -3x + 5.",
    )


def _matches_graph_function(context):
    has_function_equation = (
        ("y" in context.q_lower or "f(x)" in context.q_lower)
        and "=" in context.q_lower
    )
    graph_cue = any(
        word in context.q_lower
        for word in ("graph", "plot", "sketch", "draw")
    )
    explanation_cue = bool(
        re.search(r"\b(?:explain|interpret|what\s+does)\b", context.q_lower)
    )
    return has_function_equation and (graph_cue or explanation_cue)


def _handle_graph_function(context):
    try:
        return graph_function_interpretation(context.original)
    except ValueError as error:
        return str(error)


def _matches_coordinate_geometry(context):
    has_two_points = len(re.findall(r"\([^,()]+,\s*[^()]+\)", context.original)) >= 2
    has_coordinate_keyword = any(
        keyword in context.q_lower
        for keyword in (
            "coordinate",
            "midpoint",
            "middle point",
            "distance",
            "gradient",
            "slope",
            "equation of",
            "line through",
            "line passing",
            "straight line",
        )
    )
    return has_two_points and has_coordinate_keyword


def _handle_coordinate_geometry(context):
    return handle_coordinate_geometry(context.original)


def _handle_solve_simultaneous(context):
    cleaned = re.sub(
        r"(?i)^\s*(?:solve|find|show me|solve for|solve:)\s*",
        "",
        context.original,
    ).strip()
    parts = re.split(r"(?i)\sand\s", cleaned, maxsplit=1)
    if len(parts) == 2:
        return solve_simultaneous(parts[0].strip(), parts[1].strip())
    return None


def _handle_solve_quadratic(context):
    eq = _strip_equation_prompt(context.original)
    solution = solve_quadratic(eq)
    if solution:
        return solution
    return None


def _handle_solve_linear(context):
    eq = _strip_equation_prompt(context.original)
    linear = solve_linear(eq)
    if linear:
        return linear

    sym_solution = sympy_solve_equation(eq)
    if sym_solution:
        return sym_solution

    return None


def _matches_lesson_request(context):
    return bool(context.lesson_topic and _is_lesson_request(context.original))


def _matches_factor_inverse(context):
    return "multiplies back to" in context.q_lower and "explain why" in context.q_lower


def _matches_generate_problem(context):
    return (
        context.q_lower == "problem"
        or "practice problem" in context.q_lower
        or "another problem" in context.q_lower
        or "another question" in context.q_lower
    )


def _matches_generate_linear_problem(context):
    return (
        "another linear" in context.q_lower
        or "different linear" in context.q_lower
        or "new linear" in context.q_lower
        or "linear equation" in context.q_lower and "another" in context.q_lower
        or "linear equation" in context.q_lower and "different" in context.q_lower
        or "linear equation" in context.q_lower and "new" in context.q_lower
    )


def _matches_generate_quadratic_problem(context):
    return (
        "another quadratic" in context.q_lower
        or "different quadratic" in context.q_lower
        or "new quadratic" in context.q_lower
        or "quadratic" in context.q_lower and "another" in context.q_lower
        or "quadratic" in context.q_lower and "different" in context.q_lower
        or "quadratic" in context.q_lower and "new" in context.q_lower
    )


def _extract_inline_answer_check(text):
    """Extract equation and submitted answer from natural answer-check prompts."""
    original = str(text or "").strip()
    patterns = [
        r"(?i)^\s*(?:question|equation)\s*:\s*(?P<equation>.+?)\s+(?:answer|my answer)\s*:\s*(?P<answer>.+?)\s*$",
        r"(?i)^\s*(?:my\s+answer\s+is|answer\s+is)\s+(?P<answer>.+?)\s+(?:for|to|in)\s+(?P<equation>.+?)\s*$",
        r"(?i)^\s*check\s+my\s+answer\s+(?P<answer>.+?)\s+(?:for|to|in)\s+(?P<equation>.+?)\s*$",
        r"(?i)^\s*check\s+(?:if\s+)?(?P<answer>x\s*=.+?)\s+(?:for|to|in)\s+(?P<equation>.+?)\s*$",
        r"(?i)^\s*is\s+(?P<answer>.+?)\s+correct\s+(?:for|in)\s+(?P<equation>.+?)\s*$",
    ]

    for pattern in patterns:
        match = re.search(pattern, original)
        if not match:
            continue

        equation = match.group("equation").strip(" .?")
        answer = match.group("answer").strip(" .?")
        if equation and answer and "=" in equation:
            return equation, answer

    return None


def _matches_inline_answer_check(context):
    return _extract_inline_answer_check(context.original) is not None


def _matches_solve_simultaneous(context):
    return " and " in context.q_lower and "=" in context.q_lower and "y" in context.q_lower


def _matches_solve_quadratic(context):
    return "=" in context.q_lower and (
        "x^2" in context.q_lower
        or "quadratic" in context.q_lower
    )


def _matches_discriminant_explanation(context):
    return "discriminant" in context.q_lower and (
        "explain" in context.q_lower
        or "find" in context.q_lower
        or "calculate" in context.q_lower
        or "what is" in context.q_lower
    )


def _matches_linear_graph_form(context):
    return bool(
        re.search(r"\by\s*=\s*m\s*x\s*[+\-]\s*c\b", context.q_lower)
        or re.search(r"\by\s*=\s*mx\s*[+\-]\s*c\b", context.q_lower)
        or re.search(r"\bmx\s*[+\-]\s*c\b", context.q_lower)
    )


def _matches_balance_explanation(context):
    return (
        "balanced" in context.q_lower
        and ("equation" in context.q_lower or "step" in context.q_lower)
    ) or "why each step keeps" in context.q_lower


def _handle_inline_answer_check(context):
    extracted = _extract_inline_answer_check(context.original)
    if extracted is None:
        return None

    equation, submitted_answer = extracted
    result = evaluate_answer_details(
        equation,
        submitted_answer,
        user_id=context.user_id,
    )
    return result["details"]


def _matches_solve_linear(context):
    return "=" in context.q_lower and "x" in context.q_lower


MATH_INTENTS = (
    MathIntent(
        name="lesson_request",
        topic="Lesson",
        matcher=_matches_lesson_request,
        handler=_handle_lesson_request,
        confidence=1.0,
    ),
    MathIntent(
        name="show_full_working",
        topic="Worked Solution",
        matcher=_contains("show the full working for"),
        handler=_handle_full_working,
    ),
    MathIntent(
        name="generate_hint",
        topic="Hint",
        matcher=_contains("give me a hint for"),
        handler=_handle_linear_hint,
    ),
    MathIntent(
        name="generate_problem_harder",
        topic="Practice",
        matcher=_contains("give me a harder equation like"),
        handler=_handle_harder_problem,
    ),
    MathIntent(
        name="generate_problem_linear",
        topic="Practice",
        matcher=_matches_generate_linear_problem,
        handler=_handle_linear_problem,
    ),
    MathIntent(
        name="generate_problem_quadratic",
        topic="Practice",
        matcher=_matches_generate_quadratic_problem,
        handler=_handle_quadratic_problem,
    ),
    MathIntent(
        name="generate_problem_similar",
        topic="Practice",
        matcher=_contains("give me a similar problem to"),
        handler=_handle_similar_problem,
    ),
    MathIntent(
        name="generate_problem_factoring",
        topic="Practice",
        matcher=_contains("give me another factoring problem like"),
        handler=_handle_factoring_problem,
    ),
    MathIntent(
        name="explain_discriminant",
        topic="Quadratic Equations",
        matcher=_matches_discriminant_explanation,
        handler=_handle_discriminant_explanation,
    ),
    MathIntent(
        name="linear_graph_form",
        topic="Linear Graphs",
        matcher=_matches_linear_graph_form,
        handler=_handle_linear_graph_form,
    ),
    MathIntent(
        name="graph_function",
        topic="Functions and Graphs",
        matcher=_matches_graph_function,
        handler=_handle_graph_function,
    ),
    MathIntent(
        name="coordinate_geometry",
        topic="Coordinate Geometry",
        matcher=_matches_coordinate_geometry,
        handler=_handle_coordinate_geometry,
    ),
    MathIntent(
        name="expand_expression",
        topic="Algebraic Expressions",
        matcher=_starts_with("expand "),
        handler=_handle_expand_expression,
    ),
    MathIntent(
        name="simplify_expression",
        topic="Algebraic Expressions",
        patterns=(r"\bsimplify\b", r"\bcollect like terms\b", r"\bcombine like terms\b"),
        handler=_handle_simplify_expression,
    ),
    MathIntent(
        name="explain_factor_inverse",
        topic="Factoring",
        matcher=_matches_factor_inverse,
        handler=_handle_factor_inverse,
    ),
    MathIntent(
        name="explain_balance",
        topic="Linear Equations",
        matcher=_matches_balance_explanation,
        handler=_handle_balance_explanation,
    ),
    MathIntent(
        name="show_steps",
        topic="Validation",
        matcher=_contains("show steps"),
        handler=_handle_show_steps,
    ),
    MathIntent(
        name="validate_steps",
        topic="Validation",
        matcher=_contains("validate steps"),
        handler=_handle_validate_steps,
    ),
    MathIntent(
        name="clear_steps",
        topic="Validation",
        matcher=_contains("clear steps"),
        handler=_handle_clear_steps,
    ),
    MathIntent(
        name="record_step",
        topic="Validation",
        matcher=_starts_with("step"),
        handler=_handle_record_step,
    ),
    MathIntent(
        name="generate_hint_from_steps",
        topic="Hint",
        matcher=_contains("hint"),
        handler=_handle_recorded_step_hint,
    ),
    MathIntent(
        name="check_answer_inline",
        topic="Answer Checking",
        matcher=_matches_inline_answer_check,
        handler=_handle_inline_answer_check,
    ),
    MathIntent(
        name="check_answer",
        topic="Answer Checking",
        matcher=_contains("check my answer for"),
        handler=_handle_check_answer_guidance,
    ),
    MathIntent(
        name="check_expressions",
        topic="Answer Checking",
        matcher=_starts_with("check "),
        handler=_handle_check_expressions,
    ),
    MathIntent(
        name="guided_problem",
        topic="Practice",
        matcher=_contains("guided problem"),
        handler=_handle_guided_problem,
    ),
    MathIntent(
        name="guided_answer",
        topic="Practice",
        matcher=_starts_with("answer"),
        handler=_handle_guided_answer,
    ),
    MathIntent(
        name="generate_problem",
        topic="Practice",
        matcher=_matches_generate_problem,
        handler=_handle_generate_problem,
    ),
    MathIntent(
        name="factor_expression",
        topic="Factoring",
        patterns=(r"\bfactor\b", r"\bfactorise\b", r"\bfactorize\b"),
        handler=_handle_factor_expression,
    ),
    MathIntent(
        name="solve_simultaneous",
        topic="Simultaneous Equations",
        matcher=_matches_solve_simultaneous,
        handler=_handle_solve_simultaneous,
    ),
    MathIntent(
        name="solve_quadratic",
        topic="Quadratic Equations",
        matcher=_matches_solve_quadratic,
        handler=_handle_solve_quadratic,
    ),
    MathIntent(
        name="solve_linear",
        topic="Linear Equations",
        matcher=_matches_solve_linear,
        handler=_handle_solve_linear,
    ),
)


def classify_math_request(question):
    """Classify math workflow intent without executing the handler."""
    context = _build_context(question)
    for intent in MATH_INTENTS:
        if intent.matches(context):
            return MathIntentMatch(
                name=intent.name,
                confidence=intent.confidence,
                topic=intent.topic,
            )

    return MathIntentMatch(name="unknown", confidence=0.0, topic="Math")


def handle_math(question, user_id=None):
    """Handle mathematics questions across lessons, solving, and practice workflows."""
    context = _build_context(question, user_id=user_id)

    if has_obvious_malformed_math_input(context.original):
        return MATH_PARSE_ERROR_MESSAGE

    for intent in MATH_INTENTS:
        if not intent.matches(context):
            continue

        response = intent.handler(context)
        if response:
            return response

    return UNSUPPORTED_MATH_OPERATION_MESSAGE
