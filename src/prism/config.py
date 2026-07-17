"""Config loader — reads config.yaml and exposes typed access."""
import yaml
from pathlib import Path
from typing import Any, Dict

_CONFIG: Dict[str, Any] = {}


def load(path: Path | None = None) -> Dict[str, Any]:
    global _CONFIG
    if path is None:
        # project root is two levels up from this file: src/prism/config.py
        path = Path(__file__).resolve().parents[2] / "config.yaml"
    with open(path, "r") as f:
        raw = yaml.safe_load(f)
    _CONFIG = raw.get("prism", {})
    return _CONFIG


def get() -> Dict[str, Any]:
    if not _CONFIG:
        load()
    return _CONFIG


def get_value(*keys: str, default: Any = None) -> Any:
    node = get()
    for k in keys:
        if isinstance(node, dict) and k in node:
            node = node[k]
        else:
            return default
    return node
