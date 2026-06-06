# Audit Review — PR Review-Response & Completeness-Sweep Playbook

> How to process automated PR reviews (Codex, Copilot) and run the deep
> pre-merge audit, through the lens that matters for this repo: **`262` →
> `main` is mirrored to an internal Salesforce repo and passes through
> Salesforce audit agents.** The goal is to minimize audit passes — so every
> finding is handled as a *class*, not a one-line patch, and verified before it
> is trusted.
>
> Pairs with `apex-security-hardening/SKILL.md` (the most common finding class)
> and `doc-consistency/SKILL.md` (doc change-surface). For PR review focus areas
> see also `AGENTS.md` "PR Review Focus Areas".

## Quick Rules

1. **Audit lens on every finding:** "would a Salesforce security/compliance audit
   flag this?" If yes, it is in scope even if a bot rated it low.
2. **Completeness sweep, not a one-line patch:** when a finding is valid, sweep the
   **whole class** across the feature (every instance of that pattern), then fix all.
3. **Verify before you trust:** confirm each bot finding against the actual code.
   Classify `real` / `partial` / `false-positive`. Bots are wrong sometimes —
   reply with the evidence when they are.
4. **Group duplicates:** Codex and Copilot often flag the same issue on different
   lines/files. Fix once; reply to each thread.
5. **One cohesive follow-up commit** per review round; re-run deploy + tests; never
   stage `cumulusci.yml` (local-only flags) or internal-reference docs.
6. **Reply in-thread + react.** Document the resolution (and the commit SHA) on each
   thread; 👍/👎 bot comments that ask for it. This is the audit trail.
7. **Re-sweep after each round** — a new commit can introduce a new instance of an
   old class.

## DO NOT

- **DO NOT** take a bot finding at face value and "fix" code that is already correct
  (e.g. a `getMap()`-casing claim — `getMap()` keys are lowercase). Verify first.
- **DO NOT** patch only the cited line and move on — that leaves the rest of the class
  for the audit to find. Sweep it.
- **DO NOT** merge a round without re-running the relevant deploy + tests on the new commit.
- **DO NOT** silently truncate scope (top-N, "the obvious ones") — if you bound a sweep,
  say what was left.

## Entry Conditions

| Situation | Use this skill? |
|-----------|-----------------|
| A Codex/Copilot review posted on a PR | Yes — triage, verify, sweep, fix, reply |
| The deep pre-merge audit of a branch before `262 → main` | Yes — drive it by finding-class |
| A single trivial nit with no class | Fix inline; reply; skip the full ceremony |
| Authoring the actual CRUD/FLS fixes | Pair with `apex-security-hardening/SKILL.md` |

## Release Audit (`262` → `main` → Salesforce Labs)

When a branch is being prepared to merge to `main`, it is **mirrored to an internal
Salesforce repo and run through Salesforce audit agents** before release to devs,
partners, and customers via Salesforce Labs. The bar is higher than normal review:

1. **Clean, not just correct.** Resolve **every** finding — including pure nits
   (option-style, wording, formatting) — until a fresh bot review returns nothing.
   A nit left behind is a finding the internal audit will re-raise.
