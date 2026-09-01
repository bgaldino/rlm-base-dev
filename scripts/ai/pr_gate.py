#!/usr/bin/env python3
"""Run the mechanical checks a change actually needs, and report the status of every one.

Nothing mechanical ran on a pull request here unless it touched agent tooling: the only
`pull_request` workflow was path-filtered to `AGENTS.md`, `.cursor/**`, `.agents/**` and
`scripts/ai/**`. A PR changing `tasks/`, `tests/`, `datasets/`, `templates/`,
`force-app/`, `unpackaged/`, `robot/` or `cumulusci.yml` got **no** automated check —
not the offline suites, not the dataset validators, not the doc-step or ERD-count gates.
Every one of those was enforced only by an agent reading a checklist, which is the
enforcement that failed in #264-27, #264-55 and #264-56: all three found by hand, late.

**Why a driver instead of `paths:` filters and `if:` conditions in the workflow.** The two
fail in *opposite* directions, and this was documented backwards until a review caught it. A
workflow skipped by path filtering never reports at all: a check required on it stays
**Pending**, and a PR needing it is blocked from merging forever — so a `paths:` filter would
wedge every PR that happens not to touch the paths. A job or step skipped by an `if:`
condition is the reverse: it reports **success**, so it reads exactly like a pass. Selection
therefore happens here, in one job that always runs, with every check reported under an
explicit status. A check that did not run says so on its own line.

Four statuses that are easy to conflate and must not be:

* `SKIPPED` — not selected, because nothing the check covers changed. Benign, but printed.
* `MISSING-DEP` — selected, but its interpreter or a package is absent. **This fails the
  gate.** Treating it as a skip is how a broken install silently turns a gate green; the
  same absence hole that let a documentation check pass by finding nothing to check.
* `ADVISORY-DEP` — the same absence on an advisory check, which does *not* fail the gate.
  A separate label because the two differ only in consequence, and reading one as the
  other is the mistake this list exists to prevent.
* `ADVISORY` — runs, reports, and never fails the gate. No check currently uses it.
  `validate_sfdmu_v5_datasets.py` was the one exception, exiting non-zero on a clean tree:
  two Criticals that were the validator's own false positives (pack 123 fixed them — a
  `Readonly` object owes no source CSV; a per-pass CSV lives under `objectset_source/`), plus
  High findings standing — zero-byte `Upsert` CSVs under `datasets/sfdmu/mfg/en-US/mfg-multicurrency/`
  — real but dormant, because that plan was unwired. *Either* bucket failed the validator, so
  fixing only the Criticals could not turn it gating; pack 110 removed the plan too, and the
  check now gates like every other. The status stays defined for the next check that earns it:
  a check that always fails gets ignored, and an ignored check is worse than an absent one, so
  it gets labelled with the reason instead.

Exit codes follow `check_branch_scope.py`, so a tool error is never read as a verdict:
0 = every selected gating check passed · 1 = at least one failed · 2 = usage or tool error.

Usage:
    python scripts/ai/pr_gate.py --base origin/264        # select from the diff vs a ref
    python scripts/ai/pr_gate.py --changed-files-from f   # one path per line (tests, CI)
    python scripts/ai/pr_gate.py --all                    # ignore selection, run everything
    python scripts/ai/pr_gate.py --list                   # print the matrix, run nothing
    python scripts/ai/pr_gate.py --requirements --base X  # extra pip deps the selection needs
"""

import argparse
import os
import shutil
import subprocess
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Package -> the import that proves it is USABLE, not merely present. `cumulusci` maps to
# `cumulusci.core.tasks` because the top-level package imports on a install that cannot run
# a task: `cumulusci.core.tasks` -> `cumulusci.core.config` -> `fs` -> `pkg_resources`, which
# Python 3.12+ venvs do not ship unless setuptools is installed (`prepare-rlm-org.yml` pins
# `setuptools>=75.4,<77` ahead of CumulusCI for exactly this reason). Probed with a real
# import rather than `find_spec`, which answers "is there a file to import" and so calls such
# an install fine — the failure then surfaces as two unrelated-looking suite failures instead
# of one blocked dependency. `analyze_agent_tooling.py` also needs Python 3.10+
# (`sys.stdlib_module_names`); on 3.9 it reported `json, os, re` as non-stdlib, so the version
# is checked as a dependency rather than assumed.
DEPS = {
    "PyYAML": "yaml",
    "cumulusci": "cumulusci.core.tasks",
    "pytest": "pytest",
    "textual": "textual",
    "requests": "requests",
}

# What `--requirements` emits, so CI installs only what the selection needs. CumulusCI is
# pinned to the version `prepare-rlm-org.yml` installs: two workflows resolving different
# CumulusCI versions would let a flow-citation check pass here and fail there.
PINS = {"cumulusci": "cumulusci==4.8.1"}

# Installed alongside a package, because installing only the package leaves it unusable.
# CumulusCI imports `fs`, which imports `pkg_resources`, which Python 3.12+ venvs do not
# ship — so a caller that installs exactly what `--requirements` prints would still get
# MISSING-DEP for cumulusci. Emitting this here rather than documenting a manual extra step
# keeps that knowledge in one place: `prepare-rlm-org.yml` already installs the same pin, and
# the second workflow author should not have to rediscover why.
CO_REQUIRES = {"cumulusci": ["setuptools>=75.4,<77"]}

# Lines of an advisory check's output to keep — the FIRST lines, not the last: the SFDMU
# validator puts its summary and its Critical counts at the top and then lists every passing
# plan, so tailing kept a wall of passes and elided the only thing the reader needs.
# Gating failures are never truncated.
ADVISORY_HEAD = 20

# Per-check wall-clock ceiling. Generous: the slowest real check is ~8s.
CHECK_TIMEOUT = 900

