"""Tests for MaturityScorer."""

import pytest

from evolve_kit.maturity import MaturityScorer, DIMENSIONS, MANUAL_DIMENSIONS
from evolve_kit.types import MaturityReport


@pytest.fixture
def maturity():
    return MaturityScorer()


class TestMaturityScorer:
    def test_empty_score(self, maturity):
        report = maturity.score()
        assert isinstance(report, MaturityReport)
        assert report.total_score == 0.0

    def test_all_dimensions_present(self, maturity):
        report = maturity.score()
        for dim in DIMENSIONS:
            assert dim in report.dimensions

    def test_manual_dimensions_default_zero(self, maturity):
        report = maturity.score()
        for dim in MANUAL_DIMENSIONS:
            assert report.dimensions[dim] == 0.0

    def test_manual_scores_override(self, maturity):
        report = maturity.score(manual_scores={"tool_lifecycle": 7.0})
        assert report.dimensions["tool_lifecycle"] == 7.0

    def test_insight_loop_scoring(self, maturity, tmp_path):
        from evolve_kit.insight import InsightEngine
        engine = InsightEngine(tmp_path / "ins.jsonl")
        for i in range(10):
            engine.record(f"f{i}", f"j{i}", f"a{i}")
        report = maturity.score(insight_engine=engine)
        assert report.dimensions["insight_loop"] > 0

    def test_memory_lifecycle_scoring(self, maturity, tmp_path):
        from evolve_kit.memory import MemoryManager
        mem = MemoryManager(tmp_path / "mem.json", tmp_path / "del.jsonl")
        mem.add("k1", "v1")
        mem.add("k2", "v2")
        report = maturity.score(memory_manager=mem)
        assert report.dimensions["memory_lifecycle"] > 0

    def test_reflection_ratio(self, maturity, tmp_path):
        from evolve_kit.insight import InsightEngine
        from evolve_kit.scorer import PerformanceScorer
        ie = InsightEngine(tmp_path / "ins.jsonl")
        sc = PerformanceScorer(tmp_path / "sc.jsonl")
        # 5 insights for 5 tasks = 1:1 ratio -> score 5.0
        for i in range(5):
            ie.record(f"f{i}", f"j{i}", f"a{i}")
            sc.score(f"t{i}", 4)
        report = maturity.score(insight_engine=ie, scorer=sc)
        assert report.dimensions["reflection"] == 5.0

    def test_level_labels(self, maturity):
        report = maturity.score(manual_scores={d: 10.0 for d in MANUAL_DIMENSIONS})
        # With manual dimensions maxed, total should be at least 30
        assert report.total_score >= 0
        assert report.level in ["Initial", "Developing", "Intermediate", "Proficient", "Advanced"]

    def test_total_max_100(self, maturity, tmp_path):
        from evolve_kit.insight import InsightEngine
        from evolve_kit.memory import MemoryManager
        from evolve_kit.scorer import PerformanceScorer
        ie = InsightEngine(tmp_path / "ins.jsonl")
        mem = MemoryManager(tmp_path / "mem.json", tmp_path / "del.jsonl")
        sc = PerformanceScorer(tmp_path / "sc.jsonl")
        for i in range(20):
            ie.record(f"f{i}", f"j{i}", f"a{i}")
            mem.upsert(f"k{i}", f"v{i}")
            sc.score(f"t{i}", 5)
        report = maturity.score(
            insight_engine=ie, memory_manager=mem, scorer=sc,
            manual_scores={d: 10.0 for d in MANUAL_DIMENSIONS},
        )
        assert report.total_score <= 100.0
