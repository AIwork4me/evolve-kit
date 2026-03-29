"""Maturity Scorer — assess agent self-evolution capability across 10 dimensions."""

from __future__ import annotations

from evolve_kit.types import MaturityReport, _now_iso


# 10 dimensions, each scored 0-10
DIMENSIONS = [
    "insight_loop",          # 1. Has structured insights?
    "memory_lifecycle",      # 2. Using ADD/UPDATE/DELETE?
    "self_challenge",        # 3. Validation count
    "reflection",            # 4. Insight count vs task count ratio
    "tool_lifecycle",        # 5. Tool creation/management (manual)
    "architecture_search",   # 6. Architecture exploration (manual)
    "test_time_learning",    # 7. Session-based learning
    "population_diversity",  # 8. Multi-agent diversity (manual)
    "safety_guardrails",     # 9. Guard check count
    "co_evolving_eval",      # 10. Score trend
]

MANUAL_DIMENSIONS = {"tool_lifecycle", "architecture_search", "population_diversity"}


class MaturityScorer:
    """Score agent maturity across 10 dimensions (0-100 total).

    Based on: self-evolution assessment framework (arXiv 2507.21046 Section 7)
    """

    def score(
        self,
        memory_manager=None,
        insight_engine=None,
        scorer=None,
        validator=None,
        guard=None,
        manual_scores: dict[str, float] | None = None,
    ) -> MaturityReport:
        """Calculate maturity scores based on component data."""
        dims: dict[str, float] = {}
        manual = manual_scores or {}

        # 1. insight_loop: has insights? 0-10 based on count
        insight_count = insight_engine.count() if insight_engine else 0
        dims["insight_loop"] = min(10.0, insight_count * 0.5)

        # 2. memory_lifecycle: using ADD/UPDATE/DELETE? Based on entry count
        mem_count = memory_manager.count() if memory_manager else 0
        dims["memory_lifecycle"] = min(10.0, mem_count * 1.0)

        # 3. self_challenge: validation count
        dims["self_challenge"] = 0.0  # Would need validator log access

        # 4. reflection: insight count vs scored task count ratio
        task_count = scorer.count() if scorer else 0
        if task_count > 0:
            ratio = insight_count / task_count
            dims["reflection"] = min(10.0, ratio * 5.0)  # 2:1 ratio = perfect 10
        else:
            dims["reflection"] = 0.0

        # 5-6, 8: Manual dimensions
        for d in MANUAL_DIMENSIONS:
            dims[d] = manual.get(d, 0.0)

        # 7. test_time_learning: session count (approximated by score count)
        dims["test_time_learning"] = min(10.0, task_count * 0.5)

        # 9. safety_guardrails: guard check count (approximated)
        dims["safety_guardrails"] = 0.0  # Would need guard log access

        # 10. co_evolving_eval: score trend
        if scorer and scorer.count() >= 2:
            recent = scorer.list_recent(10)
            if len(recent) >= 2:
                avg_recent = sum(s.quality for s in recent[-3:]) / min(3, len(recent))
                avg_old = sum(s.quality for s in recent[:3]) / min(3, len(recent))
                trend = avg_recent - avg_old
                dims["co_evolving_eval"] = max(0.0, min(10.0, 5.0 + trend * 2.0))
            else:
                dims["co_evolving_eval"] = 0.0
        else:
            dims["co_evolving_eval"] = 0.0

        total = sum(dims.values())
        return MaturityReport(
            total_score=total,
            dimensions=dims,
        )
