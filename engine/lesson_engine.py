"""Lesson-catalog utilities for lesson lookup, rendering, and summaries."""

from copy import deepcopy

from data.constants import LESSON_CATALOG
from utils.formatting import _bullet_lines, _compose_message, _section


def _is_lesson_request(question):
    """Return whether a question is explicitly asking for a lesson."""
    q_lower = (question or "").lower()
    triggers = [
        "learn ",
        "lesson",
        "teach me",
        "revise ",
        "study ",
        "help me learn",
    ]
    return any(trigger in q_lower for trigger in triggers)


def find_lesson_topic(question):
    """Map a question to a lesson topic slug when a known topic is referenced."""
    q_lower = (question or "").lower()

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


def format_lesson_message(lesson):
    """Render a lesson payload into a structured, readable tutor message."""
    key_points = _bullet_lines(lesson.get("key_points", []))
    mistakes = _bullet_lines(lesson.get("common_mistakes", []))
    practice = _bullet_lines(lesson.get("practice_prompts", []))

    return _compose_message(
        _section(lesson["title"], lesson.get("summary")),
        _section("Core Idea", lesson.get("explanation")),
        _section("Key Points", key_points),
        _section("Worked Example", lesson.get("example")),
        _section("Common Mistakes", mistakes),
        _section("Practice Prompts", practice),
    )


def list_lessons():
    """Return a frontend-friendly list of lesson summaries."""
    lessons = []
    for slug, lesson in LESSON_CATALOG.items():
        lessons.append({
            "topic": slug,
            "title": lesson["title"],
            "button_label": lesson["button_label"],
            "strand": lesson["strand"],
            "level": lesson["level"],
            "summary": lesson["summary"],
            "starter_prompt": lesson["starter_prompt"],
        })
    return lessons


def generate_lesson(topic):
    """Return the full lesson payload for a topic slug."""
    slug = (topic or "").strip().lower()
    lesson = deepcopy(LESSON_CATALOG.get(slug))

    if lesson is None:
        return {
            "topic": slug or "unknown",
            "title": "Unknown topic",
            "button_label": "Unknown",
            "strand": "Math",
            "level": "General",
            "summary": "No lesson is available for that topic yet.",
            "explanation": "Try one of the topics in the lesson library.",
            "key_points": [],
            "example": "",
            "common_mistakes": [],
            "practice_prompts": [],
            "practice": [],
            "starter_prompt": "",
            "related_topics": [],
            "related_lessons": [],
            "display_text": _compose_message(
                _section("Unknown Topic", "No lesson is available for that topic yet."),
                _section("Next Step", "Choose a topic from the lesson library."),
            ),
        }

    lesson["topic"] = slug
    lesson["practice"] = lesson["practice_prompts"]
    lesson["related_lessons"] = [
        {
            "topic": related_topic,
            "title": LESSON_CATALOG[related_topic]["title"],
            "button_label": LESSON_CATALOG[related_topic]["button_label"],
        }
        for related_topic in lesson.get("related_topics", [])
        if related_topic in LESSON_CATALOG
    ]
    lesson["display_text"] = format_lesson_message(lesson)
    return lesson