# name, command, path prefixes that select it, extra pip deps, gating, note.
# `suffixes` is for a check that reads the whole repo rather than a subtree: prefixes cannot
# express "every .md file", and pretending otherwise is how a check ends up unable to select
# on the very files it audits.
CHECKS = [
    dict(
        name="agent_tooling",
        cmd=["python", "scripts/ai/analyze_agent_tooling.py", "check"],
        # CLAUDE.md is in the script's REQUIRED_FILES, so its deletion fails this check —
        # it was missing here, found by the read-enumeration in tests/test_pr_gate.py.
        triggers=["AGENTS.md", "CLAUDE.md", "REVIEW.md", ".github/copilot-instructions.md",
                  ".claude/skill-manifest.yml", ".cursor/", ".agents/", "scripts/ai/"],
        deps=[], min_python=(3, 10), gating=True,
    ),
    dict(
        name="skill_manifest",
        cmd=["python", "scripts/ai/skill_manifest.py", "--check"],
        # The audit resolves every path the manifest cites, and the manifest cites paths all
        # over the repo — so triggering only on the manifest and the skills tree let a cited
        # target be deleted or renamed under docs/, postman/, orgs/ with the check skipped,
        # which is precisely the drift it exists to catch. These are the script's own
        # _PATH_ROOTS and _ROOT_FILES; tests/test_pr_gate.py reads them back out of the
        # script and fails if the two lists diverge. Broad selection is affordable here
        # because this is the cheapest check in the matrix (~0.1s).
        triggers=[".agents/", ".claude/", ".cursor/", ".github/", "config/", "datasets/",
                  "docs/", "force-app/", "orgs/", "postman/", "robot/", "scripts/",
                  "tasks/", "templates/", "unpackaged/",
                  "AGENTS.md", "CLAUDE.md", "REVIEW.md", "README.md", "cumulusci.yml"],
        deps=[], gating=True,
    ),
    dict(
        name="plan_readme_consistency",
        # --strict: without it, operation/externalId mismatches and missing-object
        # rows are WARN-only and exit 0 — a stale object table would pass the gate
        # silently, the same "passes by absence" defect class this check exists to
        # catch in the first place (pack 147).
        cmd=["python", "scripts/ai/check_plan_readme_consistency.py", "--strict"],
        # The validator itself, not only the data it validates: a semantic regression in it
        # otherwise merges with only `agent_tooling`'s syntax scan having looked at the file,
        # and nothing having run it. Same for the generator that produces the READMEs this
        # check reads — a PR touching only generate_plan_readme.py (no datasets/sfdmu/ file)
        # would otherwise skip the one check that verifies its output against export.json/CSVs.
        # scripts/validate_sfdmu_v5_datasets.py is a trigger for the identical reason: both
        # README scripts call directly into SFDMUValidator (_normalized_object_sets,
        # _resolve_operation, _is_js_truthy) and _SKIP_SEGMENTS, so a semantic change there
        # (e.g. widening _resolve_operation to numeric enum indices) can regress how this
        # check reads real README/export.json content without touching either README script
        # or any datasets/sfdmu/ file — `sfdmu_datasets`/`sfdmu_csv_expectation` selecting on
        # it exercises the validator's own logic, not this check's consumption of it.
        triggers=["datasets/sfdmu/", "scripts/ai/check_plan_readme_consistency.py",
                  "scripts/ai/generate_plan_readme.py",
                  "scripts/validate_sfdmu_v5_datasets.py"],
        deps=[], gating=True,
    ),
    dict(
        name="plan_readme_parsing",
        cmd=["python", "tests/test_check_plan_readme_consistency.py"],
        # Synthetic-fixture suite, not a live-tree read: it pins check_plan_readme_consistency.py's
        # own parsing semantics (Pass-column narrowing, a bogus Pass value reported rather than
        # ANY-variant matched, IGNORE_MARKER/seen_objects composition, OMIT_MARKER, KEYLIKE_RE
        # gating) against crafted export.json/README pairs. Before this suite existed, only
        # `plan_readme_consistency` above ran that module — against the repo's real READMEs, which
        # exercise whatever shape they happen to have, not every shape the module's own comments
        # document handling (round 18 of PR #406's review, pack 147: no suite caught a regression
        # in these semantics unless a tracked README happened to already be in that exact shape).
        triggers=["tests/test_check_plan_readme_consistency.py",
                  "scripts/ai/check_plan_readme_consistency.py"],
        deps=[], gating=True,
    ),
    dict(
        name="plan_readme_discovery",
        cmd=["python", "tests/test_check_plan_readme_discovery.py"],
        # find_plan_dirs()/tracked_plan_dirs()/tracked_paths() — this PR's (#406) headline
        # fix, discovering a plan on export.json alone and gating the required-README set on
        # git tracked-ness — had no test of its own before round 21's hosted review (comment
        # 3901323028): plan_readme_parsing above only exercises check_plan()'s README-content
        # parsing, always against a synthetic plan that already has a README. Builds an
        # isolated synthetic git repo per case (tests/test_branch_scope.py's pattern), so it
        # does not read this checkout's real datasets/sfdmu/ tree.
        triggers=["tests/test_check_plan_readme_discovery.py",
                  "scripts/ai/check_plan_readme_consistency.py"],
        deps=[], gating=True,
    ),
    dict(
        name="generate_plan_readme_writer",
        cmd=["python", "tests/test_generate_plan_readme.py"],
        # write_readme()/generate_block()/resolve_pass_csv() — the generator PR #406 added to
        # close the gate's own gap — had no test of its own before round 21's hosted review
        # (comment 3901323059): marker-preservation on regenerate, the --force wholesale-
        # replace path, and the per-pass CSV resolution rule mirroring
        # _objects_owing_root_csv were unguarded but for the module's own comments.
        triggers=["tests/test_generate_plan_readme.py", "scripts/ai/generate_plan_readme.py",
                  "scripts/ai/check_plan_readme_consistency.py"],
        deps=[], gating=True,
    ),
    dict(
        name="erd_doc_counts",
        cmd=["python", "tests/test_erd_doc_counts.py"],
        # Exactly the files the suite reads (its TRIPLE_SITES, docs/erds/*, domains/*.md).
        # doc-consistency/ was here and the suite never reads it — over-selection is matrix
        # drift in a matrix whose job is preventing drift.
        triggers=["docs/erds/", ".cursor/skills/revenue-cloud-data-model/",
                  ".cursor/skills/schema-validation/",
                  "scripts/ai/README.md", "tests/test_erd_doc_counts.py"],
        deps=[], gating=True,
    ),
    dict(
        name="sfdmu_csv_expectation",
        cmd=["python", "tests/test_sfdmu_csv_expectation.py"],
        # Gating for its own reason, independent of `sfdmu_datasets` below: this suite is about
        # whether the validator still asks for a root CSV where one is owed. It runs on synthetic
        # fixtures, so it is green on a clean tree and can gate regardless of what the live
        # validator finds.
        #
        # `datasets/sfdmu/` IS a trigger, and the reason is worth keeping because it was wrong once
        # in each direction. The suite began hermetic — synthetic tempdirs only — so the trigger was
        # over-selection and was dropped. Then it gained `live_baseline()`, which asserts the real
        # tree's finding counts (0 Critical, 0 High, since pack 110 removed the unwired
        # mfg-multicurrency plan that carried the last High findings) so the sites quoting those
        # numbers cannot drift. That made the suite dataset-reading: a `datasets/` edit that changes
        # the live baseline (say, reintroducing an unwired plan with zero-byte CSVs) has to select
        # the suite that would fail on it, or the red is only deferred onto the next unrelated PR
        # that touches the validator.
        #
        # The doc trees below are triggers for that same reason, one round later and found by the
        # `no suite reads a file that cannot select it` guard rather than by review: the suite now
        # discovers every site quoting the baseline and pins the case count quoted in
        # `scripts/ai/README.md`, so a prose edit in any of those trees is exactly a change that can
        # fail it. Broad selection is the honest cost of asserting over prose; the alternative is an
        # assertion whose triggering edit does not run it.
        # `baseline_sites()`'s `roots` once rglobbed the whole `tests/` tree, which is why a bare
        # `tests/` prefix lived here — a baseline quotation added or edited in a *sibling* suite had
        # to be reachable, or it would be the unreachable forcing-function shape twice over in the
        # same check. `roots` has since been narrowed to the one file under `tests/` it actually
        # reads (`tests/test_pr_gate.py` — verified nothing else there matches its pattern), so the
        # bare prefix now over-selects: it runs this check for every unrelated edit under `tests/`,
        # the same matrix drift the `erd_doc_counts` trigger comment above names. Listed explicitly
        # instead — this suite's own file, so self-edits still select it (nothing else does that for
        # a suite that names no path of its own), plus the one sibling `baseline_sites()` reads.
        triggers=["scripts/validate_sfdmu_v5_datasets.py", "tests/test_sfdmu_csv_expectation.py",
                  "tests/test_pr_gate.py", "datasets/sfdmu/",
                  "AGENTS.md", "scripts/ai/", "docs/features/", ".cursor/skills/"],
        deps=[], gating=True,
    ),
    dict(
        name="branch_scope",
        cmd=["python", "tests/test_branch_scope.py"],
        # The last two are read by the suite, which asserts both cite its current size — so
        # editing either without selecting this check is how a stale count survives.
        triggers=["scripts/ai/check_branch_scope.py", "tests/test_branch_scope.py",
                  "scripts/ai/README.md", ".cursor/skills/audit-review/SKILL.md"],
        deps=[], gating=True,
    ),
    dict(
        name="doc_build_steps",
        cmd=["python", "tests/test_doc_build_steps.py"],
        # The suite walks every .md in the repo, so any .md must be able to select it.
        # With prefixes alone, live `step N of <flow>` citations in the root README and in
        # seven datasets/**/README.md files could be edited with this check skipped —
        # cumulusci.yml covered renumbering, but not writing a new wrong citation.
        triggers=["cumulusci.yml", "tests/test_doc_build_steps.py"],
        suffixes=[".md"],
        deps=["cumulusci"], gating=True,
    ),
    dict(
        name="cci_reference_drift",
        cmd=None,  # regenerate, then require a clean tree — see run_cci_reference_drift
        # The generated files themselves are triggers: they carry a "do not edit" banner, so a
        # hand edit to one is the exact case this check adjudicates, and it cannot adjudicate
        # what it is not selected for.
        triggers=["cumulusci.yml", "scripts/ai/generate_cci_reference.py",
                  ".cursor/skills/cci-orchestration/tasks-reference.md",
                  ".cursor/skills/cci-orchestration/flows-reference.md",
                  ".cursor/skills/cci-orchestration/feature-flags.md"],
        deps=["PyYAML"], gating=True,
    ),
    dict(
        name="stdlib_offline_suites",
        cmd=None,  # expanded at runtime — see STDLIB_SUITES
        # `docs/references/` is a non-code input one of these suites reads and asserts against (the
        # usage-consumption skill's stated check count), so editing it could invalidate a suite that
        # was not selected to notice.
        triggers=["tasks/", "scripts/", "tests/", "datasets/", "cumulusci.yml",
                  "force-app/", "unpackaged/",
                  ".cursor/skills/usage-consumption/", "docs/references/"],
        deps=[], gating=True,
    ),
    dict(
        name="requests_offline_suites",
        cmd=None,  # expanded at runtime — see REQUESTS_SUITES
        # The modules these two suites exercise, plus the non-code inputs they read and assert
        # against — the shipped overlay examples and the export fixture. The paths are the ones the
        # trigger-coverage rule named when this check was first added with guessed ones: a suite that
        # reads a file no trigger selects is a suite that can be invalidated without being run.
        # `tasks/expression_set_schema.py` is imported directly by
        # `tests/test_expression_set_schema.py:21`, and was missing here: a change to the module was
        # covered by no check that runs its own tests. The trigger-coverage rule this comment cites
        # reads the paths a suite *opens*, not the modules it *imports*, which is the whole reason the
        # gap survived — so the suite now asserts import coverage too, and the sweep behind that rule
        # found this to be the only instance.
        triggers=["tasks/rlm_expression_set_connect.py", "tasks/rlm_cml.py",
                  "tasks/expression_set_schema.py",
                  "scripts/expression_sets/", "scripts/cml/",
                  "tests/test_expression_set_schema.py",
                  "tests/test_rlm_cml_import_failure.py",
                  "tests/data/expression_set/",
                  "datasets/expression_set_overlays/",
                  "docs/references/expression-set-overlay-examples/"],
        deps=["requests"], gating=True,
    ),
    dict(
        name="yaml_offline_suites",
        cmd=["python", "tests/test_decision_table_tasks.py",
             "tests/test_fulfillment_scope_tolerance.py",
             "tests/test_skill_manifest_audit.py"],  # run in sequence
        # qb-dro because test_fulfillment_scope_tolerance.py reads its Product2.csv and
        # FulfillmentStepDefinition.csv and asserts the banner's count matches them — adding a
        # usage product to that dataset invalidates the assertion, so it has to select this.
        triggers=["tasks/", "cumulusci.yml", "scripts/ai/skill_manifest.py",
                  ".claude/skill-manifest.yml",
                  "datasets/sfdmu/qb/en-US/qb-dro/",
                  "tests/test_decision_table_tasks.py",
                  "tests/test_fulfillment_scope_tolerance.py",
                  "tests/test_skill_manifest_audit.py"],
        deps=["PyYAML"], gating=True,
    ),
    dict(
        name="docgen_suite",
        # The one pytest-style suite directly under tests/ (the harness directories below
        # hold ~30 more): pytest collects it and it has no __main__ block, so
        # `python tests/test_docgen_helpers.py` exits 0 having run zero tests once pytest is
        # installed (and ModuleNotFoundError before that). A silent green, so it is invoked
        # through pytest, not the repo's usual `python tests/<name>.py`.
        cmd=["python", "-m", "pytest", "-q", "tests/test_docgen_helpers.py"],
        # pyproject.toml carries [tool.pytest.ini_options], so it shapes what this command
        # collects — a change there that breaks collection has to select the pytest checks.
        triggers=["scripts/docgen/", "tests/test_docgen_helpers.py", "pyproject.toml"],
        deps=["pytest"], gating=True,
    ),
    dict(
        # 30 pytest suites under tests/build_harness/ and tests/txn_data_harness/ that no
        # check ran and no report mentioned, because discovery used a non-recursive listing.
        # They pass; build_harness needs 3.11+ for enum.StrEnum. No count here on purpose —
        # nothing offline can verify one, and it had already drifted once. Running them found a real
        # 264 regression: test_cli.py still asserted api-version 67.0 after commit 66f193f9
        # bumped the harness to 68.0 — a stale assertion nothing had executed since.
        name="harness_suites",
        cmd=["python", "-m", "pytest", "-q",
             "tests/build_harness", "tests/txn_data_harness"],
        # pyproject.toml sets testpaths/python_files/addopts for these two directories, so a
        # collection change there must select this check rather than land unexercised.
        # tui-cci because tests/build_harness/test_tui_launcher.py copies and executes that
        # root launcher: nothing else in the matrix claimed it, so a launcher regression could
        # pass the gate with its own existing test unrun.
        triggers=["scripts/build_harness/", "scripts/txn_data_harness/",
                  "tests/build_harness/", "tests/txn_data_harness/", "pyproject.toml",
                  "tui-cci"],
        deps=["pytest", "PyYAML", "textual", "requests"], min_python=(3, 11), gating=True,
    ),
    dict(
        # Kept out of stdlib_offline_suites on purpose: this suite invokes pr_gate.py as a
        # subprocess, so running it from inside a check that a `tests/` change selects
        # would nest the gate inside itself. Its own probe paths select only checks that
        # do not run it, which bounds the nesting at one level.
        name="pr_gate_suite",
        cmd=["python", "tests/test_pr_gate.py"],
        # prepare-rlm-org.yml is read by the suite, which asserts its CumulusCI pin matches
        # PINS here. Without it as a trigger the two workflows could drift apart while this
        # gate reported success — the cross-workflow guarantee unenforced from one side. The
        # scripts/ai/ prefix rather than pr_gate.py alone because the suite also reads
        # skill_manifest.py's audited roots and analyze_agent_tooling.py's required-file
        # lists, to prove the matrix still selects on them.
        #
        # tests/ because this suite holds the meta-check that every *other* suite's reads are
        # selectable. Without it, a PR could add a repo-file read to a suite and omit the
        # trigger, and the one check that would have caught the omission never ran. The suite
        # runs the gate as a subprocess, so this widening risks nesting — bounded by the
        # fixtures it feeds those runs, which main_with() asserts never select this check.
        #
        # pr-checks.yml is the job that runs this gate on a pull request, and the suite asserts
        # it cannot be defanged (no paths filter, full history, pins from --requirements). That
        # guarantee has to hold from this side too: an edit to the workflow alone must run the
        # suite that judges it. The enumeration gate below demanded this trigger the moment the
        # assertion was written, which is the intended order.
        triggers=["scripts/ai/", "tests/", ".github/workflows/prepare-rlm-org.yml",
                  ".github/workflows/pr-checks.yml"],
        deps=[], gating=True,
    ),
    dict(
        name="sfdmu_datasets",
        cmd=["python", "scripts/validate_sfdmu_v5_datasets.py"],
        triggers=["datasets/", "scripts/validate_sfdmu_v5_datasets.py"],
        deps=[], gating=True,
    ),
]

