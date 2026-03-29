"""Performance Scorer — track task quality over time."""

from __future__ import annotations

import json
from pathlib import Path

from evolve_kit.types import ScoreResult


class PerformanceScorer:
    """Record and analyze task performance scores.

    Based on: quantitative self-assessment (arXiv 2507.21046 Section 3.2.3)
    """

    def __init__(self, store_path: str | Path = "./evolve-data/scores.jsonl"):
        self._path = Path(store_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def score(
        self,
        task_name: str,
        quality: int,
        time_minutes: float = 0,
        human_intervention: int = 0,
        rework: bool = False,
        notes: str = "",
    ) -> ScoreResult:
        """Record a task performance score."""
        if not 1 <= quality <= 5:
            raise ValueError(f"quality must be 1-5, got {quality}")

        result = ScoreResult(
            task_name=task_name,
            quality=quality,
            time_minutes=time_minutes,
            human_intervention=human_intervention,
            rework=rework,
            notes=notes,
        )
        self._append(result)
        return result

    def list_recent(self, n: int = 10) -> list[ScoreResult]:
        """List the N most recent scores."""
        scores = self._read_all()
        return scores[-n:]

    def average_quality(self) -> float:
        """Average quality score across all tasks."""
        scores = self._read_all()
        if not scores:
            return 0.0
        return sum(s.quality for s in scores) / len(scores)

    def count(self) -> int:
        """Total number of scored tasks."""
        return len(self._read_all())

    def _append(self, result: ScoreResult) -> None:
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")

    def _read_all(self) -> list[ScoreResult]:
        if not self._path.exists():
            return []
        scores: list[ScoreResult] = []
        with open(self._path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    scores.append(ScoreResult.from_dict(json.loads(line)))
        return scores
