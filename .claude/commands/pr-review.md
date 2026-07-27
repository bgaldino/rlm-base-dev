---
description: Drive automated PR-review comments to zero unresolved (verify → sweep → reply+👍+resolve)
argument-hint: <pr-number>
---

Process **every** automated review comment on **PR #$ARGUMENTS** to **zero
unresolved threads**, following AGENTS.md §"Responding to Automated PR Reviews".
Use the helper `scripts/ai/pr_review.py`.

1. **List open threads:**
   `python scripts/ai/pr_review.py status $ARGUMENTS`

2. **For each open comment** (do NOT trust the bot):
   - **Verify against the code** — open the cited file; classify the finding
     *real*, *partial*, or *false positive*.
   - **Sweep the class** — if real, fix **every** instance of that pattern across
     the change, not just the cited line. Commit the fix; note the SHA.
   - **Resolve it** — for a **valid** finding, reply in-thread with the SHA, 👍,
     and resolve in one call:
     `python scripts/ai/pr_review.py handle $ARGUMENTS --comment <id> --body "<resolution + commit SHA>"`
     For a **false positive**, put an evidence-backed refutation in `--body` and add
     `--no-react` — reply + resolve but **don't** 👍, and don't change correct code.
     (👍 only on valid comments, per AGENTS.md.)

3. **Confirm clean:**
   `python scripts/ai/pr_review.py verify $ARGUMENTS` → must report **0
   unresolved**. If any remain, handle them and re-run.

4. **End the round by running the gate — this is what closes it, not step 3:**
   `python scripts/ai/pre_push_audit.py --pr $ARGUMENTS` → must exit **0**.

   Zero unresolved threads only means every finding *the bot raised* was answered.
   It says nothing about the **rest of each class**, and that is exactly where this
   repo loses rounds: on PR #317, rounds 4–9 were almost entirely unswept instances
   of classes already found in rounds 1–3, several of them in files the change never
   touched. The gate sweeps the whole surface, so it catches what a thread-by-thread
   pass cannot. Exit **2** means a check could not run or a review prompt is
   unacknowledged — neither is a pass, so fix it rather than pushing past it.

   Then push **once** for the whole round (REVIEW.md → *Push discipline*).

Never leave a thread open: branches headed for `main` mirror to the internal
Salesforce repo for audit, which re-raises any open thread.
