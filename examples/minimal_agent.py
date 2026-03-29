"""
Example: Minimal agent that evolves over multiple sessions.

Run: python minimal_agent.py

This demonstrates how an agent improves across sessions by
recording insights and scoring its performance.
"""

from evolve_kit import EvolutionEngine

engine = EvolutionEngine("./minimal-agent-data")


def run_session(task: str, quality: int):
    """Simulate one agent session."""

    print(f"\n{'='*60}")
    print(f"📋 Task: {task}")
    print(f"{'='*60}")

    # Simulate task execution
    print(f"  Executing: {task}...")

    # Record what we learned
    engine.insight(
        fact=f"Completed: {task}",
        judgment=f"Quality was {'excellent' if quality >= 4 else 'needs improvement'}",
        action="Continue current approach" if quality >= 4 else "Try alternative method",
        source_task=task,
    )

    # Score the task
    engine.score(task, quality=quality, time_minutes=5)

    # Store key knowledge
    engine.memory.upsert(
        f"last_run_{task}",
        f"quality={quality}, completed at {engine.scores.count()} total tasks"
    )

    print(f"  ✅ Recorded insight and scored {quality}/5")


def main():
    """Run multiple sessions to show evolution over time."""

    print("🧬 evolve-kit Minimal Agent Example")
    print("=" * 40)

    # Session 1: Learning the basics
    run_session("Install dependencies", quality=3)
    run_session("Configure environment", quality=4)

    # Session 2: Getting better
    run_session("Build first feature", quality=4)
    run_session("Write tests", quality=5)

    # Session 3: Mastery
    run_session("Deploy to production", quality=5)

    # Show evolution report
    print(f"\n{'='*60}")
    print("📊 EVOLUTION REPORT")
    print(f"{'='*60}")

    report = engine.report()
    print(f"\nTotal Score: {report.total_score:.1f}/100")
    print(f"Level: {report.level}")
    print(f"Total Insights: {engine.insights.count()}")
    print(f"Total Tasks Scored: {engine.scores.count()}")
    print(f"Memory Entries: {engine.memory.count()}")

    print(f"\nDimension Breakdown:")
    for dim, score in sorted(report.dimensions.items()):
        status = "✅" if score >= 5 else "⚠️" if score >= 2 else "❌"
        print(f"  {status} {dim}: {score:.1f}/10")

    # Show recent insights
    print(f"\nRecent Insights:")
    for insight in engine.insights.list_recent(3):
        print(f"  💡 {insight.fact[:60]}...")
        print(f"     → {insight.action[:60]}...")


if __name__ == "__main__":
    main()
