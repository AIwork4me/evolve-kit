"""Skill tree system for evolve-kit."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Skill:
    name: str
    icon: str
    dimension: str  # which maturity dimension this skill maps to
    threshold: float  # dimension value needed to unlock
    description: str
    unlocked: bool = False
    progress: float = 0.0  # 0.0-1.0 toward unlock


SKILL_DEFS: list[dict] = [
    {"name": "洞察之眼", "icon": "👁️", "dimension": "insight_loop", "threshold": 3.0, "description": "洞察力达到3级"},
    {"name": "永恒记忆", "icon": "🧠", "dimension": "memory_lifecycle", "threshold": 7.0, "description": "记忆管理达到7级"},
    {"name": "自省大师", "icon": "🪞", "dimension": "reflection", "threshold": 5.0, "description": "反思能力达到5级"},
    {"name": "安全守卫", "icon": "🛡️", "dimension": "safety_guardrails", "threshold": 6.0, "description": "安全守卫达到6级"},
    {"name": "工具大师", "icon": "🔧", "dimension": "tool_lifecycle", "threshold": 5.0, "description": "工具管理达到5级"},
    {"name": "架构师", "icon": "🏗️", "dimension": "architecture_search", "threshold": 5.0, "description": "架构探索达到5级"},
    {"name": "学者", "icon": "📚", "dimension": "test_time_learning", "threshold": 5.0, "description": "学习速度达到5级"},
    {"name": "进化大师", "icon": "⚡", "dimension": "co_evolving_eval", "threshold": 7.0, "description": "进化趋势达到7级"},
]


class SkillTree:
    """Evaluate and track skill unlocks based on maturity dimensions."""

    def __init__(self, data_dir: Path) -> None:
        self._dir = Path(data_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._state_file = self._dir / "skill_tree.json"
        self._persisted: set[str] = self._load_state()

    def evaluate(self, dimensions: dict[str, float]) -> list[Skill]:
        """Evaluate all skills against dimension scores.

        Returns every skill with its current unlocked status and progress.
        Skills are unlocked if either:
        - the dimension meets the threshold, or
        - the skill was previously persisted as unlocked.
        """
        skills: list[Skill] = []
        for defn in SKILL_DEFS:
            dim_val = dimensions.get(defn["dimension"], 0.0)
            threshold = defn["threshold"]
            progress = min(1.0, dim_val / threshold) if threshold > 0 else 0.0
            unlocked = dim_val >= threshold or defn["name"] in self._persisted
            skills.append(Skill(
                name=defn["name"],
                icon=defn["icon"],
                dimension=defn["dimension"],
                threshold=threshold,
                description=defn["description"],
                unlocked=unlocked,
                progress=progress,
            ))
        return skills

    def unlocked_skills(self, dimensions: dict[str, float]) -> list[Skill]:
        """Return only the unlocked skills."""
        return [s for s in self.evaluate(dimensions) if s.unlocked]

    def locked_skills(self, dimensions: dict[str, float]) -> list[Skill]:
        """Return only the locked skills with their progress."""
        return [s for s in self.evaluate(dimensions) if not s.unlocked]

    def next_skill(self, dimensions: dict[str, float]) -> Skill | None:
        """Return the locked skill closest to being unlocked (highest progress %)."""
        locked = self.locked_skills(dimensions)
        if not locked:
            return None
        return max(locked, key=lambda s: s.progress)

    # ── Persistence ───────────────────────────────────────────────────

    def save_unlocked(self, dimensions: dict[str, float]) -> None:
        """Persist currently unlocked skill names to file."""
        unlocked = self.unlocked_skills(dimensions)
        for s in unlocked:
            self._persisted.add(s.name)
        self._save_state()

    def _save_state(self) -> None:
        """Write persisted skill names to JSON."""
        data = {name: True for name in self._persisted}
        with open(self._state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_state(self) -> set[str]:
        """Load persisted skill names from file."""
        if not self._state_file.exists():
            return set()
        try:
            with open(self._state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return set(data.keys())
        except (json.JSONDecodeError, OSError):
            return set()