# Suites that need nothing but the standard library, run as one check. Enumerated rather
# than globbed: a new suite with an unmet dependency would otherwise join a stdlib check
# and fail it for a reason that has nothing to do with the change. `unlisted_suites()`
# reports anything in tests/ that no check claims, so adding one is not silently ignored.
STDLIB_SUITES = [
    "tests/test_agents_common.py",
    "tests/test_context_apply.py",
    "tests/test_context_delete.py",
    "tests/test_context_payload.py",
    "tests/test_context_plan_validator.py",
    "tests/test_context_runtime.py",
    "tests/test_decision_tables_client.py",
    "tests/test_decision_tables_toolkit.py",
    "tests/test_expression_sets_toolkit.py",
    "tests/test_fix_scratch_identity.py",
    "tests/test_qb_multicurrency_data.py",
    "tests/test_rlm_apex_file.py",
    "tests/test_snapshot_dev_guide.py",
]

# Offline like the list above, but they reach a `tasks/` module that imports `requests`, so the
# dependency is declared and installed rather than inherited by luck from another check's transitive
# tree. Kept as a separate list so `STDLIB_SUITES` means what it says.
REQUESTS_SUITES = [
    "tests/test_expression_set_schema.py",
    "tests/test_rlm_cml_import_failure.py",
]

