"""Tests for EvolutionEngine (facade)."""

import pytest

from evolve_kit.engine import EvolutionEngine
from evolve_kit.types import Insight, ScoreResult, GuardResult, MaturityReport


@pytest.fixture
def engine(tmp_path):
    return EvolutionEngine(tmp_path / "workspace")


class TestEvolutionEngine:
    def test_insight(self, engine):
        result = engine.insight("fact", "judg", "act", source_task="test")
        assert isinstance(result, Insight)
        assert result.fact == "fact"

    def test_score(self, engine):
        result = engine.score("task1", 4, notes="good")
        assert isinstance(result, ScoreResult)
        assert result.quality == 4

    def test_validate_command(self, engine):
        result = engine.validate_command("echo ok", category="test")
        assert result.passed is True

    def test_validate_file(self, engine, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello", encoding="utf-8")
        result = engine.validate_file(str(f))
        assert result.passed is True

    def test_guard(self, engine):
        result = engine.guard(["test change"])
        assert isinstance(result, GuardResult)
        assert result.all_passed is True

    def test_report(self, engine):
        engine.insight("f", "j", "a")
        engine.score("t", 4)
        report = engine.report()
        assert isinstance(report, MaturityReport)
        assert report.total_score >= 0

    def test_memory_property(self, engine):
        engine.memory.add("key1", "val1")
        assert engine.memory.get("key1") == "val1"

    def test_insights_property(self, engine):
        engine.insight("f", "j", "a")
        assert engine.insights.count() == 1

    def test_scores_property(self, engine):
        engine.score("t", 5)
        assert engine.scores.count() == 1

    def test_workspace_dir_created(self, tmp_path):
        engine = EvolutionEngine(tmp_path / "new_workspace")
        assert (tmp_path / "new_workspace" / "evolve-data").exists()

    def test_full_workflow(self, engine):
        # Simulate a full agent workflow
        engine.insight("installed paddleocr", "lightweight is better", "prefer remote APIs")
        engine.memory.add("paddleocr_version", "2.0.14")
        engine.score("install_paddleocr", 5, time_minutes=15)
        result = engine.guard(["installed paddleocr skill"])
        assert result.all_passed is True

        report = engine.report()
        assert report.total_score > 0
