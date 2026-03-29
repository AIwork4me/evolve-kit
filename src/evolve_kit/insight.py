"""Insight Engine — distill structured insights from task outcomes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from evolve_kit.types import Insight


class InsightEngine:
    """Records, stores, and retrieves structured insights.

    Each insight follows the pattern:
        [Fact] What happened (verifiable)
        [Judgment] What I learned
        [Action] What I'll do differently next time

    Based on: Expel, ReasoningBank (arXiv 2507.21046 Section 3.2.1)
    """

    def __init__(self, store_path: str | Path = "./evolve-data/insights.jsonl"):
        self._path = Path(store_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        fact: str,
        judgment: str,
        action: str,
        source_task: str = "",
        tags: Optional[list[str]] = None,
    ) -> Insight:
        """Record a structured insight."""
        insight = Insight(
            fact=fact,
            judgment=judgment,
            action=action,
            source_task=source_task,
            tags=tags or [],
        )
        self._append(insight)
        return insight

    def list_recent(self, n: int = 10) -> list[Insight]:
        """List the N most recent insights."""
        insights = self._read_all()
        return insights[-n:]

    def list_by_tag(self, tag: str) -> list[Insight]:
        """List insights matching a tag."""
        return [i for i in self._read_all() if tag in i.tags]

    def list_by_task(self, task: str) -> list[Insight]:
        """List insights from a specific task."""
        return [i for i in self._read_all() if i.source_task == task]

    def search(self, query: str) -> list[Insight]:
        """Full-text search across all insights."""
        q = query.lower()
        return [
            i
            for i in self._read_all()
            if q in i.fact.lower() or q in i.judgment.lower() or q in i.action.lower()
        ]

    def count(self) -> int:
        """Total number of insights."""
        return len(self._read_all())

    def _append(self, insight: Insight) -> None:
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(insight.to_dict(), ensure_ascii=False) + "\n")

    def _read_all(self) -> list[Insight]:
        if not self._path.exists():
            return []
        insights: list[Insight] = []
        with open(self._path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    insights.append(Insight.from_dict(json.loads(line)))
        return insights