# Which check runs which spliced list — named once, read by both `resolve()` (to build the argv) and
# `_claimed_suites()` (to account for it). Two readers of an implicit pairing is how the accounting
# came apart: `resolve` keyed on the check name while the claim unioned both lists unconditionally, so
# a deleted check kept its claim.
SPLICED_SUITES = {
    "stdlib_offline_suites": STDLIB_SUITES,
    "requests_offline_suites": REQUESTS_SUITES,
}

def _claimed_suites():
    """Every suite some check actually runs — read off `CHECKS`, never restated beside it.

    This was a hand-maintained set listing the same paths a second time, and the two lists did not
    have to agree. So deleting a whole check from `CHECKS`, or dropping one path from a check's
    `cmd`, stopped running that suite while discovery still reported "none unclaimed" — the suite
    went silent and the accounting said everything was accounted for. Three separate mutations
    exploited that, and no rule could have caught them: the invariant they broke was one nothing
    stated.

    Derived, the invariant holds by construction. A path stops being claimed at the moment a check
    stops naming it, and `unlisted_suites()` reports it on the next run.
    """
    # The two bulk checks carry `cmd=None` and get their argv spliced in by `resolve()`, so their
    # suites cannot be read off `cmd` like everyone else's. Keyed on the check *name* rather than
    # unioned in unconditionally, because unconditional is the same restatement this function was
    # written to delete: deleting the whole `requests_offline_suites` check left its two suites
    # claimed by nobody running them, discovery printed "none unclaimed", and the guard suite stayed
    # green — the exact accounting lie, surviving inside its own fix.
    claimed = set()
    for check in CHECKS:
        claimed |= set(SPLICED_SUITES.get(check["name"], ()))
    for check in CHECKS:
        for arg in check["cmd"] or ():
            if not arg.startswith("tests/"):
                continue
            # A directory argument to pytest claims the .py files under it, and the claim is
            # matched by prefix, so it needs its separator.
            is_dir = os.path.isdir(os.path.join(REPO_ROOT, arg))
            claimed.add(arg.rstrip("/") + "/" if is_dir else arg)
    return claimed


