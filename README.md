# When in Rome — AI Agent Team

Four AI specialists — Antony, Oppius, Curio, Balbus — running the day-to-day of a fictional
apparel label: prioritization, ad creative, marketing strategy, and unit economics. One human
founder in the loop, everything drafted for approval.

**[Try it live →](https://claude.ai/artifact/1WApZa6WQ6hn6BnUxDKPte)** (runs on a fictional
brand, "When in Rome," so it's safe to click around — no real business data here)

## What this is

The brand runs on Claude Code as a small, permanent team instead of one long chat:

| Agent | Job |
|---|---|
| **Antony** | Chief of staff — weekly prioritization, sequencing, what to ignore. Talk to first. |
| **Oppius** | Turns existing photos/copy into ad creative and copy. Drafts only. |
| **Curio** | Sales & marketing strategy — trends, competitor teardowns, the growth plan. |
| **Balbus** | Real numbers only — unit economics, path-to-goal modeling. Never invents a figure. |

**Agents = who. Skills = how. `CLAUDE.md` = what's true.** Every agent reads the same shared
brief before answering, which is why they don't contradict each other, and each one has
written boundaries (draft-only, never fabricate, ask instead of guess) instead of being a
generic assistant with no job description.

## Why it's built this way

Three rules did more for reliability than anything else:

1. **The coordinator routes, it doesn't do the work.** Antony assigns to a specialist instead
   of just answering itself — otherwise you lose the specialist framing and the record of who
   did what.
2. **The brief is the product.** Agents can't see each other's conversations, so if a fact
   isn't written into `CLAUDE.md` or handed to them directly, they don't have it. Most bad
   answers trace back to a thin prompt, not a weak agent.
3. **Real numbers only, everywhere.** Every agent's file has an explicit rule against
   inventing a stat, a review, or a dollar figure — missing data gets a question or a
   `[NEEDS SOURCE]` flag instead of a plausible-sounding guess.
4. **Nothing ships on the first draft.** The `review-gate` skill has one agent check another's
   work — voice, unbacked claims, real risk — before it goes anywhere public. An agent never
   clears its own output.

## Repo layout

```
CLAUDE.md                 # the shared brief every agent reads first
.claude/agents/*.md        # the four specialists — name, job, boundaries
.claude/skills/*/SKILL.md  # repeatable routines (e.g. "plan my week", "make me ads")
brand/                     # brand voice + the sample launch plan
data/                      # sample-only numbers (real figures never go in git — see CLAUDE.md's own rule)
```

## Run it yourself

```
claude   # from this folder — Claude Code loads CLAUDE.md and the agents automatically
```

Then just talk to it: `antony, what should I focus on this week` or
`have oppius draft me 3 ad angles`.

## What's real vs. sample here

The agent definitions, the skills, and the pattern are exactly what's running behind the live
demo. The numbers in `data/` and the plan in `brand/` are placeholders, clearly marked — real
business data never goes in a public repo, per the rule baked into `CLAUDE.md` itself.

---
Built by Julian De La Cadena.
