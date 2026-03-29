"""
Example: Using evolve-kit with Claude / Anthropic API.

Run: pip install anthropic evolve-kit
"""

from anthropic import Anthropic
from evolve_kit import EvolutionEngine

engine = EvolutionEngine("./claude-agent-data")
client = Anthropic()


def evolved_agent(task: str) -> str:
    """An agent that learns from past experience."""

    # Load relevant insights from previous sessions
    past_insights = engine.insights.search(task)
    memory_hints = "\n".join(str(i) for i in past_insights[-3:])

    # Load stored knowledge
    known_facts = engine.memory.list_all()

    # Build enhanced prompt with evolution context
    enhanced_prompt = f"""## Past Insights (learn from experience)
{memory_hints or 'No past insights for this task.'}

## Known Facts
{known_facts or 'No stored facts yet.'}

## Current Task
{task}"""

    # Call Claude with evolution context
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": enhanced_prompt}],
    )

    result_text = response.content[0].text

    # Record this interaction for future learning
    engine.insight(
        fact=f"Completed task: {task[:50]}",
        judgment="Approach was effective",
        action="Reuse this approach for similar tasks",
        source_task=task,
        tags=["claude", "auto-recorded"],
    )

    # Score the interaction
    engine.score(task, quality=4, time_minutes=1)

    return result_text


if __name__ == "__main__":
    # First session
    result = evolved_agent("Deploy a Flask app to AWS")
    print(f"Result: {result[:200]}...")

    # Check maturity after session
    report = engine.report()
    print(f"\n📊 Maturity: {report.total_score:.1f}/100 ({report.level})")