CLAIMED_SUITES = _claimed_suites()

# Suites deliberately outside the gate, each with the reason. Separate from CLAIMED_SUITES so
# "nothing runs it" and "we decided not to run it" cannot be confused, and so neither can
# happen silently: discovery reports anything in tests/ that appears in neither.
EXCLUDED_SUITES = {
    "tests/test-cleanup.sh": "integration script — requires a live org",
    "tests/test-prepare-rlm-org.sh": "integration script — requires a live org",
}


def die(msg):
    print(f"pr_gate: {msg}", file=sys.stderr)
    sys.exit(2)


def unlisted_suites():
    """Suites under tests/ that no check runs and no exclusion covers.

    Walks, rather than listing one directory: a flat listing missed the 30 suites in
    tests/build_harness/ and tests/txn_data_harness/ entirely, so the report said "none
    unclaimed" while editing one of them ran seventeen unrelated suites and passed. Shell
    suites are discovered too — they were previously skipped by the `.py` filter, which
    means the right outcome (not gating an org-requiring script) happened by accident
    instead of by declaration.
    """
    tests_dir = os.path.join(REPO_ROOT, "tests")
    if not os.path.isdir(tests_dir):
        # An absent tests/ is not an empty tests/; saying "none unclaimed" here would be
        # the same lie this function exists to catch.
        return ["tests/ is missing entirely"]
    found = set()
    for root, dirs, names in os.walk(tests_dir):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".pytest_cache")]
        for name in names:
            if not (name.startswith("test_") or name.startswith("test-")):
                continue
            if not name.endswith((".py", ".sh")):
                continue
            found.add(os.path.relpath(os.path.join(root, name), REPO_ROOT))
    # A directory claim covers only the .py files under it, because the checks that claim
    # directories invoke pytest. A shell suite added under tests/build_harness/ would
    # otherwise read as claimed while nothing ran it and no exclusion recorded the decision
    # — the same silent-suite gap this function exists to close, one level down.
    claimed_dirs = tuple(c for c in CLAIMED_SUITES if c.endswith("/"))
    return sorted(f for f in found
                  if f not in CLAIMED_SUITES
                  and f not in EXCLUDED_SUITES
                  and not (f.endswith(".py") and f.startswith(claimed_dirs)))