2. **Sweep ahead of the bot.** Don't wait for round N+1. After a round, run a
   preventive sweep of the *whole PR diff* for the **classes** already seen, so the
   next round dries up. Verify every shell command (task/option/value exists — check
   `cumulusci.yml` + the task's `task_options`/`VALID_TYPES`), every file/path
   reference (`test -e`), every code snippet (runnable; no undefined vars), and every
   tool/behavior claim (read the referenced task/class) **against the actual repo**.
3. **Cross-PR reference hygiene (the subtle one).** When a feature is split into a
   **code PR** and a **docs/skills PR**, the docs PR's examples can cite code that
   isn't on *its* branch yet. Rules:
   - A skill/doc must be accurate on **the branch it lives on**. Verify every cited
     path/field/behavior against *that* branch, not the eventual merged state — a bot
     (and the audit) reviews the branch in isolation.
   - **Merge the code PR before its docs PR**, so the references resolve. State the
     dependency in the docs PR.
   - If they can't be ordered, make examples **branch-true**: describe the end-state
     the pass *produces* ("after this pass, SOQL is `WITH USER_MODE`") rather than
     asserting a present-tense fact about a file that's still pre-change on this branch.
4. **No tool-coupling.** Skills are plain markdown for *any* agent — never depend on a
   specific tool name (e.g. a "Workflow tool"); describe the technique.

## The process

1. **Pull the comments.**
   `gh api --paginate repos/<owner>/<repo>/pulls/<n>/comments` (inline) and
   `…/pulls/<n>/reviews` (summaries). Note each `id`, `path`, `line`, `body`.
2. **Triage into classes.** Map findings to recurring classes (table below); merge
   duplicate findings from both bots.
3. **Verify each against the code.** Read the cited file/lines; reproduce the claim.
   Mark `real` / `partial` / `false-positive` with evidence. Prefer reading the source
   over the bot's paraphrase.
4. **Completeness sweep per valid class.** For each real finding, search the whole
   feature for the same pattern (grep/parse), not just the cited site. Expect to find
   *more* than the bot flagged (e.g. a "5 missing `WITH USER_MODE`" finding was 20).
5. **Fix cohesively**, then **deploy + run tests** on the result.
6. **Reply + react.** In-thread reply per comment with the resolution + commit SHA;
   for false positives, reply with the refutation; 👍 the P1 bot comments.
7. **Commit precisely** (the changed files only; never `cumulusci.yml`, never
   internal-reference docs) and push; the bots re-review the new SHA.

```bash
# in-thread reply to a review comment
gh api --method POST repos/<owner>/<repo>/pulls/<n>/comments/<comment_id>/replies -f body="…"
# 👍 a comment the bot asked you to react to
gh api --method POST repos/<owner>/<repo>/pulls/comments/<comment_id>/reactions -f content=+1
```

## Finding-class checklist (recurring; from real audit rounds)

| Class | What to sweep | Skill / reference |
|-------|---------------|-------------------|
| Missing `WITH USER_MODE` / `as user` | **All** entry-reachable SOQL/DML in the class's controllers | `apex-security-hardening` |
| Permission-set under/over-grant | Every user-mode object/field vs the perm set | `apex-security-hardening` |
| Feature-gated metadata in always-on output | base layouts/flexipages/profiles + assembled `post_ux` referencing flag-only fields/components | `repo-integration/ux-assembly-retrieve.md` |
| Apex bulk-safety | SOQL/DML in loops across the feature | `cci-orchestration/custom-task-authoring.md`, apex rules |
| Case-sensitivity mismatch | Formula vs Apex (`=` is case-sensitive in formulas; `equalsIgnoreCase` in Apex); field-presence checks | — |
| Flow decision logic | Lookups (`getFirstRecordOnly`, auto-store vs assigned var) + inverted `IsNull` conditions | — |
| Stale generated docs | Regenerate after `cumulusci.yml` changes | `doc-consistency`, `cci-orchestration` |
| SFDMU v5 compliance | externalId format, Upsert vs Insert+deleteOldData, `$$` columns | `sfdmu-data-plans` |

## Workflow patterns for scale

For a branch-wide audit, fan out rather than read serially — parallelize the work
across multiple agents (use whatever multi-agent / parallel-task capability your
tool provides; serial reading also works, just slower):
**find → dedup vs seen → adversarially verify (multiple skeptics / diverse lenses) →
synthesize.** Patterns that paid off here:

- **Adversarial verify:** spawn skeptics that try to *refute* each finding; keep only
  what survives. Catches plausible-but-wrong bot findings and your own.
- **Classify regression vs pre-existing:** diff the change range (e.g.
  `<baseline>..HEAD`) to decide *fix-now* (regression introduced by this work) vs
  *defer* (pre-existing / out of scope). Use `git blame`/`git log -S`.
- **Completeness critic:** a final pass asking "what class did we not sweep?"

## Examples

- **PR #203 (large_stx):** Codex 2×P1 + Copilot 13 comments → triaged to 5 classes;
  swept the `WITH USER_MODE` class from the flagged 5 to **all 20** queries; confirmed the
  gated-field-in-base-layout leak was isolated; rejected one finding (`getMap` casing) as a
  false positive with evidence; one cohesive commit; 14 in-thread replies + 2 👍.

## Validation Checks

- Every comment has an in-thread reply (resolution + SHA, or refutation).
- Each valid class was swept feature-wide (show the search, not just the one fix).
- Deploy clean + tests green on the new commit.
- `git diff --cached --name-only` excludes `cumulusci.yml` and internal-reference docs.
- Re-review round on the new SHA surfaces no new instance of an addressed class.
