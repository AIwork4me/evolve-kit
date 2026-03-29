"""Tests for PerformanceScorer."""

import pytest

from evolve_kit.scorer import PerformanceScorer
from evolve_kit.types import ScoreResult


@pytest.fixture
def scorer(tmp_path):
    return PerformanceScorer(tmp_path / "scores.jsonl")


class TestPerformanceScorer:
    def test_score_returns_result(self, scorer):
        result = scorer.score("task1", 4)
        assert isinstance(result, ScoreResult)
        assert result.task_name == "task1"
        assert result.quality == 4

    def test_score_invalid_quality(self, scorer):
        with pytest.raises(ValueError):
            scorer.score("task", 0)
        with pytest.raises(ValueError):
            scorer.score("task", 6)

    def test_score_with_all_fields(self, scorer):
        result = scorer.score(
            "task1", 5, time_minutes=30, human_intervention=0,
            rework=False, notes="perfect",
        )
        assert result.time_minutes == 30
        assert result.notes == "perfect"

    def test_stars(self, scorer):
        result = scorer.score("t", 4)
        assert result.stars == "⭐⭐⭐⭐"

    def test_grade(self, scorer):
        assert scorer.score("t", 5).grade == "Excellent"
        assert scorer.score("t", 4).grade == "Good"
        assert scorer.score("t", 3).grade == "Fair"
        assert scorer.score("t", 2).grade == "Poor"
        assert scorer.score("t", 1).grade == "Failed"

    def test_list_recent(self, scorer):
        for i in range(5):
            scorer.score(f"task{i}", 3)
        recent = scorer.list_recent(3)
        assert len(recent) == 3
        assert recent[0].task_name == "task2"

    def test_average_quality(self, scorer):
        scorer.score("t1", 3)
        scorer.score("t2", 5)
        assert scorer.average_quality() == 4.0

    def test_average_quality_empty(self, scorer):
        assert scorer.average_quality() == 0.0

    def test_count(self, scorer):
        assert scorer.count() == 0
        scorer.score("t", 3)
        assert scorer.count() == 1

    def test_persistence(self, scorer, tmp_path):
        scorer.score("t1", 4)
        # Create new scorer pointing to same file
        scorer2 = PerformanceScorer(tmp_path / "scores.jsonl")
        assert scorer2.count() == 1
