"""CLI entry point for evolve-kit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from evolve_kit.engine import EvolutionEngine


def cmd_report(engine: EvolutionEngine, args: argparse.Namespace) -> None:
    """Print a text-based evolution report to the terminal."""
    report = engine.report(
        manual_scores=_load_manual_scores(args.workspace),
    )

    insights = engine.insights.count()
    tasks = engine.scores.count()
    mem = engine.memory.count()
    avg = engine.scores.average_quality()

    level = report.level
    score = report.total_score

    # Level calculation (rough RPG mapping)
    lvl = max(1, int(score // 10))

    # JSON output mode
    json_flag = getattr(args, "json", False)
    if json_flag:
        # Evaluate skills and achievements from the proper engines
        skill_list = engine.skill_tree.evaluate(report.dimensions)
        achievement_list = engine.achievements.check_unlocks(
            insights, tasks, mem, avg, score,
        )

        data = {
            "level": engine.level,
            "xp_total": engine.xp_total,
            "xp_progress": engine.xp_progress,
            "maturity_score": score,
            "dimensions": report.dimensions,
            "achievements": [
                {"name": a.name, "icon": a.icon, "description": a.description}
                for a in achievement_list
            ],
            "skills": [
                {
                    "name": s.name,
                    "icon": s.icon,
                    "unlocked": s.unlocked,
                    "progress": s.progress,
                }
                for s in skill_list
            ],
            "insights_count": insights,
            "tasks_count": tasks,
            "memory_count": mem,
        }
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    print()
    print("🧬 Agent Evolution Report — evolve-kit v0.1.0")
    print("=" * 55)
    print()
    print(f"  📊 Maturity: {score:.1f}/100 (Lv.{lvl} — {level})")
    print()

    # Dimension bars
    dim_icons = {
        "insight_loop": "👁️",
        "memory_lifecycle": "🧠",
        "self_challenge": "⚔️",
        "reflection": "🪞",
        "tool_lifecycle": "🔧",
        "architecture_search": "🏗️",
        "test_time_learning": "📚",
        "population_diversity": "👥",
        "safety_guardrails": "🛡️",
        "co_evolving_eval": "📈",
    }

    dim_names = {
        "insight_loop": "洞察力",
        "memory_lifecycle": "记忆管理",
        "self_challenge": "自我挑战",
        "reflection": "反思能力",
        "tool_lifecycle": "工具管理",
        "architecture_search": "架构探索",
        "test_time_learning": "学习速度",
        "population_diversity": "群体多样性",
        "safety_guardrails": "安全守卫",
        "co_evolving_eval": "进化趋势",
    }

    for dim, val in report.dimensions.items():
        filled = int(val)
        bar = "█" * filled + "░" * (10 - filled)
        icon = dim_icons.get(dim, "  ")
        name = dim_names.get(dim, dim)
        status = "✅" if val >= 7 else "⚠️" if val >= 3 else "❌"
        print(f"  {icon} {name:<12} {bar} {val:.1f}/10  {status}")

    print()

    # Stats
    print(f"  📈 Quality: {'⭐' * int(avg)} (avg {avg:.1f})")
    print(f"  🧠 Memory: {mem} entries")
    print(f"  💡 Insights: {insights}")
    print(f"  ⭐ Tasks: {tasks}")
    print()

    # Recent insights
    recent = engine.insights.list_recent(3)
    if recent:
        print("  💡 Recent Insights:")
        for i, ins in enumerate(recent, 1):
            fact_short = ins.fact[:45] + "..." if len(ins.fact) > 45 else ins.fact
            action_short = ins.action[:45] + "..." if len(ins.action) > 45 else ins.action
            print(f"    {i}. {fact_short}")
            print(f"       → {action_short}")
        print()

    # Skills section
    skills = engine.skill_tree.evaluate(report.dimensions)
    if skills:
        print("  🔮 Skills:")
        for s in skills:
            status = "✅" if s.unlocked else f"░░ {s.progress * 100:.0f}%"
            print(f"    {s.icon} {s.name} {status}")
        print()

    # Achievements
    achievements = _compute_achievements(insights, tasks, mem, avg, report)
    if achievements:
        print("  🏆 Achievements:")
        for ach in achievements:
            print(f"    {ach['icon']} {ach['name']}")
        print()

    print("=" * 55)
    print()


# ---------------------------------------------------------------------------
# Dashboard HTML generation
# ---------------------------------------------------------------------------

_DIM_ICONS = {
    "insight_loop": "👁️",
    "memory_lifecycle": "🧠",
    "self_challenge": "⚔️",
    "reflection": "🪞",
    "tool_lifecycle": "🔧",
    "architecture_search": "🏗️",
    "test_time_learning": "📚",
    "population_diversity": "👥",
    "safety_guardrails": "🛡️",
    "co_evolving_eval": "📈",
}

_DIM_NAMES = {
    "insight_loop": "洞察力",
    "memory_lifecycle": "记忆管理",
    "self_challenge": "自我挑战",
    "reflection": "反思能力",
    "tool_lifecycle": "工具管理",
    "architecture_search": "架构探索",
    "test_time_learning": "学习速度",
    "population_diversity": "群体多样性",
    "safety_guardrails": "安全守卫",
    "co_evolving_eval": "进化趋势",
}


def _generate_dashboard_html(engine: EvolutionEngine) -> str:
    """Generate the enhanced RPG dashboard HTML and return it as a string.

    Extracted for testability — callers write the result to a temp file and
    open in browser.
    """
    report = engine.report()

    insights_list = engine.insights.list_recent(10)
    scores_list = engine.scores.list_recent(10)
    mem = engine.memory.count()
    avg = engine.scores.average_quality()

    # XP / Level from engine
    xp_total = engine.xp_total
    xp_level = engine.level
    xp_progress = engine.xp_progress
    xp_next = engine.xp_to_next

    # Determine XP within current level for display
    # Find thresholds
    from evolve_kit.types import XP_TABLE
    current_threshold = 0
    next_threshold = 0
    for lvl, threshold in XP_TABLE:
        if lvl == xp_level:
            current_threshold = threshold
        if lvl == xp_level + 1:
            next_threshold = threshold
    xp_in_level = xp_total - current_threshold
    xp_span = next_threshold - current_threshold if next_threshold > current_threshold else 1
    xp_pct = (xp_progress * 100) if xp_progress < 1.0 else 100.0

    # Skills
    skills = engine.skill_tree.evaluate(report.dimensions)
    unlocked_skills = [s for s in skills if s.unlocked]
    locked_skills = [s for s in skills if not s.unlocked]

    # Achievements from engine
    achievement_list = engine.achievements.check_unlocks(
        engine.insights.count(), engine.scores.count(),
        mem, avg, report.total_score,
    )

    # Legacy achievements (from _compute_achievements)
    legacy_achievements = _compute_achievements(
        engine.insights.count(), engine.scores.count(),
        mem, avg, report,
    )

    # ── Build dimension bars HTML ─────────────────────────────────────
    dim_rows = []
    for dim, val in report.dimensions.items():
        pct = val * 10
        icon = _DIM_ICONS.get(dim, "")
        name = _DIM_NAMES.get(dim, dim)
        color = "#4caf50" if val >= 7 else "#ff9800" if val >= 3 else "#f44336"
        dim_rows.append(
            f'<div class="stat-row">'
            f'<span class="stat-icon">{icon}</span>'
            f'<span class="stat-name">{name}</span>'
            f'<div class="stat-bar"><div class="stat-fill" style="width:{pct}%;background:{color}"></div></div>'
            f'<span class="stat-val">{val:.1f}</span>'
            f'</div>'
        )

    # ── Build achievements HTML ───────────────────────────────────────
    ach_html = ""
    # Merge: prefer engine achievements (with timestamps), fall back to legacy
    seen = set()
    for a in achievement_list:
        if a.name not in seen:
            seen.add(a.name)
            ach_html += f'<div class="achievement unlocked-ach">{a.icon} {a.name}</div>'
    for a in legacy_achievements:
        if a["name"] not in seen:
            seen.add(a["name"])
            ach_html += f'<div class="achievement unlocked-ach">{a["icon"]} {a["name"]}</div>'

    # ── Build skills HTML ─────────────────────────────────────────────
    skill_html = ""
    for s in unlocked_skills:
        skill_html += (
            f'<div class="skill unlocked">'
            f'<span class="skill-icon-glow">{s.icon}</span> '
            f'{s.name} ✅</div>'
        )
    for s in locked_skills:
        bar_filled = int(s.progress * 7)
        bar_empty = 7 - bar_filled
        progress_bar = "█" * bar_filled + "░" * bar_empty
        dim_val = report.dimensions.get(s.dimension, 0.0)
        skill_html += (
            f'<div class="skill locked">'
            f'{s.icon} {s.name} {progress_bar} '
            f'{dim_val:.1f}/{s.threshold:.1f}</div>'
        )

    # ── Build insights HTML ───────────────────────────────────────────
    ins_html = ""
    for ins in insights_list[-5:]:
        fact_esc = ins.fact[:60].replace("<", "&lt;").replace(">", "&gt;")
        act_esc = ins.action[:60].replace("<", "&lt;").replace(">", "&gt;")
        ins_html += (
            f'<div class="log-entry">'
            f'<div class="log-fact">📜 {fact_esc}</div>'
            f'<div class="log-action">→ {act_esc}</div>'
            f'</div>'
        )

    # ── Build quality trend bars ──────────────────────────────────────
    recent_scores = scores_list[-10:] if scores_list else []
    trend_html = ""
    for sc in recent_scores:
        pct = (sc.quality / 5) * 100
        # Gradient: low=red, mid=yellow, high=green
        if pct <= 40:
            bar_color = "#f44336"
        elif pct <= 60:
            bar_color = "#ff9800"
        elif pct <= 80:
            bar_color = "#ffc107"
        else:
            bar_color = "#4caf50"
        title_text = f"{sc.task_name}: {sc.quality}/5"
        trend_html += (
            f'<div class="trend-bar" style="height:{pct}%;background:{bar_color}" '
            f'title="{title_text}"></div>'
        )

    total_achievements = len(achievement_list) + len(
        [a for a in legacy_achievements if a["name"] not in seen]
    )

    star_str = "\u2b50" * int(avg)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>🧬 Agent Evolution — evolve-kit</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: #1a1a2e;
    color: #e0e0e0;
    font-family: 'Courier New', monospace;
    display: flex; justify-content: center; align-items: center;
    min-height: 100vh;
    image-rendering: pixelated;
  }}
  .card {{
    background: #16213e;
    border: 4px solid #0f3460;
    border-radius: 8px;
    padding: 32px;
    max-width: 600px;
    width: 100%;
    box-shadow: 0 0 40px rgba(15, 52, 96, 0.5);
  }}
  .header {{ text-align: center; margin-bottom: 24px; }}
  .header h1 {{
    font-family: 'Press Start 2P', monospace;
    font-size: 18px;
    color: #e94560;
    margin-bottom: 8px;
  }}
  .header .level {{
    font-family: 'Press Start 2P', monospace;
    font-size: 12px;
    color: #ffd700;
  }}
  .xp-section {{ margin: 16px 0; }}
  .xp-bar {{
    background: #0f3460;
    height: 20px;
    border-radius: 10px;
    overflow: hidden;
    border: 2px solid #533483;
    position: relative;
  }}
  .xp-fill {{
    background: linear-gradient(90deg, #e94560, #ffd700);
    height: 100%;
    border-radius: 8px;
    transition: width 0.5s;
    animation: xpPulse 3s ease-in-out infinite;
  }}
  @keyframes xpPulse {{
    0%, 100% {{ box-shadow: 0 0 5px rgba(233, 69, 96, 0.4); }}
    50% {{ box-shadow: 0 0 20px rgba(255, 215, 0, 0.8); }}
  }}
  .xp-label {{
    font-family: 'Press Start 2P', monospace;
    font-size: 10px;
    text-align: center;
    color: #a0a0a0;
    margin-top: 4px;
  }}
  .stats {{ margin: 20px 0; }}
  .stat-row {{
    display: flex;
    align-items: center;
    margin: 8px 0;
    gap: 8px;
  }}
  .stat-icon {{ width: 24px; text-align: center; }}
  .stat-name {{ width: 90px; font-size: 13px; color: #a0a0a0; }}
  .stat-bar {{
    flex: 1;
    background: #0f3460;
    height: 12px;
    border-radius: 6px;
    overflow: hidden;
  }}
  .stat-fill {{
    height: 100%;
    border-radius: 6px;
    transition: width 0.5s;
  }}
  .stat-val {{ width: 36px; text-align: right; font-size: 12px; color: #ffd700; }}
  .section-title {{
    font-family: 'Press Start 2P', monospace;
    font-size: 11px;
    color: #e94560;
    margin: 20px 0 12px;
    border-bottom: 2px solid #0f3460;
    padding-bottom: 6px;
  }}
  /* Skills */
  .skills {{ display: flex; flex-direction: column; gap: 6px; }}
  .skill {{
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    border: 1px solid #533483;
  }}
  .skill.unlocked {{
    background: linear-gradient(135deg, #0f3460 0%, #1a1a2e 100%);
    border: 1px solid #ffd700;
    color: #ffd700;
  }}
  .skill.locked {{
    background: #0a0a1a;
    color: #555;
    opacity: 0.7;
  }}
  .skill-icon-glow {{
    text-shadow: 0 0 8px #ffd700, 0 0 16px #ffd700;
  }}
  /* Achievements */
  .achievements {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .achievement {{
    background: #0f3460;
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    border: 1px solid #533483;
  }}
  .achievement.unlocked-ach {{
    border: 1px solid #ffd700;
  }}
  /* Quality trend */
  .quality-trend {{
    display: flex;
    align-items: flex-end;
    gap: 4px;
    height: 80px;
    margin: 10px 0;
    padding: 8px;
    background: #0f3460;
    border-radius: 6px;
    border: 1px solid #533483;
  }}
  .trend-bar {{
    width: 16px;
    min-height: 4px;
    border-radius: 3px 3px 0 0;
    transition: height 0.5s;
  }}
  /* Battle log */
  .log-entry {{
    background: #0f3460;
    padding: 8px 12px;
    border-radius: 4px;
    margin: 6px 0;
    border-left: 3px solid #e94560;
  }}
  .log-fact {{ font-size: 12px; color: #e0e0e0; }}
  .log-action {{ font-size: 11px; color: #a0a0a0; margin-top: 2px; }}
  .footer {{
    text-align: center;
    margin-top: 20px;
    font-size: 10px;
    color: #555;
  }}
</style>
</head>
<body>
<div class="card">
  <div class="header">
    <h1>🧙 AGENT-{xp_level:02d}</h1>
    <div class="level">Level {xp_level} ⭐{star_str} | {report.level}</div>
  </div>
  <div class="xp-section">
    <div class="xp-bar"><div class="xp-fill" style="width:{xp_pct:.1f}%"></div></div>
    <div class="xp-label">Level {xp_level} — {xp_in_level}/{xp_span} XP (total: {xp_total})</div>
  </div>
  <div class="stats">
    <div class="section-title">⚔️ ATTRIBUTES</div>
    {"".join(dim_rows)}
  </div>
  <div class="section-title">🔮 SKILLS ({len(unlocked_skills)}/{len(skills)})</div>
  <div class="skills">{skill_html}</div>
  <div class="section-title">🏆 ACHIEVEMENTS ({total_achievements})</div>
  <div class="achievements">{ach_html}</div>
  <div class="section-title">📈 QUALITY TREND</div>
  <div class="quality-trend">{trend_html}</div>
  <div class="section-title">📜 BATTLE LOG</div>
  {ins_html}
  <div class="footer">evolve-kit v0.1.0 · powered by 🦞 Lobster Company</div>
</div>
</body>
</html>"""
    return html


