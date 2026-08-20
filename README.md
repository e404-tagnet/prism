<!-- TAGNET README HEADER — Catppuccin Mocha — do not edit by hand -->
<div align="center">

[![License](https://img.shields.io/github/license/e404-tagnet/prism-scaffold?color=313244&labelColor=11111b&label=License&style=flat-square)](https://github.com/e404-tagnet/prism-scaffold/blob/main/LICENSE)
[![Status](https://img.shields.io/badge/Status-stable-a6e3a1?labelColor=11111b&style=flat-square)](https://github.com/e404-tagnet/prism-scaffold/pulse)
[![Version](https://img.shields.io/github/v/release/e404-tagnet/prism-scaffold?color=313244&labelColor=11111b&label=Version&style=flat-square)](https://github.com/e404-tagnet/prism-scaffold/releases)
[![Repo](https://img.shields.io/badge/Repo-prism-scaffold-94e2d5?labelColor=11111b&style=flat-square&logo=github&logoColor=94e2d5)](https://github.com/e404-tagnet/prism-scaffold)
[![Tagnet](https://img.shields.io/badge/By-Tagnet-89dceb?labelColor=11111b&style=flat-square&logo=tag&logoColor=89dceb)](https://tagnet.dev)

</div>
<!-- TAGNET README HEADER — end -->

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

<!-- TAGNET README FOOTER — start -->

<div align="center">

**Like this work? Fuel the next widget / experiment / scaffold.**

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-%23FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/e404.tagnet)
[![Patreon](https://img.shields.io/badge/Support-Patreon-ff424d?logo=patreon&logoColor=white&style=for-the-badge)](https://www.patreon.com/VeritasExMachina?utm_campaign=creatorshare_creator)

<small>Crafted with caffeine, curiosity, and a Catppuccin palette · © e404-tagnet</small>

</div>
<!-- TAGNET README FOOTER — end -->
