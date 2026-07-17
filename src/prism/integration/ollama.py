"""Ollama HTTP client for embeddings."""
import requests
import numpy as np
from typing import List

DEFAULT_EMBED_URL = "http://127.0.0.1:11434/api/embed"


class OllamaEmbedder:
    def __init__(self, model: str = "nomic-embed-text", endpoint: str = DEFAULT_EMBED_URL):
        self.model = model
        self.endpoint = endpoint

    def embed(self, text: str) -> np.ndarray:
        resp = requests.post(self.endpoint, json={"model": self.model, "input": text})
        resp.raise_for_status()
        data = resp.json()
        embeddings = data.get("embeddings", [])
        if not embeddings:
            raise ValueError(f"No embeddings returned for text: {text[:50]}...")
        return np.array(embeddings[0], dtype=np.float32)

    def embed_batch(self, texts: List[str]) -> List[np.ndarray]:
        # Ollama /api/embed supports batch; we'll use it for efficiency
        resp = requests.post(self.endpoint, json={"model": self.model, "input": texts})
        resp.raise_for_status()
        data = resp.json()
        embeddings = data.get("embeddings", [])
        if len(embeddings) != len(texts):
            raise ValueError(f"Expected {len(texts)} embeddings, got {len(embeddings)}")
        return [np.array(v, dtype=np.float32) for v in embeddings]
