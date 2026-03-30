"""Tests for the enhanced HTML dashboard generation."""

from __future__ import annotations

import argparse
import re

import pytest
from unittest.mock import patch

from evolve_kit.engine import EvolutionEngine
from evolve_kit.cli import _generate_dashboard_html, cmd_dashboard


@pytest.fixture
def engine(tmp_path):
    """Fresh engine with a clean workspace."""
    return EvolutionEngine(tmp_path / "ws")


@pytest.fixture
def populated_engine(tmp_path):
    """Engine with enough data to unlock achievements, skills, and have XP."""
    eng = EvolutionEngine(tmp_path / "ws")
    # 5 insights → 100 XP, 5 tasks → 150 XP, 3 memories → 45 XP = 295 XP
    for i in range(5):
        eng.insight(f"fact-{i}", f"judgment-{i}", f"action-{i}")
    for i in range(5):
        eng.score(f"task-{i}", quality=4)
    for i in range(3):
        eng.memory.add(f"key-{i}", f"value-{i}")
    return eng


def _make_args(workspace: str = "."):
    return argparse.Namespace(workspace=workspace)


class TestDashboardHTMLGenerated:
    def test_dashboard_html_generated(self, populated_engine):
        """_generate_dashboard_html should return a non-empty HTML string."""
        html = _generate_dashboard_html(populated_engine)
        assert isinstance(html, str)
        assert len(html) > 100
        assert "<!DOCTYPE html>" in html
        assert "</html>" in html
        assert "evolve-kit" in html

    def test_cmd_dashboard_creates_file(self, populated_engine, capsys):
        """cmd_dashboard should write an HTML file and print its path."""
        with patch("webbrowser.open"):
            args = _make_args(workspace=str(populated_engine._base.parent))
            cmd_dashboard(populated_engine, args)

        captured = capsys.readouterr().out
        assert "Dashboard opened" in captured


class TestDashboardContainsLevel:
    def test_dashboard_contains_level_number(self, populated_engine):
        """HTML must contain the XP level number."""
        html = _generate_dashboard_html(populated_engine)
        level = populated_engine.level
        # Should appear as "Level N" and in the header AGENT-NN
        assert f"Level {level}" in html
        assert f"AGENT-{level:02d}" in html

    def test_dashboard_level_1_for_empty(self, engine):
        """Empty engine should show level 1."""
        html = _generate_dashboard_html(engine)
        assert "Level 1" in html
        assert "AGENT-01" in html


class TestDashboardContainsAchievements:
    def test_dashboard_contains_achievement_names(self, populated_engine):
        """HTML must contain names of unlocked achievements."""
        html = _generate_dashboard_html(populated_engine)
        # With 5 tasks → "First Steps", 5 insights → "Insight Awakened"
        assert "First Steps" in html
        assert "Insight Awakened" in html

    def test_dashboard_has_achievements_section(self, engine):
        """Even with no data, the achievements section title should exist."""
        html = _generate_dashboard_html(engine)
        assert "ACHIEVEMENTS" in html

    def test_dashboard_achievement_badges(self, populated_engine):
        """Unlocked achievements should have the unlocked-ach class."""
        html = _generate_dashboard_html(populated_engine)
        assert 'class="achievement unlocked-ach"' in html


class TestDashboardContainsSkills:
    def test_dashboard_contains_skill_names(self, populated_engine):
        """HTML must contain skill names from the skill tree."""
        html = _generate_dashboard_html(populated_engine)
        # All skills from SKILL_DEFS should appear
        assert "洞察之眼" in html
        assert "永恒记忆" in html
        assert "自省大师" in html

    def test_dashboard_shows_unlock_status(self, populated_engine):
        """Unlocked skills should show ✅, locked skills should show progress."""
        html = _generate_dashboard_html(populated_engine)
        # At least one skill has ✅ (unlocked) or is locked with progress
        assert "✅" in html or "locked" in html

    def test_dashboard_has_skills_section(self, engine):
        """The skills section header must be present."""
        html = _generate_dashboard_html(engine)
        assert "SKILLS" in html

    def test_dashboard_locked_skill_shows_progress(self, populated_engine):
        """Locked skills should display dimension value / threshold."""
        html = _generate_dashboard_html(populated_engine)
        # At least one skill should show a progress indicator like "X.X/Y.Y"
        # Pattern: float/float
        pattern = r"\d+\.\d+/\d+\.\d+"
        assert re.search(pattern, html), "Locked skills should show progress like 3.0/7.0"


class TestDashboardContainsXPBar:
    def test_dashboard_contains_xp_bar(self, populated_engine):
        """HTML must contain an XP progress bar element."""
        html = _generate_dashboard_html(populated_engine)
        assert "xp-bar" in html
        assert "xp-fill" in html

    def test_dashboard_xp_bar_has_width(self, populated_engine):
        """XP fill bar should have a width style."""
        html = _generate_dashboard_html(populated_engine)
        # Should have a percentage width on the XP fill
        assert re.search(r"width:\s*\d+(\.\d+)?%", html)

    def test_dashboard_xp_label(self, populated_engine):
        """XP label should show total XP."""
        html = _generate_dashboard_html(populated_engine)
        xp_total = populated_engine.xp_total
        assert f"total: {xp_total}" in html

    def test_dashboard_xp_pulse_animation(self, populated_engine):
        """XP bar should have the pulse glow animation."""
        html = _generate_dashboard_html(populated_engine)
        assert "xpPulse" in html
        assert "@keyframes xpPulse" in html


class TestDashboardQualityTrend:
    def test_dashboard_has_quality_trend_section(self, populated_engine):
        """HTML must contain the quality trend section."""
        html = _generate_dashboard_html(populated_engine)
        assert "QUALITY TREND" in html
        assert "quality-trend" in html

    def test_dashboard_quality_trend_bars(self, populated_engine):
        """Quality trend should have bars for recent scores."""
        html = _generate_dashboard_html(populated_engine)
        assert 'class="trend-bar"' in html
        # Each bar should have height percentage
        assert re.search(r'height:\d+(\.\d+)?%', html)


class TestDashboardCSS:
    def test_dashboard_dark_theme(self, populated_engine):
        """Dashboard should use the dark theme colors."""
        html = _generate_dashboard_html(populated_engine)
        assert "#1a1a2e" in html
        assert "#16213e" in html

    def test_dashboard_press_start_font(self, populated_engine):
        """Dashboard should use Press Start 2P font for headers."""
        html = _generate_dashboard_html(populated_engine)
        assert "Press Start 2P" in html

    def test_dashboard_golden_glow_on_skills(self, populated_engine):
        """Unlocked skills should have a golden glow class."""
        html = _generate_dashboard_html(populated_engine)
        assert "skill-icon-glow" in html
        assert "text-shadow" in html
