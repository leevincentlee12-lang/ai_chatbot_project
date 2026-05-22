"""Central classification helpers for subjects, intents, topics, and scope."""

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, List

from core.understanding import Understanding
from data.constants import LESSON_CATALOG, SUBJECT_KEYWORDS, TOPIC_BY_SUBJECT
from data.intents import INTENTS, IntentDefinition


# Kept for compatibility with older callers that toggled classifier behavior.
HYBRID_MODE = True
understanding_model = Understanding(backend="simple", dim=256)
_TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


@dataclass
class IntentMatch:
    """Classification result with routing metadata and match evidence."""

    name: str
    confidence: float
    topic: str = "General Study Help"
    engine: str = "fallback"
    difficulty: int = 0
    score: float = 0.0
    matched_patterns: List[str] = field(default_factory=list)
    matched_keywords: List[str] = field(default_factory=list)
    matched_examples: List[str] = field(default_factory=list)


def _normalise_text(text: str) -> str:
    """Normalize user text for deterministic classification."""
    return re.sub(r"\s+", " ", str(text or "").lower()).strip()


def _tokens(text: str) -> set:
    """Tokenize text for keyword and example-overlap scoring."""
    return set(_TOKEN_PATTERN.findall(_normalise_text(text)))


def _keyword_matches(text: str, tokens: set, keywords: Iterable[str]) -> List[str]:
    """Return intent keywords present in the normalized text."""
    matches = []
    for keyword in keywords:
        normalized_keyword = _normalise_text(keyword)
        keyword_tokens = _tokens(normalized_keyword)

        if not normalized_keyword:
            continue

        if len(keyword_tokens) > 1:
            if re.search(rf"\b{re.escape(normalized_keyword)}\b", text):
                matches.append(keyword)
        elif normalized_keyword in tokens or normalized_keyword in text:
            matches.append(keyword)

    return matches


def _example_matches(tokens: set, examples: Iterable[str]) -> List[str]:
    """Return examples with strong token overlap against the question."""
    matches = []
    for example in examples:
        example_tokens = _tokens(example)
        if not example_tokens:
            continue

        overlap = len(tokens & example_tokens) / len(example_tokens)
        if overlap >= 0.6:
            matches.append(example)

    return matches


def _score_intent(question: str, tokens: set, intent: IntentDefinition) -> IntentMatch:
    """Score one intent using patterns, keywords, and examples."""
    pattern_matches = [
        pattern
        for pattern in intent.patterns
        if re.search(pattern, question, flags=re.IGNORECASE)
    ]
    keyword_matches = _keyword_matches(question, tokens, intent.keywords)
    example_matches = _example_matches(tokens, intent.examples)

    pattern_score = (
        len(pattern_matches) / len(intent.patterns)
        if intent.patterns
        else 0.0
    )
    keyword_score = (
        len(keyword_matches) / len(intent.keywords)
        if intent.keywords
        else 0.0
    )
    example_score = min(1.0, len(example_matches) / 2)

    score = (pattern_score * 0.55) + (keyword_score * 0.30) + (example_score * 0.15)

    if pattern_matches and keyword_matches:
        score += 0.10
    if any(_normalise_text(example) == question for example in intent.examples):
        score = 1.0

    confidence = max(0.0, min(1.0, score))
    return IntentMatch(
        name=intent.name,
        confidence=confidence,
        topic=intent.topic,
        engine=intent.engine,
        difficulty=intent.difficulty,
        score=score,
        matched_patterns=pattern_matches,
        matched_keywords=keyword_matches,
        matched_examples=example_matches,
    )


def classify_intent(question: str) -> IntentMatch:
    """Classify a question using deterministic pattern and keyword scoring."""
    text = _normalise_text(question)
    if not text:
        return IntentMatch(name="unknown", confidence=0.0)

    tokens = _tokens(text)
    scored = [
        _score_intent(text, tokens, intent)
        for intent in INTENTS.values()
    ]
    scored.sort(
        key=lambda match: (
            match.confidence,
            len(match.matched_patterns),
            len(match.matched_keywords),
            -INTENTS[match.name].difficulty,
        ),
        reverse=True,
    )

    best = scored[0]
    if best.confidence <= 0:
        return IntentMatch(name="unknown", confidence=0.0)
    return best


def detect_intent(question: str) -> IntentMatch:
    """Backward-compatible alias for deterministic intent classification."""
    return classify_intent(question)


def _score_subject_keywords(question: str) -> Counter:
    """Score subject keywords for subject classification."""
    q_lower = _normalise_text(question)
    scores = Counter()

    for subject, keywords in SUBJECT_KEYWORDS.items():
        for word in keywords:
            if word in q_lower:
                scores[subject] += 1

    if re.search(r"\b\d*x\b", q_lower) or "=" in q_lower or "^" in q_lower:
        scores["Math"] += 2

    if "war" in q_lower or "ww1" in q_lower or "ww2" in q_lower:
        scores["Humanities"] += 2

    return scores


def _normalise_mode_label(mode):
    """Convert a user mode label into one supported experiment mode."""
    text = str(mode or "").strip().lower()

    if text in {"direct", "direct mode"}:
        return "direct"

    if text in {
        "step-by-step",
        "step by step",
        "step-by-step mode",
        "step by step mode",
    }:
        return "step-by-step"

    if text in {"hint", "hint mode"}:
        return "hint"

    return None


