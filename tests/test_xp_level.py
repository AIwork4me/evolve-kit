"""Tests for XP / Level system (TDD -- written first)."""

from __future__ import annotations

import pytest
from evolve_kit.engine import EvolutionEngine


@pytest.fixture
def engine(tmp_path):
    """Fresh engine with a clean workspace."""
    return EvolutionEngine(tmp_path / "ws")


class TestXPTotal:
    def test_xp_total_empty(self, engine):
        """A fresh engine with no data should have 0 XP."""
        assert engine.xp_total == 0

    def test_xp_total_with_data(self, engine):
        """5 insights + 5 scores + 3 memories = 5*20 + 5*30 + 3*15 = 295 XP."""
        for i in range(5):
            engine.insight(f"fact-{i}", f"judgment-{i}", f"action-{i}")
        for i in range(5):
            engine.score(f"task-{i}", quality=4)
        for i in range(3):
            engine.memory.add(f"key-{i}", f"value-{i}")

        assert engine.xp_total == 295


class TestLevel:
    def test_level_from_xp(self, engine):
        """Verify level thresholds: 0->1, 50->2, 150->3, 300->4, 500->5."""
        # Fresh engine is level 1
        assert engine.level == 1

        # XP 50 -> level 2
        engine.insight("f", "j", "a")  # +20
        engine.score("t", quality=4)   # +30 -> total 50
        assert engine.xp_total == 50
        assert engine.level == 2

        # Reach 150 -> level 3
        for i in range(2):
            engine.score(f"t{i}", quality=4)  # +60 -> 110
        for i in range(2):
            engine.insight(f"f{i}", f"j{i}", f"a{i}")  # +40 -> 150
        assert engine.xp_total == 150
        assert engine.level == 3

        # Reach 300 -> level 4
        for i in range(5):
            engine.score(f"t2-{i}", quality=4)  # +150 -> 300
        assert engine.xp_total == 300
        assert engine.level == 4

        # Reach 500 -> level 5
        for i in range(4):
            engine.score(f"t3-{i}", quality=4)  # +120 -> 420
        for i in range(4):
            engine.insight(f"f3-{i}", f"j3-{i}", f"a3-{i}")  # +80 -> 500
        assert engine.xp_total == 500
        assert engine.level == 5


class TestXPToNext:
    def test_xp_to_next(self, engine):
        """At XP 295 (level 3), next threshold is 300, so xp_to_next = 5."""
        for i in range(5):
            engine.insight(f"fact-{i}", f"judgment-{i}", f"action-{i}")
        for i in range(5):
            engine.score(f"task-{i}", quality=4)
        for i in range(3):
            engine.memory.add(f"key-{i}", f"value-{i}")

        assert engine.xp_total == 295
        assert engine.level == 3
        assert engine.xp_to_next == 5


class TestXPProgress:
    def test_xp_progress_percent(self, engine):
        """At XP 295, level 3 (threshold 150), level 4 at 300.
        progress = (295-150)/(300-150) = 0.9667"""
        for i in range(5):
            engine.insight(f"fact-{i}", f"judgment-{i}", f"action-{i}")
        for i in range(5):
            engine.score(f"task-{i}", quality=4)
        for i in range(3):
            engine.memory.add(f"key-{i}", f"value-{i}")

        assert engine.xp_total == 295
        progress = engine.xp_progress
        assert abs(progress - (295 - 150) / (300 - 150)) < 0.001
