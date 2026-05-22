"""Routing logic that classifies questions and dispatches to subject engines."""

import re
import time

from core import classifier as classifier_state
from core.classifier import (
    _detect_experiment_topic,
    _is_algebra_question,
    _resolve_experiment_mode,
    _strip_mode_instruction,
    classify_subject,
    detect_topic,
)
from core.progression import record_question_asked, student_profile
from data.constants import (
    EXPERIMENT_MODE_PROMPT,
    EXPERIMENT_RESTRICTED_MESSAGE,
    FOLLOWUPS_BY_SUBJECT,
    FOLLOWUPS_BY_TOPIC,
    TOPIC_BY_SUBJECT,
)
from engine.english_engine import handle_english
from engine.fallback_engine import general_explainer
from engine.humanities_engine import handle_humanities
from engine.lesson_engine import _is_lesson_request, find_lesson_topic, generate_lesson
from engine.math_engine import answer_experiment_algebra_question, handle_math
from engine.science_engine import handle_science


def get_followups(subject, topic, question=""):
    """Return context-aware follow-up prompts for a response."""
    text = (question or "").strip()
    lesson_topic = find_lesson_topic(text)

    if lesson_topic and _is_lesson_request(text):
        lesson = generate_lesson(lesson_topic)
        return lesson.get("practice_prompts", [])

    if subject == "Math" and "=" in text and "x" in text:
        cleaned = re.sub(r"(?i)^\s*solve\s*", "", text).strip()
        if topic == "Linear Equations":
            return [
                f"Show the full working for {cleaned}",
                f"Give me a harder equation like {cleaned}",
                f"Check my answer for {cleaned}",
            ]
        if topic == "Quadratic Equations":
            return [
                f"Explain the discriminant in {cleaned}",
                f"Factor {cleaned.split('=', 1)[0].strip()}",
                f"Give me another quadratic like {cleaned}",
            ]

    if subject == "Math" and topic == "Factoring" and text:
        cleaned = re.sub(r"(?i)^factor\s*", "", text).strip()
        try:
            from sympy import factor as sympy_factor, simplify

            from core.parser import parse_math_expression
            from utils.formatting import _format_raw_expression

            factored = _format_raw_expression(
                sympy_factor(simplify(parse_math_expression(cleaned)))
            )
        except Exception:
            factored = cleaned
        return [
            f"Expand {factored}",
            f"Give me another factoring problem like {cleaned}",
            f"Explain why {factored} multiplies back to {cleaned}",
        ]

    if topic in FOLLOWUPS_BY_TOPIC:
        return FOLLOWUPS_BY_TOPIC[topic]

    return FOLLOWUPS_BY_SUBJECT.get(subject, FOLLOWUPS_BY_SUBJECT["Unknown"])


def academic_engine(question):
    """Dispatch a question to the matching subject engine."""
    subject = classify_subject(question)

    if subject == "Math":
        return handle_math(question)

    if subject == "Science":
        return handle_science(question)

    if subject == "English":
        return handle_english(question)

    if subject == "Humanities":
        return handle_humanities(question)

    return general_explainer(question)


def answer_question(question, mode=None, version=None):
    """Answer an experiment-scoped algebra question with routing metadata."""
    text = (question or "").strip()
    if not text:
        return {
            "answer": "Ask a question to get started.",
            "subject": "Unknown",
            "topic": TOPIC_BY_SUBJECT["Unknown"],
            "followups": FOLLOWUPS_BY_SUBJECT["Unknown"],
        }

    use_hybrid = classifier_state.HYBRID_MODE
    if version == "v1":
        use_hybrid = False
    elif version == "v2":
        use_hybrid = True

    try:
        student_profile["last_question_ts"] = time.time()
    except Exception:
        pass

    record_question_asked()
    cleaned_text = _strip_mode_instruction(text)

    if not _is_algebra_question(cleaned_text, use_hybrid=use_hybrid):
        return {
            "answer": EXPERIMENT_RESTRICTED_MESSAGE,
            "subject": "Restricted",
            "topic": "Restricted Scope",
            "followups": [],
        }

    resolved_mode = _resolve_experiment_mode(text, mode)
    if resolved_mode is None:
        return {
            "answer": EXPERIMENT_MODE_PROMPT,
            "subject": "Math",
            "topic": "Mode Selection",
            "followups": [],
        }

    answer = answer_experiment_algebra_question(cleaned_text, resolved_mode)
    topic = _detect_experiment_topic(cleaned_text)

    return {
        "answer": answer,
        "subject": "Math",
        "topic": topic,
        "followups": [],
    }
