"""Summarise tester feedback from a CSV file.

Usage:
    python tools/analyse_feedback.py tester_feedback_results.csv

The CSV should use the columns in tester_feedback_results.csv. The script does
not invent data; blank rows are ignored.
"""

from __future__ import annotations

import csv
import statistics
import sys
from collections import Counter
from pathlib import Path


IMPROVEMENT_KEYWORDS = {
    "graphs / visuals": ("graph", "visual", "diagram", "plot"),
    "common mistake feedback": ("mistake", "error feedback", "wrong answer", "incorrect"),
    "harder questions": ("hard", "difficulty", "difficult", "extension", "year 11"),
    "more question variety": ("variety", "more questions", "different questions", "range"),
    "navigation / interface": ("navigation", "ui", "interface", "layout", "button"),
    "speed / loading": ("slow", "loading", "speed", "render"),
    "hint mode": ("hint", "clue", "nudge"),
    "lessons": ("lesson", "example", "worked example"),
    "progress tracking": ("progress", "dashboard", "stats"),
}

ISSUE_KEYWORDS = {
    "incorrect answer": ("wrong answer", "incorrect", "not correct", "math error"),
    "confusing explanation": ("confusing", "unclear", "hard to follow", "difficult to follow"),
    "bug / error": ("bug", "error", "crash", "did not work", "broken"),
    "navigation issue": ("navigation", "could not find", "button", "link"),
    "slow loading": ("slow", "loading", "took long", "delay"),
}


def normalise(value: str) -> str:
    """Return a normalised lowercase string."""
    return str(value or "").strip().lower()


def yes_value(value: str) -> bool:
    """Return whether a response counts as yes."""
    text = normalise(value)
    return text.startswith("yes") or text in {"y", "true"}


def maybe_value(value: str) -> bool:
    """Return whether a response counts as maybe."""
    return normalise(value).startswith("maybe")


def load_rows(path: Path) -> list[dict[str, str]]:
    """Load non-empty feedback rows."""
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    return [
        row
        for row in rows
        if any(str(value or "").strip() for value in row.values())
    ]


def average_rating(rows: list[dict[str, str]]) -> float | None:
    """Calculate average rating from valid numeric ratings."""
    ratings = []
    for row in rows:
        try:
            value = float(row.get("rating_out_of_10", ""))
        except ValueError:
            continue
        if 0 <= value <= 10:
            ratings.append(value)

    if not ratings:
        return None
    return round(statistics.mean(ratings), 2)


def keyword_counts(rows: list[dict[str, str]], field: str, keywords: dict[str, tuple[str, ...]]) -> Counter:
    """Count keyword categories in free-text responses."""
    counts = Counter()
    for row in rows:
        text = normalise(row.get(field, ""))
        if not text or text in {"no", "none", "n/a", "na"}:
            continue

        matched = False
        for category, terms in keywords.items():
            if any(term in text for term in terms):
                counts[category] += 1
                matched = True

        if not matched:
            counts["other"] += 1

    return counts


def print_counter(title: str, counts: Counter) -> None:
    """Print a counter in ranked order."""
    print(title)
    if not counts:
        print("- No responses recorded")
        return

    for label, count in counts.most_common():
        print(f"- {label}: {count}")


def main() -> int:
    """Run feedback analysis."""
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tester_feedback_results.csv")
    if not path.exists():
        print(f"Could not find CSV file: {path}")
        return 1

    rows = load_rows(path)
    if not rows:
        print("No tester feedback rows found yet.")
        return 0

    preferred_modes = Counter(
        row.get("preferred_mode", "").strip()
        for row in rows
        if row.get("preferred_mode", "").strip()
    )
    rating = average_rating(rows)

    use_again_yes = sum(1 for row in rows if yes_value(row.get("use_again", "")))
    use_again_maybe = sum(1 for row in rows if maybe_value(row.get("use_again", "")))
    use_again_rate = round((use_again_yes / len(rows)) * 100, 2)

    print("Tester Feedback Summary")
    print("=======================")
    print(f"Total testers: {len(rows)}")
    print(f"Most preferred feedback mode: {preferred_modes.most_common(1)[0][0] if preferred_modes else 'Not available'}")
    print(f"Average rating: {rating if rating is not None else 'Not available'} / 10")
    print(f"Would use again: {use_again_rate}% yes ({use_again_yes}/{len(rows)})")
    if use_again_maybe:
        print(f"Maybe use again: {use_again_maybe}/{len(rows)}")
    print()

    print_counter(
        "Most common improvement suggestions:",
        keyword_counts(rows, "improvements_or_additions", IMPROVEMENT_KEYWORDS),
    )
    print()
    issue_counts = keyword_counts(rows, "bugs_or_errors", ISSUE_KEYWORDS)
    issue_counts.update(keyword_counts(rows, "confusing_explanations", ISSUE_KEYWORDS))
    print_counter("Most commonly reported issues:", issue_counts)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
