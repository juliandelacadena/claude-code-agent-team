# Claude Code Agent Team

A four-agent AI team, built on Claude Code, that runs the day-to-day operations of a small
apparel brand — prioritization, ad creative, marketing strategy, and financial modeling.

**[Live demo](https://claude.ai/artifact/1WApZa6WQ6hn6BnUxDKPte)**

## What it does

| Agent | Role |
|---|---|
| **Antony** | Chief of staff — weekly prioritization, sequencing, what to drop. Entry point. |
| **Oppius** | Ad creative and copy from existing assets. Drafts only. |
| **Curio** | Marketing strategy — trends, competitor comparisons, growth plan. |
| **Balbus** | Unit economics and financial modeling. Never invents a figure. |

Each agent has a defined scope and boundaries, and all four read one shared context file
(`CLAUDE.md`) so they stay consistent instead of behaving like a single generalist assistant.
A `review-gate` skill has one agent check another's output before anything ships.

> **Note:** the brand ("When in Rome"), its numbers, and its dates are fictional sample data.
> The agent architecture itself is production — this pattern runs a real independent apparel
> brand today, with the real data swapped out here so the repo is safe to share and run.

## Install

Requires [Claude Code](https://docs.claude.com/en/docs/claude-code).

```bash
git clone https://github.com/<your-username>/claude-code-agent-team.git
cd claude-code-agent-team
claude
```

## Usage

```
antony, what should I focus on this week
have oppius draft 3 ad angles for the capsule drop
curio, how does this compare to Uniqlo's approach
```

## Structure

```
CLAUDE.md                  shared context every agent reads first
.claude/agents/*.md        the four specialists
.claude/skills/*/SKILL.md  repeatable routines, including review-gate
brand/                     brand voice + sample launch plan
data/                      sample-only figures (real data never goes in git)
```

---
Julian De La Cadena