def changed_files(base):
    """Paths changed against `base`, via the merge base so unrelated base commits do not
    enlarge the selection (the mistake `check_branch_scope.py` documents)."""
    # Three dots, not two: `base...HEAD` diffs from the merge base, so commits that
    # landed on the base after this branch diverged do not enter the selection.
    # --no-renames, because git's rename detection reports only the destination — so
    # moving a plan README *out* of datasets/sfdmu/ would not select the check that
    # notices the plan lost its README. -z, because git quotes and escapes non-ASCII
    # paths ("docs/caf\303\251.md"), and a leading quote matches no trigger prefix.
    diffed = git(["diff", "--no-renames", "-z", "--name-only", f"{base}...HEAD"],
                 f"diff against {base!r}")
    files = [p for p in diffed.split("\0") if p]
    # Uncommitted work counts too, so running this locally before a commit is honest.
    # --untracked-files=all, because the default collapses a wholly new directory to a
    # single `?? docs/` entry — the TOPMOST new directory, not even the leaf. Every
    # file in a new subtree would then be invisible to selection: the `.md` suffix
    # never matches `docs/`, so adding docs/new-guide/page.md with a wrong
    # `step N of <flow>` citation selected nothing while the report said uncommitted
    # work was covered.
    #
    # A failed status is fatal inside git(), not assumed clean: its empty stdout is
    # indistinguishable from a clean tree, so an unreadable index would otherwise drop every
    # uncommitted path from the selection and still exit 0.
    status = git(["status", "--porcelain", "--untracked-files=all", "-z"], "status")
    # -z separates entries with NUL and, for a rename or copy, emits "XY new\0old\0" — both halves
    # are wanted here. Read positionally rather than by guessing: a status entry always begins with
    # two status characters and a space, and R/C are the only ones followed by a bare path entry.
    # Sniffing for a space in the third column instead truncated any old path that happened to have
    # one (`ab cd/x.md` became `cd/x.md`), which both invents a path and loses the real one.
    entries = [e for e in status.split("\0") if e]
    i = 0
    while i < len(entries):
        entry = entries[i]
        i += 1
        if len(entry) > 3 and entry[2] == " ":
            files.append(entry[3:])
            if entry[0] in ("R", "C") or entry[1] in ("R", "C"):
                if i < len(entries):
                    files.append(entries[i])
                    i += 1
        else:
            # Not a status entry and not consumed as a rename source: keep it rather than reshape it,
            # since dropping a path here silently narrows the selection.
            files.append(entry)
    return sorted(set(files))


def git(args, purpose):
    """Run git from the repo root and return stdout, or die — never return a verdict.

    Centralised after the same two guards had to be added to each call site separately and were
    not: `run()` grew an `OSError` guard while this path kept only `FileNotFoundError`, so a git
    on PATH that cannot be executed (`PermissionError`) still escaped as a traceback, which the
    interpreter reports as exit 1 — a code verdict for an environment failure. Non-zero is fatal
    here too, because every caller reads git's *stdout* as its answer and an empty stdout from a
    failed command is indistinguishable from a clean tree.
    """
    try:
        out = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)
    except OSError as exc:
        die(f"could not run git ({purpose}): {exc}")
    if out.returncode != 0:
        die(f"git {purpose} failed: {out.stderr.strip()}")
    return out.stdout


def selects(check, files):
    if any(f.startswith(t) for t in check["triggers"] for f in files):
        return True
    return any(f.endswith(s) for s in check.get("suffixes", ()) for f in files)


def missing_deps(check):
    missing = [pkg for pkg in check["deps"]
               if not have_module(DEPS.get(pkg, pkg))]
    need = check.get("min_python")
    if need and sys.version_info[:2] < need:
        missing.append(f"python>={'.'.join(str(n) for n in need)}"
                       f" (running {sys.version_info.major}.{sys.version_info.minor})")
    return missing


_IMPORTABLE = {}


def have_module(name):
    """True when `import name` actually succeeds, in a child so nothing leaks in here."""
    if name not in _IMPORTABLE:
        try:
            proc = subprocess.run([sys.executable, "-c", f"import {name}"],
                                  capture_output=True, timeout=120)
            _IMPORTABLE[name] = proc.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            _IMPORTABLE[name] = False
    return _IMPORTABLE[name]


def run(cmd):
    """Run one command from the repo root, streaming nothing but returning everything."""
    argv = list(cmd)
    # Both spellings, because the suite's argv whitelist admitted `python3` while this normalised only
    # `python` — so a check spelled that way ran under whatever `python3` resolved to, while its `deps`
    # were probed against `sys.executable` and its `min_python` against this interpreter's version. The
    # guarantee, not the verdict, is what that voided. The whitelist no longer admits `python3`; this
    # keeps the two from disagreeing again if it is ever re-added.
    if argv and argv[0] in ("python", "python3"):
        argv[0] = sys.executable
    started = time.time()
    try:
        # Bounded, so one hung check cannot burn the whole CI job's budget with no output.
        proc = subprocess.run(argv, cwd=REPO_ROOT, capture_output=True, text=True,
                              timeout=CHECK_TIMEOUT)
    except subprocess.TimeoutExpired:
        # A timeout stays a check failure, not a tool error: a check that hangs is a property
        # of the change under test, unlike an interpreter that will not start.
        return 1, (f"timed out after {CHECK_TIMEOUT}s: {' '.join(argv)}"), time.time() - started
    except OSError as exc:
        die(f"could not run {argv[0]!r}: {exc}")
    # `subprocess` reports a child killed by a signal as *negative* (-9 for SIGKILL). Left negative
    # it loses every ordering comparison against 0, so an OOM-killed suite ranked below a clean one
    # and reported a pass. Normalised here rather than at each caller: a signal kill produced no
    # verdict, which is the definition of a tool error in this file's 0/1/2 contract.
    #
    # This line alone did not deliver that contract, and the sentence above used to imply it did. It
    # fixed the *ranking* — a signal kill no longer sorts below a clean run — while `main()`'s booking
    # loop still sent 1 and 2 down one branch, so the job exited 1 and published a code verdict on a
    # check that never reached one. The contract is kept where the exit code is chosen; the two halves
    # are noted in each other's comments because neither is sufficient alone.
    code = 2 if proc.returncode < 0 else proc.returncode
    return code, proc.stdout + proc.stderr, time.time() - started


