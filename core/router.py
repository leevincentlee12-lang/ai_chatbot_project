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
from core.progression import record_question, update_last_question_time
from data.constants import (
    EXPERIMENT_MODE_PROMPT,
    FOLLOWUPS_BY_SUBJECT,
    FOLLOWUPS_BY_TOPIC,
    TOPIC_BY_SUBJECT,
)
from engine.english_engine import handle_english
from engine.fallback_engine import general_explainer
from engine.humanities_engine import handle_humanities
from engine.lesson_engine import _is_lesson_request, find_lesson_topic, generate_lesson
from engine.math_engine import (
    answer_experiment_algebra_question,
    classify_math_request,
    handle_math,
)
from engine.science_engine import handle_science


WORKFLOW_INTENTS = {
    "check_answer",
    "clear_steps",
    "explain_balance",
    "explain_factor_inverse",
    "generate_hint_from_steps",
    "generate_hint",
    "generate_problem",
    "generate_problem_factoring",
    "generate_problem_harder",
    "generate_problem_linear",
    "generate_problem_quadratic",
    "generate_problem_similar",
    "guided_answer",
    "guided_problem",
    "record_step",
    "show_full_working",
    "show_steps",
    "validate_steps",
    "check_answer_inline",
}

SCOPE_FREE_WORKFLOW_INTENTS = {
    "clear_steps",
    "explain_balance",
    "generate_problem",
    "generate_problem_factoring",
    "generate_problem_harder",
    "generate_problem_linear",
    "generate_problem_quadratic",
    "generate_problem_similar",
    "guided_answer",
    "guided_problem",
    "record_step",
    "show_steps",
    "validate_steps",
}


def _clean_math_prompt(text):
    """Remove common command wrappers while keeping the underlying algebra."""
    return re.sub(
        r"(?i)^\s*(?:solve(?:\s+for\s+x)?|find\s+x(?:\s+(?:in|if|when))?|"
        r"what\s+is\s+x(?:\s+(?:if|in|when))?|calculate\s+x(?:\s+(?:if|in|when))?|"
        r"determine\s+x(?:\s+(?:if|in|when))?|work\s+out\s+x(?:\s+(?:if|in|when))?|"
        r"show\s+the\s+full\s+working\s+for|give\s+me\s+a\s+hint\s+for|"
        r"give\s+me\s+a\s+harder\s+equation\s+like|give\s+me\s+a\s+similar\s+problem\s+to|"
        r"give\s+me\s+another\s+quadratic\s+like|check\s+my\s+answer\s+for|"
        r"explain\s+the\s+discriminant\s+in)\s*[:,]?\s*",
        "",
        str(text or "").strip(),
    ).strip()


def _is_quadratic_text(text):
    """Return whether a prompt or equation appears to be quadratic."""
    lowered = str(text or "").lower()
    return "x^2" in lowered or "quadratic" in lowered


def _extract_answer_section_line(answer_text):
    """Return the first non-empty line in the Answer section."""
    lines = str(answer_text or "").splitlines()
    for index, line in enumerate(lines):
        if line.strip().lower() != "answer":
            continue
        for candidate in lines[index + 1:]:
            cleaned = candidate.strip()
            if cleaned:
                return cleaned

    for line in lines:
        cleaned = line.strip()
        if cleaned:
            return cleaned
    return ""


def _extract_generated_equation(answer_text):
    """Extract a generated practice equation from a structured response."""
    candidate = _extract_answer_section_line(answer_text)
    if "=" in candidate and "x" in candidate.lower():
        return candidate
    return ""


