"""Tests for Achievement system (TDD — written FIRST)."""

import json
from pathlib import Path

import pytest

from evolve_kit.achievements import AchievementEngine, Achievement


@pytest.fixture
def data_dir(tmp_path):
    return tmp_path / "achieve-data"


@pytest.fixture
def engine(data_dir):
    data_dir.mkdir(parents=True, exist_ok=True)
    return AchievementEngine(data_dir)


# ── 1. Fresh engine, no data ──────────────────────────────────────────


class TestFreshEngine:
    def test_no_achievements_fresh(self, engine):
        """Fresh engine with all-zero stats → no achievements unlocked."""
        result = engine.check_unlocks(
            insight_count=0,
            task_count=0,
            mem_count=0,
            avg_quality=0.0,
            maturity_score=0.0,
        )
        assert result == []


# ── 2–9. Individual achievement unlocks ───────────────────────────────


class TestIndividualAchievements:
    def test_first_steps(self, engine):
        """1 task completed → unlocks 'First Steps' (🌟)."""
        result = engine.check_unlocks(
            insight_count=0, task_count=1, mem_count=0,
            avg_quality=0.0, maturity_score=0.0,
        )
        names = [a.name for a in result]
        assert "First Steps" in names
        first = next(a for a in result if a.name == "First Steps")
        assert first.icon == "🌟"

    def test_insight_awakened(self, engine):
        """1 insight recorded → unlocks 'Insight Awakened' (💡)."""
        result = engine.check_unlocks(
            insight_count=1, task_count=0, mem_count=0,
            avg_quality=0.0, maturity_score=0.0,
        )
        names = [a.name for a in result]
        assert "Insight Awakened" in names
        ia = next(a for a in result if a.name == "Insight Awakened")
        assert ia.icon == "💡"

    def test_insight_scholar(self, engine):
        """10 insights → unlocks 'Insight Scholar' (📚)."""
        result = engine.check_unlocks(
            insight_count=10, task_count=0, mem_count=0,
            avg_quality=0.0, maturity_score=0.0,
        )
        names = [a.name for a in result]
        assert "Insight Scholar" in names
        is_ = next(a for a in result if a.name == "Insight Scholar")
        assert is_.icon == "📚"

    def test_memory_keeper(self, engine):
        """5 memory entries → unlocks 'Memory Keeper' (🧠)."""
        result = engine.check_unlocks(
            insight_count=0, task_count=0, mem_count=5,
            avg_quality=0.0, maturity_score=0.0,
        )
        names = [a.name for a in result]
        assert "Memory Keeper" in names
        mk = next(a for a in result if a.name == "Memory Keeper")
        assert mk.icon == "🧠"

    def test_quality_player(self, engine):
        """average quality >= 4.0 → unlocks 'Quality Player' (🔥)."""
        result = engine.check_unlocks(
            insight_count=0, task_count=0, mem_count=0,
            avg_quality=4.0, maturity_score=0.0,
        )
        names = [a.name for a in result]
        assert "Quality Player" in names
        qp = next(a for a in result if a.name == "Quality Player")
        assert qp.icon == "🔥"

    def test_battle_hardened(self, engine):
        """5 tasks → unlocks 'Battle Hardened' (⚔️)."""
        result = engine.check_unlocks(
            insight_count=0, task_count=5, mem_count=0,
            avg_quality=0.0, maturity_score=0.0,
        )
        names = [a.name for a in result]
        assert "Battle Hardened" in names
        bh = next(a for a in result if a.name == "Battle Hardened")
        assert bh.icon == "⚔️"

    def test_half_century(self, engine):
        """maturity score >= 50 → unlocks 'Half Century' (🏆)."""
        result = engine.check_unlocks(
            insight_count=0, task_count=0, mem_count=0,
            avg_quality=0.0, maturity_score=50.0,
        )
        names = [a.name for a in result]
        assert "Half Century" in names
        hc = next(a for a in result if a.name == "Half Century")
        assert hc.icon == "🏆"

    def test_evolution_master(self, engine):
        """maturity score >= 70 → unlocks 'Evolution Master' (👑)."""
        result = engine.check_unlocks(
            insight_count=0, task_count=0, mem_count=0,
            avg_quality=0.0, maturity_score=70.0,
        )
        names = [a.name for a in result]
        assert "Evolution Master" in names
        em = next(a for a in result if a.name == "Evolution Master")
        assert em.icon == "👑"


# ── 10. Multiple achievements at once ──────────────────────────────────


class TestMultipleAchievements:
    def test_multiple_achievements(self, engine):
        """Enough data → multiple achievements unlocked at once."""
        result = engine.check_unlocks(
            insight_count=10, task_count=5, mem_count=5,
            avg_quality=4.5, maturity_score=70.0,
        )
        names = {a.name for a in result}
        # Should unlock at least 5 achievements simultaneously
        assert len(result) >= 5
        assert "First Steps" in names
        assert "Insight Awakened" in names
        assert "Insight Scholar" in names
        assert "Battle Hardened" in names
        assert "Evolution Master" in names


# ── 11. check_new_unlocks returns only newly unlocked ─────────────────


class TestNewUnlocks:
    def test_new_unlocks(self, engine):
        """Second call returns only newly unlocked (diff from previous)."""
        # First call: moderate stats
        first = engine.check_new_unlocks(
            insight_count=1, task_count=1, mem_count=0,
            avg_quality=3.0, maturity_score=10.0,
        )
        first_names = {a.name for a in first}
        assert "First Steps" in first_names
        assert "Insight Awakened" in first_names

        # Second call: improved stats — new achievements only
        second = engine.check_new_unlocks(
            insight_count=10, task_count=5, mem_count=5,
            avg_quality=4.5, maturity_score=70.0,
        )
        second_names = {a.name for a in second}
        # These were already unlocked, should NOT appear again
        assert "First Steps" not in second_names
        assert "Insight Awakened" not in second_names
        # These are new
        assert "Battle Hardened" in second_names
        assert "Memory Keeper" in second_names
        assert "Quality Player" in second_names


# ── 12. Persistence ───────────────────────────────────────────────────


class TestPersistence:
    def test_achievement_persistence(self, data_dir, engine):
        """Unlocked achievements saved to file, reloadable."""
        engine.check_unlocks(
            insight_count=5, task_count=1, mem_count=5,
            avg_quality=4.0, maturity_score=30.0,
        )
        # Verify file exists
        state_file = data_dir / "achievements.json"
        assert state_file.exists()

        # Reload a new engine from same dir
        engine2 = AchievementEngine(data_dir)
        # Calling check_unlocks should already know about previously unlocked
        # and NOT return them as new
        new = engine2.check_new_unlocks(
            insight_count=5, task_count=1, mem_count=5,
            avg_quality=4.0, maturity_score=30.0,
        )
        new_names = {a.name for a in new}
        # Nothing new — same stats, already unlocked
        assert "First Steps" not in new_names
        assert "Memory Keeper" not in new_names

        # But check_unlocks (all) should still return them
        all_unlocked = engine2.check_unlocks(
            insight_count=5, task_count=1, mem_count=5,
            avg_quality=4.0, maturity_score=30.0,
        )
        all_names = {a.name for a in all_unlocked}
        assert "First Steps" in all_names
        assert "Memory Keeper" in all_names
