"""Embedding-based bias classifier using real centroids."""
import json
import numpy as np
from pathlib import Path
from typing import Dict, Tuple

from prism.integration.ollama import OllamaEmbedder


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


class EmbeddingClassifier:
    def __init__(self, centroids_path: Path | None = None, embedder: OllamaEmbedder | None = None):
        if centroids_path is None:
            # Default: project root / centroids / bias-centroids.json
            # This file lives at src/prism/classifiers/embedding.py -> 3 up = project root
            centroids_path = Path(__file__).resolve().parents[3] / "centroids" / "bias-centroids.json"
        self.centroids_path = centroids_path
        self.embedder = embedder or OllamaEmbedder()
        self.centroids: Dict[str, np.ndarray] = {}
        self._load()

    def _load(self) -> None:
        if not self.centroids_path.exists():
            raise FileNotFoundError(f"Centroids not found at {self.centroids_path}")
        with open(self.centroids_path, "r") as f:
            raw = json.load(f)
        for bias, meta in raw.items():
            self.centroids[bias] = np.array(meta["centroid"], dtype=np.float32)

    def classify(self, text: str) -> Dict[str, float]:
        vec = self.embedder.embed(text)
        scores: Dict[str, float] = {}
        for bias, centroid in self.centroids.items():
            scores[bias] = cosine_similarity(vec, centroid)
        # Shift to 0–1 range (cosine similarity is -1 to 1; bias texts are usually positive)
        min_s = min(scores.values())
        max_s = max(scores.values())
        if max_s > min_s:
            scores = {k: (v - min_s) / (max_s - min_s) for k, v in scores.items()}
        else:
            scores = {k: 0.5 for k in scores}
        return scores

    def dominant(self, text: str) -> Tuple[str, float]:
        scores = self.classify(text)
        best = max(scores, key=lambda k: scores[k])
        return best, scores[best]
