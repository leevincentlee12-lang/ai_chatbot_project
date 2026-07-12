"""Public facade for math tutoring behavior.

Implementation is split by responsibility:
- algebra_solver: symbolic solving and factoring
- math_answer_checker: answer evaluation and diagnostics
- math_practice: guided practice sessions
- math_modes: direct / step-by-step / hint algebra responses
- math_workflows: general math chat workflows
"""

from engine.coordinate_geometry import (
    distance_between_points,
    equation_of_line_through_points,
    extract_points,
    gradient_between_points,
    handle_coordinate_geometry,
    midpoint_between_points,
)
from engine.algebra_solver import (
    _parse_linear_equation,
    factor_expression,
    solve_linear,
    solve_quadratic,
    solve_simultaneous,
    solve_value,
    solve_values,
    sympy_solve_equation,
)
from engine.graph_engine import graph_function_data, graph_function_interpretation
from engine.math_answer_checker import (
    _diagnose_linear_answer,
    evaluate_answer,
    evaluate_answer_details,
)
from engine.math_modes import (
    _answer_expand_question,
    _answer_factor_question,
    _answer_gradient_question,
    _answer_linear_question,
    _answer_quadratic_question,
    _answer_ratio_question,
    _answer_simplify_question,
    _answer_simultaneous_question,
    _answer_symbolic_equation,
    _answer_trig_question,
    _extract_gradient,
    _is_gradient_question,
    _ratio_parts,
    answer_experiment_algebra_question,
)
from engine.math_practice import guided_response, start_guided_problem
from engine.math_workflows import MATH_INTENTS, classify_math_request, handle_math


__all__ = [
    "_answer_expand_question",
    "_answer_factor_question",
    "_answer_gradient_question",
    "_answer_linear_question",
    "_answer_quadratic_question",
    "_answer_ratio_question",
    "_answer_simplify_question",
    "_answer_simultaneous_question",
    "_answer_symbolic_equation",
    "_answer_trig_question",
    "_diagnose_linear_answer",
    "_extract_gradient",
    "_is_gradient_question",
    "_parse_linear_equation",
    "_ratio_parts",
    "answer_experiment_algebra_question",
    "distance_between_points",
    "equation_of_line_through_points",
    "evaluate_answer",
    "evaluate_answer_details",
    "extract_points",
    "factor_expression",
    "classify_math_request",
    "gradient_between_points",
    "guided_response",
    "graph_function_data",
    "graph_function_interpretation",
    "handle_coordinate_geometry",
    "handle_math",
    "MATH_INTENTS",
    "midpoint_between_points",
    "solve_linear",
    "solve_quadratic",
    "solve_simultaneous",
    "solve_value",
    "solve_values",
    "start_guided_problem",
    "sympy_solve_equation",
]
