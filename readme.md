<div align="center">

# 🧬 evolve-kit

**The missing self-evolution layer for AI agents**

[![CI](https://github.com/AIwork4me/evolve-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/AIwork4me/evolve-kit/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/evolve-kit.svg)](https://pypi.org/project/evolve-kit/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-green.svg)]()

English | [中文](README_zh-CN.md)

*The missing self-evolution layer for AI agents — structured memory, insight distillation, and self-improvement in 5 lines of code.*

</div>

---

## 🎮 RPG Dashboard

Watch your agent evolve like an RPG character — with XP bars, skill unlocks, and achievements!

```bash
evolve dashboard
```

![RPG Dashboard](docs/dashboard.png)

Your agent gets stronger with every task. Each completed task grants XP, insights unlock new skills, and achievements appear as your agent matures.

```bash
# Terminal report (no browser needed)
evolve report

# Browse insights
evolve insights
```

---

## 🤔 Why evolve-kit?

Every AI agent today has the same problem: **they start fresh every session.**

They don't remember what worked. They don't learn from mistakes. They don't get better over time.

evolve-kit fixes this. It's a **framework-agnostic** self-evolution layer that any agent can use — whether you're building with OpenAI, Anthropic, LangChain, AutoGen, or raw HTTP calls.

```python
from evolve_kit import EvolutionEngine

engine = EvolutionEngine("./my-agent-data")

# After each task, record what happened
engine.insight(
    "Used retry logic for API calls",
    "Exponential backoff reduced failures by 90%",
    "Always use backoff for external APIs"
)
engine.score("api_integration", 5)

# Check maturity anytime
report = engine.report()
print(f"Agent maturity: {report.total_score}/100 ({report.level})")
```

That's it. Your agent now has:
- 🧠 **Structured memory** with ADD/UPDATE/DELETE lifecycle
- 💡 **Insight distillation** (fact → judgment → action)
- ⭐ **Performance scoring** (1-5 stars per task)
- ✅ **Self-validation** (verify commands, files, installs)
- 🛡️ **Evolution guard** (safety checks after self-modification)
- 📊 **Maturity assessment** (10 dimensions, 0-100 score)

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Zero dependencies** | Pure Python stdlib. No pip conflicts, ever. |
| **Framework agnostic** | Works with any agent: Claude, GPT, LangChain, AutoGen, CrewAI, etc. |
| **File-based storage** | JSON/JSONL. No database. No server. Just files. |
| **71 tests, 100% pass** | Battle-tested on Windows/macOS/Linux, Python 3.10-3.13 |
| **Research-backed** | Based on [arXiv 2507.21046](https://arxiv.org/abs/2507.21046) — "A Survey of Self-Evolving Agents" |

## 📦 Install

```bash
pip install evolve-kit
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv pip install evolve-kit
```

## 🚀 Quick Start

### 1. Basic Usage

```python
from evolve_kit import EvolutionEngine

engine = EvolutionEngine("./agent-workspace")

# Record an insight after completing a task
engine.insight(
    fact="npm cache was corrupted on Windows",
    judgment="npx is unreliable on Windows; prefer global install",
    action="Use 'npm install -g' instead of npx on Windows",
    source_task="install_acpx",
    tags=["environment", "windows", "npm"]
)

# Score the task
engine.score("install_acpx", quality=3, notes="Had to work around npx bug")

# Store knowledge for future sessions
engine.memory.upsert("windows_npm_tip", "Use npm install -g instead of npx")
```

### 2. Self-Validation

```python
# Verify your agent's work
result = engine.validate_command("python -c 'import my_package'", category="install")
if not result.passed:
    engine.insight("install failed", "package missing", "retry with --force")

# Check files exist
engine.validate_file("./config.json", expected_content="api_key")
```

### 3. Evolution Safety Guard

```python
# Before applying self-modifications, run safety checks
result = engine.guard(
    changes=["Modified SOUL.md", "Installed new skill"],
    custom_checks={"new_skill_safe": True}
)

if not result.all_passed:
    print("⚠️ Evolution blocked! Safety check failed.")
```

### 4. Maturity Assessment

```python
report = engine.report()
print(f"Score: {report.total_score}/100")
print(f"Level: {report.level}")

# Dimension breakdown
for dim, score in report.dimensions.items():
    print(f"  {dim}: {score}/10")
```

Output:
```
Score: 42.0/100
Level: Developing
  insight_loop: 5.0/10
  memory_lifecycle: 3.0/10
  self_challenge: 0.0/10
  reflection: 4.0/10
  tool_lifecycle: 0.0/10    ← manual
  architecture_search: 0.0/10  ← manual
  test_time_learning: 2.5/10
  population_diversity: 0.0/10  ← manual
  safety_guardrails: 0.0/10
  co_evolving_eval: 2.5/10
```

## 🔌 Integrations

### With Claude / Anthropic

```python
import anthropic
from evolve_kit import EvolutionEngine

engine = EvolutionEngine("./claude-agent")

def agent_with_evolution(task: str):
    past = engine.insights.search(task)
    memory_hints = "\n".join(str(i) for i in past[-3:])

    response = anthropic.Anthropic().messages.create(
        model="claude-sonnet-4-20250514",
        messages=[{"role": "user", "content": f"Past insights:\n{memory_hints}\n\nTask: {task}"}]
    )

    engine.insight("completed task", "approach worked", "keep using it", source_task=task)
    engine.score(task, quality=4)
    return response
```

### With OpenAI

```python
from openai import OpenAI
from evolve_kit import EvolutionEngine

engine = EvolutionEngine("./gpt-agent")
client = OpenAI()

memory = engine.memory.list_all()
system = f"You are an evolving agent. Known facts: {memory}"

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": "Deploy the app"}
    ]
)
```

### With LangChain

```python
from langchain.memory import ConversationBufferMemory
from evolve_kit import EvolutionEngine

engine = EvolutionEngine("./langchain-agent")

class EvolvingMemory(ConversationBufferMemory):
    def save_context(self, inputs, outputs):
        super().save_context(inputs, outputs)
        engine.insight(inputs.get("input", ""), "processed", outputs.get("output", ""))
```

## 🏗️ Architecture

```
evolve-kit/
├── src/evolve_kit/
│   ├── types.py        # Data classes (Insight, MemoryEntry, ScoreResult, ...)
│   ├── insight.py      # InsightEngine — structured insight recording
│   ├── memory.py       # MemoryManager — ADD/UPDATE/DELETE lifecycle
│   ├── validator.py    # SelfValidator — command/file/install verification
│   ├── scorer.py       # PerformanceScorer — task quality tracking
│   ├── guard.py        # EvolutionGuard — safety checks
│   ├── maturity.py     # MaturityScorer — 10-dimension assessment
│   ├── engine.py       # EvolutionEngine — unified facade
│   └── __init__.py     # Public API exports
├── tests/              # 71 tests, all passing
├── pyproject.toml      # Modern Python packaging
└── README.md
```

**Data flow:**

```
Task completes
  → InsightEngine.record()     # What happened? What did I learn?
  → PerformanceScorer.score()  # How well did I do?
  → MemoryManager.upsert()     # What should I remember?
  → EvolutionGuard.verify()    # Am I still safe?
  → MaturityScorer.score()     # How mature am I now?
```

## 🧪 Testing

```bash
python -m pytest tests/ -v
```

## 📖 The 10 Dimensions of Agent Maturity

Based on [arXiv 2507.21046](https://arxiv.org/abs/2507.21046):

| # | Dimension | Auto | Description |
|---|-----------|:---:|-------------|
| 1 | insight_loop | ✅ | Has structured insights? |
| 2 | memory_lifecycle | ✅ | Using ADD/UPDATE/DELETE? |
| 3 | self_challenge | ✅ | How many validations run? |
| 4 | reflection | ✅ | Insight-to-task ratio |
| 5 | tool_lifecycle | 📝 | Tool creation/management |
| 6 | architecture_search | 📝 | Architecture exploration |
| 7 | test_time_learning | ✅ | Session-based learning |
| 8 | population_diversity | 📝 | Multi-agent diversity |
| 9 | safety_guardrails | ✅ | Guard check count |
| 10 | co_evolving_eval | ✅ | Score trend over time |

## 🗺️ Roadmap

- [ ] **v0.2** — CLI tool (`evolve report`, `evolve insights`)
- [ ] **v0.3** — LLM-powered insight synthesis (auto-distill from raw logs)
- [ ] **v0.4** — Agent-to-agent knowledge sharing (population evolution)
- [ ] **v0.5** — Web dashboard for maturity visualization
- [ ] **v1.0** — Full self-evolution loop (closed-loop improvement)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for your feature
4. Ensure all tests pass (`python -m pytest tests/ -v`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Give your agent the ability to evolve. Not just execute.**

[Get started →](https://github.com/AIwork4me/evolve-kit#quick-start)

</div>
