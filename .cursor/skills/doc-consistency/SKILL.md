# Documentation Consistency — Pre-Merge Doc Review

Use this skill **before marking a PR ready** to verify that all affected
documentation stays aligned with code changes. It replaces multi-round
review-loop fixes ("fix stale description", "update README task name",
"regenerate CCI reference") with a single lookup pass.

## Quick Rules

1. **If you changed `cumulusci.yml`** — run `python scripts/ai/generate_cci_reference.py` and commit the output. Verify `git diff` on `tasks-reference.md`, `flows-reference.md`, `feature-flags.md` shows only your intended changes.
2. **If you renamed or added a CCI task** — grep `README.md`, `AGENTS.md`, `docs/`, and `.cursor/skills/` for the **old name**; update or remove every stale reference.
3. **If you changed an SFDMU plan** (`export.json`, CSVs, objects, operations) — update the plan's `README.md` in the **same commit**, then run `python scripts/ai/check_plan_readme_consistency.py <plan_dir>` to confirm the README's object table and `# N records` listings still match the plan (record counts, operations, externalIds, object presence). Also run `python scripts/validate_sfdmu_v5_datasets.py`.
4. **If you changed feature flags** (added, removed, renamed, changed default) — update the flag table in `README.md` and verify `feature-flags.md` was regenerated (rule 1).
5. **If you changed a Python task class** (`tasks/*.py`) — check the task's `description` in `cumulusci.yml`, the `README.md` Custom Tasks table, and any `docs/` guide that names it.
6. **If you changed Robot test suites or resources** — check `robot-testing/SKILL.md` tables (Setup tasks / E2E tasks) and the `README.md` troubleshooting section.
7. **If you created a new skill or sub-file** — follow `.cursor/skills/skill-authoring/SKILL.md`: add top-level skills to `AGENTS.md`, `.cursor/skills/README.md`, and `.claude/skill-manifest.yml` when cross-repo discoverability applies; register sub-files in the parent `SKILL.md`, which is their only registry — `AGENTS.md` carries no second-level index.
8. **Quick verification** — run `python scripts/ai/generate_cci_reference.py` and then `git diff` to confirm only intended changes appear. Run `python scripts/validate_sfdmu_v5_datasets.py` (should pass).

## DO NOT

- **DO NOT** duplicate procedural content across `README.md`, `AGENTS.md`, and skill files — keep one source and add pointers.
- **DO NOT** re-add a hand-maintained task listing (e.g. the removed `docs/references/cci-task-reference.md`). The single source for project tasks is the generated `.cursor/skills/cci-orchestration/tasks-reference.md` (run `python scripts/ai/generate_cci_reference.py`); for CumulusCI built-in tasks use `cci task list` / `cci task info <name>`.
- **DO NOT** edit `CLAUDE.md` — it is a symlink to `AGENTS.md`.
- **DO NOT** skip the plan README when changing SFDMU plan behavior.

---

## Change-Surface Map

The core lookup: **when X changes, verify Y**.

