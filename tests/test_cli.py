"""Tests for CLI commands (report, insights, JSON output)."""

from __future__ import annotations

import argparse
import json
import pytest
from io import StringIO
from unittest.mock import patch

from evolve_kit.engine import EvolutionEngine


@pytest.fixture
def engine(tmp_path):
    """Fresh engine with a clean workspace."""
    return EvolutionEngine(tmp_path / "ws")


@pytest.fixture
def populated_engine(tmp_path):
    """Engine with some data so report is interesting."""
    eng = EvolutionEngine(tmp_path / "ws")
    for i in range(5):
        eng.insight(f"fact-{i}", f"judgment-{i}", f"action-{i}")
    for i in range(5):
        eng.score(f"task-{i}", quality=4)
    for i in range(3):
        eng.memory.add(f"key-{i}", f"value-{i}")
    return eng


def _make_args(workspace: str = ".", json_flag: bool = False, n: int = 10):
    """Build a minimal argparse.Namespace for CLI commands."""
    return argparse.Namespace(
        workspace=workspace,
        json=json_flag,
        n=n,
    )


class TestReportTextOutput:
    def test_report_text_output(self, populated_engine, capsys):
        """Text report should contain header, level info, and dimension bars."""
        from evolve_kit.cli import cmd_report

        args = _make_args(workspace=str(populated_engine._base.parent))
        cmd_report(populated_engine, args)

        captured = capsys.readouterr().out
        assert "Agent Evolution Report" in captured
        # Should show level/XP info (e.g. "Lv." or "Level" or "XP")
        assert "Lv." in captured or "Level" in captured or "XP" in captured

    def test_report_text_has_dimensions(self, populated_engine, capsys):
        """Text report should show at least some dimension names."""
        from evolve_kit.cli import cmd_report

        args = _make_args(workspace=str(populated_engine._base.parent))
        cmd_report(populated_engine, args)

        captured = capsys.readouterr().out
        # Should contain some dimension display (either bars or names)
        assert "洞察" in captured or "insight" in captured.lower() or "10" in captured

    def test_report_text_has_achievements(self, populated_engine, capsys):
        """Text report should show achievements when data warrants it."""
        from evolve_kit.cli import cmd_report

        args = _make_args(workspace=str(populated_engine._base.parent))
        cmd_report(populated_engine, args)

        captured = capsys.readouterr().out
        # With 5 tasks and 5 insights, should have at least "First Steps" and "Insight Awakened"
        assert "Achievement" in captured or "First Steps" in captured or "🏆" in captured

    def test_report_text_has_skills(self, populated_engine, capsys):
        """Text report should show skill tree info."""
        from evolve_kit.cli import cmd_report

        args = _make_args(workspace=str(populated_engine._base.parent))
        cmd_report(populated_engine, args)

        captured = capsys.readouterr().out
        # Should show skills section
        assert "Skill" in captured or "技能" in captured or "✅" in captured or "skill" in captured.lower()


class TestReportJSONOutput:
    def test_report_json_output(self, populated_engine, capsys):
        """JSON report should be valid JSON with required keys."""
        from evolve_kit.cli import cmd_report

        args = _make_args(
            workspace=str(populated_engine._base.parent),
            json_flag=True,
        )
        cmd_report(populated_engine, args)

        captured = capsys.readouterr().out
        data = json.loads(captured)

        # Required top-level keys
        assert "level" in data
        assert "xp_total" in data
        assert "xp_progress" in data
        assert "dimensions" in data
        assert "achievements" in data
        assert "skills" in data

    def test_report_json_values(self, populated_engine, capsys):
        """JSON report should have sensible values."""
        from evolve_kit.cli import cmd_report

        args = _make_args(
            workspace=str(populated_engine._base.parent),
            json_flag=True,
        )
        cmd_report(populated_engine, args)

        captured = capsys.readouterr().out
        data = json.loads(captured)

        # Populated engine: 5 insights*20 + 5 scores*30 + 3 memory*15 = 295 XP
        assert data["xp_total"] == 295
        assert data["level"] == 3  # 295 XP -> level 3 (150 threshold)
        assert 0.0 <= data["xp_progress"] <= 1.0
        assert isinstance(data["dimensions"], dict)
        assert isinstance(data["achievements"], list)
        assert isinstance(data["skills"], list)

    def test_report_json_counts(self, populated_engine, capsys):
        """JSON report should include activity counts."""
        from evolve_kit.cli import cmd_report

        args = _make_args(
            workspace=str(populated_engine._base.parent),
            json_flag=True,
        )
        cmd_report(populated_engine, args)

        captured = capsys.readouterr().out
        data = json.loads(captured)

        assert data.get("insights_count") == 5
        assert data.get("tasks_count") == 5
        assert data.get("memory_count") == 3

    def test_report_json_maturity_score(self, populated_engine, capsys):
        """JSON report should include maturity_score."""
        from evolve_kit.cli import cmd_report

        args = _make_args(
            workspace=str(populated_engine._base.parent),
            json_flag=True,
        )
        cmd_report(populated_engine, args)

        captured = capsys.readouterr().out
        data = json.loads(captured)

        assert "maturity_score" in data
        assert isinstance(data["maturity_score"], (int, float))
        assert data["maturity_score"] >= 0


class TestInsightsCommand:
    def test_insights_command(self, populated_engine, capsys):
        """cmd_insights should list recorded insights."""
        from evolve_kit.cli import cmd_insights

        args = _make_args(workspace=str(populated_engine._base.parent), n=10)
        cmd_insights(populated_engine, args)

        captured = capsys.readouterr().out
        assert "Insight" in captured or "fact" in captured.lower() or "fact-0" in captured

    def test_insights_empty(self, engine, capsys):
        """cmd_insights on empty engine should say no insights."""
        from evolve_kit.cli import cmd_insights

        args = _make_args(workspace=str(engine._base.parent), n=10)
        cmd_insights(engine, args)

        captured = capsys.readouterr().out
        assert "No insights" in captured or "no insight" in captured.lower()


class TestEmptyWorkspaceReport:
    def test_empty_workspace_report_text(self, engine, capsys):
        """Report on fresh workspace should not crash (text mode)."""
        from evolve_kit.cli import cmd_report

        args = _make_args(workspace=str(engine._base.parent))
        cmd_report(engine, args)

        captured = capsys.readouterr().out
        assert "Agent Evolution Report" in captured

    def test_empty_workspace_report_json(self, engine, capsys):
        """Report on fresh workspace should not crash (JSON mode)."""
        from evolve_kit.cli import cmd_report

        args = _make_args(
            workspace=str(engine._base.parent),
            json_flag=True,
        )
        cmd_report(engine, args)

        captured = capsys.readouterr().out
        data = json.loads(captured)
        assert data["xp_total"] == 0
        assert data["level"] == 1
        assert data["maturity_score"] == 0.0
