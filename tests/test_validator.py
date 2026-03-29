"""Tests for SelfValidator."""

import pytest

from evolve_kit.validator import SelfValidator


@pytest.fixture
def validator(tmp_path):
    return SelfValidator(tmp_path / "validations.jsonl")


class TestSelfValidator:
    def test_validate_file_exists(self, validator, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world", encoding="utf-8")
        result = validator.validate_file(str(f))
        assert result.passed is True

    def test_validate_file_not_exists(self, validator, tmp_path):
        result = validator.validate_file(str(tmp_path / "nope.txt"))
        assert result.passed is False

    def test_validate_file_content(self, validator, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world", encoding="utf-8")
        result = validator.validate_file(str(f), expected_content="hello")
        assert result.passed is True

    def test_validate_file_content_missing(self, validator, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world", encoding="utf-8")
        result = validator.validate_file(str(f), expected_content="goodbye")
        assert result.passed is False

    def test_validate_command_success(self, validator):
        result = validator.validate_command("echo hello", category="test")
        assert result.passed is True

    def test_validate_command_failure(self, validator):
        result = validator.validate_command("exit 1", category="test")
        assert result.passed is False

    def test_validate_command_timeout(self, validator):
        # Windows: ping -n 10 127.0.0.1 sleeps ~10 seconds; cross-platform fallback
        result = validator.validate_command("ping -n 10 127.0.0.1", category="test", timeout=1)
        assert result.passed is False

    def test_validate_install_success(self, validator):
        result = validator.validate_install("python", "python --version")
        assert result.passed is True

    def test_validate_install_failure(self, validator):
        result = validator.validate_install("fake_pkg", "exit 1")
        assert result.passed is False
        assert "install:fake_pkg" in result.category