| What changed | Docs to verify or update |
| ------------ | ------------------------ |
| `cumulusci.yml` (tasks, flows, flags) | Generated refs (run script), `README.md` task/flag tables, `AGENTS.md` Common Workflows |
| `tasks/*.py` (class, options, description) | `cumulusci.yml` description, `README.md` Custom Tasks table, relevant `docs/` guide |
| `datasets/sfdmu/**/export.json` or CSVs | Plan `README.md` in same directory, then `check_plan_readme_consistency.py` (README ↔ plan) **and** the SFDMU v5 validator (plan compliance) |
| Feature flag add/rename/default change | `README.md` Feature Flags tables, `AGENTS.md` edition flags, generated `feature-flags.md` |
| `robot/**` (new suite, renamed keyword) | `robot-testing/SKILL.md` task tables, `patterns.md`, `README.md` troubleshooting |
| `templates/` or UX assembly logic | `ux-assembly-retrieve.md`, `docs/features/dynamic-ux-assembly.md` |
| New `.cursor/skills/` file | Parent `SKILL.md` sub-file list (the only registry), and `.cursor/skills/README.md` Skill Router for a new *top-level* skill |
| `orgs/*.json` (scratch org definitions) | `README.md` Quick Start if it names specific configs |
| `scripts/apex/*.apex` | `troubleshooting/SKILL.md` if it references the script |
| `.forceignore` | No doc update, but verify retrieve/deploy intent is consistent |
| `scripts/ai/*.py` | The skill that owns the script (see `AGENTS.md` **Script Reference** for the owner). Only a brand-new script *directory* earns an `AGENTS.md` row |
| **New** `scripts/*.py` (top level) | `AGENTS.md` Repository Layout — top-level utilities are easy to add and never document |
| **New** `scripts/apex/*.apex` | `troubleshooting/SKILL.md` (if it diagnoses a failure) and `.cursor/rules/apex-scripts.mdc` (if it establishes a pattern) |
| **New** `docs/guides/*.md` | `README.md` **Primary Guides** table — an unindexed guide is invisible |
| `unpackaged/**/classes/*.cls` behavior change | `docs/references/revenue-cloud-permissions.md` if the class is permission-gated — especially when its **destructive scope** grows |
| A **product/SKU added** to any dataset | *Every* plan CSV that carries that SKU, and each of their READMEs — see below |
| `scripts/build_harness/harness/` or `harness.py` | `.cursor/skills/build-harness/SKILL.md`, `docs/guides/build-harness.md` |
| `scripts/build_harness/tui/` or `tui-cci` | `scripts/build_harness/tui/README.md`, `.cursor/skills/build-harness/SKILL.md` |
| **API version bump** for a new release | Every doc carrying a `vNN.0` **except the frozen corpora** (below) — and see *An API bump must not rewrite a verified capture*: a verified capture is provenance, not a version to retarget |

### Excluded from the sweep ≠ never updated

"Every doc" above excludes material the mechanical sweep must not touch — but that
covers **two different reasons**, and conflating them is a live trap in both directions.
`EXCLUDED_PREFIXES` in `scripts/ai/bump_api_version.py` refuses both by path prefix;
only the first group is genuinely frozen.

**Frozen — never bump, in the sweep or by hand.** Their whole value is recording a
*past* release; relabelling a 262 snapshot as v68.0 destroys the baseline the next
release is diffed against.

| Frozen | Why |
|---|---|
| `docs/salesforce/**` | per-release Help/dev-guide snapshot corpora |
| `docs/enablement/260/`, `docs/enablement/262/` | released per-release enablement extracts |
| `postman/` | version-branded end to end; regenerate, do not `sed` |

**Retarget by hand — excluded because a blanket rewrite would corrupt them, not
because they are historical.**

| Hand-retargeted | Why it is excluded, and why it still must change |
|---|---|
| `.agents/context/**` | `project-map.md` and `project-memory.json` record the **active** release and API version, so leaving them behind strands every agent on the previous release. They are excluded because each also deliberately records the *prior* GA in the same file (`prior_ga_api_version`, "`main` (Release 262 … API `67.0` GA target)") — a blanket rewrite would flatten the distinction the file exists to draw. Edit the current-target fields, leave the prior-GA fields alone. |

`.agents/artifacts/**` is a private nested repo, gitignored and therefore unreachable
by either pass; nothing there needs retargeting.

Read the authoritative list from `EXCLUDED_PREFIXES` rather than trusting these tables
to stay current; it also carries per-PR exclusions (deliberate dual-baseline overlays,
prototype-specific low pins) that come and go, and each entry states which of the two
kinds it is. `docs/enablement/{version}/` gains an entry each release, at the moment
that release ships — the *current* target release is still swept.

One caution on verifying any of this: `git grep -E` does **not** honour `\b`, so a
word-boundary pattern silently matches nothing. A sweep that returns zero hits on
`.agents/context/` is a broken pattern, not a clean tree — `project-map.md` alone
carries several version references.

### An API bump must not rewrite a verified capture

`bump_api_version.py` handles code; the docs are a **manual** pass, and that pass is
where provenance gets overwritten. A section headed `✅ VERIFIED LIVE` or
"verified against `<org>`, `<date>`" records what was actually *exercised*, and the
capture org's **maximum API version caps what could have been called at all** — so
retargeting the path inside it does not merely overstate the evidence, it asserts a
request that was impossible to make.