def cmd_dashboard(engine: EvolutionEngine, args: argparse.Namespace) -> None:
    """Generate an HTML dashboard and open it in the browser."""
    import webbrowser
    import tempfile

    html = _generate_dashboard_html(engine)

    # Write to temp file and open
    tmp = Path(tempfile.mkdtemp()) / "evolve-dashboard.html"
    tmp.write_text(html, encoding="utf-8")
    webbrowser.open(tmp.as_uri())
    print(f"🧬 Dashboard opened in browser: {tmp}")


def cmd_insights(engine: EvolutionEngine, args: argparse.Namespace) -> None:
    """List recent insights."""
    recent = engine.insights.list_recent(args.n)
    if not recent:
        print("No insights recorded yet.")
        return
    for i, ins in enumerate(recent, 1):
        print(f"\n{'─' * 50}")
        print(f"💡 Insight #{i}")
        print(f"   📜 Fact:      {ins.fact}")
        print(f"   🧠 Judgment:  {ins.judgment}")
        print(f"   🎯 Action:    {ins.action}")
        if ins.source_task:
            print(f"   📋 Task:      {ins.source_task}")
        if ins.tags:
            print(f"   🏷️  Tags:      {', '.join(ins.tags)}")
        print(f"   🕐 Time:      {ins.timestamp}")


