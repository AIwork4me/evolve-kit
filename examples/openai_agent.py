"""
Example: Using evolve-kit with OpenAI API.

Run: pip install openai evolve-kit
"""

from openai import OpenAI
from evolve_kit import EvolutionEngine

engine = EvolutionEngine("./gpt-agent-data")
client = OpenAI()


def evolved_agent(task: str) -> str:
    """An agent that injects memory into system prompt."""

    # Load all stored knowledge
    memory = engine.memory.list_all()
    insights = engine.insights.list_recent(5)

    # Build system prompt with evolution context
    system_prompt = f"""You are an evolving AI agent that learns from experience.

## Stored Knowledge
{memory}

## Recent Insights
{chr(10).join(str(i) for i in insights)}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task},
        ],
    )

    result = response.choices[0].message.content

    # Auto-record
    engine.insight(task[:50], "processed", "stored for future", source_task=task)
    engine.score(task, quality=4)

    return result


if __name__ == "__main__":
    result = evolved_agent("Write a Python web scraper")
    print(f"Result: {result[:200]}...")

    report = engine.report()
    print(f"\n📊 Maturity: {report.total_score:.1f}/100 ({report.level})")
