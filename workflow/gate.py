#!/usr/bin/env python3
"""
V4 — Machine-enforced review workflow.

The invariants below are enforced by this script's control flow, not by asking an agent to
follow them in a system prompt. If you try to violate one, the script refuses before making
any API call, or before the state can advance.

Enforced invariants:
  - An agent cannot review its own work. Checked in code before the review call is made.
  - A rejected artifact cannot be marked ready. It sits in `needs_revision` until re-submitted
    and it passes review — there is no code path from `needs_revision` to `human_approved`.
  - Nothing reaches `human_approved` without first being in `approved_pending_human`, which
    only `review` can set, and only on an APPROVE verdict.
  - `approve` requires a literal typed "APPROVE" on stdin. There is no flag or argument that
    skips this.

Usage:
    python3 workflow/gate.py submit <author_agent> <content_file>
    python3 workflow/gate.py review <record_id> <reviewer_agent>
    python3 workflow/gate.py approve <record_id>
    python3 workflow/gate.py status [record_id]
"""
import json
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STATE_FILE = Path(__file__).resolve().parent / "state.json"
TIMEOUT = 180


def load():
    return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}


def save(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))


def now():
    return datetime.now(timezone.utc).isoformat()


def call_agent(agent, prompt):
    cmd = ["claude", "--agent", agent, "-p", prompt,
           "--permission-mode", "acceptEdits", "--output-format", "text"]
    r = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=TIMEOUT)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "agent call failed")
    return r.stdout.strip()


def parse_verdict(verdict):
    """Take the LAST standalone APPROVE/REJECT line in the response, not the first.

    A reviewer can start typing one answer and correct itself mid-response (this happened in
    testing — a real model wrote "APPROVE", then "Wait — that's wrong... REJECT"). Reading only
    the first line would have recorded the reviewer's mistake, not its actual verdict. Falls
    back to a first-line check only if no standalone marker line exists anywhere.
    """
    markers = re.findall(r"(?m)^\s*\**\s*(APPROVE|REJECT)\s*\**\s*$", verdict.upper())
    if markers:
        return markers[-1] == "APPROVE"
    first = verdict.strip().splitlines()[0].strip().upper() if verdict.strip() else ""
    return first.startswith("APPROVE")


def cmd_submit(author, content_file):
    content = Path(content_file).read_text()
    rid = uuid.uuid4().hex[:8]
    state = load()
    state[rid] = {
        "id": rid, "author": author, "content": content,
        "status": "pending_review", "reviewer": None, "review_feedback": None,
        "history": [{"at": now(), "event": "submitted", "by": author}],
    }
    save(state)
    print(f"Submitted. Record id: {rid}  status: pending_review")


def cmd_review(rid, reviewer):
    state = load()
    if rid not in state:
        sys.exit(f"No such record: {rid}")
    rec = state[rid]
    if rec["status"] not in ("pending_review", "needs_revision"):
        sys.exit(f"Refused: record {rid} is '{rec['status']}' — nothing to review.")
    if reviewer == rec["author"]:
        # THE ENFORCED INVARIANT — checked before any API call is made, no override exists.
        sys.exit(f"Refused: '{reviewer}' authored this artifact and cannot review its own "
                 f"work. Choose a different reviewer.")

    prompt = (
        f"Run the review-gate check on this draft, written by {rec['author']}, before it can "
        f"ship. Check it against brand voice, unbacked claims/numbers, and real risk (fake "
        f"urgency/scarcity).\n\nDRAFT:\n{rec['content']}\n\n"
        "Respond with a first line of exactly 'APPROVE' or 'REJECT', then your reasoning."
    )
    verdict = call_agent(reviewer, prompt)
    passed = parse_verdict(verdict)

    rec["reviewer"] = reviewer
    rec["review_feedback"] = verdict
    rec["status"] = "approved_pending_human" if passed else "needs_revision"
    rec["history"].append({"at": now(), "event": "reviewed", "by": reviewer, "result": rec["status"]})
    save(state)

    print(f"Review by {reviewer}: {'APPROVE' if passed else 'REJECT'}\n")
    print(verdict)
    print(f"\nStatus: {rec['status']}")
    if not passed:
        print("This artifact CANNOT be marked ready. It stays in needs_revision until "
              "re-submitted and it passes review — there is no path around that in this script.")


def cmd_approve(rid):
    state = load()
    if rid not in state:
        sys.exit(f"No such record: {rid}")
    rec = state[rid]
    if rec["status"] != "approved_pending_human":
        sys.exit(f"Refused: record {rid} is '{rec['status']}' — it must pass review "
                 f"(status: approved_pending_human) before a human can approve it.")

    print("--- Content awaiting approval ---")
    print(rec["content"])
    print("\n--- Reviewer verdict ---")
    print(rec["review_feedback"])
    confirm = input("\nType APPROVE to confirm a human is authorizing this to ship: ").strip()
    if confirm != "APPROVE":
        print("Not approved. No state change.")
        return

    rec["status"] = "human_approved"
    rec["history"].append({"at": now(), "event": "human_approved"})
    save(state)
    print(f"\nRecord {rid} is now human_approved — the only status a real publish step in "
          f"this system would be allowed to act on.")


def cmd_status(rid=None):
    state = load()
    if rid:
        print(json.dumps(state.get(rid, {"error": "not found"}), indent=2))
        return
    for r in state.values():
        print(f"{r['id']}  {r['status']:<22} author={r['author']:<8} reviewer={r['reviewer']}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    cmd, rest = args[0], args[1:]
    {"submit": cmd_submit, "review": cmd_review, "approve": cmd_approve,
     "status": cmd_status}.get(cmd, lambda *_: sys.exit(__doc__))(*rest)
