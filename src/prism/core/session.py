"""Session tracker: topic drift, repeat asks, frustration arc."""
from dataclasses import dataclass, field
from typing import List, Set
from collections import Counter

from prism.config import get_value
import re


@dataclass
class SessionState:
    turns: List[str] = field(default_factory=list)
    topics: List[Set[str]] = field(default_factory=list)
    repeat_counts: Counter = field(default_factory=Counter)
    last_route: str = ""


class SessionTracker:
    def __init__(self):
        self.recent_window = get_value("session", "recent_turns_window", default=6)
        self.drift_threshold = get_value("session", "topic_drift_threshold", default=0.35)
        self.frustration_threshold = get_value("session", "frustration_repeat_threshold", default=3)

    def _topic_words(self, text: str) -> Set[str]:
        # Naive tokenization: lowercase words > 3 chars, drop stopwords
        stop = {
            "the", "and", "that", "have", "for", "not", "with", "you", "this",
            "but", "his", "from", "they", "she", "her", "been", "their", "said",
            "each", "which", "will", "about", "could", "would", "there", "them",
            "what", "when", "where", "how", "why", "can", "should", "does", "are",
            "was", "were", "did", "has", "had", "does", "do", "is", "it", "its",
            "than", "then", "too", "very", "just", "now", "only", "also", "into",
            "your", "our", "my", "me", "him", "us", "we", "i", "a", "an", "as",
            "at", "be", "by", "he", "in", "of", "on", "or", "so", "to", "up",
        }
        words = re.findall(r"[a-z]{4,}", text.lower())
        return set(w for w in words if w not in stop)

    def _jaccard(self, a: Set[str], b: Set[str]) -> float:
        if not a and not b:
            return 1.0
        inter = len(a & b)
        union = len(a | b)
        return inter / union if union else 0.0

    def add_turn(self, state: SessionState, user_input: str) -> SessionState:
        new_topics = self._topic_words(user_input)
        new_state = SessionState(
            turns=state.turns + [user_input],
            topics=state.topics + [new_topics],
            repeat_counts=Counter(state.repeat_counts),
            last_route=state.last_route,
        )
        new_state.repeat_counts[user_input.lower().strip()] += 1
        return new_state

    def topic_drift(self, state: SessionState) -> float:
        if len(state.topics) < 2:
            return 1.0
        recent = state.topics[-self.recent_window:]
        if len(recent) < 2:
            return 1.0
        # Compare consecutive topic sets
        sims = []
        for i in range(1, len(recent)):
            sims.append(self._jaccard(recent[i - 1], recent[i]))
        return sum(sims) / len(sims)

    def is_frustrated(self, state: SessionState) -> bool:
        most_common = state.repeat_counts.most_common(1)
        if not most_common:
            return False
        return most_common[0][1] >= self.frustration_threshold

    def is_topic_drift(self, state: SessionState) -> bool:
        return self.topic_drift(state) < self.drift_threshold
