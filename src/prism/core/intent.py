"""Lightweight intent extraction from user input."""
import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Intent:
    goal: str
    constraints: List[str]
    context_phrases: List[str]
    is_factual: bool
    question_words: List[str]


# Simple keyword triggers for factual lock (mirrors config)
FACTUAL_TRIGGERS = [
    "what is", "how many", "how much", "date", "version",
    "exact", "accurate", "who is", "when did", "where is",
    "define", "list the", "calculate", "compute", "true or false"
]

QUESTION_WORDS = ["what", "how", "why", "when", "where", "who", "which", "can", "should", "would", "could", "is", "are", "does", "do"]


def extract(user_input: str) -> Intent:
    text_lower = user_input.lower().strip()

    # Factual detection
    is_factual = any(trig in text_lower for trig in FACTUAL_TRIGGERS)

    # Question words
    question_words = [w for w in QUESTION_WORDS if re.search(rf"\b{w}\b", text_lower)]

    # Naive goal: first sentence or first 10 words
    sentences = re.split(r"[.!?]", user_input)
    goal = sentences[0].strip() if sentences else user_input.strip()
    if len(goal.split()) > 15:
        goal = " ".join(goal.split()[:15]) + "..."

    # Constraints: phrases after "but", "however", "unless", "if", "without"
    constraint_markers = ["but", "however", "unless", "if", "without", "as long as", "only if", "given that"]
    constraints = []
    for marker in constraint_markers:
        if marker in text_lower:
            # capture rest of sentence after marker
            idx = text_lower.find(marker)
            tail = user_input[idx:].split(".")[0].strip()
            if len(tail) > len(marker) + 1:
                constraints.append(tail)

    # Context: quoted phrases, references to prior turns ("you said", "earlier")
    context_phrases = []
    quoted = re.findall(r'"([^"]+)"', user_input)
    context_phrases.extend(quoted)
    prior_refs = ["you said", "earlier", "before", "last time", "as we discussed", "remember"]
    for ref in prior_refs:
        if ref in text_lower:
            context_phrases.append(ref)

    return Intent(
        goal=goal,
        constraints=constraints,
        context_phrases=context_phrases,
        is_factual=is_factual,
        question_words=question_words,
    )
