"""Tests for the skill tree system."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evolve_kit.skill_tree import SkillTree, Skill, SKILL_DEFS


@pytest.fixture
def tmp_data(tmp_path: Path) -> Path:
    """Return a temporary data directory."""
    d = tmp_path / "skill-tree-data"
    d.mkdir()
    return d


@pytest.fixture
def tree(tmp_data: Path) -> SkillTree:
    """Create a fresh SkillTree."""
    return SkillTree(tmp_data)


def _zero_dims() -> dict[str, float]:
    """All dimensions at 0."""
    return {s["dimension"]: 0.0 for s in SKILL_DEFS}


class TestSkillTree:
    """Skill tree evaluation tests."""

    def test_no_skills_fresh(self, tree: SkillTree) -> None:
        """Fresh engine, all dimensions 0 → no skills unlocked."""
        dims = _zero_dims()
        unlocked = tree.unlocked_skills(dims)
        assert unlocked == []

    def test_unlock_insight_eye(self, tree: SkillTree) -> None:
        """insight_loop >= 3 unlocks 洞察之眼."""
        dims = _zero_dims()
        dims["insight_loop"] = 3.5
        unlocked = tree.unlocked_skills(dims)
        names = [s.name for s in unlocked]
        assert "洞察之眼" in names

    def test_unlock_eternal_memory(self, tree: SkillTree) -> None:
        """memory_lifecycle >= 7 unlocks 永恒记忆."""
        dims = _zero_dims()
        dims["memory_lifecycle"] = 7.0
        unlocked = tree.unlocked_skills(dims)
        names = [s.name for s in unlocked]
        assert "永恒记忆" in names

    def test_unlock_reflection_master(self, tree: SkillTree) -> None:
        """reflection >= 5 unlocks 自省大师."""
        dims = _zero_dims()
        dims["reflection"] = 5.0
        unlocked = tree.unlocked_skills(dims)
        names = [s.name for s in unlocked]
        assert "自省大师" in names

    def test_unlock_safety_guardian(self, tree: SkillTree) -> None:
        """safety_guardrails >= 6 unlocks 安全守卫."""
        dims = _zero_dims()
        dims["safety_guardrails"] = 6.5
        unlocked = tree.unlocked_skills(dims)
        names = [s.name for s in unlocked]
        assert "安全守卫" in names

    def test_unlock_tool_master(self, tree: SkillTree) -> None:
        """tool_lifecycle >= 5 unlocks 工具大师."""
        dims = _zero_dims()
        dims["tool_lifecycle"] = 5.0
        unlocked = tree.unlocked_skills(dims)
        names = [s.name for s in unlocked]
        assert "工具大师" in names

    def test_locked_skills_show_progress(self, tree: SkillTree) -> None:
        """Locked skills report their progress toward the threshold."""
        dims = _zero_dims()
        dims["insight_loop"] = 1.5  # threshold is 3.0 → 50%
        locked = tree.locked_skills(dims)
        insight = [s for s in locked if s.name == "洞察之眼"]
        assert len(insight) == 1
        assert insight[0].progress == pytest.approx(0.5, abs=0.01)

    def test_next_skill(self, tree: SkillTree) -> None:
        """Returns the locked skill closest to being unlocked."""
        dims = _zero_dims()
        # insight_loop threshold=3, set to 2.7 → 90%
        # reflection threshold=5, set to 1.0 → 20%
        dims["insight_loop"] = 2.7
        dims["reflection"] = 1.0
        result = tree.next_skill(dims)
        assert result is not None
        assert result.name == "洞察之眼"

    def test_multiple_unlocked(self, tree: SkillTree) -> None:
        """Multiple dimensions high → multiple skills unlocked."""
        dims = _zero_dims()
        dims["insight_loop"] = 4.0
        dims["memory_lifecycle"] = 8.0
        dims["reflection"] = 6.0
        dims["safety_guardrails"] = 7.0
        dims["tool_lifecycle"] = 5.5
        unlocked = tree.unlocked_skills(dims)
        names = {s.name for s in unlocked}
        assert "洞察之眼" in names
        assert "永恒记忆" in names
        assert "自省大师" in names
        assert "安全守卫" in names
        assert "工具大师" in names
        assert len(unlocked) >= 5

    def test_skill_persistence(self, tmp_data: Path) -> None:
        """Unlocked skills state persists to file and reloads."""
        dims = _zero_dims()
        dims["insight_loop"] = 4.0
        dims["memory_lifecycle"] = 8.0

        # First instance: evaluate and save
        tree1 = SkillTree(tmp_data)
        unlocked1 = tree1.unlocked_skills(dims)
        names1 = {s.name for s in unlocked1}
        assert "洞察之眼" in names1

        # Persist unlocked state
        tree1.save_unlocked(dims)

        # Second instance: reload — should show persisted skills
        tree2 = SkillTree(tmp_data)
        # Even with zero dimensions, persisted skills stay unlocked
        zero = _zero_dims()
        unlocked2 = tree2.unlocked_skills(zero)
        names2 = {s.name for s in unlocked2}
        assert "洞察之眼" in names2