Retarget prose that answers "which endpoint do I call now"; leave captures alone. If
the body and sequencing are still the contract you want to publish at the new
release, keep the new path and **say so in the banner** — state the release and API
the capture was taken at, and that `VERIFIED LIVE` attests to the body, response
shape, and sequencing rather than the version in the path.
`scripts/txn_data_harness/docs/contracts-*.md` carry the worked wording.

**Sweep with the full marker set, or you will miss files.** The 264 pass found three
instances and declared the class swept; a reviewer then found a fourth, because the
first sweep matched only `VERIFIED LIVE` / `Verified payload` / `verified against`.
These forms all exist in this repo and all carry the same weight:

```bash
git ls-files '*.md' | xargs grep -lniE \
  'live-(verified|tested|proven|confirmed)|verified (live|on|in|against|by|via|payload)|✅ *verified'
```

Read that as a **grammar, not a closed list**: `live-<past participle>` and
`verified <preposition>`. It is written that way because the enumeration needed three
revisions — the first pass missed `live-tested`, the second missed `verified payload`,
the third missed `live-proven`, `verified by`, and `verified via`, each found by a
reviewer rather than by the sweep. If you meet a new phrasing that fits the grammar,
add it here; do not assume the alternatives above are exhaustive. Resist the urge to
collapse it to a bare `verif` stem — that matches 219 files against 60, almost all of
them ordinary instructions to "verify" something, which is a worse signal-to-noise
ratio than the mechanical check rejected below.

**Two provenance styles, and only one of them can be silently invalidated.** Most
files name the version *inline on each claim* — "live-verified v67.0",
"verified live on v67.0" — which is self-disambiguating: the version travels with
the assertion, so the manual sweep cannot separate them, and a reader can see at a
glance which release the claim belongs to. Prefer this style when writing a new
claim. **Nothing automated protects it in markdown** — `bump_api_version.py` encodes
the same idea in `PROVENANCE_LINE_RE`, and applies it to every file it rewrites
(`sfdx-project.json`, `cumulusci.yml`, `-meta.xml`, `export.json`, `.py`,
`.cls`/`.apex`) — but `.md` is not among them and never is, which is exactly why this
pass is manual. That guard now matches the **same grammar** as the sweep above, and
`validate_rules()` fails the build if a form drops out of it; the two were written
independently and had already drifted, so treat them as one thing kept in two places
and update both together. The vulnerable style is a **document-scoped** header —
"Verified on Release 262, API v67.0. All patterns below are live-tested" — whose
version governs paths hundreds of lines away that state no version of their own.
That is the shape that broke, in both places it occurred.

So when triaging a sweep hit, the question is not "does this file mix versions" but
**"is there a version-bearing claim whose scope covers a path that does not state
its own version?"** Of six candidates in the 264 sweep, five were fine — prescriptive
`sf api request` examples, endpoint tables under a "paths are relative to
`/services/data/vNN.0/`" base-path line, and inline-versioned claims. Only the
document-scoped header genuinely needed the caveat. A mechanical file-level
co-occurrence check was considered and rejected for that reason: at a 5-in-6
false-positive rate it would train people to ignore it.

### Adding one product touches many plans

A single new SKU fans out across every plan that carries it — catalog, pricing,
images, rating, rates, tax. Each of those plans has a README with record counts.
Missing one is silent until the consistency check runs, so **always run it repo-wide
rather than on the plan you were editing**:

```bash
python scripts/ai/check_plan_readme_consistency.py    # no argument = all plans
```

⚠ The checker validates **object tables and file-tree listings only** — it does
**not** read counts written in prose or headings. Those you must update by hand.

---

## Doc Layers in This Repo

Understanding where truth lives prevents duplication drift.

