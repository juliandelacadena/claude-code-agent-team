#!/usr/bin/env python3
"""
V3 — Agent evaluation suite.

Runs real, live calls against the actual agents in this repo (no mocking, no fixtures) and
checks the responses with structured assertions, not just "did it say the magic phrase":

  - "grounded"  — extracts every $amount in the response and fails if any of them isn't
                  backed by a real figure in this repo's data files, plus requires an
                  explicit missing-data flag phrase.
  - "contains"  — deterministic phrase presence/absence (used for the mutable-state and
                  role-boundary cases, where the correct behavior is a specific fact).
  - "judged"    — for cases that need real judgment (did it accept a false premise, did it
                  catch an unsupported claim), a second live Claude call grades the response
                  against a written rubric and returns PASS/FAIL + a reason. This is a real
                  LLM-as-judge call, not a hardcoded verdict.

Usage:
    python3 evals/run_evals.py            # run every case in cases.json
    python3 evals/run_evals.py G1 S1      # run only the named case(s), for quick iteration

Writes evals/results.json (every case's full response + verdict) and prints a summary table.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CASES_FILE = Path(__file__).resolve().parent / "cases.json"
RESULTS_FILE = Path(__file__).resolve().parent / "results.json"
TIMEOUT = 180


def run_agent(agent, prompt):
    cmd = ["claude", "--agent", agent, "-p", prompt,
           "--permission-mode", "acceptEdits", "--output-format", "text"]
    r = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=TIMEOUT)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "agent call failed")
    return r.stdout.strip()


def run_judge(prompt):
    cmd = ["claude", "-p", prompt, "--permission-mode", "acceptEdits", "--output-format", "text"]
    r = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=TIMEOUT)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "judge call failed")
    return r.stdout.strip()


def strip_brackets(text):
    return re.sub(r"\[[^\]]*\]", "", text)


def extract_dollar_amounts(text):
    return [m.replace(",", "") for m in re.findall(r"\$([0-9]{1,3}(?:,[0-9]{3})*)", strip_brackets(text))]


def known_dollar_amounts():
    amounts = set()
    for fname in ("data/financials.md", "data/inventory.md", "CLAUDE.md"):
        text = (REPO / fname).read_text()
        amounts.update(extract_dollar_amounts(text))
    return amounts


def check_grounded(response, case):
    known = known_dollar_amounts()
    found = extract_dollar_amounts(response)
    unknown = [n for n in found if n not in known]
    phrases = case["check"].get("flag_phrases", [])
    has_flag = any(p.lower() in response.lower() for p in phrases)
    ok = has_flag and not unknown
    reasons = []
    if not has_flag:
        reasons.append(f"missing an expected missing-data flag phrase (one of {phrases})")
    if unknown:
        reasons.append(f"contains dollar amount(s) not backed by any data file: {unknown}")
    return ok, "; ".join(reasons) or "flagged missing data correctly and used no unbacked numbers"


def check_contains(response, case):
    c = case["check"]
    text = response.lower()
    for p in c.get("must_contain", []):
        if p.lower() not in text:
            return False, f"missing required text: '{p}'"
    for p in c.get("must_not_contain", []):
        if p.lower() in text:
            return False, f"contains text that should have been replaced by the state override: '{p}'"
    return True, "all required/forbidden text conditions satisfied"


def check_judged(response, case):
    rubric = case["check"]["rubric"]
    prompt = (
        "You are a strict evaluator for an AI-agent test suite. Judge ONLY against this rubric, "
        "nothing else.\n\nRUBRIC:\n" + rubric +
        "\n\nMODEL OUTPUT TO GRADE:\n" + response +
        "\n\nRespond with exactly one line 'PASS' or 'FAIL', then a second line with a "
        "one-sentence reason. No other text."
    )
    verdict = run_judge(prompt)
    lines = [l.strip() for l in verdict.strip().splitlines() if l.strip()]
    ok = bool(lines) and lines[0].upper().startswith("PASS")
    reason = lines[1] if len(lines) > 1 else verdict
    return ok, reason


CHECKERS = {"grounded": check_grounded, "contains": check_contains, "judged": check_judged}


def apply_state_override(case):
    override = case.get("state_override")
    if not override:
        return None
    path = REPO / override["file"]
    original = path.read_text()
    if override["find"] not in original:
        raise RuntimeError(f"state_override text not found in {override['file']}: {override['find']!r}")
    path.write_text(original.replace(override["find"], override["replace"], 1))
    return path, original


def restore_state(backup):
    if backup:
        path, original = backup
        path.write_text(original)


def run_case(case):
    backup = None
    try:
        backup = apply_state_override(case)
        response = run_agent(case["agent"], case["input"])
        ok, reason = CHECKERS[case["check"]["type"]](response, case)
    except Exception as e:  # noqa: BLE001 — a failed live call is a real eval failure, not silently swallowed
        response, ok, reason = "", False, f"ERROR: {e}"
    finally:
        restore_state(backup)
    return {
        "id": case["id"], "category": case["category"], "agent": case["agent"],
        "check_type": case["check"]["type"], "pass": ok, "reason": reason, "response": response,
    }


def main():
    all_cases = json.loads(CASES_FILE.read_text())
    only = set(sys.argv[1:])
    cases = [c for c in all_cases if not only or c["id"] in only]
    if not cases:
        sys.exit(f"No matching case ids in {sorted(only)}")

    results = []
    for case in cases:
        print(f"[{case['id']}] {case['category']} -> {case['agent']} ... ", end="", flush=True)
        r = run_case(case)
        print("PASS" if r["pass"] else "FAIL", "-", r["reason"])
        results.append(r)

    RESULTS_FILE.write_text(json.dumps(results, indent=2))

    by_cat = {}
    for r in results:
        p, t = by_cat.setdefault(r["category"], [0, 0])
        by_cat[r["category"]] = [p + (1 if r["pass"] else 0), t + 1]

    print("\nAgent Evaluation Suite\n")
    width = max(len(c) for c in by_cat) + 2
    for cat, (p, t) in by_cat.items():
        flag = "PASS" if p == t else ""
        print(f"{cat:<{width}}{p}/{t} {flag}")
    total_pass = sum(r["pass"] for r in results)
    print(f"\nOverall: {total_pass}/{len(results)}")
    print(f"\nFull results written to {RESULTS_FILE.relative_to(REPO)}")


if __name__ == "__main__":
    main()
