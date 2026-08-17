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
per-PR branch scope. Note what running does *not* mean — a red job blocks nothing until
`Mechanical checks` is configured as a **required status check**, which is repository settings
rather than anything in this repo.

The suite asserts the workflow cannot be quietly defanged, because every way of disabling it
leaves a green PR behind — the same absence the gate exists to close, one level up. Load-bearing
rather than stylistic: no `paths:` filter (a skipped job reports success), `fetch-depth: 0` (a
shallow clone has no merge base to diff against, so selection comes up empty and passes having
checked nothing), an *executed* invocation that is not `--requirements` (that one resolves
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

A full `--all` run is 13 checks in about 17 seconds, of which `check_branch_scope.py` is 8 —
so the gate costs roughly one branch-scope run more than nothing, and a typical docs-only
selection is a couple of seconds.

Verified by `tests/test_pr_gate.py` (216 checks, hermetic throwaway repos, no network), which
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
pytest-driven check's triggers, each of the eleven trigger lists narrowed back off an input its
check reads or a script it runs, and each of the four read-enumeration shapes stopped being recognised (directory
arguments unexpanded, rooted single segments unseen, chain prefixes unfiltered, a root
directory counted as a read). **Seventy-four** more break the CI workflow instead of the driver, all
killed, in nine families. The families are what the rules cover; the parenthesised shapes are the
ones actually mutated, which is narrower — an earlier version of this list named `paths-ignore:`,
`|| :` and `|| exit 0` as though they had been probed when only the rules mentioned them.
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
`|| :`, `|| exit 0`, `|| echo`, `|| /bin/true`, `&`, `$( )`, `continue-on-error:`, `set -e`
dropped, `set +e` without a check, a trailing `echo` or `exit 0`, or `code=$?` replaced by
`code=0`, an `echo` that then `exit 0`s or shadows `python` as a function); the checker is defanged
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

Six *correct* edits are separately confirmed to be accepted, because a rule that fires on a
legitimate change is a rule someone deletes: a re-raising handler
(`|| { echo "::error::…"; exit 1; }`), a trailing `echo "::notice::"`, a progress `echo` before the
call, `--no-fetch` moved onto the invocation instead of the argument list, a `types:` filter that is a
*superset* of the default three, and a second job that carries its own `if:`.

The doubled shapes are there because **fifty-four of these guards were vacuous on the first
attempt**, in five waves of 7, 5, 26, 2 and 14 — each wave a narrower version of one mistake, and
each found *after* the previous wave's fix was reported complete.

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
taking the first word of each shell segment (split on `&&`, `||`, `;`, and `|`; `echo`, `printf`,
`:`, or `true` there means the script is an argument) and rejecting masking in the text that
*follows* that segment, so a cleanup like `rm -f log || true; python …` is still accepted.

**Twenty-six retired the approach rather than extended it.** A line-scoped rule cannot
see the step around a command, and that is where most ways to neutralise one live — so the two
load-bearing steps are read as steps and pinned to a single permitted shape each: no `if:`, no
`continue-on-error:`, `set -euo pipefail` first, exactly one command executing the gate, only bare
`echo`s around it. The `on:` block must contain `pull_request:` and no filter; the gate job may carry
only keys that cannot stop it running; `SEL` may only be `--all` or `--base ${BASE}`; and the
checker's `$?` must be captured on the line after it runs. That is a whitelist, deliberately: a
blacklist has to imagine every way to break the job, a whitelist only has to describe the one way it
may work.

**The last fourteen are the reason those whitelists are now read from a parse rather than matched as
text**, and they are the most instructive of the five waves, because the whitelist was the right
idea implemented against the wrong representation. A whitelist of *keys* enforced by a regex over
unquoted keys is not a whitelist: `"continue-on-error": true` slipped through it, and so did every
key the regex did not name — `shell: "cat {0}"`, which makes the runner print the script instead of
running it, at step level or as a job-wide `defaults.run.shell`; a step `env:` re-pointing `SEL`. A
whitelist of *job* keys enforced by "the text between `jobs:` and the first `- name:`" is not one
either: `if: false` appended after the `steps:` list lands outside that window, and a decoy job above
the real one collapses it entirely. So the workflow is now parsed — 90 lines of stdlib block YAML,
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

Two of the fifty-four were caught by the mutation sweep and fifty-two by review, each time *after*
a sweep reported every mutation killed — five rounds running. A sweep only mutates in the shapes
its author already imagined, and here the blind spot moved rather than closed each time: comments,
then echoes, then masking, then the step and trigger levels the rules never read at all, then
the two shapes a whitelist of *permitted commands* still cannot see — a permitted command whose
status the shell throws away (`&`), and a value that crosses a step boundary through `$GITHUB_ENV`
rather than appearing in the step being read — and finally the gap between a whitelist and the text
it was matched against. The durable lesson is not any one of those shapes; it
is that "all mutations killed" is evidence about the sweep, and a guard is only as good as the
narrowest question it asks. Round 5 also retired a claim this file used to make — that the job "may
not be conditional" — which two mutations disproved: documentation asserting a property the code does
not have is worse than silence, because it is what the next reviewer trusts instead of re-deriving.
The corpus is kept at `.agents/artifacts/sweeps/` for that reason — 74 mutations across four files,
all killed.

How a sweep runs turned out to matter as much as what it mutates. The first three files mutate the
tracked workflow in place and restore it with `git checkout`, and that design produced two confident
wrong answers: one reported 21/25 with two anchors "missing" against a workflow one line off HEAD
(25/25 once restored), and a suite run in another terminal failed on `SEL="--base HEAD"` — a mutation
from this corpus, caught mid-flight, in a shell that had touched nothing. Any concurrent reader sees a
mutated tree, so results are noise in both directions. All of them now refuse to run on a modified
tree or a failing baseline, and the round-5 file goes further: it mutates a throwaway `git worktree`
and copies in only the files under test, so a sweep can no longer be seen by anything but itself.

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
