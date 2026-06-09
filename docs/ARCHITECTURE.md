# PRISM Architecture

## What We Are Building

A **shadow Bayesian scaffold** that sits next to any local LLM conversation. It observes user input, classifies the dominant cognitive bias, runs a Bayesian update to compute confidence, selects a recommended route, and tracks whether that recommendation was useful — but it **does not govern the LLM**. The LLM runs as normal. PRISM is the commentary track.

## Core Concepts

### 1. Temperature as Discovery Phase

| Conversation Phase | Temperature | Behavior |
|--|--|--|
| Early (turns 1–4) | High | Explore formats, vary phrasing, suggest alternatives even if imperfect. Build the probability table fast. |
| Late (turns 5+) | Low | Narrow to confident, validated patterns. Solidify the route map. |
| **Factual data** | **Locked cold** | Names, numbers, dates, technical facts — always accurate. Never exploratory. |

This means the **Bayesian update must weight high-temperature outcomes as noisy samples**, not equal evidence. A "wrong" outcome during exploration is expected noise; a wrong outcome during exploitation is signal.

### 2. Data Is Readable, Not Editable by Hand

All memory lives in **Markdown with YAML frontmatter** (or clean JSON if structured data). The human reads it. The human never `vi` confidence scores. The only editing surface is:** conversation** — including an **editable conversation mode** where the AI writes and the human approves.

```markdown
---
turn: 14
bias: authority
confidence_human: 0.62
confidence_ai: 0.74
route: reframe
temperature: 0.3
outcome: accepted
---
User asked for the "right way" again after being given options.
```

### 3. State Management — Tiered Memory Model

Borrowed from the Pi persistent-memory framework:

| Tier | File | Purpose | Example |
|--|--|--|--|
| **Core** | `memory/core.md` | Invariant beliefs about the human | "User abandons projects when confidence < 0.4" |
| **Session** | `memory/session.md` | Rolling window (last N turns) | Today's conversation flow |
| **Decision log** | `memory/decisions.md` | PRISM's own calls + ground-truth outcomes | "Advised CHALLENGE, user rephrased positively" |
| **Ephemeral** | `memory/scratch.md` | Working draft, discardable | Current turn draft |

### 4. Bayesian Formula — With Error and Temperature

```
P(bias|evidence) ∝ P(evidence|bias) × P_prior(bias)

P_prior_next = P_posterior × (1 - exploration_penalty) + temperature_decay
```

- **Exploration penalty**: If `temperature > 0.7`, new evidence counts at reduced weight (e.g., 0.5×) because the signal is noisier.
- **Temperature decay**: As turns increase, `temperature` decays toward a floor. This is external to the Bayes update — it's a control parameter, not a belief.
- **Assertiveness drift**: When `wrong_outcome_rate > threshold`, PRISM becomes bolder in its routing recommendations (not the LLM's tone — just the scaffold's suggestion).

## Module Map

```
Input
  │
  ▼
┌─────────────────────┐
│  Intent Extractor   │  (lightweight — goal, constraints, context)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Hybrid Classifier  │  (keywords + embeddings; LLM classifier disabled by default)
│  ├─ keyword module  │
│  └─ embed module    │  (calls Ollama /api/embed)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Co-Occurrence      │  (detects compounding bias pairs)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Session Tracker    │  (topic drift, repeat asks, frustration arc)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Confidence Floor   │  (PRODUCE / CLARIFY / REFUSE gate)
│  ├─ applies temp    │
│  └─ applies penalty │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Bayesian Update    │  (posterior + assertiveness drift)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Route Selector     │  (comply / reframe / clarify / challenge)
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │  Outcome     │  (delayed — inferred from next user message)
    │  Feedback    │
    └──────────────┘
```

## Kill Switches

In `config.yaml`:

```yaml
prism:
  enabled: true          # false = bypass entirely
  mode: shadow           # shadow = log only; active = inject into system prompt
  temperature:
    strategy: adaptive
    initial: 0.8
    floor: 0.2
    decay_rate: 0.15
    factual_lock: true     # always 0.0 for data queries
```

## What Is Missing Right Now

1. Real centroids (will generate from hand-labeled examples once embedding model is pulled).
2. Async HTTP layer (currently synchronous in research code).
3. Held-out evaluation set (will log real conversations and label them).

## What Works in Principle vs Reality

| Component | Principle | Reality Gap |
|--|--|--|
| Keyword classifier | Works now | Coarse but fast |
| Embedding classifier | Works if centroids are real | Centroids are fiction until we generate them |
| Session tracker | Session JSON + timestamps | Needs robust JSON read/write |
| Bayesian math | Formula is correct | Priors are arbitrary; they'll self-correct with data |
| Outcome feedback | Needs next message | Requires stateful turn tracking |

## Backup Strategy

1. `data/` lives inside Dropbox workspace. Synced by existing timers.
2. Everything is plain text. No binary blobs.
3. Stop PRISM: set `enabled: false`. It disappears. No lock-in.
