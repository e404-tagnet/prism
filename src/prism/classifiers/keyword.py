"""Keyword-based bias classifier."""
import re
from typing import Dict, Tuple

# Keyword maps: bias -> list of regex patterns or literal strings
KEYWORD_MAP: Dict[str, list] = {
    "authority": [
        r"\bcorrect\b", r"\bright\s+answer\b", r"\bofficial\b", r"\bexpert\b",
        r"\brecommend\b", r"\bindustry\s+standard\b", r"\bdefinitive\b",
        r"\bresearch\s+says\b", r"\bleading\s+expert\b", r"\bauthoritative\b",
        r"\bwhat\s+is\s+the\s+best\b", r"\bgive\s+me\s+the\s+answer\b",
    ],
    "confirmation": [
        r"\bconfirm\b", r"\bback\s+that\s+up\b", r"\bsupport\s+my\b",
        r"\bI\s+knew\b", r"\bvalidate\b", r"\breassurance\b",
        r"\bproves?\b", r"\bagree\b", r"\bright\?\b",
    ],
    "sunk_cost": [
        r"\balready\s+spent\b", r"\binvested\s+too\s+much\b", r"\bcan't\s+quit\b",
        r"\bhave\s+to\s+finish\b", r"\bcome\s+this\s+far\b", r"\bwasted\b",
        r"\bcommitted\s+resources\b", r"\bbuilt\s+this\b", r"\bsunk\s+cost\b",
        r"\bcan't\s+leave\b",
    ],
    "anchoring": [
        r"\baround\b", r"\bfirst\s+number\b", r"\binitially\b", r"\bfirst\s+price\b",
        r"\banchored?\b", r"\bfirst\s+offer\b", r"\bfirst\s+example\b",
        r"\bshaped\s+my\b", r"\binitial\b",
    ],
    "framing": [
        r"\bsurvival\s+rate\b", r"\bmortality\b", r"\blimited\s+time\b",
        r"\bframing\b", r"\bphrased\s+as\b", r"\bfat\s+free\b",
        r"\bworded\b", r"\bpresented\s+as\b", r"\bhow\s+they\b",
    ],
    "availability": [
        r"\bsaw\s+it\s+on\b", r"\bvivid\b", r"\brecent\s+events\b",
        r"\beasy\s+to\s+recall\b", r"\bmedia\s+coverage\b", r"\bshocking\b",
        r"\bhappens\s+all\s+the\s+time\b", r"\bcommon\b",
    ],
    "conjunction": [
        r"\band\s+a\b", r"\band\b.*\band\b", r"\bmore\s+plausible\b",
        r"\bmore\s+believable\b", r"\bricher\s+story\b", r"\bcomplex\s+explanation\b",
        r"\bmore\s+likely\b", r"\bprobable\b",
    ],
    "overconfidence": [
        r"\babsolutely\s+certain\b", r"\bno\s+way\s+I\b", r"\bnever\s+wrong\b",
        r"\b100%\s+sure\b", r"\bfigured\s+out\b", r"\bdon't\s+need\s+to\s+check\b",
        r"\bmy\s+intuition\b", r"\bknow\s+this\s+inside\b", r"\btrust\s+me\b",
    ],
}


def classify(text: str) -> Dict[str, float]:
    """Return keyword scores for each bias (0.0–1.0)."""
    text_lower = text.lower()
    scores: Dict[str, float] = {bias: 0.0 for bias in KEYWORD_MAP}

    for bias, patterns in KEYWORD_MAP.items():
        hits = 0
        for pat in patterns:
            if re.search(pat, text_lower):
                hits += 1
        # Normalize by number of patterns in category to avoid category-size bias
        scores[bias] = min(hits / max(len(patterns) * 0.3, 1.0), 1.0)

    return scores


def dominant(text: str) -> Tuple[str, float]:
    scores = classify(text)
    best = max(scores, key=lambda k: scores[k])
    return best, scores[best]
