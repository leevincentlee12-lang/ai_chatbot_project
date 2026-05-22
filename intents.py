"""Compatibility wrapper for deterministic intent classification."""

from core.classifier import IntentMatch, classify_intent, detect_intent
from data.intents import INTENT_PATTERNS, INTENTS, TRAINING_EXAMPLES, IntentDefinition

__all__ = [
    "INTENT_PATTERNS",
    "INTENTS",
    "TRAINING_EXAMPLES",
    "IntentDefinition",
    "IntentMatch",
    "classify_intent",
    "detect_intent",
]
