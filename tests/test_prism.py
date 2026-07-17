"""Tests for Bayesian math and classifier logic."""
import pytest
import math
from prism.core.bayesian import BayesianEngine, BayesianState
from prism.classifiers.keyword import classify as kw_classify, dominant as kw_dominant
from prism.classifiers.hybrid import HybridClassifier
from prism.core.intent import extract as extract_intent
from prism.routes.selector import RouteSelector


class TestBayesianEngine:
    def test_initial_state_uniform(self):
        engine = BayesianEngine()
        state = engine.initial_state(["a", "b", "c"])
        assert pytest.approx(state.priors["a"]) == 1 / 3
        assert pytest.approx(state.priors["b"]) == 1 / 3
        assert pytest.approx(state.priors["c"]) == 1 / 3

    def test_posterior_update(self):
        engine = BayesianEngine()
        state = engine.initial_state(["authority", "confirmation"])
        new_state = engine.update(state, "authority", confidence=0.9, temperature=0.3, outcome="accepted")
        # After a strong positive signal, authority prior should increase
        assert new_state.priors["authority"] > new_state.priors["confirmation"]

    def test_exploration_penalty(self):
        engine = BayesianEngine()
        state = engine.initial_state(["authority", "confirmation"])
        hot = engine.update(state, "authority", confidence=0.9, temperature=0.85, outcome="accepted")
        cold = engine.update(state, "authority", confidence=0.9, temperature=0.3, outcome="accepted")
        # Hot temperature should dampen the update vs cold
        assert hot.priors["authority"] < cold.priors["authority"]

    def test_assertiveness_drift(self):
        engine = BayesianEngine()
        state = engine.initial_state(["authority", "confirmation"])
        for _ in range(5):
            state = engine.update(state, "authority", confidence=0.5, temperature=0.4, outcome="wrong")
        assert state.assertiveness > 0.0
        assert state.assertiveness <= engine.max_assertiveness


class TestKeywordClassifier:
    def test_authority_detection(self):
        scores = kw_classify("Tell me the right answer from an expert")
        assert scores["authority"] > 0.0

    def test_confirmation_detection(self):
        scores = kw_classify("Can you confirm what I already know?")
        assert scores["confirmation"] > 0.0

    def test_dominant_returns_tuple(self):
        bias, conf = kw_dominant("What is the official correct way?")
        assert isinstance(bias, str)
        assert 0.0 <= conf <= 1.0


class TestIntentExtractor:
    def test_factual_detection(self):
        intent = extract_intent("What is the capital of France?")
        assert intent.is_factual is True

    def test_non_factual(self):
        intent = extract_intent("I feel like this is a bad idea.")
        assert intent.is_factual is False

    def test_constraints(self):
        intent = extract_intent("Do this but only if it is safe.")
        assert any("only if" in c.lower() for c in intent.constraints)


class TestRouteSelector:
    def test_low_confidence_clarify(self):
        sel = RouteSelector()
        route = sel.select("authority", confidence=0.1)
        assert route.route == "clarify"
        assert route.confidence_ok is False

    def test_bias_route_map(self):
        sel = RouteSelector()
        route = sel.select("sunk_cost", confidence=0.8)
        assert route.route == "challenge"

    def test_assertiveness_escalation(self):
        sel = RouteSelector()
        route = sel.select("authority", confidence=0.8, assertiveness=0.4)
        assert route.route == "challenge"
