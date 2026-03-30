"""EvolutionEngine — facade that ties all sub-engines together."""

from __future__ import annotations

from pathlib import Path

from evolve_kit.insight import InsightEngine
from evolve_kit.memory import MemoryManager
from evolve_kit.validator import SelfValidator
from evolve_kit.scorer import PerformanceScorer
from evolve_kit.guard import EvolutionGuard
from evolve_kit.maturity import MaturityScorer
from evolve_kit.achievements import AchievementEngine
from evolve_kit.skill_tree import SkillTree
from evolve_kit.types import (
    Insight, MemoryEntry, ValidationResult,
    ScoreResult, GuardResult, MaturityReport,
    XP_TABLE,
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
        self._base = Path(workspace_dir) / "evolve-data"
        self._base.mkdir(parents=True, exist_ok=True)

        self._insight_engine = InsightEngine(self._base / "insights.jsonl")
        self._memory_manager = MemoryManager(
            self._base / "memory.json",
            self._base / "deletions.jsonl",
        )
        self._validator = SelfValidator(self._base / "validations.jsonl")
        self._scorer = PerformanceScorer(self._base / "scores.jsonl")
        self._guard = EvolutionGuard(self._base / "guard-log.jsonl")
        self._maturity = MaturityScorer()

    @property
    def achievements(self) -> AchievementEngine:
        """Lazily-created achievement engine."""
        if not hasattr(self, "_achievement_engine"):
            self._achievement_engine = AchievementEngine(self._base / "achievements")
        return self._achievement_engine

    @property
    def skill_tree(self) -> SkillTree:
        """Lazily-created skill tree engine."""
        if not hasattr(self, "_skill_tree"):
            self._skill_tree = SkillTree(self._base / "skill-tree")
        return self._skill_tree

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

    # ── XP / Level system ────────────────────────────────────────────

    @property
    def xp_total(self) -> int:
        """Total XP earned: insights×20 + scores×30 + memory×15."""
        return (
            self._insight_engine.count() * 20
            + self._scorer.count() * 30
            + self._memory_manager.count() * 15
        )

    @property
    def level(self) -> int:
        """Current level derived from XP total."""
        xp = self.xp_total
        current_level = 1
        for lvl, threshold in XP_TABLE:
            if xp >= threshold:
                current_level = lvl
            else:
                break
        return current_level

    @property
    def xp_to_next(self) -> int:
        """XP needed to reach the next level (0 if already max)."""
        xp = self.xp_total
        for lvl, threshold in XP_TABLE:
            if xp < threshold:
                return threshold - xp
        return 0

    @property
    def xp_progress(self) -> float:
        """Progress within the current level as a 0.0–1.0 fraction."""
        xp = self.xp_total
        current_level = self.level
        # Find current level threshold
        current_threshold = 0
        next_threshold = 0
        for lvl, threshold in XP_TABLE:
            if lvl == current_level:
                current_threshold = threshold
            if lvl == current_level + 1:
                next_threshold = threshold
        if next_threshold == 0:
            return 1.0  # max level
        span = next_threshold - current_threshold
        if span == 0:
            return 1.0
        return (xp - current_threshold) / span

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
