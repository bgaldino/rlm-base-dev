# Merge Gates and Review Procedures

Detailed procedures and enforcement history for the compact requirements in
[`AGENTS.md`](../../../AGENTS.md). Read this when preparing a PR, changing a gate,
or processing review threads. Repository-relative command paths below assume
the repository root as the working directory.

## Pre-merge checklists for AI agents

Use these before opening or updating a PR. They complement the [PR Review Focus Areas](../../../AGENTS.md#pr-review-focus-areas) in the root contract.

**Run `python scripts/ai/pr_gate.py --base origin/264` first.** It selects the mechanical
checks your diff actually needs, runs them, and prints a status for **every** check — including the
ones it skipped and why. That is the point: the checks below already existed and were enforced only
by an agent reading this list, which is the enforcement that failed in `#264-27`, `#264-55` and
`#264-56`. A missing dependency **fails** the gate rather than skipping, and every check gates —
including `validate_sfdmu_v5_datasets.py`, which used to be **advisory** because it exited non-zero
on a clean tree for two reasons. Two Critical findings were the validator's own false positives, and
pack 123 fixed them: a `Readonly` object is queried from the target org and owes no CSV, and a
per-pass object's CSV can live under `objectset_source/object-set-N/`, an alternative to its root CSV
**for that pass only** — and only when the plan sets `useSeparatedCSVFiles: true`; pass 1 always
reads the root regardless of the flag. Absent either qualifier, the root CSV is still owed. The other
findings were High — zero-byte `Upsert` CSVs in `datasets/sfdmu/mfg/en-US/mfg-multicurrency/` — a real
defect, but a dormant one: `grep -ic mfg cumulusci.yml` returned **0**, so that plan and its eleven
`mfg` siblings were all unwired. Pack 110 removed the plan rather than adding header rows,
following its precedent `q3-multicurrency`, deleted in `dab545ab` carrying zero-byte
`CostBook`/`CostBookEntry` CSVs of its own — the same finding, disposed of the same way. With both
fixes landed the check now gates like every other one. (Pack numbers refer to entries in the durable
todo tracker under `.agents/artifacts/todos/`, which is gitignored — the reference resolves only from
a tree that carries it.) The checklists below remain the reference for *what* each check means and for
the judgement steps no gate can make.

**The same gate now runs in CI** on every pull request (`.github/workflows/pr-checks.yml`, plus
`check_branch_scope.py`, which needs a PR number, so only CI can supply it automatically — run it
locally by passing `--pr <n>`, as *Merges and unintended diffs* below instructs). Run the gate
locally anyway — a local failure costs seconds, a CI one costs a round trip. The workflow is
deliberately **not** path-filtered, though not for the reason usually given: a path-skipped workflow
reports *nothing*, so a required check on it sits **Pending** and blocks every PR that misses the
paths. (What reports success is a *job-level* `if:` skip, which is a different mechanism.) Either
way selection is the driver's job and never the trigger's.

**Running is blocking, and a skipped run is too.** `Mechanical checks` is a **required status
check** on `main`, `264` and `release/*` — the `Approvals` ruleset requires the context from the
GitHub Actions app, so no other actor can report a same-named check to satisfy it. Three consequences
worth knowing.

A skip directive in the head commit message — `[skip ci]` and its five siblings (`[ci skip]`,
`[no ci]`, `[skip actions]`, `[actions skip]`, or a `skip-checks: true` trailer) — no longer bypasses
anything: it produces **no run at all**, which leaves the check **Pending**, which blocks. The bypass
and the enforcement are the same mechanism; requiring the check is what flipped its sign. **Corollary,
learned by tripping it:** GitHub scans commit *messages* for those strings, so a commit that merely
quotes one skips every workflow — and the commits most likely to quote one are the commits editing this
paragraph. Name the directives in commit messages; never write their bracketed form there. File
contents are unaffected, which is why the list above is safe here.

The requirement is matched on the **job's published name**, and the ruleset lives outside this repo,
so renaming `name: Mechanical checks` does not un-require anything — the ruleset goes on waiting for
a context nobody publishes, which leaves it **Pending** on every PR to `main`, `264` and `release/*`
at once. That is the same mechanism as a skipped run, and it fails *closed*: a rename is a repo-wide
merge outage, not a bypass. The guard suite pins that string for this reason, and the pin is not
cosmetic. (The bypass hazard is the opposite shape — a *second* job publishing the same name, since
the requirement is satisfied by the most recent check run bearing it. The suite pins the published
set for that.)

And admins keep `always` bypass, unchanged from the ruleset's three pre-existing rules, so a red gate
can still be overridden deliberately. Treat doing so as a decision to record, not a workaround.

### SFDMU data plans (`datasets/sfdmu/**`, `export.json`, CSVs)

1. Run `python scripts/validate_sfdmu_v5_datasets.py` and require the clean-tree thresholds stated in `AGENTS.md`. The former `mfg/en-US/mfg-multicurrency` baseline (zero-byte CSVs in an unwired plan) was resolved by deleting that plan (pack 110). Treat any Critical or High as new.
2. Keep **`externalId`** (`;` delimiters) and CSV `$$` columns aligned with the SFDMU rules in `AGENTS.md` — do not change `Upsert` to `Insert` + `deleteOldData: true` without explicit user approval.
3. Every tracked plan needs a **README** — a new plan without one, or an existing plan whose behavior or objects changed without a README update, both fail `python scripts/ai/check_plan_readme_consistency.py --strict <plan_dir>` (repo-wide with no argument): a missing README is a named error, and an existing one fails if its object table or `# N records` listings drift from the actual `export.json`/CSVs (record counts). Operation/externalId mismatches and missing-object rows are WARN-only and pass by exit code without `--strict` — `pr_gate.py` runs this check with it specifically so they gate too; the command shown here carries it for the same reason. `scripts/ai/generate_plan_readme.py <plan_dir>` derives a minimal, mechanically-accurate object table + file listing from `export.json`/CSVs for a plan that has none, between `<!-- generate_plan_readme:begin/end -->` markers; regenerate (same command) after a real change rather than hand-editing the table — content outside the markers, e.g. hand-written narrative, is preserved. A README with no markers is left alone unless `--force` is passed. Must report **0 errors, 0 warnings**.

### `cumulusci.yml` and CCI tasks

1. After editing `cumulusci.yml` (tasks, flows, options): run `python scripts/ai/generate_cci_reference.py` and commit the regenerated reference files.
2. **If you inserted or removed a flow step, run `python tests/test_doc_build_steps.py`.** Docs cite build steps as `N.M` with no generator behind them, so one inserted step silently invalidates every citation after it — eight rows went off by one that way, and the doc that goes stale is usually **not** in the same PR as the flow change.
3. If you rename a task or change its description, search the repo for the **old task name** in docs (`README.md`, `docs/`) and fix stale references.
4. For Python task changes in `tasks/`, follow `.cursor/skills/cci-orchestration/custom-task-authoring.md` — especially **CLI vs REST** (`username` for `sf`, not `access_token`).

### Documentation consistency

Follow `.cursor/skills/doc-consistency/SKILL.md` — it provides a
**change-surface map** (when X changes, update Y) covering task names,
flag tables, SFDMU plan READMEs, generated CCI references, skill
indexes, and more.

### Merges and unintended diffs

1. **Run `python scripts/ai/check_branch_scope.py --pr <n>` before merging.** It fails a branch carrying commits it does not own — the signature of a branch cut from a *composed* integration branch, which inherits other fixes **in their pre-review state** and can revert landed review fixes on merge. A branch that re-accumulated five foreign commits reached the point of merging twice (`#264-56`); this is what catches it. It reports two distinct findings: `FOREIGN` (content already upstream) and `STACKED` (built on another **open** PR, which the first signal cannot see because nothing has merged yet). Rebuild a `FOREIGN` branch from the base rather than reverting on top of it; a `STACKED` one must at minimum not merge before its parent. Pass `--pr` for both signals. Details and the two weaker checks that do *not* work: `.cursor/skills/audit-review/SKILL.md` → **Step −1**.
2. Before push, review the diff/stat against the intended PR base: `git diff origin/264 --stat` for the active release line (substitute the target base for other PRs). Pay extra attention to **`orgs/`**, **`datasets/`**, **`unpackaged/post_ux/`**, and scratch data — unexpected churn often means files were **swept in from another branch**.
3. Changes under **`unpackaged/post_ux/`** should come from **`assemble_and_deploy_ux`** or the **UX drift** flows, not manual XML edits (see `.cursor/skills/repo-integration/ux-assembly-retrieve.md`).

## Responding to Automated PR Reviews

> **How review is *conducted* — what to look for, the severity rubric, the defect classes
> this repo actually produces, and push discipline — lives in [`REVIEW.md`](../../../REVIEW.md) at
> the repo root.** It is read automatically alongside `AGENTS.md`, by Claude and by Copilot.
> This section covers only the *protocol*: what to do with a review comment once it exists.

Automated reviewers (GitHub Copilot, the Codex / `chatgpt-codex-connector` bot, and
similar) post inline comments on PRs. **Policy — every agent, every PR:** each review
comment is handled to completion, and **every review round ends with zero unresolved
threads.**

**Batch fixes into one push per review round.** Every push to an open PR triggers a fresh
automated review; re-reviews are not incremental (a hosted reviewer may repeat comments
already dismissed or resolved), and a push mid-review lands against a superseded commit,
spending a whole round on findings that no longer apply. Fix everything from a round,
verify locally, then push once. See `REVIEW.md` → *Push discipline*.

**Tooling — `python scripts/ai/pr_review.py`** (or the `/pr-review <pr>` command in Claude
Code) automates the mechanical steps so a round can't be left half-finished:
`status <pr>` lists unresolved threads (paginated), `handle <pr> --comment <id> --body "…"`
replies + resolves one thread (adds 👍 **by default** — pass `--no-react` to refute a false
positive without the 👍, per the "react on valid comments" rule below), and `verify <pr>`
confirms 0 unresolved (exit 1 if any remain). It's tool-agnostic (shells out to `gh`); defaults to the current repo, or pass
`--repo owner/name`. Verifying findings and sweeping the class (steps 1–2) stay your job.

For each comment:

1. **Verify against the code.** Don't trust the bot — confirm the claim in the actual
   source and classify it *real*, *partial*, or *false positive*.
2. **Sweep the whole class.** If a finding is real, fix **every** instance of that
   pattern across the change, not just the cited line.
3. **Reply in-thread** with the resolution **and the commit SHA** (or a clear,
   evidence-backed refutation for a false positive):
   `gh api --method POST repos/<owner>/<repo>/pulls/<n>/comments/<id>/replies -f body="…"`
4. **React** 👍 on a valid comment:
   `gh api --method POST repos/<owner>/<repo>/pulls/comments/<id>/reactions -H "Accept: application/vnd.github+json" -f content="+1"`
5. **Resolve the thread** (REST cannot — use GraphQL). List threads with the full query
   root — `reviewThreads` lives under `repository(owner:, name:){ pullRequest(number:N){ … } }`
   (`pullRequest` is **not** a GraphQL root field) — and **paginate** so PRs with >100
   threads aren't truncated:
   `repository(owner:$o,name:$r){ pullRequest(number:$n){ reviewThreads(first:100, after:$cursor){ pageInfo{ hasNextPage endCursor } nodes{ id isResolved comments(first:1){ nodes{ databaseId path line } } } } } }`
   — loop, passing `endCursor` as `after`, until `hasNextPage` is false. Resolve each
   unresolved id with `mutation($tid:ID!){ resolveReviewThread(input:{threadId:$tid}){ thread{ isResolved } } }`.
6. **Confirm clean** — re-query `reviewThreads` across **all** pages (same pagination) and
   verify `unresolved == 0` for the round.

Refute false positives (with evidence) rather than changing correct code — but still
reply, and resolve the thread once the point is settled. This matters most on branches
headed for `main`, which mirror to the internal Salesforce repo for audit: a left-open
thread is a finding the audit will re-raise.