def _extract_answer_check_equation(text):
    """Extract the equation portion from common answer-check prompts."""
    original = str(text or "").strip()
    patterns = [
        r"(?i)^\s*(?:question|equation)\s*:\s*(?P<equation>.+?)\s+(?:answer|my answer)\s*:",
        r"(?i)^\s*(?:my\s+answer\s+is|answer\s+is)\s+.+?\s+(?:for|to|in)\s+(?P<equation>.+?)\s*$",
        r"(?i)^\s*check\s+my\s+answer\s+.+?\s+(?:for|to|in)\s+(?P<equation>.+?)\s*$",
        r"(?i)^\s*check\s+(?:if\s+)?.+?\s+(?:for|to|in)\s+(?P<equation>.+?)\s*$",
        r"(?i)^\s*is\s+.+?\s+correct\s+(?:for|in)\s+(?P<equation>.+?)\s*$",
    ]

    for pattern in patterns:
        match = re.search(pattern, original)
        if match:
            equation = match.group("equation").strip(" .?")
            if "=" in equation:
                return equation

    return _clean_math_prompt(original)


def _practice_followups(equation):
    """Build varied, actionable practice follow-ups around one equation."""
    if not equation:
        return [
            "Give me another linear equation",
            "Give me another quadratic like x^2 - 5x + 6 = 0",
            "Practice problem",
        ]

    if _is_quadratic_text(equation):
        return [
            f"Show the full working for {equation}",
            f"Explain the discriminant in {equation}",
            "Give me a different quadratic problem",
        ]

    return [
        f"Show the full working for {equation}",
        f"Give me a hint for {equation}",
        "Give me a different linear equation",
    ]


