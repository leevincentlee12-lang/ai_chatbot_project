"""
Lightweight understanding layer for the tutor.

- Provides a simple, dependency-free embedding fallback (hash-based) and
  optional backends (sentence-transformers or OpenAI embeddings if installed).
- Delegates classification calls to core.classifier so classification logic
  stays centralized.

The goal is to offer a pluggable understanding layer so the system can move
from fragile keyword checks to semantic similarity without requiring heavy
dependencies by default.
"""

import re
import math

# try optional backends
try:
    from sentence_transformers import SentenceTransformer
    HF_AVAILABLE = True
except Exception:
    HF_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False


class Understanding:
    def __init__(self, backend: str = "simple", dim: int = 256, hf_model_name: str = "all-MiniLM-L6-v2"):
        self.backend = backend
        self.dim = int(dim)
        self.hf_model = None
        if self.backend == "hf" and HF_AVAILABLE:
            try:
                self.hf_model = SentenceTransformer(hf_model_name)
            except Exception:
                self.hf_model = None

    def _tokenize(self, text: str):
        return re.findall(r"\w+", (text or "").lower())

    def _hash_embedding(self, text: str):
        vec = [0.0] * self.dim
        for token in self._tokenize(text):
            idx = abs(hash(token)) % self.dim
            vec[idx] += 1.0
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def _embed(self, text: str):
        text = str(text or "")
        # HuggingFace SentenceTransformer if requested and available
        if self.backend == "hf" and self.hf_model:
            try:
                emb = self.hf_model.encode(text, convert_to_numpy=False)
                emb_list = list(emb)
                norm = math.sqrt(sum(x * x for x in emb_list)) or 1.0
                return [x / norm for x in emb_list]
            except Exception:
                pass

        # OpenAI embeddings if available and selected
        if self.backend == "openai" and OPENAI_AVAILABLE:
            try:
                # caller must set OPENAI_API_KEY in environment for this to work
                model = "text-embedding-3-small"
                resp = openai.Embedding.create(model=model, input=text)
                arr = resp["data"][0]["embedding"]
                norm = math.sqrt(sum(x * x for x in arr)) or 1.0
                return [x / norm for x in arr]
            except Exception:
                pass

        # fallback: simple hash-based embedding
        return self._hash_embedding(text)

    def embed(self, text: str):
        return self._embed(text)

    @staticmethod
    def _cosine(a, b):
        # both are lists
        if not a or not b:
            return 0.0
        dot = 0.0
        na = 0.0
        nb = 0.0
        for x, y in zip(a, b):
            dot += x * y
            na += x * x
            nb += y * y
        if na == 0 or nb == 0:
            return 0.0
        return dot / (math.sqrt(na) * math.sqrt(nb))

    def detect_intent(self, text: str, threshold: float = 0.45):
        from core.classifier import classify_intent

        match = classify_intent(text)
        if match.confidence >= threshold:
            return match.name, match.confidence
        return None, match.confidence

    def detect_topic(self, text: str, threshold: float = 0.4):
        from core.classifier import classify_intent

        match = classify_intent(text)
        if match.confidence >= threshold:
            return match.topic
        return None

    def is_algebra_question(self, text: str, threshold: float = 0.4) -> bool:
        from core.classifier import classify_intent

        match = classify_intent(text)
        return match.engine == "math" and match.confidence >= threshold
