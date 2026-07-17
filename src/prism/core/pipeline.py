"""Main PRISM pipeline orchestrator."""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pathlib import Path

from prism.config import get, get_value
from prism.core.intent import extract as extract_intent, Intent
from prism.classifiers.hybrid import HybridClassifier, HybridResult
from prism.core.bayesian import BayesianEngine, BayesianState
from prism.routes.selector import RouteSelector, RouteResult
from prism.core.memory import MemoryStore, MemoryEntry
from prism.core.session import SessionTracker, SessionState


@dataclass
class PipelineResult:
    intent: Intent
    classification: HybridResult
    route: RouteResult
    temperature: float
    bayesian_state: BayesianState
    session_state: SessionState
    turn_number: int
    meta: Dict[str, Any] = field(default_factory=dict)


class PrismPipeline:
    def __init__(self, project_root: Path | None = None):
        if project_root is None:
            project_root = Path(__file__).resolve().parents[2]
        self.config = get()
        self.classifier = HybridClassifier()
        self.bayesian = BayesianEngine()
        self.selector = RouteSelector()
        self.memory = MemoryStore(project_root)
        self.tracker = SessionTracker()
        self._bayesian_state = self.bayesian.initial_state()
        self._session_state = SessionState()
        self._turn_counter = 0

    @property
    def bayesian_state(self) -> BayesianState:
        return self._bayesian_state

    @property
    def session_state(self) -> SessionState:
        return self._session_state

    def compute_temperature(self, intent: Intent, turn: int) -> float:
        strategy = get_value("temperature", "strategy", default="adaptive")
        if strategy != "adaptive":
            return get_value("temperature", "initial", default=0.85)

        if intent.is_factual and get_value("temperature", "factual_lock", default=True):
            return get_value("temperature", "floor", default=0.2)

        initial = get_value("temperature", "initial", default=0.85)
        floor = get_value("temperature", "floor", default=0.2)
        decay = get_value("temperature", "decay_rate", default=0.12)
        temp = max(initial - (decay * turn), floor)
        return float(temp)

    def process(self, user_input: str, previous_outcome: str = "unknown") -> PipelineResult:
        self._turn_counter += 1
        turn = self._turn_counter

        # 1. Intent extraction
        intent = extract_intent(user_input)

        # 2. Temperature
        temperature = self.compute_temperature(intent, turn)

        # 3. Classification
        classification = self.classifier.classify(user_input)

        # 4. Bayesian update
        self._bayesian_state = self.bayesian.update(
            state=self._bayesian_state,
            bias=classification.bias,
            confidence=classification.confidence,
            temperature=temperature,
            outcome=previous_outcome,
        )

        # 5. Route selection
        route = self.selector.select(
            bias=classification.bias,
            confidence=classification.confidence,
            assertiveness=self._bayesian_state.assertiveness,
        )

        # 6. Session tracking
        self._session_state = self.tracker.add_turn(self._session_state, user_input)
        self._session_state.last_route = route.route

        # 7. Meta
        meta: Dict[str, Any] = {
            "topic_drift": self.tracker.topic_drift(self._session_state),
            "is_frustrated": self.tracker.is_frustrated(self._session_state),
            "is_topic_drift": self.tracker.is_topic_drift(self._session_state),
        }

        # 8. Memory log (shadow mode — just record)
        entry = MemoryEntry(
            turn=turn,
            bias=classification.bias,
            confidence_human=0.0,  # placeholder until human feedback
            confidence_ai=classification.confidence,
            route=route.route,
            temperature=temperature,
            outcome=previous_outcome,
            notes=f"User: {user_input[:120]}",
        )
        self.memory.append_decision(entry)
        self.memory.append_session(entry)

        return PipelineResult(
            intent=intent,
            classification=classification,
            route=route,
            temperature=temperature,
            bayesian_state=self._bayesian_state,
            session_state=self._session_state,
            turn_number=turn,
            meta=meta,
        )

    def reset(self) -> None:
        self._bayesian_state = self.bayesian.initial_state()
        self._session_state = SessionState()
        self._turn_counter = 0
