"""Achievement system for evolve-kit."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


@dataclass
class Achievement:
    """An unlocked achievement instance."""
    name: str
    icon: str
    description: str
    unlocked: bool = False
    unlocked_at: str | None = None


@dataclass
class AchievementDef:
    """Definition of an achievement and its unlock condition."""
    name: str
    icon: str
    description: str
    condition: Callable[..., bool]


ACHIEVEMENT_DEFS: list[AchievementDef] = [
    AchievementDef(
        name="First Steps",
        icon="🌟",
        description="Complete your first task",
        condition=lambda ic, tc, mc, aq, ms: tc >= 1,
    ),
    AchievementDef(
        name="Insight Awakened",
        icon="💡",
        description="Record your first insight",
        condition=lambda ic, tc, mc, aq, ms: ic >= 1,
    ),
    AchievementDef(
        name="Insight Scholar",
        icon="📚",
        description="Record 10 insights",
        condition=lambda ic, tc, mc, aq, ms: ic >= 10,
    ),
    AchievementDef(
        name="Memory Keeper",
        icon="🧠",
        description="Store 5 memory entries",
        condition=lambda ic, tc, mc, aq, ms: mc >= 5,
    ),
    AchievementDef(
        name="Quality Player",
        icon="🔥",
        description="Maintain average quality >= 4.0",
        condition=lambda ic, tc, mc, aq, ms: aq >= 4.0,
    ),
    AchievementDef(
        name="Battle Hardened",
        icon="⚔️",
        description="Complete 5 tasks",
        condition=lambda ic, tc, mc, aq, ms: tc >= 5,
    ),
    AchievementDef(
        name="Half Century",
        icon="🏆",
        description="Reach maturity score >= 50",
        condition=lambda ic, tc, mc, aq, ms: ms >= 50.0,
    ),
    AchievementDef(
        name="Evolution Master",
        icon="👑",
        description="Reach maturity score >= 70",
        condition=lambda ic, tc, mc, aq, ms: ms >= 70.0,
    ),
]


class AchievementEngine:
    """Track and persist achievement unlocks."""

    def __init__(self, data_dir: Path) -> None:
        self._dir = Path(data_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._state_file = self._dir / "achievements.json"
        self._unlocked_names: set[str] = self._load_state()

    def check_unlocks(
        self,
        insight_count: int,
        task_count: int,
        mem_count: int,
        avg_quality: float,
        maturity_score: float,
    ) -> list[Achievement]:
        """Return ALL achievements that are currently unlocked."""
        results: list[Achievement] = []
        newly_unlocked: list[str] = []

        for defn in ACHIEVEMENT_DEFS:
            if defn.condition(insight_count, task_count, mem_count, avg_quality, maturity_score):
                unlocked_at: str | None = None
                if defn.name in self._unlocked_names:
                    # Already persisted — keep existing timestamp
                    unlocked_at = self._get_saved_timestamp(defn.name)
                else:
                    # Newly unlocked now
                    unlocked_at = datetime.now(timezone.utc).isoformat()
                    newly_unlocked.append(defn.name)

                results.append(Achievement(
                    name=defn.name,
                    icon=defn.icon,
                    description=defn.description,
                    unlocked=True,
                    unlocked_at=unlocked_at,
                ))

        if newly_unlocked:
            for name in newly_unlocked:
                self._unlocked_names.add(name)
            self._save_state()

        return results

    def check_new_unlocks(
        self,
        insight_count: int,
        task_count: int,
        mem_count: int,
        avg_quality: float,
        maturity_score: float,
    ) -> list[Achievement]:
        """Return ONLY achievements newly unlocked since last check."""
        previously = set(self._unlocked_names)

        # Run check_unlocks which updates internal state
        all_unlocked = self.check_unlocks(
            insight_count, task_count, mem_count, avg_quality, maturity_score,
        )

        # Filter to only the new ones
        return [a for a in all_unlocked if a.name not in previously]

    # ── Persistence ───────────────────────────────────────────────────

    def _save_state(self) -> None:
        """Persist unlocked achievement names + timestamps to JSON."""
        data: dict[str, str] = {}
        # Load existing to preserve timestamps
        existing = self._read_file()
        for name in self._unlocked_names:
            data[name] = existing.get(name, datetime.now(timezone.utc).isoformat())

        with open(self._state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_state(self) -> set[str]:
        """Load previously unlocked achievement names from file."""
        data = self._read_file()
        return set(data.keys())

    def _read_file(self) -> dict[str, str]:
        """Read the raw JSON state file."""
        if not self._state_file.exists():
            return {}
        try:
            with open(self._state_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _get_saved_timestamp(self, name: str) -> str | None:
        """Get the saved timestamp for a previously unlocked achievement."""
        data = self._read_file()
        return data.get(name)
