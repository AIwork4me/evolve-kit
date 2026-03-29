"""evolve-kit: Structured self-evolution for AI agents."""

__version__ = "0.1.0"

from evolve_kit.types import (
    Insight,
    MemoryEntry,
    MemoryOp,
    ValidationResult,
    ScoreResult,
    GuardResult,
    MaturityReport,
)
from evolve_kit.insight import InsightEngine
from evolve_kit.memory import MemoryManager
from evolve_kit.validator import SelfValidator
from evolve_kit.scorer import PerformanceScorer
from evolve_kit.guard import EvolutionGuard
from evolve_kit.maturity import MaturityScorer
from evolve_kit.engine import EvolutionEngine

__all__ = [
    "EvolutionEngine",
    "InsightEngine", "Insight",
    "MemoryManager", "MemoryEntry", "MemoryOp",
    "SelfValidator", "ValidationResult",
    "PerformanceScorer", "ScoreResult",
    "EvolutionGuard", "GuardResult",
    "MaturityScorer", "MaturityReport",
]
