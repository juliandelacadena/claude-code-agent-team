# Example: refusing to invent a missing number

Real output from `balbus`, run against this repo's actual sample data.

**Input:**
> What's our exact cost of goods for the wool blend used in the field jacket, broken out
> separately from labor?

**Output:**

> **Real numbers I have (as of `data/financials.md`, no date stamped on the file itself):**
>
> | SKU | Cost | Retail | Margin |
> |---|---|---|---|
> | Field Jacket | $79 | $198 | 60% |
>
> **What I don't have:** `financials.md` gives only a single blended per-unit cost ($79) for
> the Field Jacket. There's no breakout by material vs. labor vs. trim — just the one
> landed-cost figure.
>
> I can't split that $79 into "wool blend fabric" vs. "labor" without fabricating numbers —
> CLAUDE.md and my own rules are explicit: never invent costs, missing data → ask.
>
> To give you the breakout, I need one of:
> - Your factory/supplier costing sheet for the Field Jacket (fabric cost/unit + labor
>   cost/unit), or
> - Fabric cost per yard × yards used, plus the labor line from your manufacturer invoice.
>
> **Takeaway:** the $79 Field Jacket cost is currently one blended figure, not broken out —
> material vs. labor is `[NEEDS SOURCE]`. Lever: get the factory costing sheet; fastest way to
> see if fabric or labor is the bigger driver on your thinnest-margin SKU (60%, lowest of the 8).

**What this shows:** asked for something that sounds like a reasonable follow-up question,
Balbus doesn't estimate a plausible-sounding split. It states exactly what data exists, names
exactly what's missing, and says what would need to be provided to actually answer it.
