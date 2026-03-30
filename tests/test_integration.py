"""Integration tests — full lifecycle, dashboard, and CLI JSON consistency."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from evolve_kit.engine import EvolutionEngine
from evolve_kit.cli import _generate_dashboard_html, _compute_achievements


# ─── Helpers ────────────────────────────────────────────────────────────────


def _cli_json(workspace: Path) -> dict | None:
    """Run `evolve report --json` and return parsed JSON, or None on failure."""
    env = {**__import__("os").environ, "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(
        [
            sys.executable, "-m", "evolve_kit.cli",
            "--workspace", str(workspace),
            "report", "--json",
        ],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(workspace),
        env=env,
    )
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)


def _populated_engine(tmp_path: Path) -> EvolutionEngine:
    """Return an engine pre-loaded with 3 insights, 3 scores, and 2 memories."""
    engine = EvolutionEngine(tmp_path)

    for i in range(3):
        engine.insight(
            f"fact_{i}",
            f"judgment_{i}",
            f"action_{i}",
            source_task=f"task_{i}",
        )

    qualities = [5, 4, 4]
    for i, q in enumerate(qualities):
        engine.score(f"task_{i}", quality=q)

    engine.memory.upsert("key_a", "value_a")
    engine.memory.upsert("key_b", "value_b")

    return engine


# ─── Test 1: Full evolution lifecycle ──────────────────────────────────────


class TestFullEvolutionLifecycle:
    """End-to-end: create engine → add data → guard check → verify all systems."""

    def test_full_evolution_lifecycle(self, tmp_path: Path) -> None:
        engine = _populated_engine(tmp_path)

        # Run a guard check (adds to guard log)
        guard_result = engine.guard(
            changes=["test change"],
            checks=["safety_check"],
        )
        assert guard_result.all_passed is True

        # ── XP totals ──────────────────────────────────────────────
        # 3 insights × 20 + 3 scores × 30 + 2 memories × 15 = 180
        assert engine.xp_total == 180

        # ── Level ──────────────────────────────────────────────────
        # 180 XP → level 3 (thresholds: 0→1, 50→2, 150→3, 300→4)
        assert engine.level == 3

        # ── Achievements (via engine.achievements) ─────────────────
        achievements = engine.achievements.check_unlocks(
            insight_count=engine.insights.count(),
            task_count=engine.scores.count(),
            mem_count=engine.memory.count(),
            avg_quality=engine.scores.average_quality(),
            maturity_score=0.0,  # will be overridden by actual report below
        )
        ach_names = {a.name for a in achievements}
        assert "First Steps" in ach_names
        assert "Insight Awakened" in ach_names

        # ── Skills show progress ───────────────────────────────────
        report = engine.report()
        skills = engine.skill_tree.evaluate(report.dimensions)
        # At least some skills should show progress > 0
        assert any(s.progress > 0 for s in skills), "At least one skill should have progress"

        # ── Report is a MaturityReport with total_score > 0 ────────
        from evolve_kit.types import MaturityReport
        assert isinstance(report, MaturityReport)
        assert report.total_score > 0

        # ── JSON output via CLI subprocess ─────────────────────────
        data = _cli_json(tmp_path)
        assert data is not None, "CLI --json returned no data"

        required_keys = [
            "level", "xp_total", "xp_progress", "maturity_score",
            "dimensions", "achievements", "skills",
            "insights_count", "tasks_count", "memory_count",
        ]
        for key in required_keys:
            assert key in data, f"Missing key in JSON output: {key}"

        assert data["xp_total"] == 180
        assert data["level"] == 3
        assert data["insights_count"] == 3
        assert data["tasks_count"] == 3
        assert data["memory_count"] == 2


# ─── Test 2: Dashboard end-to-end ──────────────────────────────────────────


class TestDashboardEndToEnd:
    """Generate dashboard HTML and verify it contains expected sections."""

    def test_dashboard_end_to_end(self, tmp_path: Path) -> None:
        engine = _populated_engine(tmp_path)

        html = _generate_dashboard_html(engine)

        # Contains level number
        level = engine.level
        assert f"Level {level}" in html

        # Contains XP total
        assert f"total: {engine.xp_total}" in html

        # Contains at least one achievement
        # With 3 tasks, "First Steps" should be in the achievements
        assert "First Steps" in html

        # Contains skill names
        assert "洞察之眼" in html or "SKILLS" in html

        # Contains quality trend section
        assert "QUALITY TREND" in html


# ─── Test 3: CLI JSON matches text report ──────────────────────────────────


class TestCLIJsonMatchesReport:
    """Verify the --json output is consistent with the text report."""

    def test_cli_json_matches_report(self, tmp_path: Path) -> None:
        engine = _populated_engine(tmp_path)

        # Get report from engine directly
        report = engine.report()

        # Get JSON from CLI
        data = _cli_json(tmp_path)
        assert data is not None, "CLI --json returned no data"

        # Cross-check values
        assert abs(data["maturity_score"] - report.total_score) < 0.01
        assert data["insights_count"] == engine.insights.count()
        assert data["tasks_count"] == engine.scores.count()
        assert data["memory_count"] == engine.memory.count()

        # Dimensions match
        for dim_key, dim_val in report.dimensions.items():
            assert dim_key in data["dimensions"]
            assert abs(data["dimensions"][dim_key] - dim_val) < 0.01

        # Achievements in JSON include the ones from _compute_achievements
        json_ach_names = {a["name"] for a in data["achievements"]}
        legacy_ach = _compute_achievements(
            engine.insights.count(),
            engine.scores.count(),
            engine.memory.count(),
            engine.scores.average_quality(),
            report,
        )
        legacy_names = {a["name"] for a in legacy_ach}
        # Engine achievements should be a superset of legacy achievements
        assert legacy_names.issubset(json_ach_names), (
            f"Legacy achievements {legacy_names} not in JSON {json_ach_names}"
        )
