# Briefing an External Review Agent

> How to commission a code review from another agent — a cowork/`/code-review ultra`
> run, a Codex bundled reviewer, or any other model — and what to put in the prompt so
> the round is worth what it costs. The parent skill (`SKILL.md`) covers what to do with
> findings once they exist; this covers getting good ones in the first place.
>
> Read with `SKILL.md` → *Workflow patterns for scale*, which describes the fan-out
> shape (find → dedup → adversarially verify → synthesize) this briefing feeds.

## Quick Rules

1. **Cite a LOCAL ref, never `origin/main`.** Pushing this repo fires a metered Copilot
   review, so pre-push rounds review unpushed commits. Give the merge-base SHA
   explicitly (`git merge-base main HEAD`) — an agent told to diff against a remote will
   diff against work that is not there and report nothing.
2. **The exclusion list is the whole economy.** Without it, every reviewer independently
   rediscovers what you already know, and you pay per rediscovery. It has two sources:
   what a previous round verified clean, and what a commit *deliberately* bounded out.
   Name both.
3. **State severity in the feature's own terms.** Generic reviewers optimise for finding
   count. Tell them which failure direction actually matters here, and which one is the
   intended design (e.g. "over-refusing is the sanctioned direction; a confident wrong
   answer is not"). This is what makes a review lead with the finding that matters
   instead of five nits.
4. **Point them at your premises, not just your code.** The valuable target is the thing
   only you have scrutinised — the assumption a design rests on. Ask them to attack it.
5. **Tell them to flag unverifiable premises rather than skip them.** The single most
   valuable finding of the review this file came from was raised as "Important *pending
   live confirmation* — cannot be established offline", and turned out to be a real
   false-Fresh across 12 tables. A reviewer that stays silent on what it cannot prove is
   worth less than one that says so.
6. **One artifact per reviewer per round**, named with BOTH the round and the model —
   distinct reports must never overwrite each other (see *Artifacts* below).
7. **Read-only.** Say it explicitly: no pushing, no deploying, no file edits, no org
   mutations. A reviewer that "helpfully" fixes things costs you the diff.

## DO NOT

- **DO NOT** let two reviewers write to the same filename. Round 2 of the run behind this
  file produced a `-round2.md`, a `-round2-claude.md`, and a stray `-round2-prior.md`
  precisely because the naming was decided after the fact.
- **DO NOT** ask for a re-review of the whole branch each round. Give the full range for
  context but name the delta commit as the focus, or you pay for the same reading again.
- **DO NOT** accept a finding because a reviewer sounds certain. Verify against the
  source and classify real / partial / false-positive per `SKILL.md`. In the run behind
  this file, one reviewer's *correct* finding came with a proposed fix that would have
  discarded two correct verdicts.
- **DO NOT** treat an offline review as covering data-shaped defects. See *What a
  briefing cannot buy*.

## What goes in the prompt

| Element | Why |
|---|---|
| Branch, HEAD SHA, and `<merge-base>..HEAD` range | The reviewer must diff the right thing, locally |
| "Baseline is a local ref; none of this is on the remote" | Stops a silent diff against `origin/main` |
| Round number + path to previous rounds' reports | Carries forward what is settled |
| Explicit **do-not-re-report** list | The cost control |
| The delta commit to focus on | Avoids re-reading the whole branch |
| 3–5 named targets, phrased as questions | Directs effort at what you cannot self-check |
| Severity framing in the feature's terms | Gets the important finding first |
| Skills to follow (`audit-review`, `REVIEW.md`, `AGENTS.md`) | Repo conventions, verification discipline |
| Output path **including the model name** | Distinct reports survive |
| "Read-only" | Protects the diff |

## Artifacts

Reports are agent-generated analysis, so they live in the private nested repo, never the
public tree (`.cursor/rules/analysis-artifacts.mdc`):

```
.agents/artifacts/code-reviews/<branch>/code-review-round<N>-<model>.md
```

The **model belongs in the filename**, not only in the report header. Two reviewers on
one round is the point — convergence between independent models is the strongest signal
either produces — and that only works if both reports still exist afterwards.

## Adjudicating two reviewers

- **Convergent** (both found it independently) → treat as settled-real; verify once, fix
  once, credit both.
- **Divergent** → the disagreement is usually about *burden of proof*, not facts. In the
  run behind this file, one reviewer declined to report a datetime-timezone risk for lack
  of a proven mismatch while the other reported it because the class's stated bar is
  *provable faithfulness*. Both were reasoning correctly; the stated bar decided it.
  Record the divergence rather than silently picking one.
- **Unique to one reviewer** → no weaker for being unique. Judge on the evidence.

## What a briefing cannot buy

State these limits when you report the round's outcome, so the review is not mistaken
for more assurance than it gives:

- **Data-shaped defects are invisible offline.** A fix in the run behind this file
  refused a table for reading an object named `"null"` — because `DomainObject` holds the
  literal four-character string `'null'` for 206 of 309 rows. No reviewer could have seen
  that; one live run did. **Run the thing after a review round, not just the tests.**
- **Reported figures are taken on trust.** A reviewer with no org cannot reproduce your
  "N tests pass / M queries" numbers.
- **Engine behaviour is not establishable from source.** Whether the platform does X is a
  live question; a good reviewer flags it (rule 5) rather than assuming either way.

## The diagnostic

**A round that returns findings you already knew about is a PROMPT failure, not a
reviewer failure.** Fix the exclusion list before blaming the model. Conversely, a round
that returns nothing at all usually means the targets were too narrow — widen to the
premises rather than concluding the code is clean.

## Validation Checks

- The prompt names a local merge-base SHA, and says the work is not on the remote.
- Every previously-settled and deliberately-bounded item is listed as do-not-re-report.
- Severity framing names this feature's dangerous direction, not "find bugs".
- The output path contains both the round and the model.
- Reports from the same round coexist; none overwrote another.
- After the round: findings verified against source before any fix, and the code **run**,
  not just tested.