def run_cci_reference_drift():
    """Regenerate the CCI reference and require the tree to come back clean.

    The generator is the check: it exits 0 whether or not it rewrote anything, so the
    verdict is the git diff afterwards, scoped to what it writes.
    """
    code, out, secs = run(["python", "scripts/ai/generate_cci_reference.py"])
    if code != 0:
        return code, out, secs
    # Scoped to exactly the three files the generator writes. It was scoped to
    # docs/references/ as well, which it never writes and which is hand-authored — so any
    # unrelated edit there failed the check with "commit the regenerated result".
    generated = [f".cursor/skills/cci-orchestration/{name}"
                 for name in ("tasks-reference.md", "flows-reference.md",
                              "feature-flags.md")]
    # Through git(), which dies on both a spawn failure and a non-zero exit. Here the
    # empty-output-means-clean trap is worse than in changed_files: this status *is* the
    # verdict, so a failed one would read as "no drift" and pass the check.
    drift = git(["status", "--porcelain", "--", *generated], "status for reference drift")
    if drift.strip():
        return 1, (out + "\nRegenerating changed committed files — commit the result:\n"
                   + drift), secs
    return 0, out + "\nno drift", secs


def resolve(check):
    if check["name"] == "cci_reference_drift":
        return run_cci_reference_drift
    if check["name"] in SPLICED_SUITES:
        suites = SPLICED_SUITES[check["name"]]
        return lambda: run_sequence([["python", s] for s in suites])
    if check["name"] == "yaml_offline_suites":
        return lambda: run_sequence([["python", s] for s in check["cmd"][1:]])
    if check["cmd"] is None:
        # A runtime-expanded check whose branch above was never added would otherwise reach
        # run(None) and raise, aborting the loop before any result printed — and exit 1,
        # reading as a gating failure rather than the tool error it is.
        die(f"{check['name']} has cmd=None and resolve() has no branch for it")
    return lambda: run(check["cmd"])


