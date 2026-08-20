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
    "bandwagon": [
        r"\beveryone\s+else\b", r"\bmost\s+people\b", r"\bthe\s+whole\s+team\b",
        r"\bdepartment\s+knows\b", r"\bpopular\b", r"\btrending\b",
        r"\bconsensus\b", r"\bwidely\s+accepted\b",
    ],
    "belief_bias": [
        r"\bseems\s+about\s+right\b", r"\bbelievable\b", r"\bplausible\b",
        r"\bconclusion\s+feels\b", r"\bdoesn't\s+follow\b", r"\bcan't\s+argue\b",
    ],
    "blind_spot": [
        r"\bignore\s+her\b", r"\bignore\s+his\b", r"\bshe's\s+biased\b",
        r"\bhe's\s+biased\b", r"\bnot\s+objective\b", r"\blacks\s+perspective\b",
    ],
    "clustering_illusion": [
        r"\bpattern\b", r"\bcluster\b", r"\bthree\s+times\b", r"\bhappened\s+again\b",
        r"\bsecond\s+week\b", r"\bthere\s+must\s+be\b", r"\bcoincidence\b",
    ],
    "courtesy_bias": [
        r"\blet's\s+move\s+on\b", r"\bavoid\s+offence\b", r"\bsocially\s+acceptable\b",
        r"\bnot\s+worth\s+arguing\b", r"\bagree\s+to\s+disagree\b",
    ],
    "endowment": [
        r"\bcost\s+us\b", r"\balready\s+paid\b", r"\bcost\s+a\s+fortune\b",
        r"\bcan't\s+throw\s+it\s+away\b", r"\bwe\s+built\b", r"\bwe\s+own\b",
    ],
    "gambler_fallacy": [
        r"\bdue\b", r"\boverdue\b", r"\bunlikely\s+again\b", r"\bthree\s+times\b",
        r"\bprobability\s+changed\b", r"\bluck\s+is\s+turning\b",
    ],
    "hyperbolic_discounting": [
        r"\bASAP\b", r"\bsooner\b", r"\bright\s+now\b", r"\bquick\s+win\b",
        r"\bimmediate\b", r"\bdelay\b", r"\blater\s+reward\b",
    ],
    "illusion_of_validity": [
        r"\bworked\s+fine\s+before\b", r"\bshould\s+work\s+fine\b",
        r"\bcoherent\s+story\b", r"\bprediction\s+accurate\b", r"\bdata\s+tells\b",
    ],
    "ostrich": [
        r"\brun\s+out\s+of\s+time\b", r"\bpretending\s+it\s+doesn't\s+exist\b",
        r"\bignoring\s+the\b", r"\bavoid\s+negative\b", r"\bnot\s+looking\b",
    ],
    "post_purchase": [
        r"\bgood\s+call\b", r"\bwe\s+chose\s+well\b", r"\bright\s+decision\b",
        r"\bwould\s+do\s+it\s+again\b", r"\bno\s+regrets\b",
    ],
    "reactive_devaluation": [
        r"\bcompetitors\b", r"\btheir\s+products\b", r"\badversary\b",
        r"\bopponent\b", r"\bnot\s+our\s+idea\b", r"\bcame\s+from\b",
    ],
    "risk_compensation": [
        r"\bnew\s+equipment\b", r"\bcut\s+the\s+time\b", r"\bsafer\s+now\b",
        r"\bless\s+careful\b", r"\btake\s+bigger\s+risks\b",
    ],
    "status_quo": [
        r"\bif\s+it\s+(?:ain't|is\s+not)\s+broke\b", r"\bdon't\s+fix\b", r"\bcurrent\s+state\b",
        r"\bwhy\s+change\b", r"\balways\s+done\s+this\s+way\b",
    ],
    "stereotyping": [
        r"\balways\s+pessimists\b", r"\balways\s+optimists\b", r"\bthose\s+people\b",
        r"\btypical\b", r"\ball\s+of\s+them\b", r"\bjust\s+like\b",
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
