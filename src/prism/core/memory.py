"""Memory I/O for Markdown-with-YAML-frontmatter tiers."""
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
import yaml

from prism.config import get_value


@dataclass
class MemoryEntry:
    turn: int
    bias: str
    confidence_human: float
    confidence_ai: float
    route: str
    temperature: float
    outcome: str
    notes: str = ""


def _entry_to_text(entry: MemoryEntry) -> str:
    front = {k: v for k, v in asdict(entry).items() if k != "notes"}
    yaml_front = yaml.dump(front, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return f"---\n{yaml_front}---\n{entry.notes}\n"


def _entry_from_text(text: str) -> MemoryEntry:
    match = re.match(r"^---\n(.*?)---\n(.*)$", text, re.DOTALL)
    if not match:
        raise ValueError("Invalid memory entry format")
    front = yaml.safe_load(match.group(1))
    notes = match.group(2).strip()
    return MemoryEntry(
        turn=front.get("turn", 0),
        bias=front.get("bias", ""),
        confidence_human=front.get("confidence_human", 0.0),
        confidence_ai=front.get("confidence_ai", 0.0),
        route=front.get("route", ""),
        temperature=front.get("temperature", 0.0),
        outcome=front.get("outcome", ""),
        notes=notes,
    )


class MemoryStore:
    def __init__(self, project_root: Path | None = None):
        if project_root is None:
            project_root = Path(__file__).resolve().parents[2]
        self.core_path = project_root / get_value("memory", "core", default="data/memory/core.md")
        self.session_path = project_root / get_value("memory", "session", default="data/memory/session.md")
        self.decisions_path = project_root / get_value("memory", "decisions", default="data/memory/decisions.md")
        self.scratch_path = project_root / get_value("memory", "scratch", default="data/memory/scratch.md")
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        for p in (self.core_path, self.session_path, self.decisions_path, self.scratch_path):
            p.parent.mkdir(parents=True, exist_ok=True)

    def append_decision(self, entry: MemoryEntry) -> None:
        with open(self.decisions_path, "a") as f:
            f.write(_entry_to_text(entry))
            f.write("\n---\n\n")

    def read_decisions(self, limit: int = 50) -> List[MemoryEntry]:
        if not self.decisions_path.exists():
            return []
        raw = self.decisions_path.read_text()
        # Split on horizontal rule separators
        blocks = [b.strip() for b in raw.split("\n---\n") if b.strip()]
        entries = []
        for block in blocks:
            try:
                entries.append(_entry_from_text(block))
            except Exception:
                continue
        return entries[-limit:]

    def write_scratch(self, content: str) -> None:
        with open(self.scratch_path, "w") as f:
            f.write(content)

    def read_scratch(self) -> str:
        if not self.scratch_path.exists():
            return ""
        return self.scratch_path.read_text()

    def append_session(self, entry: MemoryEntry) -> None:
        with open(self.session_path, "a") as f:
            f.write(_entry_to_text(entry))
            f.write("\n---\n\n")

    def read_session(self, limit: int = 10) -> List[MemoryEntry]:
        if not self.session_path.exists():
            return []
        raw = self.session_path.read_text()
        blocks = [b.strip() for b in raw.split("\n---\n") if b.strip()]
        entries = []
        for block in blocks:
            try:
                entries.append(_entry_from_text(block))
            except Exception:
                continue
        return entries[-limit:]
