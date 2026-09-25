---
name: agent-builder
description: Build a new agent for When in Rome, on demand. Use when the founder says "I need an agent for <X>", "add a teammate", "hire an agent", or describes a recurring job no current agent owns. Researches the role, drafts a proper agent file, and only saves it after the founder approves.
---

# Agent builder

The team hires itself when a real gap shows up, instead of the founder hand-rolling a new
agent from scratch every time.

1. **Clarify the role.** Ask the founder: what will this agent own, when would they call it,
   what does a great result look like? Confirm no existing agent (antony, oppius, curio,
   balbus) already covers it — if one does, say so and stop.
2. **Research the domain.** Use web search to learn the expertise, frameworks, and best
   practices the role needs, so the new agent is genuinely good and not generic.
3. **Draft the agent file** to match the existing four:
   - `name`, a routing `description`, and a `model` recommendation (default `sonnet`).
   - **What it always reads first** — always `CLAUDE.md`, plus any relevant `brand/` or
     `data/` files.
   - **Its job**, **how it works**, and a clear **output format**.
   - **Boundaries** carrying the house rules: never fabricate numbers or claims, label
     assumptions, keep financial data local, draft-don't-publish where relevant.
4. **Show the founder the full draft** and the recommended model. Do **not** save yet.
5. **On approval**, write the file to `.claude/agents/<name>.md` and add the new agent to the
   "team" list in `CLAUDE.md`.
6. Remind the founder to keep the team small — add an agent only when a gap is real, not
   merely interesting.
