"""Backward-compatible entry point for the modular tutoring system."""

from core import classifier as _classifier
from core import parser as _parser
from core import progression as _progression
from core import router as _router
from core import validator as _validator
from data import constants as _constants
from engine import english_engine as _english
from engine import fallback_engine as _fallback
from engine import humanities_engine as _humanities
from engine import lesson_engine as _lesson
from engine import math_engine as _math
from engine import science_engine as _science
from utils import formatting as _formatting


HYBRID_MODE = _classifier.HYBRID_MODE
understanding_model = _classifier.understanding_model

_EXPORTS = {
    _classifier: {
        "classify_intent",
        "classify_algebra_intent",
        "classify_subject",
        "detect_intent",
        "detect_topic",
        "find_lesson_topic",
        "_detect_experiment_topic",
        "_detect_mode_from_text",
        "_is_algebra_question",
        "_normalise_mode_label",
        "_resolve_experiment_mode",
        "_strip_mode_instruction",
    },
    _parser: {
        "PARSE_LOCALS",
        "TRANSFORMATIONS",
        "x",
        "y",
        "parse_math_expression",
        "normalise_expression",
        "normalise_equation",
        "_equation_to_expression",
        "_extract_numeric_answer",
    },
    _progression: {
        "student_stats",
        "student_profile",
        "student_steps",
        "guided_sessions",
        "detect_math_skill",
        "adjust_skill",
        "append_student_step",
        "clear_guided_session",
        "clear_student_steps",
        "generate_adaptive_problem",
        "generate_problem",
        "get_difficulty",
        "get_guided_session",
        "get_learning_state",
        "get_mistake_history",
        "get_recent_questions",
        "get_or_create_skill",
        "get_student_profile",
        "get_student_skills",
        "get_student_steps",
        "get_student_stats",
        "record_mistake",
        "record_correct_answer",
        "record_lesson_completed",
        "record_problem_attempt",
        "record_question",
        "record_question_asked",
        "set_current_topic",
        "set_guided_session",
        "update_last_question_time",
        "update_progression",
        "update_skill",
        "_clamp_score",
    },
    _router: {
        "academic_engine",
        "get_followups",
    },
    _validator: {
        "check_student_answer",
        "classify_transformation",
        "diagnose_error",
        "equations_equivalent",
        "expressions_equivalent",
        "generate_hint",
        "step_complexity",
        "validate_steps",
    },
    _constants: {
        "EXPERIMENT_MODE_PROMPT",
        "EXPERIMENT_RESTRICTED_MESSAGE",
        "FOLLOWUPS_BY_SUBJECT",
        "FOLLOWUPS_BY_TOPIC",
        "LESSON_CATALOG",
        "SUBJECT_KEYWORDS",
        "TOPIC_BY_SUBJECT",
    },
    _english: {
        "generate_teel",
        "handle_english",
    },
    _fallback: {
        "general_explainer",
    },
    _humanities: {
        "handle_humanities",
    },
    _lesson: {
        "format_lesson_message",
        "generate_lesson",
        "list_lessons",
        "_is_lesson_request",
    },
    _math: {
        "answer_experiment_algebra_question",
        "classify_math_request",
        "evaluate_answer",
        "evaluate_answer_details",
        "factor_expression",
        "guided_response",
        "handle_math",
        "solve_linear",
        "solve_quadratic",
        "solve_simultaneous",
        "solve_value",
        "start_guided_problem",
        "sympy_solve_equation",
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
        "MATH_INTENTS",
    },
    _science: {
        "handle_science",
    },
    _formatting: {
        "_build_explanation",
        "_bullet_lines",
        "_compose_message",
        "_format_expression",
        "_format_raw_expression",
        "_format_skill_label",
        "_format_value",
        "_section",
    },
}

_EXPORT_BY_NAME = {
    name: module
    for module, names in _EXPORTS.items()
    for name in names
}
_ALIASES = {
    "_answer_experiment_algebra_question": (
        _math,
        "answer_experiment_algebra_question",
    ),
}


def answer_question(question, mode=None, version=None, user_id=None):
    """Delegate to the router while preserving legacy config mutation."""
    _classifier.HYBRID_MODE = HYBRID_MODE
    _classifier.understanding_model = understanding_model
    return _router.answer_question(
        question,
        mode=mode,
        version=version,
        user_id=user_id,
    )


__all__ = sorted(
    name
    for name in {
        "HYBRID_MODE",
        "understanding_model",
        "answer_question",
        *_EXPORT_BY_NAME,
    }
    if not name.startswith("_")
)


def __getattr__(name):
    alias = _ALIASES.get(name)
    if alias is not None:
        module, target = alias
        return getattr(module, target)

    module = _EXPORT_BY_NAME.get(name)
    if module is not None:
        return getattr(module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | set(__all__) | set(_ALIASES))
