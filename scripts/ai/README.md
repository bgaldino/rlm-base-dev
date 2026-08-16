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
| `scripts/ai/README.md` (this file) | objects, fields, relationships, **and `1,148` reference fields — the only copy** | the triple, yes; `1,148`, **no** |
| `docs/erds/README.md` | objects, fields, relationships | yes, prose **and** the Statistics bullets |
| `.cursor/skills/revenue-cloud-data-model/SKILL.md` | objects, fields, relationships | yes |
| `.cursor/skills/schema-validation/SKILL.md` | objects, fields, relationships | yes |

**`python tests/test_erd_doc_counts.py` now gates the triple in all four**, per site
rather than in aggregate, so a file that reworded or renamed its citation fails instead
of quietly leaving the audit. The wrapped citation above — `263` on one line, `objects,
4,252 platform fields…` on the next — is exactly the shape that escaped the first
version of that check, so keep the phrase within three lines. Still unchecked, and
still needing the manual sweep: the **`1,148` reference-field total** here, the
org-describe pair (254 objects / 3,913 fields), and the orphan/gap baselines.

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
of a dozen validators a given diff should have run.

```bash
python scripts/ai/pr_gate.py --base origin/264   # select from the diff vs a base ref
python scripts/ai/pr_gate.py --all               # run everything
python scripts/ai/pr_gate.py --list              # the matrix: check, gating, deps, triggers
python scripts/ai/pr_gate.py --requirements --base origin/264   # pip deps the selection needs
```

Selection lives here rather than in a workflow's `paths:` filter because a path filter makes
the job **skip**, and a skipped job cannot serve as a required status check while reading
exactly like a pass in the PR summary. The same reasoning drives three statuses that are
easy to conflate:

| status | meaning | fails? |
|--------|---------|--------|
| `SKIPPED` | not selected — nothing it covers changed | no, and it says so on its own line |
| `MISSING-DEP` | selected, but a package or the interpreter floor is absent | **yes** — otherwise a broken install silently turns a gate green |
| `ADVISORY` | runs and reports, never fails | no, and the reason is printed inline |

Exactly one check is advisory: `validate_sfdmu_v5_datasets.py` exits non-zero on a clean
tree today, on two known validator false positives (pack 123). A check that always fails
gets ignored, and an ignored check is worse than an absent one, so it is labelled with its
reason instead of being dropped or allowed to fail every PR touching `datasets/`.

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
than a suite that fails outside pytest: run as `python tests/test_docgen_helpers.py` it exits
**0 having run nothing**, because the file is all `def test_*` and no `__main__`. That is why
it is invoked through pytest rather than the repo's usual `python tests/<name>.py`; the
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
never read as a verdict).

What it deliberately does not cover: `check_branch_scope.py --pr <n>` itself. The matrix runs
that checker's *tests*, which is a path-selectable thing, but the per-PR branch verification
takes a PR number and talks to GitHub, so it belongs in the workflow (which has
`github.event.pull_request.number`) rather than in a local, hermetic gate. Keep running it by
hand before a merge until the workflow lands.

A full `--all` run is 13 checks in about 17 seconds, of which `check_branch_scope.py` is 8 —
so the gate costs roughly one branch-scope run more than nothing, and a typical docs-only
selection is a couple of seconds.

Verified by `tests/test_pr_gate.py` (126 checks, hermetic throwaway repos, no network), which
drives the verdict rather than the helpers. Every mutation below is confirmed to fail the
suite: a prefix trigger loosened to a substring match, a two-dot diff, a runtime failure
reclassified as advisory, a gating failure that still exits 0, a missing dependency counted
as a skip or relabelled `SKIPPED`, the unclaimed-suite check blinded or its new suite left
unclaimed, the silent-failure section dropped, an advisory flipped to gating, `run_sequence`
short-circuiting, a drifting CumulusCI pin, an emptied trigger list, a usage error exiting 1,
a dropped Python floor, a dropped requirements pin, renames collapsed to the destination
only, the per-check timeout removed, advisory output truncated from the tail again, the
dependency probe reverted to `find_spec` or to a shallow `cumulusci` import, either
`git status` return code left unchecked — which matters because a failed `git status` returns
empty stdout, indistinguishable from a clean tree, so it would drop uncommitted paths from
the selection and, in the CCI-reference check, report "no drift" and pass — `--untracked-files=all`
dropped, the setuptools co-requirement dropped or emitted after the package that needs it,
a directory claim swallowing shell suites again, `pyproject.toml` removed from either
pytest-driven check's triggers, each of the nine trigger lists narrowed back off an input its
check reads, and each of the four read-enumeration shapes stopped being recognised (directory
arguments unexpanded, rooted single segments unseen, chain prefixes unfiltered, a root
directory counted as a read). The first round of mutations found two live holes in these tests,
both in the gap between a helper returning the right value and the gate acting on it. The
nesting guard is the one property confirmed by hang rather than by failure, for the reason
given above.

Building it turned up five real defects rather than only proving the wiring. Making
`skill_manifest.py --check` gating exposed that it could not pass in CI at all: it demanded a
path inside the gitignored private artifacts tree, so it failed on every fresh clone while
passing on the workstation that held the clone (fixed above, in that script's own section). A
stale `--api-version 67.0` assertion in `tests/txn_data_harness/test_cli.py` had survived the 264
bump because nothing ran that suite. Three suites bound an exception class from CumulusCI
while the module under test bound its own fallback shim, so on a partially importable
CumulusCI the `except` clause missed and the suite failed with a confusing traceback instead
of a clear environment error; they now bind the class from the module under test. The root
`tui-cci` launcher was read and executed by a test that no check selected, so nothing ran it on
a launcher change. And the gate's own unclaimed-suite check caught its own new suite.

**Used by:** `AGENTS.md` §"Pre-merge checklists". The workflow that runs it on every PR is
drafted in pack 125 and is the remaining half of `#264-58`.

---

## Dependencies

- **Python 3.10+** (the schema-diff and skill-manifest scripts use PEP 604
  union types like `list[Path] | None`; the repo's CI workflow pins Python
  3.13 and the README recommends 3.12 for CumulusCI itself, so 3.10 is a
  safe lower bound and is what we test against in practice). The previous
  "3.8+" claim predated the schema-diff tooling.
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
