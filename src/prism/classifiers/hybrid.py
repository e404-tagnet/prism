"""Hybrid classifier combining keyword + embedding with configurable weights."""
from typing import Dict, Tuple
from dataclasses import dataclass

from prism.config import get_value
from prism.classifiers.keyword import classify as keyword_classify
from prism.classifiers.embedding import EmbeddingClassifier


@dataclass
class HybridResult:
    bias: str
    confidence: float
    keyword_scores: Dict[str, float]
    embedding_scores: Dict[str, float]
    combined_scores: Dict[str, float]


class HybridClassifier:
    def __init__(self, keyword_weight: float | None = None, embedding: EmbeddingClassifier | None = None):
        if keyword_weight is None:
            keyword_weight = float(get_value("classifiers", "weights", "keyword", default=0.6))
        self.keyword_weight = keyword_weight
        self.embedding_weight = 1.0 - keyword_weight
        self.embedding = embedding or EmbeddingClassifier()

    def classify(self, text: str) -> HybridResult:
        kw_scores = keyword_classify(text)
        emb_scores = self.embedding.classify(text)

        combined: Dict[str, float] = {}
        all_biases = set(kw_scores.keys()) | set(emb_scores.keys())
        for bias in all_biases:
            combined[bias] = (
                self.keyword_weight * kw_scores.get(bias, 0.0)
                + self.embedding_weight * emb_scores.get(bias, 0.0)
            )

        best = max(combined, key=lambda k: combined[k])
        return HybridResult(
            bias=best,
            confidence=combined[best],
            keyword_scores=kw_scores,
            embedding_scores=emb_scores,
            combined_scores=combined,
        )