def run_sequence(cmds):
    """Run every command even after one fails, so a single failure does not hide the rest.

    `worst` means worst: a tool error (2) outranks a verdict failure (1), which outranks success.
    Spelled `worst = worst or code` it kept the *first* non-zero, so a suite that could not run at
    all was reported as a suite that ran and disagreed — the one conflation this script exists to
    prevent everywhere else.
    """
    worst, chunks, total = 0, [], 0.0
    for cmd in cmds:
        code, out, secs = run(cmd)
        total += secs
        # Ranked, not `max()`d: any negative code is normalised to 2 in `run()`, but ranking states
        # the intended order (tool error beats verdict beats clean) instead of relying on 0 < 1 < 2
        # happening to hold for the values that reach here.
        worst = max(worst, code, key=lambda c: (c == 2, c != 0))
        chunks.append(f"$ {' '.join(cmd)}  -> exit {code} ({secs:.1f}s)\n{out}")
    return worst, "\n".join(chunks), total


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", help="git ref to diff against (e.g. origin/264)")
    ap.add_argument("--changed-files-from", help="file with one changed path per line")
    ap.add_argument("--all", action="store_true", help="run every check regardless of paths")
    ap.add_argument("--list", action="store_true", help="print the matrix and exit")
    ap.add_argument("--requirements", action="store_true",
                    help="print pip deps the selection needs, one per line, then exit")
    args = ap.parse_args()

    if args.list:
        print(f"{'check':26} {'gating':7} {'deps':34} triggers")
        for c in CHECKS:
            selectors = list(c["triggers"]) + [f"*{s}" for s in c.get("suffixes", ())]
            print(f"{c['name']:26} {str(c['gating']):7} "
                  f"{','.join(c['deps']) or '-':34} {', '.join(selectors)}")
        print("\nexcluded from the gate, deliberately:")
        for path, reason in sorted(EXCLUDED_SUITES.items()):
            print(f"  {path:40} {reason}")
        orphans = unlisted_suites()
        print(f"\nsuites no check runs and no exclusion covers: {orphans or 'none'}")
        return 0

    if sum(bool(x) for x in (args.base, args.changed_files_from, args.all)) != 1:
        die("pass exactly one of --base, --changed-files-from, --all")

    if args.all:
        files, selected = None, list(CHECKS)
    else:
        if args.changed_files_from:
            try:
                with open(args.changed_files_from) as f:
                    files = [ln.strip() for ln in f if ln.strip()]
            except OSError as exc:
                die(f"cannot read {args.changed_files_from}: {exc}")
        else:
            files = changed_files(args.base)
        selected = [c for c in CHECKS if selects(c, files)]

    if args.requirements:
        needed = sorted({d for c in selected for d in c["deps"]})
        emitted = []
        for pkg in needed:
            # Co-requirements first: pip installs in order, and setuptools has to be there
            # before the package that imports pkg_resources at import time.
            for extra in CO_REQUIRES.get(pkg, ()):
                if extra not in emitted:
                    emitted.append(extra)
            emitted.append(PINS.get(pkg, pkg))
        for line in emitted:
            print(line)
        return 0

    orphans = unlisted_suites()
    if files is not None:
        print(f"{len(files)} changed path(s) vs {args.base or 'file'}; "
              f"{len(selected)} of {len(CHECKS)} checks selected\n")

    # `tool_errors` is separate from `failures` because the two mean different things and this script's
    # exit contract turns on the difference. `run()` normalises a signal-killed child to 2 and its
    # comment there calls that "the definition of a tool error in this file's 0/1/2 contract" — but the
    # booking loop below used to send 1 and 2 down the same branch, so an OOM-killed suite was appended
    # to `failures` and published as exit 1: a code verdict on a check that never produced one. Verified
    # before the fix — a runner returning 2 made `main()` return 1. The normalisation achieved its
    # *ranking* purpose (a signal kill no longer sorts below a clean run) and none of its contract
    # purpose, and the comment claimed both.
    results, failures, advisory_failures, tool_errors = [], [], [], []
    for check in CHECKS:
        if check not in selected:
            results.append((check, "SKIPPED", "", 0.0))
            continue
        missing = missing_deps(check)
        if missing:
            # Gating: a missing dependency is a failure, not a skip. Otherwise a broken
            # install is indistinguishable from a change that needed no checking.
            status = "MISSING-DEP" if check["gating"] else "ADVISORY-DEP"
            results.append((check, status, f"missing: {', '.join(missing)}", 0.0))
            if check["gating"]:
                failures.append(check["name"])
            continue
        code, out, secs = resolve(check)()
        if code == 0:
            results.append((check, "PASS", "", secs))
        elif code == 2:
            # No verdict, so not a failure. A gating check that could not run makes the whole gate a
            # tool error (exit 2); an *advisory* one does not, because an advisory check exists
            # precisely so that nothing it reports can block a merge, and turning its broken
            # environment into the one exit code that blocks would invert that. It is still printed
            # and still named in the summary, so it cannot pass silently either way.
            status = "ERROR" if check["gating"] else "ADVISORY-ERROR"
            results.append((check, status, out, secs))
            (tool_errors if check["gating"] else advisory_failures).append(check["name"])
        elif check["gating"]:
            results.append((check, "FAIL", out, secs))
            failures.append(check["name"])
        else:
            results.append((check, "ADVISORY", out, secs))
            advisory_failures.append(check["name"])

    width = max(len(c["name"]) for c in CHECKS)
    print("=" * 78)
    for check, status, _, secs in results:
        timing = f"{secs:5.1f}s" if secs else "      "
        note = "" if status != "SKIPPED" else "  (nothing it covers changed)"
        if status in ("ADVISORY", "ADVISORY-DEP"):
            note = f"  ({check['note']})"
        print(f"[{status:11}] {check['name']:{width}} {timing}{note}")
    print("=" * 78)

    for check, status, out, _ in results:
        # Every non-passing check gets a section, including one that failed silently:
        # "[FAIL]" with no detail anywhere is indistinguishable from a reporting bug.
        if status in ("FAIL", "ERROR", "MISSING-DEP", "ADVISORY", "ADVISORY-ERROR",
                      "ADVISORY-DEP"):
            body = out.rstrip() or "(the check produced no output)"
            # A gating failure is echoed whole — it has to be diagnosable from the log
            # alone. An advisory one is informational, and the SFDMU validator prints a
            # ~280-line report every run, so it is truncated to its HEAD (where the summary
            # and the Critical counts are) rather than allowed to bury
            # the failures above it.
            if not check["gating"]:
                lines = body.split("\n")
                if len(lines) > ADVISORY_HEAD:
                    body = ("\n".join(lines[:ADVISORY_HEAD])
                            + f"\n({len(lines) - ADVISORY_HEAD} later line(s) elided; run "
                              f"the check directly for the full report)")
            print(f"\n----- {check['name']} ({status}) -----\n{body}")

    if orphans:
        print(f"\n[FAIL       ] suites no check runs: {', '.join(orphans)}\n"
              "              add each to a check in CHECKS, or to EXCLUDED_SUITES with a "
              "reason — an unrun suite is not a passing suite")
        failures.append("unlisted_suites")

    # Every check appears in exactly one bucket and the buckets sum to len(CHECKS).
    # MISSING-DEP previously fell out of both counts, so a reader reconciling "11 executed,
    # 0 skipped" against 12 checks found one unaccounted for — the shape this file exists
    # to eliminate.
    # A check killed by a signal *ran* — it just produced no verdict — so it belongs in `executed`,
    # not in a fourth bucket. Leaving it out of all three broke the assert below, which is the
    # accounting this block exists to keep honest.
    executed = sum(1 for _, s, _, _ in results
                   if s in ("PASS", "FAIL", "ERROR", "ADVISORY", "ADVISORY-ERROR"))
    skipped = sum(1 for _, s, _, _ in results if s == "SKIPPED")
    blocked = sum(1 for _, s, _, _ in results if s in ("MISSING-DEP", "ADVISORY-DEP"))
    assert executed + skipped + blocked == len(CHECKS), "a check fell out of the summary"
    # Three disjoint buckets that sum to the total, then failures in their own sentence. `failed` is
    # not a bucket: it overlaps all three (a gating check blocked on a missing dependency is both), and
    # `unlisted_suites` is in it without being a check at all. Listed as a fourth peer it read as a
    # fourth bucket — `6 + 7 + 1 + 1` against 14 checks, one too many. Attached with "of which" it read
    # as a subset of the *nearest* bucket, which produced the flat contradiction
    # "0 blocked on a missing dependency, of which 1 failed". Both spellings were trying to avoid a
    # second sentence; the second sentence is the fix.
    print(f"\n{len(CHECKS)} checks: {executed} executed, {skipped} skipped, "
          f"{blocked} blocked on a missing dependency."
          + (f" {len(failures)} failed (a count across those buckets, not a fourth one)"
             if failures else " Nothing failed.")
          + (f" {len(advisory_failures)} advisory failure(s): "
             f"{', '.join(advisory_failures)}" if advisory_failures else "")
          + (f" {len(tool_errors)} produced no verdict: {', '.join(tool_errors)}"
             if tool_errors else ""))

    # Before `failures`, and deliberately: a run with both a real failure and a check that could not
    # run is not a clean verdict on the change, so the tool error is the honest answer. Reporting exit 1
    # there would tell a reader the gate reached a conclusion it did not reach.
    if tool_errors:
        print(f"\nNO VERDICT: {', '.join(tool_errors)}\n"
              "These checks did not run to completion — a signal kill (OOM is the usual cause) or an "
              "interpreter that could not start. Exit 2 says so: this is not a verdict on the change, "
              f"and it is not the same answer as a failure."
              + (f" Also failing: {', '.join(failures)}." if failures else ""))
        return 2
    if failures:
        print(f"\nFAILED: {', '.join(failures)}")
        return 1
    print("\nAll selected gating checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
