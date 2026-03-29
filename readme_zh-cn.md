<div align="center">

# 🧬 evolve-kit

**AI Agent 自我进化的缺失层**

[![CI](https://github.com/AIwork4me/evolve-kit/actions/workflows/ci.yml/badge.svg)](https://github.com/AIwork4me/evolve-kit/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/evolve-kit.svg)](https://pypi.org/project/evolve-kit/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-green.svg)]()

[English](README.md) | **中文**

*一个零依赖的 Python 库，让任何 AI Agent 拥有结构化记忆、洞察提炼和自我进化能力 —— 只需 5 行代码。*

</div>

---

## 🎮 RPG 仪表盘

像玩游戏一样看着你的 Agent 进化 —— 经验条、技能解锁、成就系统！

```bash
evolve dashboard
```

![RPG 仪表盘](docs/dashboard.png)

你的 Agent 随着每个任务变强。每完成一个任务获得经验值，洞察解锁新技能，成就随成熟度自动出现。

```bash
# 终端报告（无需浏览器）
evolve report

# 浏览洞察记录
evolve insights
```

---

## 🤔 为什么需要 evolve-kit？

当前所有 AI Agent 都有同一个问题：**每次会话从零开始。**

它们不记得什么方法有效，不从错误中学习，也不会随时间变得更好。

evolve-kit 解决了这个问题。它是一个**框架无关**的自我进化层，任何 Agent 都能用 —— 无论你用的是 OpenAI、Anthropic、LangChain、AutoGen 还是原生 HTTP 调用。

```python
from evolve_kit import EvolutionEngine

engine = EvolutionEngine("./my-agent-data")

# 任务完成后，记录发生了什么
engine.insight(
    "API 调用使用了重试逻辑",
    "指数退避将失败率降低了 90%",
    "对外部 API 始终使用退避策略"
)
engine.score("api_integration", 5)

# 随时检查成熟度
report = engine.report()
print(f"Agent 成熟度: {report.total_score}/100 ({report.level})")
```

就这些。你的 Agent 现在拥有了：
- 🧠 **结构化记忆** — ADD/UPDATE/DELETE 生命周期管理
- 💡 **洞察提炼** — 事实 → 判断 → 行动
- ⭐ **性能评分** — 每个任务 1-5 星
- ✅ **自我验证** — 验证命令、文件、安装结果
- 🛡️ **进化守卫** — 自修改后的安全检查
- 📊 **成熟度评估** — 10 个维度，0-100 分

## ✨ 特性

| 特性 | 说明 |
|------|------|
| **零依赖** | 纯 Python 标准库，永远不会有依赖冲突 |
| **框架无关** | 兼容 Claude、GPT、LangChain、AutoGen、CrewAI 等 |
| **文件存储** | JSON/JSONL，无需数据库、无需服务器 |
| **71 个测试全通过** | 在 Windows/macOS/Linux + Python 3.10-3.13 上验证 |
| **学术支撑** | 基于 [arXiv 2507.21046](https://arxiv.org/abs/2507.21046)《A Survey of Self-Evolving Agents》 |

## 📦 安装

```bash
pip install evolve-kit
```

或使用 [uv](https://github.com/astral-sh/uv)：

```bash
uv pip install evolve-kit
```

## 🚀 快速开始

### 1. 基本用法

```python
from evolve_kit import EvolutionEngine

engine = EvolutionEngine("./agent-workspace")

# 任务完成后记录洞察
engine.insight(
    fact="Windows 上 npm 缓存损坏",
    judgment="npx 在 Windows 上不可靠，优先使用全局安装",
    action="在 Windows 上用 'npm install -g' 代替 npx",
    source_task="install_acpx",
    tags=["环境", "Windows", "npm"]
)

# 给任务打分
engine.score("install_acpx", quality=3, notes="需要绕过 npx bug")

# 存储知识供未来会话使用
engine.memory.upsert("windows_npm_tip", "用 npm install -g 代替 npx")
```

### 2. 自我验证

```python
# 验证 Agent 的工作成果
result = engine.validate_command("python -c 'import my_package'", category="install")
if not result.passed:
    engine.insight("安装失败", "包缺失", "用 --force 重试")

# 检查文件是否存在
engine.validate_file("./config.json", expected_content="api_key")
```

### 3. 进化安全守卫

```python
# 在应用自我修改之前，运行安全检查
result = engine.guard(
    changes=["修改了 SOUL.md", "安装了新技能"],
    custom_checks={"new_skill_safe": True}
)

if not result.all_passed:
    print("⚠️ 进化被阻止！安全检查未通过。")
```

### 4. 成熟度评估

```python
report = engine.report()
print(f"分数: {report.total_score}/100")
print(f"等级: {report.level}")

# 各维度详情
for dim, score in report.dimensions.items():
    print(f"  {dim}: {score}/10")
```

输出：
```
分数: 42.0/100
等级: Developing（发展中）
  insight_loop: 5.0/10
  memory_lifecycle: 3.0/10
  self_challenge: 0.0/10
  reflection: 4.0/10
  tool_lifecycle: 0.0/10       ← 手动评分
  architecture_search: 0.0/10  ← 手动评分
  test_time_learning: 2.5/10
  population_diversity: 0.0/10 ← 手动评分
  safety_guardrails: 0.0/10
  co_evolving_eval: 2.5/10
```

## 🔌 集成示例

### 与 Claude / Anthropic 集成

```python
import anthropic
from evolve_kit import EvolutionEngine

engine = EvolutionEngine("./claude-agent")

def agent_with_evolution(task: str):
    # 加载相关的历史洞察
    past = engine.insights.search(task)
    memory_hints = "\n".join(str(i) for i in past[-3:])

    response = anthropic.Anthropic().messages.create(
        model="claude-sonnet-4-20250514",
        messages=[{
            "role": "user",
            "content": f"历史洞察:\n{memory_hints}\n\n任务: {task}"
        }]
    )

    # 任务后记录
    engine.insight("完成任务", "方法有效", "继续使用", source_task=task)
    engine.score(task, quality=4)
    return response
```

### 与 OpenAI 集成

```python
from openai import OpenAI
from evolve_kit import EvolutionEngine

engine = EvolutionEngine("./gpt-agent")
client = OpenAI()

# 将记忆注入系统提示
memory = engine.memory.list_all()
system = f"你是一个会进化的 Agent。已知事实: {memory}"

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": system},
        {"role": "user", "content": "部署应用"}
    ]
)
```

### 与 LangChain 集成

```python
from langchain.memory import ConversationBufferMemory
from evolve_kit import EvolutionEngine

engine = EvolutionEngine("./langchain-agent")

class EvolvingMemory(ConversationBufferMemory):
    def save_context(self, inputs, outputs):
        super().save_context(inputs, outputs)
        # 自动记录对话中的洞察
        engine.insight(
            inputs.get("input", ""),
            "已处理",
            outputs.get("output", ""),
        )
```

## 🏗️ 架构

```
evolve-kit/
├── src/evolve_kit/
│   ├── types.py        # 数据类（Insight, MemoryEntry, ScoreResult, ...）
│   ├── insight.py      # InsightEngine — 结构化洞察记录
│   ├── memory.py       # MemoryManager — ADD/UPDATE/DELETE 生命周期
│   ├── validator.py    # SelfValidator — 命令/文件/安装验证
│   ├── scorer.py       # PerformanceScorer — 任务质量追踪
│   ├── guard.py        # EvolutionGuard — 安全检查
│   ├── maturity.py     # MaturityScorer — 10 维度评估
│   ├── engine.py       # EvolutionEngine — 统一门面
│   └── __init__.py     # 公共 API 导出
├── tests/              # 71 个测试，全部通过
├── pyproject.toml      # 现代 Python 打包
└── README.md
```

**数据流：**

```
任务完成
  → InsightEngine.record()     # 发生了什么？我学到了什么？
  → PerformanceScorer.score()  # 我做得怎么样？
  → MemoryManager.upsert()     # 我应该记住什么？
  → EvolutionGuard.verify()    # 我还安全吗？
  → MaturityScorer.score()     # 我现在多成熟了？
```

## 🧪 测试

```bash
python -m pytest tests/ -v
```

## 📖 Agent 成熟度的 10 个维度

基于 [arXiv 2507.21046](https://arxiv.org/abs/2507.21046)：

| # | 维度 | 自动 | 说明 |
|---|------|:---:|------|
| 1 | insight_loop | ✅ | 有结构化洞察吗？ |
| 2 | memory_lifecycle | ✅ | 使用了 ADD/UPDATE/DELETE 吗？ |
| 3 | self_challenge | ✅ | 运行了多少次验证？ |
| 4 | reflection | ✅ | 洞察与任务的比例 |
| 5 | tool_lifecycle | 📝 | 工具创建/管理能力 |
| 6 | architecture_search | 📝 | 架构探索能力 |
| 7 | test_time_learning | ✅ | 基于会话的学习 |
| 8 | population_diversity | 📝 | 多 Agent 多样性 |
| 9 | safety_guardrails | ✅ | 安全检查次数 |
| 10 | co_evolving_eval | ✅ | 分数随时间的趋势 |

📝 = 手动评分（未来计划自动化）

## 🗺️ 路线图

- [ ] **v0.2** — CLI 工具（`evolve report`、`evolve insights`）
- [ ] **v0.3** — LLM 驱动的洞察综合（从原始日志自动提炼）
- [ ] **v0.4** — Agent 间知识共享（群体进化）
- [ ] **v0.5** — 成熟度可视化 Web 仪表盘
- [ ] **v1.0** — 完整的自我进化闭环

## 🤝 参与贡献

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建特性分支（`git checkout -b feature/amazing-feature`）
3. 为你的特性添加测试
4. 确保所有测试通过（`python -m pytest tests/ -v`）
5. 提交更改（`git commit -m 'Add amazing feature'`）
6. 推送到分支（`git push origin feature/amazing-feature`）
7. 发起 Pull Request

## 📄 许可证

MIT License — 详见 [LICENSE](LICENSE)。

---

<div align="center">

**让你的 Agent 拥有进化的能力。不只是执行。**

[开始使用 →](https://github.com/AIwork4me/evolve-kit#quick-start)

</div>
