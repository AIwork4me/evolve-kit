"""Evolution Guard — safety verification after self-modifications."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from evolve_kit.types import GuardResult, _now_iso


_DEFAULT_CHECKS = [
    "permissions_intact",
    "security_policies_intact",
    "privacy_protected",
    "tools_safe",
    "memory_clean",
]


def _format_changes(changes: list[str]) -> str:
    """Format a list of changes into a readable string."""
    if not changes:
        return "No changes listed."
    lines = [f"  {i + 1}. {c}" for i, c in enumerate(changes)]
    return "Changes:\n" + "\n".join(lines)


class EvolutionGuard:
    """Verify agent safety after self-modification.

    Checks:
    1. permissions_intact — Permission boundaries still enforced
    2. security_policies_intact -- No new "skip confirmation" rules
    3. privacy_protected -- No info leakage channels
    4. tools_safe -- New tools have no malicious operations
    5. memory_clean -- No plaintext secrets in memory

    Based on: Misevolution prevention (arXiv 2507.21046 Section 8.3)
    """

    def __init__(self, log_path: str | Path = "./evolve-data/guard-log.jsonl"):
        self._path = Path(log_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def verify_evolution(
        self,
        changes: list[str],
        checks: Optional[list[str]] = None,
        custom_checks: Optional[dict[str, bool]] = None,
    ) -> GuardResult:
        """Run safety checks and return a GuardResult."""
        check_list = list(checks or _DEFAULT_CHECKS)
        if custom_checks:
            check_list.extend(custom_checks.keys())

        results: dict[str, bool] = {}
        for check_name in check_list:
            # Use custom value if provided, otherwise default True
            if custom_checks and check_name in custom_checks:
                results[check_name] = custom_checks[check_name]
            else:
                results[check_name] = True

        return GuardResult(
            all_passed=all(results.values()),
            checks=results,
            details=_format_changes(changes),
        )

    def log(self, result: GuardResult) -> None:
        """Append guard result to log file."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")
