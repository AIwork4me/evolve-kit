"""Tests for MemoryManager."""

import json
from pathlib import Path

import pytest

from evolve_kit.memory import MemoryManager
from evolve_kit.types import MemoryOp


@pytest.fixture
def mem(tmp_path):
    return MemoryManager(
        tmp_path / "memory.json",
        tmp_path / "deletions.jsonl",
    )


class TestMemoryManager:
    def test_add_and_get(self, mem):
        mem.add("key1", "value1")
        assert mem.get("key1") == "value1"

    def test_add_duplicate_raises(self, mem):
        mem.add("key1", "value1")
        with pytest.raises(KeyError):
            mem.add("key1", "value2")

    def test_update(self, mem):
        mem.add("key1", "value1")
        entry = mem.update("key1", "value2")
        assert mem.get("key1") == "value2"
        assert entry.previous_value == "value1"

    def test_update_missing_raises(self, mem):
        with pytest.raises(KeyError):
            mem.update("nope", "val")

    def test_upsert_add(self, mem):
        mem.upsert("key1", "val1")
        assert mem.get("key1") == "val1"

    def test_upsert_update(self, mem):
        mem.add("key1", "val1")
        mem.upsert("key1", "val2")
        assert mem.get("key1") == "val2"

    def test_delete(self, mem):
        mem.add("key1", "value1")
        entry = mem.delete("key1", reason="outdated")
        assert mem.get("key1") is None
        assert entry.reason == "outdated"
        assert entry.previous_value == "value1"

    def test_delete_logs_to_file(self, mem):
        mem.add("k", "v")
        mem.delete("k", reason="test")
        lines = mem._del_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["reason"] == "test"

    def test_delete_missing_raises(self, mem):
        with pytest.raises(KeyError):
            mem.delete("nope")

    def test_list_all(self, mem):
        mem.add("a", "1")
        mem.add("b", "2")
        all_kv = mem.list_all()
        assert all_kv == {"a": "1", "b": "2"}

    def test_detect_conflicts(self, mem):
        mem.add("api_key", "xxx")
        mem.add("api_key_backup", "yyy")
        conflicts = mem.detect_conflicts()
        assert len(conflicts) == 1
        assert conflicts[0]["type"] == "similar_keys"

    def test_no_conflicts(self, mem):
        mem.add("alpha", "1")
        mem.add("beta", "2")
        assert mem.detect_conflicts() == []

    def test_count(self, mem):
        assert mem.count() == 0
        mem.add("k", "v")
        assert mem.count() == 1

    def test_tags_preserved_on_update(self, mem):
        mem.add("k", "v", tags=["important"])
        mem.update("k", "v2")
        # tags should be preserved when not explicitly passed
        data = mem._load()
        assert data["k"]["tags"] == ["important"]

    def test_get_missing_returns_none(self, mem):
        assert mem.get("nope") is None

    def test_entry_operation_enum(self, mem):
        entry = mem.add("k", "v")
        assert entry.operation == MemoryOp.ADD
