"""Bayesian confidence update with temperature penalty and assertiveness drift."""
from dataclasses import dataclass
from typing import Dict
from prism.config import get_value


@dataclass
class BayesianState:
    priors: Dict[str, float]          # bias -> prior probability
    assertiveness: float              # 0.0–1.0, capped by max_assertiveness
    wrong_outcome_count: int
    total_outcomes: int


class BayesianEngine:
    def __init__(self):
        self.exploration_penalty = get_value("bayesian", "exploration_penalty", default=0.5)
        self.wrong_threshold = get_value("bayesian", "wrong_outcome_threshold", default=0.3)
        self.assertiveness_step = get_value("bayesian", "assertiveness_step", default=0.05)
        self.max_assertiveness = get_value("bayesian", "max_assertiveness", default=0.6)

    def update(
        self,
        state: BayesianState,
        bias: str,
        confidence: float,
        temperature: float,
        outcome: str,   # "accepted", "rejected", "wrong", "unknown"
    ) -> BayesianState:
        # Likelihood: scale confidence so that values > 0.5 amplify, < 0.5 shrink
        likelihood = 0.5 + confidence  # range 0.5–1.5

        # Exploration penalty: if temperature is high, discount evidence
        if temperature > 0.7:
            likelihood *= self.exploration_penalty

        # Prior
        prior = state.priors.get(bias, 1.0 / len(state.priors))

        # Posterior ∝ likelihood × prior
        posterior = likelihood * prior

        # Renormalize all priors (treat this as a softmax update)
        new_priors = dict(state.priors)
        new_priors[bias] = posterior
        total = sum(new_priors.values())
        if total > 0:
            new_priors = {k: v / total for k, v in new_priors.items()}
        else:
            n = len(new_priors)
            new_priors = {k: 1.0 / n for k in new_priors}

        # Assertiveness drift
        total_outcomes = state.total_outcomes + 1
        wrong_count = state.wrong_outcome_count + (1 if outcome == "wrong" else 0)
        wrong_rate = wrong_count / total_outcomes if total_outcomes > 0 else 0.0

        new_assertiveness = state.assertiveness
        if wrong_rate > self.wrong_threshold:
            new_assertiveness = min(
                state.assertiveness + self.assertiveness_step,
                self.max_assertiveness,
            )

        return BayesianState(
            priors=new_priors,
            assertiveness=new_assertiveness,
            wrong_outcome_count=wrong_count,
            total_outcomes=total_outcomes,
        )

    def initial_state(self, biases: list[str] | None = None) -> BayesianState:
        if biases is None:
            biases = [
                "authority", "confirmation", "sunk_cost", "anchoring",
                "framing", "availability", "conjunction", "overconfidence",
            ]
        n = len(biases)
        return BayesianState(
            priors={b: 1.0 / n for b in biases},
            assertiveness=0.0,
            wrong_outcome_count=0,
            total_outcomes=0,
        )