| Layer | Location | How to keep current |
| ----- | -------- | ------------------- |
| Generated CCI refs | `.cursor/skills/cci-orchestration/tasks-reference.md`, `.cursor/skills/cci-orchestration/flows-reference.md`, `.cursor/skills/cci-orchestration/feature-flags.md` | `python scripts/ai/generate_cci_reference.py` |
| SFDMU plan READMEs | `datasets/sfdmu/**/README.md` (e.g. `datasets/sfdmu/qb/en-US/*/README.md`, `datasets/sfdmu/mfg/README.md`, `datasets/sfdmu/procedure-plans/README.md`) | Must match the plan's `export.json` + CSVs — enforce with `python scripts/ai/check_plan_readme_consistency.py` (counts, operations, externalIds, object presence) |
| Agent instructions | `AGENTS.md` (`CLAUDE.md` is a symlink) | Single source; edit `AGENTS.md` only |
| Human setup / reference | `README.md` | Manual — task tables, flag tables, troubleshooting |
| Skill files | `.cursor/skills/*/SKILL.md` + sub-files | Manual — cross-references to task names, paths |
| Guides and features | `docs/guides/`, `docs/features/`, `docs/references/` | Manual prose; watch for stale task/flow names |
| Copilot instructions | `.github/copilot-instructions.md` | Pointer only — keep thin, link to `AGENTS.md` |

---

## Verification Commands

```bash
python scripts/ai/generate_cci_reference.py              # regenerate references
git diff .cursor/skills/cci-orchestration/               # should show only intended changes
python scripts/validate_sfdmu_v5_datasets.py             # plan v5 compliance — should pass
python scripts/ai/check_plan_readme_consistency.py       # plan README ↔ export.json/CSVs — should PASS (0 errors)
python tests/test_doc_build_steps.py                     # doc `N.M | <flow>` step numbers ↔ cumulusci.yml
python tests/test_erd_doc_counts.py                      # ERD object/field/domain counts in docs ↔ erd-data.json
```

`test_erd_doc_counts.py` covers the same shape of drift one level down. The
**headline** ERD triple gets swept on every refresh — 4,190 → 4,252 fields at 264,
all seven citations updated — but the **per-domain** counts under it never did, and
the sweep does not look at them: 8 of the 9 rows in the Domain Overview table of
`revenue-cloud-data-model/SKILL.md` disagreed with the data, summing to 185 against
an actual 263, directly beneath a correct "263 objects" headline. 7 of the 9
`domains/*.md` headlines were wrong too — 15 numbers in all.

Three things make this worth a check rather than another sweep. The drift was **not**
uniformly stale-low — `rates.md` claimed 15 Rate Management objects where the data
has 11 — so "add the new ones" would not have found it. The numbers had stopped
describing anything measurable: most matched neither the ERD nor the file's own
object table. And the refresh is not what staled them — the per-domain counts in
`erd-data.json` are byte-identical at `release/262`, so these were **never** right.
Run it after any ERD refresh anyway, since that is when someone is looking at the
figures; see `schema-validation` for where it sits in that procedure.

Two of its layers exist only because the first version of this check had the same
defect it was written to catch. Asking whether *any* headline citation matched let a
file that reworded or renamed its own citation leave the audit while the run reported
clean — wrong numbers in a reworded `scripts/ai/README.md` passed 33/33 — so every
site is now asserted individually and **the total check count is pinned**, which is
what turns "one citation quietly stopped being audited" into a failure. The other
layer covers the Statistics bullet block in `docs/erds/README.md`, which restates all
three totals in a form the triple pattern cannot match; that file was being audited at
three prose citations while four bullets in it went unchecked. **When you add a
citation or a site, expect the pin to fail and raise `EXPECTED_CHECKS` deliberately.**

⭐ **The most instructive finding came last: the first sweep fixed 15 of 31 instances and
declared the class swept.** The mermaid inventories in `docs/erds/README.md` and
`docs/erds/erd-quickstart.md` carried the same stale set (11/14/15/4/37/27/22/54) — 16
more, in a file that sweep already had open — because they *look* like a different
quantity. They are: entities drawn in a diagram, a relationship-focused subset. But they
had been populated from the domain counts, so they drifted with them, and two of the
eight coincidentally matched their diagram, which made the other six look deliberate.
Both are now gated against the `.mermaid` files. **When sweeping a class, enumerate every
instance mechanically before claiming the class is closed** — "I fixed the ones I found"
is not the same claim, and a near-miss quantity is where the rest hide.