def _detect_mode_from_text(question):
    """Detect an explicit response mode request inside question text."""
    q_lower = (question or "").lower()
    patterns = [
        (
            "step-by-step",
            [
                r"\bstep[- ]by[- ]step(?: mode)?\b",
                r"\bshow the full working\b",
                r"\bfull working\b",
                r"\bshow working\b",
                r"\bshow steps\b",
            ],
        ),
        (
            "hint",
            [
                r"\bhint mode\b",
                r"\bgive me a hint\b",
                r"\bhint for\b",
                r"\bjust a hint\b",
            ],
        ),
        (
            "direct",
            [
                r"\bdirect mode\b",
                r"\bdirect answer\b",
                r"\bin direct mode\b",
            ],
        ),
    ]

    for mode, mode_patterns in patterns:
        if any(re.search(pattern, q_lower) for pattern in mode_patterns):
            return mode

    return None


def _resolve_experiment_mode(question, mode=None):
    """Resolve an explicit API mode first, then fall back to text intent."""
    return _normalise_mode_label(mode) or _detect_mode_from_text(question)


def _strip_mode_instruction(question):
    """Remove natural-language mode instructions before algebra parsing."""
    cleaned = re.sub(
        r"^\s*(direct|hint|step(?:-by-step| by step))(?:\s+mode)?\s*[:,-]?\s*",
        "",
        str(question or ""),
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"\s+in\s+(direct|hint|step(?:-by-step| by step))\s+mode\s*$",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(
        r"^\s*(show the full working for|show working for|give me a hint for|just a hint for)\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    return cleaned.strip()


def _is_algebra_question(question, use_hybrid=None):
    """Return whether text is inside the experiment's algebra scope."""
    q_lower = _normalise_text(question)
    if not q_lower:
        return False

    blocked_patterns = [
        r"\bphotosynthesis\b",
        r"\bforce\b",
        r"\bvelocity\b",
        r"\bdensity\b",
        r"\bessay\b",
        r"\btheme\b",
        r"\bparagraph\b",
        r"\bteel\b",
        r"\bww1\b",
        r"\bww2\b",
        r"\bworld war\b",
        r"\bclimate\b",
        # Note: trig terms intentionally omitted so trig equations can be
        # handled by the math engine when the question includes numeric
        # or variable context (e.g. "find x if sin 35 = x/12").
    ]

    if any(re.search(pattern, q_lower) for pattern in blocked_patterns):
        return False

    match = classify_intent(q_lower)
    if match.engine == "math" and match.confidence >= 0.20:
        return True

    if re.search(r"-?\d+\s*:\s*-?\d+", q_lower):
        return True

    # Accept short natural-language cues like "solve" or "find" when they
    # are accompanied by numeric or variable hints to avoid false positives.
    tokens = _tokens(q_lower)
    math_cue_tokens = {"solve", "find", "simplify", "factor", "expand"}
    if tokens & math_cue_tokens:
        if (
            "=" in q_lower
            or re.search(r"(?<![a-z])(?:\d*)[xy](?:\^\d+)?\b", q_lower)
            or ":" in q_lower
            or re.search(r"\d", q_lower)
        ):
            return True

    has_variable = bool(re.search(r"(?<![a-z])(?:\d*)[xy](?:\^\d+)?\b", q_lower))
    return "=" in q_lower and has_variable


def _detect_experiment_topic(question):
    """Return the experiment topic label for an algebra-scoped question."""
    q_lower = _normalise_text(question)
    match = classify_intent(q_lower)
    if match.confidence >= 0.20 and match.topic not in {
        "Hint",
        "Practice",
        "Worked Solution",
        "Answer Checking",
        "Explanation",
    }:
        return match.topic

    if re.search(r"-?\d+\s*:\s*-?\d+", q_lower) or "ratio" in q_lower:
        return "Ratios"

    if "=" in q_lower and "x" in q_lower:
        return "Linear Equations"

    return "Algebra"


def classify_algebra_intent(question):
    """Return the algebra intent label used by math_engine dispatch."""
    match = classify_intent(question)
    return match.name if match.engine == "math" else "unknown"


def classify_subject(question: str):
    """Infer the academic subject for a user question."""
    scores = _score_subject_keywords(question)

    if not scores:
        return "Unknown"

    return scores.most_common(1)[0][0]


def find_lesson_topic(question):
    """Find a lesson slug from user text using title, label, slug, or keywords."""
    q_lower = _normalise_text(question)

    for slug, lesson in LESSON_CATALOG.items():
        aliases = {
            slug.replace("_", " "),
            lesson["title"].lower(),
            lesson["button_label"].lower(),
        }
        aliases.update(term.lower() for term in lesson.get("keywords", []))

        if any(alias in q_lower for alias in aliases):
            return slug

    return None


def detect_topic(subject, question):
    """Determine a user-facing topic label for a classified question."""
    q_lower = _normalise_text(question)
    lesson_topic = find_lesson_topic(question)

    if subject == "Math":
        if lesson_topic:
            return LESSON_CATALOG[lesson_topic]["title"]

        match = classify_intent(q_lower)
        if match.confidence >= 0.20 and match.topic not in {
            "Hint",
            "Practice",
            "Worked Solution",
            "Answer Checking",
            "Explanation",
        }:
            return match.topic

        if "=" in q_lower and "x" in q_lower:
            return "Linear Equations"
        return TOPIC_BY_SUBJECT["Math"]

    return TOPIC_BY_SUBJECT.get(subject, TOPIC_BY_SUBJECT["Unknown"])
