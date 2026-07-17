"""Route selector: maps bias+confidence to a recommended interaction route."""
from dataclasses import dataclass
from typing import Dict
from prism.config import get_value

ROUTES: Dict[str, str] = {
    "comply": "Acknowledge and proceed.",
    "reframe": "Offer alternatives or broaden perspective.",
    "clarify": "Probe for missing constraints or context.",
    "challenge": "Gently push back on assumptions or bias.",
}

ROUTE_THRESHOLDS = {
    "produce": 0.55,
    "clarify": 0.30,
}

BIAS_ROUTE_MAP = {
    "authority": "comply",
    "confirmation": "clarify",
    "sunk_cost": "challenge",
    "anchoring": "reframe",
    "framing": "reframe",
    "availability": "challenge",
    "conjunction": "clarify",
    "overconfidence": "challenge",
}


@dataclass
class RouteResult:
    route: str
    reason: str
    system_prompt_addition: str
    confidence_ok: bool


class RouteSelector:
    def __init__(self):
        self.produce_threshold = get_value("confidence", "produce_threshold", default=0.55)
        self.clarify_threshold = get_value("confidence", "clarify_threshold", default=0.30)
        self.routes_meta = get_value("routes", default={})

    def select(self, bias: str, confidence: float, assertiveness: float = 0.0) -> RouteResult:
        if confidence < self.clarify_threshold:
            reason = (
                f"Confidence ({confidence:.2f}) below clarify threshold "
                f"({self.clarify_threshold:.2f}). Request more context."
            )
            return RouteResult(
                route="clarify",
                reason=reason,
                system_prompt_addition=self._prompt_for("clarify"),
                confidence_ok=False,
            )

        base_route = BIAS_ROUTE_MAP.get(bias, "comply")

        # Assertiveness drift: if assertiveness is high, escalate from comply -> challenge, reframe -> challenge
        if assertiveness > 0.3 and base_route in ("comply", "reframe"):
            base_route = "challenge"
            reason = f"Assertiveness drift triggered ({assertiveness:.2f}). Escalated to challenge."
        else:
            reason = f"Bias '{bias}' with confidence {confidence:.2f} maps to route '{base_route}'."

        return RouteResult(
            route=base_route,
            reason=reason,
            system_prompt_addition=self._prompt_for(base_route),
            confidence_ok=True,
        )

    def _prompt_for(self, route: str) -> str:
        meta = self.routes_meta.get(route, {})
        return meta.get("system_prompt_addition", "")