`test_doc_build_steps.py` covers a class of drift that reading cannot catch.
Build-step numbers in docs are hand-maintained with no generator, so **inserting
or removing a single step silently invalidates every citation downstream of it**.
Eight rows in `docs/references/revenue-cloud-permissions.md` had gone off by one
that way, and the `prepare_agents` permission-set row was additionally wrong on
its *substep* because a step had been removed from that subflow. Two reviewers
flagged the substep; nobody caught the parents; and the first fix attempt
refuted a correct finding because it audited a stale checkout. The check reads
the flows and asserts, for every `| N.M |` cell on a line naming a subflow, that
`N` is that subflow's step in `prepare_rlm_org` and `M` exists inside it. Run it
whenever a step is added to or removed from a flow — not only when a doc changes,
since **the doc that goes stale is usually not in the same PR**.

It audits both citation forms — the `| N.M |` table coordinate and the prose
`` `flow` step N ``. Where prose also names the task (`` `prepare_agents` step 8 →
`activate_agents` ``, or `via`/`:`/`—` in place of the arrow) the task is checked
too, so the citation is pinned by identity rather than existence. **Where it does
not, only existence is checked, and that gap is load-bearing**: five citations in
the permissions reference named steps of `prepare_core` that all exist and all held
a different task, and the check passed over every one — so **write the task after
the step number** (`` `flow` step N → `task` ``), which is what moves a citation
from existence to identity. Putting the name *before* the number does not count;
the five corrections were first written that way and stayed unchecked until they
were reordered. The name must be one CumulusCI declares, so ordinary prose after a
step number ("step 4 — see `api_names`", "step 11 via `sf`") is not read as a claim.

Two forms remain existence-only by construction, and are worth knowing before
trusting a green run: a step whose target is itself a **subflow**, and a citation
naming a **standalone flow** (`run_qb_idempotency_tests`, `prepare_billing_portal`).
Both resolve for existence but have no task at that coordinate to compare against.

It also audits flows that are **not** part of `prepare_rlm_org`
(`run_qb_idempotency_tests`, `prepare_billing_portal`) by resolving each on its own
numbering, rather than dropping them for being unreachable from the root. A cited
name CumulusCI does not know at all is **reported by name and location** instead of
skipped, so renaming a flow surfaces its citations rather than quietly removing them
from the audit; it is a note, not a failure, because a doc here may legitimately
describe a flow defined on another branch (`prepare_manufacturing` is the current
example). An unreadable file is fatal. The check also self-tests over fixture docs:
without that, deleting the standalone-flow resolution or restoring the silent read
skip removed *coverage* while still reporting a full pass — the same defect class it
was written to find in the docs.

Run it from the repo root, with the CumulusCI venv's python. It resolves the flow
through CumulusCI rather than parsing `cumulusci.yml`, so it inherits CumulusCI's
own repo detection, which looks for a `.git` **directory** — and in a git worktree
`.git` is a file. So **the check cannot run inside a worktree**, which is worth
knowing because rebuilding a branch in a worktree is this repo's remedy for a
branch that has picked up foreign commits. It fails loudly either way and names
which of the two it hit (CumulusCI absent, versus CumulusCI present but no project
resolved) — it never reports a clean audit it did not perform.

If the diff shows unintended changes, investigate before committing. To commit the regenerated files:

```bash
python scripts/ai/generate_cci_reference.py
git add .cursor/skills/cci-orchestration/tasks-reference.md \
       .cursor/skills/cci-orchestration/flows-reference.md \
       .cursor/skills/cci-orchestration/feature-flags.md
```

---

## Related Skills

- **CCI Orchestration** — `.cursor/skills/cci-orchestration/SKILL.md`
- **SFDMU Data Plans** — `.cursor/skills/sfdmu-data-plans/SKILL.md`
- **Repository Integration** — `.cursor/skills/repo-integration/SKILL.md`
- **Robot Testing** — `.cursor/skills/robot-testing/SKILL.md`
- **Release Enablement** — `.cursor/skills/release-enablement/SKILL.md`
- **Revenue Cloud Docs** — `.cursor/skills/revenue-cloud-docs/SKILL.md`
- **Revenue Cloud Data Model** — `.cursor/skills/revenue-cloud-data-model/SKILL.md`
- **Usage & Consumption** — `.cursor/skills/usage-consumption/SKILL.md`
- **Troubleshooting** — `.cursor/skills/troubleshooting/SKILL.md`
