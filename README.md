# PRISM

**P**robability-based **R**easoning / **I**ntent / **S**caffold / **M**iddleware

A shadow cognitive layer for local LLM conversations. Classifies cognitive bias in user input, computes Bayesian confidence, recommends interaction routes, and learns from inferred outcomes, all without governing the actual response.

> Human-readable. AI-editable. Human-protected.

## Philosophy

- **Architecture first.** No UI. No integration hooks until the mechanism is sound.
- **Local only.** Everything runs on the local machine via Ollama.
- **Exploration built in.** Early turns run hotter (diverse formats, approaches) to populate the probability table quickly. Factual accuracy is ring-fenced and always cold.
- **Tamper-evident.** The human reads the memory, but edits it only through conversation and never by hand.

## Status

Core pipeline implemented. Shadow-mode CLI operational. 13 tests passing. Centroids are real (nomic-embed-text, 768-dim).

## Quick Start

```bash
cd /path/to/prism-scaffold
PYTHONPATH=src:$PYTHONPATH python3 -m prism.cli "Your message here" --json
```

Or run interactively:

```bash
PYTHONPATH=src:$PYTHONPATH python3 -m prism.cli
```

Type `quit` to exit, `reset` to clear session state.

## Running Tests

```bash
PYTHONPATH=src:$PYTHONPATH pytest tests/test_prism.py -v
```

## Project Structure

```
src/prism/
  config.py              # Typed config.yaml loader
  cli.py                 # Shadow-mode CLI entry point
  core/
    intent.py            # Lightweight intent extraction
    bayesian.py          # Posterior updates + assertiveness drift
    memory.py            # Markdown+YAML frontmatter I/O
    pipeline.py          # Main orchestrator
    session.py           # Topic drift + frustration tracking
  classifiers/
    keyword.py           # Regex-based bias detection
    embedding.py         # Cosine-similarity against centroids
    hybrid.py            # Configurable keyword/embedding blend
  routes/
    selector.py          # Bias-to-route mapper with confidence floors
  integration/
    ollama.py            # HTTP client for /api/embed
centroids/
  bias-centroids.json    # Real embeddings (8 categories × 768 dims)
tests/
  test_prism.py          # 13 tests for core logic
```