def get_followups(subject, topic, question="", answer_text=""):
    """Return context-aware follow-up prompts for a response."""
    text = (question or "").strip()
    lesson_topic = find_lesson_topic(text)

    if lesson_topic and _is_lesson_request(text):
        lesson = generate_lesson(lesson_topic)
        return lesson.get("practice_prompts", [])

    if subject == "Math" and "=" in text and "x" in text:
        cleaned = _clean_math_prompt(text)
        if topic == "Linear Equations":
            return [
                f"Give me a harder equation like {cleaned}",
                f"Give me a similar problem to {cleaned}",
                "Explain why each step keeps the equation balanced",
            ]
        if topic == "Quadratic Equations":
            left_side = cleaned.split("=", 1)[0].strip()
            if "discriminant" in text.lower():
                return [
                    f"Show the full working for {cleaned}",
                    f"Factor {left_side}",
                    f"Give me another quadratic like {cleaned}",
                ]
            return [
                f"Explain the discriminant in {cleaned}",
                f"Factor {left_side}",
                f"Give me another quadratic like {cleaned}",
            ]

        if topic == "Practice":
            return _practice_followups(_extract_generated_equation(answer_text) or cleaned)

        if topic == "Answer Checking":
            checked_equation = _extract_answer_check_equation(text)
            return [
                f"Show the full working for {checked_equation}",
                f"Give me a similar problem to {checked_equation}",
                f"Give me a hint for {checked_equation}",
            ]

        if topic == "Hint":
            return [
                f"Show the full working for {cleaned}",
                f"Give me a similar problem to {cleaned}",
                "Give me a different linear equation",
            ]

        if topic == "Worked Solution":
            return [
                f"Give me a similar problem to {cleaned}",
                f"Give me a harder equation like {cleaned}",
                "Explain why each step keeps the equation balanced",
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

    if subject == "Math" and topic == "Algebraic Expressions":
        return [
            "Simplify 4x - 2 + 3x",
            "Expand (x + 2)(x - 5)",
            "Factor x^2 - 9",
        ]

    if subject == "Math" and topic == "Ratios":
        return [
            "Simplify the ratio 12:18",
            "Simplify the ratio 15:25",
            "Learn fractions",
        ]

    if subject == "Math" and topic == "Trigonometry":
        return [
            "Find x if cos 40 = x/10",
            "Learn trigonometry",
            "Explain sine cosine and tangent",
        ]

    if subject == "Math" and topic == "Practice":
        return _practice_followups(_extract_generated_equation(answer_text))

    if subject == "Math" and topic == "Answer Checking":
        return [
            "Practice problem",
            "Show the full working for 2x + 4 = 10",
            "Give me a hint for 2x + 4 = 10",
        ]

    if subject == "Math" and topic == TOPIC_BY_SUBJECT["Math"]:
        return [
            "Solve 2x + 4 = 10",
            "Learn algebra and functions",
            "Practice problem",
        ]

    if topic in FOLLOWUPS_BY_TOPIC:
        return FOLLOWUPS_BY_TOPIC[topic]

    return FOLLOWUPS_BY_SUBJECT.get(subject, FOLLOWUPS_BY_SUBJECT["Unknown"])


def academic_engine(question, user_id=None):
    """Dispatch a question to the matching subject engine."""
    subject = classify_subject(question)

    if subject == "Math":
        return handle_math(question, user_id=user_id)

    if subject == "Science":
        return handle_science(question)

    if subject == "English":
        return handle_english(question)

    if subject == "Humanities":
        return handle_humanities(question)

    return general_explainer(question)


def _with_algebra_focus(answer):
    """Add a gentle algebra focus nudge to non-algebra responses."""
    text = str(answer or "").strip()
    if not text:
        text = general_explainer("")

    if "Algebra Focus" in text:
        return text

    return (
        f"{text}\n\n"
        "Algebra Focus\n"
        "By the way, this platform is strongest for algebra. If you want to "
        "focus there, try an equation, a graph question, or Practice Mode next."
    )


def answer_question(question, mode=None, version=None, user_id=None):
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

    update_last_question_time(time.time(), user_id=user_id)
    raw_workflow_match = classify_math_request(text)
    cleaned_text = _strip_mode_instruction(text)
    if raw_workflow_match.name in WORKFLOW_INTENTS:
        workflow_match = raw_workflow_match
        workflow_text = text
    else:
        workflow_match = classify_math_request(cleaned_text)
        workflow_text = cleaned_text
    is_algebra_scoped = _is_algebra_question(cleaned_text, use_hybrid=use_hybrid)

    if (
        workflow_match.name in WORKFLOW_INTENTS
        and (
            is_algebra_scoped
            or workflow_match.name in SCOPE_FREE_WORKFLOW_INTENTS
        )
    ):
        answer = handle_math(workflow_text, user_id=user_id)
        topic = workflow_match.topic
        record_question(
            workflow_text,
            subject="Math",
            topic=topic,
            mode=mode,
            user_id=user_id,
        )
        return {
            "answer": answer,
            "subject": "Math",
            "topic": topic,
            "followups": get_followups("Math", topic, workflow_text, answer),
        }

    if not is_algebra_scoped:
        subject = classify_subject(text)
        if subject == "Unknown":
            topic = TOPIC_BY_SUBJECT["Unknown"]
        else:
            topic = detect_topic(subject, text)

        answer = _with_algebra_focus(academic_engine(text, user_id=user_id))
        record_question(
            text,
            subject=subject,
            topic=topic,
            mode=mode,
            user_id=user_id,
        )
        return {
            "answer": answer,
            "subject": subject,
            "topic": topic,
            "followups": get_followups(subject, topic, text, answer),
        }

    resolved_mode = _resolve_experiment_mode(text, mode)
    if resolved_mode is None:
        record_question(
            text,
            subject="Math",
            topic="Mode Selection",
            mode=mode,
            user_id=user_id,
        )
        return {
            "answer": EXPERIMENT_MODE_PROMPT,
            "subject": "Math",
            "topic": "Mode Selection",
            "followups": [],
        }

    answer = answer_experiment_algebra_question(cleaned_text, resolved_mode)
    topic = _detect_experiment_topic(cleaned_text)
    record_question(
        cleaned_text,
        subject="Math",
        topic=topic,
        mode=resolved_mode,
        user_id=user_id,
    )

    return {
        "answer": answer,
        "subject": "Math",
        "topic": topic,
        "followups": get_followups("Math", topic, cleaned_text, answer),
    }
