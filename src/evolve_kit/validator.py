"""Self-Validator — run subprocess checks to verify task outcomes."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

from evolve_kit.types import ValidationResult


class SelfValidator:
    """Run validation commands and record results.

    Based on: self-correction via executable verification (arXiv 2507.21046 Section 3.2.2)
    """

    def __init__(self, log_path: str | Path = "./evolve-data/validations.jsonl"):
        self._path = Path(log_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def validate_install(
        self,
        package: str,
        test_command: str,
        timeout: int = 30,
    ) -> ValidationResult:
        """Validate that a package is installed by running a test command."""
        return self.validate_command(
            command=test_command,
            category=f"install:{package}",
            timeout=timeout,
        )

    def validate_file(
        self,
        path: str | Path,
        expected_content: Optional[str] = None,
    ) -> ValidationResult:
        """Validate that a file exists and optionally contains expected content."""
        p = Path(path)
        if not p.exists():
            return ValidationResult(
                passed=False,
                category=f"file:{p}",
                evidence=f"File does not exist: {p}",
            )

        if expected_content is not None:
            content = p.read_text(encoding="utf-8")
            if expected_content not in content:
                return ValidationResult(
                    passed=False,
                    category=f"file:{p}",
                    evidence=f"Expected content not found in {p}",
                )

        return ValidationResult(
            passed=True,
            category=f"file:{p}",
            evidence=f"File exists" + (", content verified" if expected_content else ""),
        )

    def validate_command(
        self,
        command: str,
        category: str = "command",
        timeout: int = 30,
    ) -> ValidationResult:
        """Run a shell command and check return code."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            passed = result.returncode == 0
            evidence = result.stdout.strip()[-500:] if result.stdout else result.stderr.strip()[-500:]
            return ValidationResult(
                passed=passed,
                category=category,
                evidence=evidence or f"exit code: {result.returncode}",
            )
        except subprocess.TimeoutExpired:
            return ValidationResult(
                passed=False,
                category=category,
                evidence=f"Command timed out after {timeout}s",
            )
        except Exception as e:
            return ValidationResult(
                passed=False,
                category=category,
                evidence=str(e),
            )

    def _log(self, result: ValidationResult) -> None:
        """Append validation result to log."""
        import json
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")
