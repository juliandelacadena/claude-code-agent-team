# Roadmap — V5 through V8

This is an architecture plan, not a to-do list of things half-built. Nothing below is
implemented. It exists so the next layer, if it's ever built, doesn't require rewriting V3/V4
— the interfaces here are designed against what already exists, not invented in the abstract.

**Why these aren't built yet:** V3 (evals) and V4 (the workflow gate) didn't expose a real
need for any of this. The agents ground themselves correctly, propagate state correctly, and
respect their boundaries in 15/16 real test cases. Building orchestration, a data layer, or a
benchmark on top of that isn't solving a problem this repo currently has — it would be
complexity for its own sake. Each section below states the specific trigger that would
justify building it.

---

## V5 — State-aware orchestration

**Trigger to build this:** running a full weekly cycle by hand (talk to Antony, then whichever
specialist it names, then feed that back) becomes something Julian actually does often enough
that automating the hand-offs saves real time, not hypothetical time.

**What it is not:** `for agent in [antony, curio, balbus]: call(agent)`. That's automation with
none of the actual value — it calls agents that aren't needed and can't route around a failure.

**Interface:**

```python
def run_weekly_cycle(state_path="CLAUDE.md") -> CycleResult:
    state = load_state(state_path)                    # parse the current goals/constraints
    objective = call_antony(state)                     # "what matters most right now"
    needed = objective.required_specialists            # e.g. ["curio"], not all three
    outputs = {}
    for agent in needed:
        result = call_specialist(agent, objective, state)
        if result.needs_review:
            verdict = gate.review(result, reviewer=pick_reviewer(agent))
            if not verdict.passed:
                result = call_specialist(agent, objective, state, revision_of=result, feedback=verdict)
        outputs[agent] = result
    brief = assemble_brief(objective, outputs)
    return CycleResult(brief=brief, needs_human_approval=any_consequential(outputs))
```

`pick_reviewer(agent)` must never return `agent` itself — this reuses `workflow/gate.py`'s
existing invariant rather than re-implementing it. `call_specialist` is only invoked for agents
`objective.required_specialists` actually names — the "conditional execution," not a fixed
chain. Retry is bounded (one revision pass, not an unbounded loop) and a second failed review
surfaces to the human rather than looping forever.

---

## V6 — Real data/tool layer

**Trigger to build this:** the sample data in `data/*.md` stops being representative because
a real deployment needs live numbers, or a real integration (Shopify, a spreadsheet) exists to
pull from.

**What changes, what doesn't:** agents keep reading `CLAUDE.md` for durable rules and voice.
Quantitative facts move from static prose into a queryable local store — SQLite, to avoid
requiring any paid account or API key for the core repo to run.

```python
# data/store.py
def get_revenue(sku: str | None = None) -> Decimal: ...
def get_inventory(sku: str | None = None) -> dict[str, int]: ...
def get_ad_spend(channel: str | None = None) -> list[SpendRecord]: ...
def get_current_goals() -> Goals: ...          # reads CLAUDE.md's goal section, not duplicated data
```

Balbus's agent definition doesn't change its responsibilities — it still owns unit economics
and never invents a figure. What changes is where "read the data first" points: a function
call instead of a markdown table. `get_current_goals()` reading `CLAUDE.md` directly (not a
copy of it) is the point — it's the same "don't duplicate mutable state" rule V3/V4 already
enforce, just extended to code instead of only prompts. External integrations (Meta, Shopify)
stay optional adapters behind this same interface — never required to run the demo.

---

## V7 — Tracing and observability

**Trigger to build this:** V5 exists and a run does something confusing enough that "what did
it actually see, and why did it call that agent" needs answering after the fact.

```
runs/<run-id>/
  input.json          # the objective/state the cycle started from
  routing.json         # which specialists were called and why (objective.required_specialists)
  agent_outputs/*.json # each specialist's raw output
  reviews/*.json        # each review-gate verdict, pass or fail
  final.md              # the assembled brief
  trace.json            # ordered event log: called X, reviewed by Y, revised, approved by human
  metrics.json           # call count, approximate tokens/latency per step — no secrets, ever
```

This only has value once V5 exists — tracing a manual chat session is just reading the
transcript, which is already what `examples/` does.

---

## V8 — Single-agent baseline and benchmark

**Trigger to build this:** someone credibly asks "does the four-agent structure actually beat
one well-prompted agent, or is this complexity for its own sake" — which is a fair question,
and the honest answer requires a real, unrigged comparison, not an assertion.

**Design constraints, non-negotiable:**
- The baseline agent gets the same task and the same context (all of `CLAUDE.md`, `brand/`,
  `data/`) as a single system prompt — not weakened, not given less information.
- Same eval scenarios from `evals/cases.json` run against both.
- Every dimension gets reported, including ones where the baseline wins:

| Dimension | Single agent | Agent team |
|---|---:|---:|
| Unsupported claims | ? | ? |
| Invented numbers | ? | ? |
| Missed constraints | ? | ? |
| Review catches | n/a | ? |
| Calls per task | 1 | ? |
| Approx. tokens | ? | ? |

- **No fixture results presented as live-model results, ever.** If live invocation can't run
  repeatably in whatever environment builds this, the report says so explicitly and marks
  every number as a fixture, not a benchmark.

The real engineering question V8 answers isn't "is multi-agent better" — it's **when does
specialization justify its added cost and complexity, and when doesn't it.** A benchmark that
can't show the agent team losing on some dimension isn't a benchmark.
