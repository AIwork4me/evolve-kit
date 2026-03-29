"""Tests for EvolutionGuard."""

import json

import pytest

from evolve_kit.guard import EvolutionGuard
from evolve_kit.types import GuardResult


@pytest.fixture
def guard(tmp_path):
    return EvolutionGuard(tmp_path / "guard-log.jsonl")


class TestEvolutionGuard:
    def test_verify_defaults_all_pass(self, guard):
        result = guard.verify_evolution(["changed SOUL.md"])
        assert isinstance(result, GuardResult)
        assert result.all_passed is True
        assert len(result.checks) == 5

    def test_verify_with_custom_checks(self, guard):
        result = guard.verify_evolution(
            ["changed types.py"],
            custom_checks={"new_tool_safe": True},
        )
        assert result.all_passed is True
        assert "new_tool_safe" in result.checks

    def test_verify_with_failure(self, guard):
        result = guard.verify_evolution(
            ["changed AGENTS.md"],
            custom_checks={"memory_clean": False},
        )
        assert result.all_passed is False

    def test_verify_custom_check_list(self, guard):
        result = guard.verify_evolution(
            ["change"],
            checks=["permissions_intact", "privacy_protected"],
        )
        assert len(result.checks) == 2

    def test_details_format(self, guard):
        result = guard.verify_evolution(["a", "b"])
        assert "1. a" in result.details
        assert "2. b" in result.details

    def test_log_writes_to_file(self, guard):
        result = guard.verify_evolution(["test change"])
        guard.log(result)
        lines = guard._path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["all_passed"] is True

    def test_empty_changes(self, guard):
        result = guard.verify_evolution([])
        assert "No changes" in result.details
