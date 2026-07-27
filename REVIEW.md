# Code Review Guide

How pull requests in this repository get reviewed — by humans and by AI reviewers.

**Audience:** everyone. Salesforce employees (PMs, SEs), partners, customers and public
contributors all work in this repo, on a mix of workstations. Nothing here requires
Salesforce-internal tooling. Where such tooling exists it is an *accelerator*, never a
prerequisite — see [Optional accelerators](#optional-accelerators).

**For AI reviewers:** this file is read automatically alongside `AGENTS.md`. `AGENTS.md`
is the canonical source for *what the code must do*; this file governs *how review is
conducted*.

The two overlap on three points by design — verifying a finding, sweeping a class, and
push discipline. `AGENTS.md` carries the short operational form of each inside its
step-by-step PR protocol; this file carries the reasoning behind it. Keep those three in
sync when either file changes, and do not add duplication beyond them.

---

## The one instruction that matters most

> **Only report findings that are real problems: a defect, a security issue, a
> correctness gap, or a rule in `AGENTS.md` being broken. If there are none, say so and
> return nothing.**

Comment volume is not a quality signal. An empty review on a clean diff is a correct
review. The most common failure of a capable reviewer is producing plausible-sounding
comments to avoid staying silent — every false positive costs a contributor's attention
and trains them to skim.

Do **not** report: style preferences the linter does not enforce, speculative
refactors, "consider extracting this", or anything already covered by an automated
check.

---

## Severity

| Severity | Meaning | Expected action |
|----------|---------|-----------------|
| **Critical** | Data loss, a security hole, or a violation of a documented `AGENTS.md` DO NOT | Fix before merge, no exceptions |
| **Important** | Wrong behaviour under a reachable condition | Fix before merge, or state explicitly why not |
| **Nit** | Real but minor; correctness unaffected | Author's discretion |
| **Pre-existing** | Already on `main`, surfaced by this diff | Do not block; file follow-up work |

State the severity on every finding. An unranked list of comments is a dump, not a
review.

---

## What to look for

Ordered by priority. Weight the first two above everything else.

1. **Correctness** — does it do what it claims, including on the failure paths?
2. **Safety** — destructive operations, data deletion, `deleteOldData`, anything
   irreversible. See `AGENTS.md` → *DO NOT* and the SFDMU rules.
3. **Bulk safety (Apex)** — SOQL or DML inside a loop; unbounded queries; governor
   limits; missing `USER_MODE`/CRUD-FLS where required.
4. **Idempotency** — can this run twice without duplicating or corrupting?
5. **Verification** — is the claim actually tested, and by something that would fail if
   the behaviour regressed?
6. **Documentation drift** — does a doc, README or skill now say something untrue?
   `AGENTS.md` → *Documentation consistency* has the change-surface map.

---

## The defect classes this repo actually produces

Derived from real findings on this repository. Check these specifically — they recur,
they are subtle, and they survive ordinary review.

**A partial failure hiding behind an aggregate.** A map or set built from query results
cannot contain what the query never returned, so any check that iterates it validates
only what already succeeded. *The fix is always to iterate the EXPECTED set and diff
against what was found.* This is the single most common defect class here.

**Reporting without failing.** Code that prints, logs or warns about a problem and then
returns success. A missing record printed but not counted; a skipped item logged but the
exit code still 0. If it is worth reporting, it is worth failing on — or the report must
say plainly that the operation was partial.

**A check scoped narrower than the bug it ships with.** A validation added alongside a
fix, but filtered so it cannot see the very failure that motivated it. When reviewing a
new check, ask: *would this have caught the bug in this same PR?*

**A field selected but never read.** `Status`, `IsActive` and similar pulled into a query
and then not used, so inactive or draft rows silently satisfy the check.

**A fix that stops the damage but does not propagate the signal.** An early return, a
clamp, or a guard that protects internal state while the caller still sees success.
Check the return value and the exit code, not just the logic.

**Silent scope narrowing.** A `WHERE` clause that quietly excludes rows the caller
believes are included — filtering by status, type or ownership without saying so.

**Unverified numbers in documentation.** Arithmetic, record counts and rates asserted in
a guide without a recorded live run behind them. Mark unverified figures as such rather
than stating them plainly.

---

## Verifying a finding before acting on it

**Applies to both directions:** to an AI reviewer writing a finding, and to anyone
triaging comments an AI reviewer produced.

1. **Open the file and confirm the claim.** Fluent, confident wording is not evidence.
   AI reviewers are wrong a substantial fraction of the time, and the wrong ones read
   exactly like the right ones.
2. **Classify it:** real / partially real / false positive.
3. **If real, sweep the whole class.** Fix every instance of the pattern in the change,
   not the cited line. A finding is a symptom; the pattern is the bug.
4. **If false, refute it with evidence** — quote the code, the schema, or the run that
   disproves it. Do not change correct code to silence a reviewer.
5. **Treat test changes with extra scrutiny.** An assertion edited to match new
   behaviour may be a fix or may be a bug being ratified. Establish which.

`AGENTS.md` → *Responding to Automated PR Reviews* defines the reply/resolve protocol
and the tooling. Every round ends at zero unresolved threads.

---

## Push discipline

**Batch fixes into one push per review round.**

Every push to an open PR triggers a fresh automated review, and hosted reviewers are
metered — most plans allow far fewer reviews per month than you would guess, and a
single PR reviewed per-fix can consume the lot. But cost is only half the reason:

- **Re-reviews are not incremental.** A hosted reviewer re-reads the whole diff and may
  repeat comments you already dismissed or resolved, so iterating with it means
  re-adjudicating the same findings.
- **A review races the next push.** Push again while one is running and it lands against
  a superseded commit, spending a full round on findings that no longer apply.

Neither improves with more pushes. So:

- Take **all** findings from a round, fix them, verify locally, push **once**.
- Multiple commits are fine — just do not push between them.
- Finish local verification *before* pushing, not between pushes.
- Never push a lone typo or comment fix; fold it into the next batch.

**"Verify locally" is now a command, not a judgement call:**

```bash
python scripts/ai/pre_push_audit.py --pr <n>
```

It must exit **0**. This exists because the judgement is what failed: PR #317 ran
to **nine** rounds, and rounds 4–9 were almost entirely unswept instances of classes
already found in rounds 1–3 — several of them earlier fixes left half delivered. Every
one was a metered round spent on a defect that was knowable locally, and the tooling to
catch it already existed and simply was not run. Asking people to remember did not
work, so the gate fails instead: five tiers, exit **1** on a failure and **2** when a
check *could not run* or a review prompt is unacknowledged, because an unknown result is
worse than a known bad one.

Install it once per clone (`scripts/bash/install-git-hooks.sh`) and it runs on every
push. `git push --no-verify` still bypasses it — deliberately, since a gate with no exit
is a gate people uninstall — but that is a choice on the record, not a default.

**Keep diffs small.** Beyond roughly 10,000 changed lines, automated reviewers begin
truncating or skipping. A PR that outgrows review is a PR that ships unreviewed.

---

## Optional accelerators

Not required, and not available to every contributor. Use them where you have them.

- **Local AI review before pushing.** Reviewing your own diff locally costs nothing
  against a PR-review budget and removes most findings before a hosted reviewer runs.
- **A second, independent reviewer.** Coverage comes from *different* reviewers, not
  more passes from one — a model reviewing its own output carries the same blind spots
  it had while writing. If you have two, run the cheaper one first and reserve the other
  as a final sweep on an already-clean diff.
  **Fetch before you review.** A reviewer working from a stale clone compares the diff
  against an old base, which produces confident *false negatives* — the quiet kind you
  never notice. A cross-workstation review here reported a test file as "not present on
  any branch" when it had merged to `main` hours earlier; it was retracted, but only
  because someone checked. If tooling is misbehaving (`gh` auth, TLS), assume `git fetch`
  may be affected too, and confirm your base before trusting the pass.
- **Salesforce-internal reviewers** (PRizm, CodeGenie and similar) operate on internal
  Git hosts, not on this public repository. They are the internal-repo playbook, not an
  option here.

---

## When an automated reviewer catches something we missed

Add the pattern to *The defect classes this repo actually produces* above. That section
is not a fixed list — it is how review quality compounds. A class captured once is a
class caught for free on every later PR.
