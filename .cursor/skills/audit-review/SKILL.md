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
6. **Reply in-thread, react, and resolve.** Document the resolution (and the commit SHA)
   on each thread; 👍 valid comments; then **resolve the thread** (GraphQL — REST can't).
   **Every review round ends with zero unresolved threads** — that is the audit trail.
   See `AGENTS.md` "Responding to Automated PR Reviews" for the canonical command set.
   **Tooling:** `python scripts/ai/pr_review.py` (`status` / `handle` / `verify`) automates the
   reply + 👍 + resolve + paginated 0-unresolved check; the `/pr-review <pr>` Claude command drives
   the full round with it. Both default to the current repo (`--repo owner/name` to override).
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
6. **Commit precisely** (the changed files only; never `cumulusci.yml`, never
   internal-reference docs) and push — this gives you the SHA to cite; the bots
   re-review the new SHA.
7. **Reply, react, resolve.** Per comment: in-thread reply with the resolution + commit
   SHA (for false positives, the evidence-backed refutation); 👍 valid comments; then
   **resolve the thread** (GraphQL).
8. **Confirm zero unresolved.** Re-query `reviewThreads` across **all** pages and verify
   the round closed with `unresolved == 0`.

```bash
# in-thread reply to a review comment (pull_number IS in the path — GitHub's documented endpoint)
gh api --method POST repos/<owner>/<repo>/pulls/<n>/comments/<comment_id>/replies -f body="…"
# 👍 a valid comment (Reactions API is GA — standard Accept header; quote +1 for the shell)
gh api --method POST repos/<owner>/<repo>/pulls/comments/<comment_id>/reactions \
  -H "Accept: application/vnd.github+json" -f content="+1"
# list review threads (repository-wrapped + paginated) — loop on endCursor until hasNextPage is false
gh api graphql -f query='query($o:String!,$r:String!,$n:Int!,$after:String){
  repository(owner:$o,name:$r){ pullRequest(number:$n){
    reviewThreads(first:100, after:$after){
      pageInfo{ hasNextPage endCursor }
      nodes{ id isResolved comments(first:1){ nodes{ databaseId path line } } } } } }' \
  -f o=<owner> -f r=<repo> -F n=<n>
# resolve a thread (REST cannot)
gh api graphql -f query='mutation($tid:ID!){ resolveReviewThread(input:{threadId:$tid}){ thread{ isResolved } } }' -f tid=<thread_id>
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
  false positive with evidence; one cohesive commit; in-thread replies + 👍 on each valid
  finding; **every thread resolved, round closed at 0 unresolved.**

## Pre-merge main comparison audit

Before merging a long-running feature branch, verify that files changed on the
branch do not silently overwrite newer versions that landed on `main` after the
branch diverged. This is the "swept-in file" risk mentioned in AGENTS.md
§"Merges and unintended diffs".

### Step 1 — Find the overlap

```bash
# Files changed on the feature branch since it diverged from main
git diff --name-only main...HEAD > /tmp/branch_files.txt

# Files changed on main since the branch diverged
MERGE_BASE=$(git merge-base main HEAD)
git diff --name-only "$MERGE_BASE" main > /tmp/main_files.txt

# Intersection — files touched on BOTH sides
comm -12 <(sort /tmp/branch_files.txt) <(sort /tmp/main_files.txt)
```

### Step 2 — Triage each overlap file

For every file in the intersection:

1. `git log --oneline "$MERGE_BASE"..main -- <file>` — what changed on main?
2. `git log --oneline "$MERGE_BASE"..HEAD -- <file>` — what changed on the branch?
3. `git diff main HEAD -- <file>` — what does the merge resolution need to do?

Classify each as:
- **Branch wins** — branch change is a superset or intentional update; main's change is already absorbed.
- **Main wins** — main has a fix/update the branch should adopt; cherry-pick or rebase.
- **Conflict** — both sides changed the same region; requires manual resolution.

### Step 3 — High-risk areas (always check)

| Path | Risk |
|------|------|
| `cumulusci.yml` | Flow/task additions on main not present on branch; merge produces duplicates or stale references |
| `datasets/sfdmu/` | externalId, operation, or CSV changes on main overwritten by branch's older copy |
| `tasks/` | Bug fixes on main regressed by branch's older task version |
| `unpackaged/post_ux/` | Auto-generated; any manual edit on either side is wrong — run `assemble_and_deploy_ux` post-merge |
| `docs/` + `.cursor/skills/` | Doc-consistency changes on main (task renames, flag table updates) lost if branch has older versions |
| `orgs/` | Scratch def pins; branch may carry a stale instance pin (see feedback_scratch_org_instance) |

### Step 4 — For each "main wins" file

```bash
# Cherry-pick the main-side change onto the branch
git checkout main -- <file>       # take main's version wholesale, OR
git diff main HEAD -- <file>      # review and merge selectively
```

Then re-run `python scripts/validate_sfdmu_v5_datasets.py` (for data plan
files) and `python scripts/ai/generate_cci_reference.py` (if cumulusci.yml
was touched).

### When to run

- Before opening a PR that merges a branch > 2 weeks old against main.
- Before requesting a merge review when main has had active commits since the branch diverged.
- After a rebase onto main — verify the rebase did not silently drop main-side changes.

## Validation Checks

- Every comment has an in-thread reply (resolution + SHA, or refutation), a 👍 on the
  valid ones, and a **resolved thread**; the round closed with `unresolved == 0` (checked
  across all pages).
- Each valid class was swept feature-wide (show the search, not just the one fix).
- Deploy clean + tests green on the new commit.
- `git diff --cached --name-only` excludes `cumulusci.yml` and internal-reference docs.
- Re-review round on the new SHA surfaces no new instance of an addressed class.
