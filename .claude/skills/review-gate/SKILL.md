---
name: review-gate
description: A second pass before anything goes public — an ad, a caption, a claim with a number in it. Use when the founder says "review this before it ships" or before publishing any customer-facing draft. Any agent can run it; it never approves its own work.
---

# Review gate

Nothing ships on the first draft alone. This is the check that runs before it does.

1. **Who reviews:** whichever agent didn't write the draft. Curio checks Oppius's ad copy;
   Oppius checks a Curio recommendation that's about to be posted; Antony reviews anything the
   founder brings in from outside. An agent never clears its own work.
2. **Check against three things:**
   - **Voice** — does this sound like `brand/brand-identity.md`, or does it read like generic
     ad copy?
   - **Unbacked claims** — any number, stat, or review not sourced in `CLAUDE.md` or the
     `data/` files gets fixed or cut. `[NEEDS SOURCE]` is not a claim, it's a flag.
   - **Real risk** — fake urgency, fake scarcity, anything a customer could reasonably
     misread.
3. **Verdict:** approve, approve with a specific fix, or send back with what's wrong named
   plainly. No vague "make it better."
4. **Output:** the verdict plus the fixed version if anything changed. The founder still hits
   publish — this gate catches problems, it doesn't grant permission.
