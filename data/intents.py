"""Intent metadata used by core.classifier."""

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class IntentDefinition:
    """Metadata and matching signals for one supported user intent."""

    name: str
    patterns: Tuple[str, ...]
    keywords: Tuple[str, ...]
    topic: str
    engine: str
    difficulty: int
    examples: Tuple[str, ...]


INTENTS: Dict[str, IntentDefinition] = {
    "linear_equation": IntentDefinition(
        name="linear_equation",
        patterns=(
            r"\bsolve\b.*(?:\d*\s*x|x\s*[+\-=])",
            r"\bfind\s+x\b.*=",
            r"\bwhat\s+is\s+x\b.*=",
            r"(?<![a-z])\d*\s*x\s*[+\-]\s*\d+\s*=",
        ),
        keywords=("solve", "linear", "equation", "find x", "x"),
        topic="Linear Equations",
        engine="math",
        difficulty=1,
        examples=(
            "solve 2x + 3 = 7",
            "find x in 4x - 9 = 3",
            "what is x if 3x = 12",
        ),
    ),
    "quadratic_equation": IntentDefinition(
        name="quadratic_equation",
        patterns=(
            r"\bx\^?2\b",
            r"\bx\s*squared\b",
            r"\bquadratic\b",
            r"\broots?\b.*\bx\b",
        ),
        keywords=("quadratic", "x^2", "squared", "roots", "parabola"),
        topic="Quadratic Equations",
        engine="math",
        difficulty=3,
        examples=(
            "solve x^2 + 5x + 6 = 0",
            "find the roots of x^2 + 5x + 6",
            "solve the quadratic x^2 - 9 = 0",
        ),
    ),
    "explain_discriminant": IntentDefinition(
        name="explain_discriminant",
        patterns=(
            r"\b(?:explain|find|calculate|work\s+out|what\s+is)\b.*\bdiscriminant\b",
            r"\bdiscriminant\b.*(?:x\^?2|quadratic)",
            r"\bdiscriminant\b.*=",
        ),
        keywords=("discriminant", "quadratic", "x^2", "roots", "explain"),
        topic="Quadratic Equations",
        engine="math",
        difficulty=3,
        examples=(
            "explain the discriminant in x^2 - 4x + 3 = 0",
            "find the discriminant of x^2 + 5x + 6 = 0",
            "what is the discriminant of this quadratic",
        ),
    ),
    "factoring": IntentDefinition(
        name="factoring",
        patterns=(
            r"\bfactor(?:ise|ize)?\b",
            r"\bput\b.*\bbrackets\b",
            r"\bwrite\b.*\bas\s+brackets\b",
        ),
        keywords=("factor", "factorise", "factorize", "brackets"),
        topic="Factoring",
        engine="math",
        difficulty=2,
        examples=(
            "factor x^2 + 5x + 6",
            "put x squared plus 5x plus 6 into brackets",
            "factor x^2 - 9",
        ),
    ),
    "expand_expression": IntentDefinition(
        name="expand_expression",
        patterns=(
            r"\bexpand\b",
            r"\bmultiply\s+out\b",
            r"\bremove\s+brackets\b",
        ),
        keywords=("expand", "multiply out", "brackets", "expression"),
        topic="Algebraic Expressions",
        engine="math",
        difficulty=2,
        examples=(
            "expand (x+2)(x+3)",
            "multiply out 2(x + 5)",
            "remove brackets from (x - 3)(x + 4)",
        ),
    ),
    "simplify": IntentDefinition(
        name="simplify",
        patterns=(
            r"\bsimplify\b",
            r"\bcollect\s+like\s+terms\b",
            r"\bcombine\s+like\s+terms\b",
        ),
        keywords=("simplify", "collect", "combine", "like terms"),
        topic="Algebraic Expressions",
        engine="math",
        difficulty=1,
        examples=(
            "simplify 2x + 3x - 4",
            "collect like terms in 5x - 2 + 3x",
            "simplify x + x + 7",
        ),
    ),
    "ratio": IntentDefinition(
        name="ratio",
        patterns=(
            r"\bratio\b",
            r"-?\d+\s*:\s*-?\d+",
            r"\bsimplify\b.*-?\d+\s*:\s*-?\d+",
        ),
        keywords=("ratio", "simplify ratio", ":"),
        topic="Ratios",
        engine="math",
        difficulty=1,
        examples=(
            "simplify the ratio 6:9",
            "reduce 12:18",
            "what is 10:15 in simplest form",
        ),
    ),
    "simultaneous_equations": IntentDefinition(
        name="simultaneous_equations",
        patterns=(
            r"\bsimultaneous\b",
            r"\bsystem\s+of\s+equations\b",
            r"=.*\band\b.*=",
        ),
        keywords=("simultaneous", "system", "elimination", "substitution", "x", "y"),
        topic="Simultaneous Equations",
        engine="math",
        difficulty=3,
        examples=(
            "solve x+y=5 and x-y=1",
            "solve simultaneous equations x + y = 7 and x - y = 1",
            "use elimination for 2x + y = 11 and x - y = 1",
        ),
    ),
    "linear_graph_form": IntentDefinition(
        name="linear_graph_form",
        patterns=(
            r"\by\s*=\s*m\s*x\s*[+\-]\s*c\b",
            r"\by\s*=\s*mx\s*[+\-]\s*c\b",
            r"\bmx\s*[+\-]\s*c\b",
        ),
        keywords=("linear graph", "straight line", "gradient", "intercept", "mx"),
        topic="Linear Graphs",
        engine="math",
        difficulty=2,
        examples=(
            "explain y = mx + c",
            "what does y = mx + c mean",
            "explain the straight line equation y = mx + c",
        ),
    ),
    "function_graph": IntentDefinition(
        name="function_graph",
        patterns=(
            r"\b(?:graph|plot|sketch|draw|explain|interpret)\b.*\by\s*=",
            r"\by\s*=.*\b(?:graph|plot|sketch|draw|explain|interpret)\b",
            r"\bf\(x\)\s*=",
        ),
        keywords=("graph", "function", "linear graph", "parabola", "intercepts", "vertex"),
        topic="Functions and Graphs",
        engine="math",
        difficulty=3,
        examples=(
            "explain the graph of y = 2x + 3",
            "graph y = x^2 - 4x + 3",
            "interpret the parabola y = x^2 - 5x + 6",
        ),
    ),
    "coordinate_geometry": IntentDefinition(
        name="coordinate_geometry",
        patterns=(
            r"\b(?:midpoint|distance|gradient|slope)\b.*\([^,()]+,\s*[^()]+\)",
            r"\bequation\s+of\s+(?:the\s+)?line\b.*\([^,()]+,\s*[^()]+\)",
            r"\bline\s+(?:through|passing)\b.*\([^,()]+,\s*[^()]+\)",
        ),
        keywords=(
            "coordinate",
            "midpoint",
            "distance",
            "gradient",
            "slope",
            "equation of line",
            "line through",
        ),
        topic="Coordinate Geometry",
        engine="math",
        difficulty=3,
        examples=(
            "find the midpoint of (2, 3) and (6, 11)",
            "find the gradient between (2, 3) and (6, 11)",
            "find the equation of the line through (2, 3) and (6, 11)",
        ),
    ),
    "gradient": IntentDefinition(
        name="gradient",
        patterns=(
            r"\bgradient\b",
            r"\bslope\b",
            r"\brate\s+of\s+change\b",
            r"\by\s*=\s*[+-]?\d*\.?\d*\s*x",
        ),
        keywords=("gradient", "slope", "rate of change", "linear graph"),
        topic="Linear Graphs",
        engine="math",
        difficulty=2,
        examples=(
            "what is the gradient of y = 4x - 7",
            "find the slope of y = -3x + 5",
            "what is the rate of change in y = 2x + 1",
        ),
    ),
    "lesson": IntentDefinition(
        name="lesson",
        patterns=(
            r"\bteach\s+me\b",
            r"\blesson\b",
            r"\blearn\b",
            r"\brevise\b",
        ),
        keywords=("teach", "lesson", "learn", "revise", "study"),
        topic="Lesson",
        engine="lesson",
        difficulty=0,
        examples=(
            "teach me algebra",
            "lesson on quadratics",
            "learn trigonometry",
        ),
    ),
    "show_working": IntentDefinition(
        name="show_working",
        patterns=(
            r"\bshow\b.*\bworking\b",
            r"\bfull\s+working\b",
            r"\bstep[- ]by[- ]step\b",
            r"\bshow\b.*\bsteps\b",
        ),
        keywords=("show working", "full working", "step by step", "steps"),
        topic="Worked Solution",
        engine="math",
        difficulty=0,
        examples=(
            "show the full working for 2x + 4 = 10",
            "solve this step by step",
            "show steps for x^2 - 9 = 0",
        ),
    ),
    "hint": IntentDefinition(
        name="hint",
        patterns=(
            r"\bhint\b",
            r"\bgive\s+me\s+a\s+hint\b",
            r"\bjust\s+a\s+hint\b",
        ),
        keywords=("hint", "clue", "nudge"),
        topic="Hint",
        engine="math",
        difficulty=0,
        examples=(
            "give me a hint for 2x + 4 = 10",
            "just a hint",
            "hint for factoring x^2 - 9",
        ),
    ),
    "check_answer": IntentDefinition(
        name="check_answer",
        patterns=(
            r"\bcheck\b.*\banswer\b",
            r"\bmy\s+answer\b",
            r"\bis\s+this\s+correct\b",
        ),
        keywords=("check", "answer", "correct", "mark"),
        topic="Answer Checking",
        engine="math",
        difficulty=0,
        examples=(
            "check my answer for 2x + 4 = 10",
            "is this correct x = 3",
            "mark my answer",
        ),
    ),
    "generate_problem": IntentDefinition(
        name="generate_problem",
        patterns=(
            r"\bpractice\b.*\bproblem\b",
            r"\bgive\s+me\b.*\bproblem\b",
            r"\banother\s+(?:question|problem)\b",
        ),
        keywords=("practice", "problem", "question", "another"),
        topic="Practice",
        engine="math",
        difficulty=0,
        examples=(
            "give me a practice problem",
            "another question like this",
            "give me a harder equation",
        ),
    ),
    "explain": IntentDefinition(
        name="explain",
        patterns=(
            r"\bexplain\b",
            r"\bwhy\b",
            r"\bhow\s+does\b",
            r"\bwhat\s+is\b",
        ),
        keywords=("explain", "why", "how", "what is", "meaning"),
        topic="Explanation",
        engine="fallback",
        difficulty=0,
        examples=(
            "explain the discriminant",
            "why does this step work",
            "what is a variable",
        ),
    ),
}

INTENT_PATTERNS = {
    name: list(definition.patterns)
    for name, definition in INTENTS.items()
}
TRAINING_EXAMPLES = [
    (example, name)
    for name, definition in INTENTS.items()
    for example in definition.examples
]
