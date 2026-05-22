"""Compatibility API for deterministic intent classification.

This module no longer loads ML models. It delegates to core.classifier so callers
using the older `intent_classifier.classify_intent` API keep working.
"""

from typing import Optional, Tuple, Union

from core.classifier import classify_intent as _classify_intent


def classify_intent(
    question: str,
    return_score: bool = False,
    threshold: Optional[float] = None,
) -> Union[str, Tuple[str, float]]:
    """Return the best deterministic intent label, optionally with confidence."""
    match = _classify_intent(question)
    cutoff = 0.0 if threshold is None else float(threshold)
    label = match.name if match.confidence >= cutoff else "unknown"

    if return_score:
        return label, match.confidence
    return label


def is_available() -> bool:
    """Return True because deterministic intent classification is always local."""
    return True


def reset_model():
    """Compatibility no-op; deterministic classification has no model state."""
    return None


__all__ = ["classify_intent", "is_available", "reset_model"]
