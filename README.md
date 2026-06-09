# PRISM

**P**robability-based **R**easoning / **I**ntent / **S**caffold / **M**iddleware

A shadow cognitive layer for local LLM conversations. Classifies cognitive bias in user input, computes Bayesian confidence, recommends interaction routes, and learns from inferred outcomes — without governing the actual response.

> Human-readable. AI-editable. Human-protected.

## Philosophy

- **Architecture first.** No UI. No integration hooks until the mechanism is sound.
- **Local only.** Everything runs on the AG2i stack via Ollama.
- **Exploration built in.** Early turns run hotter (diverse formats, approaches) to populate the probability table quickly. Factual accuracy is ring-fenced and always cold.
- **Tamper-evident.** The human reads the memory, but edits it only through conversation — never by hand.

## Status

Architecture phase. Research prototypes live elsewhere.
