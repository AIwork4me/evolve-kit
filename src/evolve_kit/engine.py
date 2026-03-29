"""EvolutionEngine — facade that ties all sub-engines together."""

from __future__ import annotations

from pathlib import Path

from evolve_kit.insight import InsightEngine
from evolve_kit.memory import MemoryManager
from evolve_kit.validator import SelfValidator
from evolve_kit.scorer import PerformanceScorer
from evolve_kit.guard import EvolutionGuard
from evolve_kit.maturity import MaturityScorer
from evolve_kit.types import (
    Insight, MemoryEntry, ValidationResult,
    ScoreResult, GuardResult, MaturityReport,
)


class EvolutionEngine:
    """Unified facade for agent self-evolution.

    Usage:
        engine = EvolutionEngine("./my-workspace")
        engine.insight("fact", "judgment", "action")
        engine.score("task", 4)
        report = engine.report()
    """

    def __init__(self, workspace_dir: str | Path = "."):
        base = Path(workspace_dir) / "evolve-data"
        base.mkdir(parents=True, exist_ok=True)

        self._insight_engine = InsightEngine(base / "insights.jsonl")
        self._memory_manager = MemoryManager(
            base / "memory.json",
            base / "deletions.jsonl",
        )
        self._validator = SelfValidator(base / "validations.jsonl")
        self._scorer = PerformanceScorer(base / "scores.jsonl")
        self._guard = EvolutionGuard(base / "guard-log.jsonl")
        self._maturity = MaturityScorer()

    @property
    def memory(self) -> MemoryManager:
        return self._memory_manager

    @property
    def insights(self) -> InsightEngine:
        return self._insight_engine

    @property
    def scores(self) -> PerformanceScorer:
        return self._scorer

    def insight(
        self,
        fact: str,
        judgment: str,
        action: str,
        source_task: str = "",
        tags: list[str] | None = None,
    ) -> Insight:
        """Record a structured insight."""
        return self._insight_engine.record(fact, judgment, action, source_task, tags)

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
        return self._scorer.score(
            task_name, quality, time_minutes, human_intervention, rework, notes
        )

    def validate_command(
        self,
        command: str,
        category: str = "command",
        timeout: int = 30,
    ) -> ValidationResult:
        """Run a validation command."""
        return self._validator.validate_command(command, category, timeout)

    def validate_file(
        self,
        path: str,
        expected_content: str | None = None,
    ) -> ValidationResult:
        """Validate a file exists and optionally contains content."""
        return self._validator.validate_file(path, expected_content)

    def guard(
        self,
        changes: list[str],
        checks: list[str] | None = None,
        custom_checks: dict[str, bool] | None = None,
    ) -> GuardResult:
        """Run evolution safety guard."""
        result = self._guard.verify_evolution(changes, checks, custom_checks)
        self._guard.log(result)
        return result

    def report(
        self,
        manual_scores: dict[str, float] | None = None,
    ) -> MaturityReport:
        """Generate a maturity report."""
        return self._maturity.score(
            memory_manager=self._memory_manager,
            insight_engine=self._insight_engine,
            scorer=self._scorer,
            validator=self._validator,
            guard=self._guard,
            manual_scores=manual_scores,
        )
