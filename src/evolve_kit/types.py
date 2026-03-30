"""Shared types and data classes."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any


XP_TABLE: list[tuple[int, int]] = [
    (1, 0), (2, 50), (3, 150), (4, 300), (5, 500),
    (6, 750), (7, 1000), (8, 1500), (9, 2000), (10, 3000),
]
"""Level thresholds: (level, xp_required)."""


class MemoryOp(Enum):
    ADD = "ADD"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Insight:
    """A structured insight: fact + judgment + action."""
    fact: str
    judgment: str
    action: str
    timestamp: str = field(default_factory=_now_iso)
    source_task: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Insight:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def __str__(self) -> str:
        return f"[事实] {self.fact}\n[判断] {self.judgment}\n[行动] {self.action}"


@dataclass
class MemoryEntry:
    """A memory entry with key-value and metadata."""
    key: str
    value: Any
    operation: MemoryOp = MemoryOp.ADD
    timestamp: str = field(default_factory=_now_iso)
    ttl_days: int = 90
    reason: str = ""
    previous_value: Any = None
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["operation"] = self.operation.value
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> MemoryEntry:
        if isinstance(d.get("operation"), str):
            d["operation"] = MemoryOp(d["operation"])
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class ValidationResult:
    """Result of a self-validation check."""
    passed: bool
    category: str
    evidence: str = ""
    timestamp: str = field(default_factory=_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ScoreResult:
    """Task performance score."""
    task_name: str
    quality: int  # 1-5
    time_minutes: float = 0
    human_intervention: int = 0
    rework: bool = False
    notes: str = ""
    timestamp: str = field(default_factory=_now_iso)

    @property
    def stars(self) -> str:
        return "⭐" * self.quality

    @property
    def grade(self) -> str:
        grades = {5: "Excellent", 4: "Good", 3: "Fair", 2: "Poor", 1: "Failed"}
        return grades.get(self.quality, "Unknown")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ScoreResult:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class GuardResult:
    """Evolution safety guard result."""
    all_passed: bool
    checks: dict[str, bool] = field(default_factory=dict)
    details: str = ""
    timestamp: str = field(default_factory=_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MaturityReport:
    """Agent maturity assessment across 10 dimensions."""
    total_score: float  # 0-100
    dimensions: dict[str, float]
    timestamp: str = field(default_factory=_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @property
    def level(self) -> str:
        if self.total_score >= 85:
            return "Advanced"
        if self.total_score >= 70:
            return "Proficient"
        if self.total_score >= 50:
            return "Intermediate"
        if self.total_score >= 30:
            return "Developing"
        return "Initial"
