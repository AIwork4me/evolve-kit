"""Tests for InsightEngine."""

import json
from pathlib import Path

import pytest

from evolve_kit.insight import InsightEngine
from evolve_kit.types import Insight


@pytest.fixture
def engine(tmp_path):
    return InsightEngine(tmp_path / "insights.jsonl")


class TestInsightEngine:
    def test_record_returns_insight(self, engine):
        result = engine.record("fact1", "judg1", "act1", source_task="t1")
        assert isinstance(result, Insight)
        assert result.fact == "fact1"
        assert result.judgment == "judg1"
        assert result.action == "act1"

    def test_record_persists_to_file(self, engine):
        engine.record("f", "j", "a", tags=["bug"])
        lines = (engine._path).read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["fact"] == "f"
        assert data["tags"] == ["bug"]

    def test_list_recent(self, engine):
        for i in range(5):
            engine.record(f"fact{i}", f"j{i}", f"a{i}")
        recent = engine.list_recent(3)
        assert len(recent) == 3
        assert recent[0].fact == "fact2"

    def test_list_by_tag(self, engine):
        engine.record("f1", "j1", "a1", tags=["bug"])
        engine.record("f2", "j2", "a2", tags=["feature"])
        engine.record("f3", "j3", "a3", tags=["bug"])
        bugs = engine.list_by_tag("bug")
        assert len(bugs) == 2

    def test_list_by_task(self, engine):
        engine.record("f1", "j1", "a1", source_task="install")
        engine.record("f2", "j2", "a2", source_task="install")
        engine.record("f3", "j3", "a3", source_task="deploy")
        install = engine.list_by_task("install")
        assert len(install) == 2

    def test_search(self, engine):
        engine.record("paddleocr install", "it worked", "do it again")
        engine.record("npm cache broken", "clear cache", "use uv")
        results = engine.search("cache")
        assert len(results) == 1
        assert "npm" in results[0].fact

    def test_count(self, engine):
        assert engine.count() == 0
        engine.record("f", "j", "a")
        assert engine.count() == 1

    def test_insight_str(self, engine):
        insight = engine.record("did X", "learned Y", "will Z")
        s = str(insight)
        assert "[事实]" in s
        assert "did X" in s

    def test_empty_store(self, tmp_path):
        engine = InsightEngine(tmp_path / "nonexistent.jsonl")
        assert engine.count() == 0
        assert engine.list_recent() == []
