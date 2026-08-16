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
264 figures while the line above still said 262. Four files carry them; sweep all
four:

| File | Carries |
|---|---|
| `scripts/ai/README.md` (this file) | objects, fields, relationships, **and `1,148` reference fields — the only copy** |
| `docs/erds/README.md` | objects, fields, relationships |
| `.cursor/skills/revenue-cloud-data-model/SKILL.md` | objects, fields, relationships |
| `.cursor/skills/schema-validation/SKILL.md` | fields, relationships |

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

**Data source:** `.claude/skill-manifest.yml`
**Used by:** `.cursor/skills/pmos-integration/SKILL.md`

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