def _load_manual_scores(workspace: str) -> dict[str, float] | None:
    """Load manual dimension scores from workspace config if present."""
    config_path = Path(workspace) / "evolve-data" / "manual_scores.json"
    if config_path.exists():
        return json.loads(config_path.read_text(encoding="utf-8"))
    return None


def _compute_achievements(
    insight_count: int, task_count: int, mem_count: int,
    avg_quality: float, report,
) -> list[dict]:
    """Compute unlocked achievements based on stats."""
    achievements = []
    if task_count >= 1:
        achievements.append({"icon": "🌟", "name": "First Steps", "desc": "Complete your first task"})
    if insight_count >= 1:
        achievements.append({"icon": "💡", "name": "Insight Awakened", "desc": "Record your first insight"})
    if insight_count >= 10:
        achievements.append({"icon": "📚", "name": "Insight Scholar", "desc": "Record 10 insights"})
    if mem_count >= 5:
        achievements.append({"icon": "🧠", "name": "Memory Keeper", "desc": "Store 5 memory entries"})
    if avg_quality >= 4.0:
        achievements.append({"icon": "🔥", "name": "Quality Player", "desc": "Average quality ≥ 4.0"})
    if task_count >= 5:
        achievements.append({"icon": "⚔️", "name": "Battle Hardened", "desc": "Complete 5 tasks"})
    if report.total_score >= 50:
        achievements.append({"icon": "🏆", "name": "Half Century", "desc": "Reach 50 maturity score"})
    if report.total_score >= 70:
        achievements.append({"icon": "👑", "name": "Evolution Master", "desc": "Reach 70 maturity score"})
    # Check individual dimensions
    for dim, val in report.dimensions.items():
        if val >= 8:
            achievements.append({"icon": "⚡", "name": f"Max {dim.replace('_', ' ').title()}", "desc": f"{dim} ≥ 8"})
    return achievements


def main():
    parser = argparse.ArgumentParser(
        prog="evolve",
        description="🧬 evolve-kit — Agent Self-Evolution Toolkit",
    )
    parser.add_argument(
        "--workspace", "-w",
        default=".",
        help="Agent workspace directory (default: current directory)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # report
    report_parser = subparsers.add_parser("report", help="Show evolution report")
    report_parser.add_argument("-n", type=int, default=10, help="Number of recent items")
    report_parser.add_argument("--json", action="store_true", dest="json", help="Output as JSON")

    # insights
    insights_parser = subparsers.add_parser("insights", help="List recent insights")
    insights_parser.add_argument("-n", type=int, default=10, help="Number of insights")

    # dashboard
    subparsers.add_parser("dashboard", help="Open RPG dashboard in browser")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    engine = EvolutionEngine(args.workspace)

    if args.command == "report":
        cmd_report(engine, args)
    elif args.command == "insights":
        cmd_insights(engine, args)
    elif args.command == "dashboard":
        cmd_dashboard(engine, args)


if __name__ == "__main__":
    main()
