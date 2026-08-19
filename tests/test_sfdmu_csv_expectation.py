#!/usr/bin/env python3
"""Does `validate_sfdmu_v5_datasets.py` expect a root CSV exactly where one is owed?

The root-CSV check used to fire unconditionally, which made the validator permanently red on
two shapes that correctly have no file at the plan root (`#264-51` / pack 123):

  * `operation: Readonly` — the records are queried from the *target org*, so there is no
    source file to read. The wrong fix is an empty CSV; the right one is not to ask.
  * a per-pass override — the file lives at `objectset_source/object-set-N/<Object>.csv` and
    is validated there. The root path is an *alternative* location, not an extra requirement.

A permanently-red validator is worse than none: it trains readers to ignore the only
automated check this repo has over its data plans, which is how the seven
`mfg-multicurrency` findings survived. So narrowing it is the point — but narrowing a check
is also how a check quietly stops working, and the two gates are only correct while each
stays conditional on its own reason. These cases pin that: an Upsert object with no CSV
*anywhere* must still fail Critical, including when some *other* object has a per-pass file.

Run: `python tests/test_sfdmu_csv_expectation.py` (offline, no org).
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
VALIDATOR = REPO / "scripts" / "validate_sfdmu_v5_datasets.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("sfdmu_validator", VALIDATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


V = load_validator()

UPSERT = {"query": "SELECT Id, Name FROM Widget__c", "operation": "Upsert", "externalId": "Name"}
READONLY = {"query": "SELECT Id, Name FROM Gadget__c", "operation": "Readonly", "externalId": "Name"}
HEADER = "Id,Name\n1,a\n"


def issues(passes, root_files=None, per_pass_files=None, severity=None):
    """Validate a synthetic plan and return its issue strings, optionally filtered by severity.

    `passes` is a list of objectSets, each a list of object configs, so a case can put the same
    object in more than one pass — the shape the whole per-pass question turns on.
    `per_pass_files` maps a 1-based pass number to `{filename: body}` under
    `objectset_source/object-set-N/`.

    Synthetic rather than a copy of a real plan: a fixture carved out of one passes or fails for
    reasons the case did not choose, which is how a control ends up vacuous.
    """
    with tempfile.TemporaryDirectory() as td:
        plan = pathlib.Path(td) / "plan"
        plan.mkdir()
        (plan / "export.json").write_text(json.dumps({"objectSets": [{"objects": p} for p in passes]}))
        for name, body in (root_files or {}).items():
            (plan / name).write_text(body)
        for pass_number, files in (per_pass_files or {}).items():
            d = plan / "objectset_source" / f"object-set-{pass_number}"
            d.mkdir(parents=True, exist_ok=True)
            for name, body in files.items():
                (d / name).write_text(body)
        result = V.SFDMUValidator(base_dir=str(plan.parent), verbose=False).validate_dataset(plan)
        return [f"{i.severity.value}/{i.object_name}: {i.message}" for i in result.issues
                if severity is None or i.severity == severity]


def fix_mode_writes(plan_body, root_files=None, per_pass_files=None, **fix_flags):
    """Run a fix mode over a synthetic plan and return the bytes of every CSV afterwards.

    The repo had no fix-mode coverage at all — nothing referenced `fix_headers` or
    `fix_composite_keys` — so a change to pass resolution could silently start or stop writing to a
    file. That is not hypothetical: normalizing flat plans made `--fix-headers` newly write into
    `objectset_source/object-set-1/` for a plan shape no shipped dataset happens to have, and
    both-bounds stopped it mutating an `object-set-0/` file it used to resolve against the last pass.
    """
    with tempfile.TemporaryDirectory() as td:
        plan = pathlib.Path(td) / "plan"
        plan.mkdir()
        (plan / "export.json").write_text(json.dumps(plan_body))
        for name, body in (root_files or {}).items():
            (plan / name).write_text(body)
        for pass_number, files in (per_pass_files or {}).items():
            d = plan / "objectset_source" / f"object-set-{pass_number}"
            d.mkdir(parents=True, exist_ok=True)
            for name, body in files.items():
                (d / name).write_text(body)
        # Through `validate_dataset`, which is what the CLI drives — the fix loop runs from there
        # when the flags are set, so this exercises the same path a `--fix-all` run takes.
        V.SFDMUValidator(base_dir=str(plan.parent), verbose=False, **fix_flags).validate_dataset(plan)
        return {p.relative_to(plan).as_posix(): p.read_bytes()
                for p in sorted(plan.rglob("*.csv"))}


def criticals(objects, root_files=None, per_pass_files=None):
    """Criticals for a single-pass plan — the common case, kept short."""
    return issues([objects], root_files,
                  {1: per_pass_files} if per_pass_files else None,
                  severity=V.Severity.CRITICAL)


def flat_plan(per_pass=None):
    """Criticals for a plan using the flat `objects` key rather than `objectSets`.

    Both older plans and hand-written ones use this shape, and it is the shape the three
    pass-resolving functions disagreed about. `per_pass` is keyed by directory number, so `{0: ...}`
    writes a literal `object-set-0/` — a name that maps to pass_index -1.
    """
    with tempfile.TemporaryDirectory() as td:
        plan = pathlib.Path(td) / "plan"
        plan.mkdir()
        (plan / "export.json").write_text(json.dumps({"objects": [UPSERT]}))
        for n, files in (per_pass or {}).items():
            d = plan / "objectset_source" / f"object-set-{n}"
            d.mkdir(parents=True, exist_ok=True)
            for name, body in files.items():
                (d / name).write_text(body)
        result = V.SFDMUValidator(base_dir=str(plan.parent), verbose=False).validate_dataset(plan)
        return [f"{i.object_name}: {i.message}" for i in result.issues
                if i.severity == V.Severity.CRITICAL]


CASES = [
    # (label, expect_critical, criticals)
    ("an Upsert object with no CSV anywhere still fails — the finding worth keeping",
     True, criticals([UPSERT])),
    ("an Upsert object with its root CSV present passes — control for the case above",
     False, criticals([UPSERT], {"Widget__c.csv": HEADER})),
    ("a Readonly object with no CSV is silent: it is queried from the target org",
     False, criticals([READONLY])),
    ("an Upsert object supplied per-pass is silent at the root: the file lives under "
     "objectset_source/ and is validated there",
     False, criticals([UPSERT], None, {"Widget__c.csv": HEADER})),
    # The gate keys on *this* object having a per-pass file, not on the plan having any. Keyed
    # on the plan, one override would excuse every missing CSV in it.
    #
    # The other object must be one the plan DECLARES in that pass. Written with an undeclared
    # `Unrelated__c`, this passed without ever constructing plan-wide coverage — the override was
    # discarded upstream, so the condition the label refutes never existed, and mutating the gate
    # to key on the plan left the case green.
    ("an Upsert object whose per-pass CSV is absent still fails, even though a *different* "
     "object in the same pass has one",
     True, issues([[UPSERT, dict(UPSERT, query="SELECT Id, Name FROM Other__c")]], None,
                  {1: {"Other__c.csv": HEADER}}, severity=V.Severity.CRITICAL)),
    # `_parse_object_configs` keeps the first declaration, so a Readonly first pass decides the
    # merged operation. No plan in the repo declares that shape
    # (surveyed: 0 of the 76 export.json files under datasets/sfdmu, a superset of the 39 the
    # validator scans — it skips test/ and *.bak via _SKIP_SEGMENTS), and if one appears the gate
    # would silence a writable pass — so pin it now.
    # Two objectSets, not two entries in one — the label says "pass" and the case has to mean it.
    # Written as a single set, this passed for the wrong reason and left the multi-pass path it
    # advertises untested.
    ("a Readonly first pass followed by an Upsert pass for the same object is NOT silenced",
     True, issues([[READONLY], [dict(UPSERT, query="SELECT Id, Name FROM Gadget__c")]],
                  severity=V.Severity.CRITICAL)),
    # Same merged-config trap, different key: `excluded` is also read from the first declaration.
    ("an object excluded in pass 1 but Upsert in pass 2, with no CSV, still fails",
     True, issues([[dict(UPSERT, excluded=True)], [UPSERT]], severity=V.Severity.CRITICAL)),
    # The converse, and the direction a surviving mutation showed was unpinned: dropping the
    # `excluded` skip in _writable_passes_by_object makes pass 2 count as writable, so the pass-1
    # override no longer covers every writable pass and a spurious Critical appears.
    ("an object Upsert in pass 1 with an override, excluded in pass 2, owes nothing",
     False, issues([[UPSERT], [dict(UPSERT, excluded=True)]], None,
                   {1: {"Widget__c.csv": HEADER}}, severity=V.Severity.CRITICAL)),
    # A flat `objects` plan (no objectSets) with per-pass CSVs: three functions disagreed about
    # normalizing that shape, so the CSVs were silently discarded behind a WARN suppressed at
    # default verbosity. And `object-set-0` maps to pass_index -1, which an upper-bound-only check
    # let through into a negative index — an IndexError aborting the whole run rather than
    # reporting the one bad plan.
    ("a flat objects-key plan supplies its CSV per-pass and owes nothing at the root",
     False, flat_plan(per_pass={1: {"Widget__c.csv": HEADER}})),
    ("a flat objects-key plan with an object-set-0 directory does not treat it as coverage",
     True, flat_plan(per_pass={0: {"Widget__c.csv": HEADER}})),
    # A malformed plan must be reported, not crash the run — `.lower()` on a non-string aborts
    # every plan after it, which converts one bad plan into no validation at all.
    ("a non-string operation does not abort the run",
     False, issues([[{"query": "SELECT Id FROM Widget__c", "operation": True, "externalId": "Name"}]],
                   {"Widget__c.csv": HEADER}, severity=V.Severity.CRITICAL)),

    # ---- the shape that shipped broken, and the reason it shipped: nothing modelled a writable
    # pass with no override. This is `BillingPolicy` in qb/en-US/qb-billing (Upsert in pass 1,
    # Update in pass 3, override only for pass 3) and 15 other objects across 7 scanned plans — 11 of
    # them in the 5 plans cumulusci.yml wires.
    # Keyed on the object name, pass 1's root CSV stops being checked and the plan reports PASS
    # with it deleted — verified against the real plan, not only here.
    ("an object writable in two passes with an override for only ONE still owes its root CSV",
     True, issues([[UPSERT], [dict(UPSERT, operation="Update")]], None,
                  {2: {"Widget__c.csv": HEADER}}, severity=V.Severity.CRITICAL)),
    ("...and is silent once EVERY writable pass is supplied per-pass",
     False, issues([[UPSERT], [dict(UPSERT, operation="Update")]], None,
                   {1: {"Widget__c.csv": HEADER}, 2: {"Widget__c.csv": HEADER}},
                   severity=V.Severity.CRITICAL)),
    # Relabelled to what it proves. It previously claimed to pin a filter against misfiled
    # overrides; it passed on pass arithmetic alone and the filter turned out to be inert — a
    # coverage index cancels only its own pass, which is the property below and the reason no
    # filter is needed.
    ("a coverage index cancels only its own pass, so an override for a pass that does not declare "
     "the object leaves the declaring pass owing its root CSV",
     True, issues([[READONLY], [UPSERT]], None, {1: {"Widget__c.csv": HEADER}},
                  severity=V.Severity.CRITICAL)),
]

# What SFDMU can actually resolve, which is not what the first version of this check assumed.
# `ScriptLoader._resolveOperation` trims and case-folds; `ScriptObject.getOperation` does neither,
# and reading the wrong one made the repo's nine `"ReadOnly"` declarations look like defects. These
# cases pin the rule to the loader, so the next reader cannot re-derive it from the other function.
OPERATION_RESOLUTION = [
    ("a case variant SFDMU resolves is accepted — 'ReadOnly' appears 9 times in this repo",
     False, [i for i in issues([[dict(READONLY, operation="ReadOnly")]], {"Gadget__c.csv": HEADER})
             if "resolve" in i]),
    ("...and so is a whitespace-padded value, which the loader trims",
     False, [i for i in issues([[dict(READONLY, operation=" Readonly ")]], {"Gadget__c.csv": HEADER})
             if "resolve" in i]),
    ("a word outside the enum is reported: SFDMU drops the declaration and silently uses its "
     "default operation instead",
     True, [i for i in issues([[dict(UPSERT, operation="Upser")]], {"Widget__c.csv": HEADER})
            if "resolve" in i]),
    ("a non-string is reported rather than crashing the run",
     True, [i for i in issues([[dict(UPSERT, operation=True)]], {"Widget__c.csv": HEADER})
            if "resolve" in i]),
    ("an absent operation is legal — SFDMU applies its own default",
     False, [i for i in issues([[{"query": "SELECT Id, Name FROM Widget__c", "externalId": "Name"}]],
                               {"Widget__c.csv": HEADER}) if "resolve" in i]),
]

# Fix modes had zero coverage anywhere in the repo, which is how a pass-resolution change could
# start or stop writing to a file with nothing to notice.
FIX_MODES = [
    ("--fix-headers writes a header into a flat plan's object-set-1 CSV, a file the pre-normalization "
     "version left untouched",
     True, [n for n, b in fix_mode_writes(
         {"apiVersion": "68.0", "objects": [UPSERT]}, {"Widget__c.csv": HEADER},
         {1: {"Widget__c.csv": ""}}, fix_headers=True).items()
         if n.endswith("object-set-1/Widget__c.csv") and b.strip()]),
    ("--fix-headers does NOT write into an object-set-0 directory, which maps to no pass and which "
     "an upper-bound-only check resolved against the last one",
     False, [n for n, b in fix_mode_writes(
         {"objectSets": [{"objects": [UPSERT]}, {"objects": [UPSERT]}]}, {"Widget__c.csv": HEADER},
         {0: {"Widget__c.csv": ""}}, fix_headers=True).items()
         if "object-set-0" in n and b.strip()]),
    ("--dry-run writes nothing",
     False, [n for n, b in fix_mode_writes(
         {"objectSets": [{"objects": [UPSERT]}]}, {"Widget__c.csv": ""}, None,
         fix_headers=True, dry_run=True).items() if b.strip()]),
    # The directory that maps to no pass is now a finding, not just a WARN suppressed at default
    # verbosity — before this, a mistyped name meant every CSV under it was silently never read.
    ("an object-set-0 directory is REPORTED, so a mistyped directory name is not invisible",
     True, [i for i in issues([[UPSERT]], {"Widget__c.csv": HEADER}, {0: {"Widget__c.csv": HEADER}})
            if "maps to no pass" in i]),
]

# Pins the premise the exemption rests on: that a per-pass CSV is actually validated where it
# lives. Deleting per-pass validation outright left the six cases above green, because they only
# assert on the *root* check — the exemption would have degraded to a blanket pass in silence.
PER_PASS_IS_VALIDATED = [
    ("an EMPTY per-pass CSV is reported, so the exemption rests on real validation and not on "
     "the file merely existing",
     True, [i for i in issues([[UPSERT]], None, {1: {"Widget__c.csv": ""}})
            if "empty" in i.lower()]),
    # `object-set-0` maps to pass_index -1. An upper-bound-only check (`pass_index >= len`) admits
    # it, and the negative index then resolves to the LAST pass — so a misnamed directory is
    # silently attributed to a real pass, and the per-pass loop reports the object as missing from
    # "pass 0". Pinning the absence of that phantom report is the only externally visible
    # difference the bounds fix makes, now that normalizing flat plans removed the IndexError it
    # also used to cause. Known gap, deliberately not fixed here: a directory that maps to no pass
    # still produces only a WARN, suppressed at default verbosity, rather than a finding.
    ("an object-set-0 directory is not silently attributed to the last pass",
     False, [i for i in issues([[UPSERT]], {"Widget__c.csv": HEADER}, {0: {"Widget__c.csv": HEADER}})
             if "no matching object" in i]),
]


"""Same object, `Readonly` in pass 1 and `Upsert` with a composite key in pass 2."""
_RO_FIRST = {"query": "SELECT Id, Name FROM Widget__c", "operation": "Readonly", "externalId": "Name"}
_UP_SECOND = {"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
              "externalId": "Name;Code"}

MERGED_CONFIG = [
    # `_parse_object_configs` keeps an object's FIRST declaration, so every check reading the merged
    # config validated pass 1 and exempted passes 2..n. The root file is read by pass 2 here, whose
    # composite key needs a `$$Name$Code` column; against pass 1's config a CSV carrying only `Name`
    # passed. This is the third instance of the same trap in this file (`operation` and `excluded`
    # were the first two), which is why the per-pass view is now a primitive.
    ("a pass-2 composite key is required of the root CSV, not just pass 1's simple key",
     True, [i for i in issues([[_RO_FIRST], [_UP_SECOND]], {"Widget__c.csv": "Name\nwidget-a\n"})
            if "composite key column" in i]),
    # `apiVersion` is filtered rather than supplied: `issues()` writes a minimal plan without one, so
    # an unfiltered control asserts "no findings at all" and fails on an unrelated High — a control
    # that passes for the wrong reason in one direction and fails for the wrong reason in the other.
    ("...and is silent when that column is present — control for the case above",
     False, [i for i in issues([[_RO_FIRST], [_UP_SECOND]],
                               {"Widget__c.csv": "$$Name$Code,Name,Code\nwidget-a;c1,widget-a,c1\n"})
             if "apiVersion" not in i]),
    # The guard on the fix's own blast radius, in the direction that actually bit. Applying the
    # externalId/SELECT-coverage check to declarations that do *not* read the root file reported 241
    # spurious High findings on correct plans. A Readonly later pass is the clearest case: it reads
    # nothing from a file, and commonly carries a narrow SELECT with an inherited composite key, so
    # it must contribute no coverage finding. (The blunt guard on the whole 241 is the live-tree
    # baseline below — a synthetic cannot stand in for 39 real plans, and should not pretend to.)
    ("a Readonly later pass with a narrow SELECT contributes no externalId coverage finding",
     False, [i for i in issues(
         [[{"query": "SELECT Id, Name, Code FROM Widget__c", "operation": "Upsert",
            "externalId": "Name;Code"}],
          [{"query": "SELECT Id FROM Widget__c", "operation": "Readonly", "externalId": "Name;Code"}]],
         {"Widget__c.csv": "$$Name$Code,Name,Code\nwidget-a;c1,widget-a,c1\n"})
         if "not found in query SELECT clause" in i]),
    # And the reason a raw declaration cannot be substituted for a normalized one: the checks read
    # derived keys (`fields`, the parsed SELECT), not the raw JSON. Passing raw declarations made
    # `fields` empty and every externalId component read as absent — the mechanism behind those 241.
    ("per-pass configs carry the derived `fields` key the checks actually read",
     True, [k for k in V.SFDMUValidator(base_dir=".")._all_pass_configs(
         {"objectSets": [{"objects": [_UP_SECOND]}]})["Widget__c"][0] if k == "fields"]),
]


def live_baseline():
    """The validator's findings on the real tree, by severity.

    Several files state this baseline so a reader can tell a regression from the known state. The
    set is **discovered** by `baseline_sites()` below rather than listed here, because listing it
    was wrong twice: "four documents" was written while adding two more, and the recount to "seven
    sites across five files" missed three (`AGENTS.md`'s checklist item, `pr_gate.py`'s module
    docstring, and `sfdmu-data-plans/SKILL.md`, whose file the list omitted entirely) and
    double-counted one file's pair while counting another's as one. A hand-maintained list of the
    places a number must be swept is itself a number that must be swept.

    An unpinned number in prose drifts — `pr_gate.py`'s advisory note said "9 findings ... are
    validator false positives" for one commit past the point where that became false, while the
    adjacent `678` figure stayed correct because a test forces it. This is that forcing function
    for the baseline: when pack 110 deletes `mfg-multicurrency` the count goes to zero, this fails,
    and every site gets updated in the same change rather than a later one.
    """
    validator = V.SFDMUValidator(base_dir=str(REPO), verbose=False)
    by_sev, plans = {}, set()
    for plan in validator.find_sfdmu_datasets():
        res = validator.validate_dataset(plan)
        for issue in res.issues:
            if issue.severity in (V.Severity.CRITICAL, V.Severity.HIGH):
                by_sev[issue.severity.value] = by_sev.get(issue.severity.value, 0) + 1
                plans.add(res.dataset_name)
    return by_sev, plans


# The count words the repo actually writes, plus every neighbour of 7 — a wrong claim is most
# likely to be off by one, and a detector that only knows the right word cannot see a wrong one.
_WORD_COUNTS = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
                "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}


def baseline_sites():
    """Every tracked file that states the High-findings baseline, with the value each one claims.

    Discovery is deliberately **independent of the expected number**, and that is the whole design.
    An earlier version matched only `7`/`seven`, which inverted the guard: editing a site to say
    "8 High" removed it from the result set rather than failing, and the only assertion downstream
    was that the set is non-empty — so the one edit the sweep exists to catch was the one edit it
    could not see. Matching *any* count and validating the captured values afterwards is what makes
    a wrong claim a failure instead of a disappearance.

    Anchored on the nouns the repo attaches the count to. That list is wider than it looks
    necessary, and deliberately: a first version matched only `High` and missed
    `sfdmu-data-plans/SKILL.md`, which spells the same baseline "7 zero-byte `Upsert` CSVs" —
    reproducing, in the detector, the exact omission the detector exists to prevent. `findings` is
    *not* in the list, though every real site does end "…High findings": as a standalone noun it
    also matches unrelated review narration ("five of its seven findings"), and a sweep set with a
    false member sends a reader to edit a line that must not change. A noun the repo has not used
    yet is the remaining gap in the other direction; that is why the assertion below prints the set
    rather than trusting it silently.

    Deliberately *not* keyed on `mfg-multicurrency` alone: `plan-dependency-graph.md` names the
    plan and its pack-110 removal without quoting a count, so it needs no edit when the count
    changes and including it would send a reader to a file with nothing to sweep.

    Returns `{path: [(line_number, claimed_count), ...]}`.
    """
    counts = "|".join(_WORD_COUNTS)
    pattern = re.compile(
        rf"\b(\d+|{counts})\b[\s\-*`]*(?:high|zero-byte)", re.IGNORECASE)
    roots = ["AGENTS.md", "scripts/ai", "docs/features", ".cursor/skills", "tests"]
    sites = {}
    for root in roots:
        base = REPO / root
        paths = [base] if base.is_file() else [
            p for p in base.rglob("*") if p.suffix in (".md", ".py") and p.is_file()]
        for path in paths:
            if path.name == pathlib.Path(__file__).name:
                continue  # this file describes the mechanism; it is not a site to sweep
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError, OSError):
                continue
            hits = []
            for n, line in enumerate(lines, 1):
                for raw in pattern.findall(line):
                    token = raw.lower()
                    hits.append((n, int(token) if token.isdigit() else _WORD_COUNTS.get(token)))
            if hits:
                sites[path.relative_to(REPO).as_posix()] = hits
    return sites


_sev, _plans = live_baseline()
_sites = baseline_sites()
BASELINE = [
    ("the live tree has 0 Critical findings — the two pack 123 fixed were false positives",
     False, [f"{k}={v}" for k, v in _sev.items() if k == V.Severity.CRITICAL.value]),
    ("the live tree has exactly 7 High findings, the documented baseline",
     True, [f"High={_sev.get(V.Severity.HIGH.value, 0)}"]
           if _sev.get(V.Severity.HIGH.value, 0) == 7 else []),
    # The exact dataset name, not a substring. `"multicurrency" in p` also accepts a restored
    # `q3-multicurrency` — the very plan `dab545ab` deleted for carrying zero-byte CSVs of its own —
    # so the loose form would report the documentation green while the findings had moved to a
    # different plan than every one of those documents names.
    ("all 7 are in mfg/en-US/mfg-multicurrency exactly, so the docs name the plan that has them",
     True, sorted(_plans) if _plans == {"mfg/en-US/mfg-multicurrency"} else []),
    # Not an assertion about *how many* sites there are — that number went stale twice as prose and
    # would go stale again as a literal here. It asserts that the sweep set is non-empty and that
    # every site claims the real baseline, and prints them, so a failure arrives with the list of
    # files to edit attached.
    (f"the baseline is stated in {sum(len(v) for v in _sites.values())} place(s) across "
     f"{len(_sites)} file(s), swept together: "
     + ", ".join(f"{f}:{','.join(str(n) for n, _ in ls)}" for f, ls in sorted(_sites.items())),
     True, sorted(_sites)),
    (f"...and every one of them claims {_sev.get(V.Severity.HIGH.value, 0)}, the live High count",
     True, [f"{f}:{n}={c}" for f, ls in sorted(_sites.items()) for n, c in ls]
           if _sites and all(c == _sev.get(V.Severity.HIGH.value, 0)
                             for ls in _sites.values() for _, c in ls) else []),
]


def own_case_count_is_quoted_correctly(total):
    """`scripts/ai/README.md` quotes this suite's size; pin it where the size is known.

    It went stale twice in a row — two commits each raised the suite and each said the new number
    in its own message while leaving the sentence reading 13. The adjacent `680` in that same
    paragraph never drifted, because a test forces it, which is the whole argument. Pinned here
    rather than in `tests/test_pr_gate.py` next to the other two figures: this suite already knows
    its own total, so the check costs nothing, while over there it would mean importing this module
    and paying for a full validator run to learn a number.
    """
    quoted = re.search(r"pins both\s*\n?directions in (\d+) cases",
                       (REPO / "scripts/ai/README.md").read_text(encoding="utf-8"))
    if quoted is None:
        return ["the sentence in scripts/ai/README.md quoting this suite's size is gone"]
    return [] if int(quoted.group(1)) == total else [f"README says {quoted.group(1)}, suite has {total}"]


def main() -> int:
    failures = []
    all_cases = [("root-CSV expectation", CASES),
                 ("per-pass validation actually runs", PER_PASS_IS_VALIDATED),
                 ("operation values SFDMU can and cannot resolve", OPERATION_RESOLUTION),
                 ("fix modes write where they should and nowhere else", FIX_MODES),
                 ("later passes are validated, not just the merged first declaration", MERGED_CONFIG),
                 ("the documented live baseline still holds", BASELINE)]
    # +1 for the self-count check appended below, which needs the total it asserts against.
    total = sum(len(c) for _, c in all_cases) + 1
    all_cases.append(("this suite's own size, as quoted in prose", [
        (f"scripts/ai/README.md says this suite pins both directions in {total} cases",
         False, own_case_count_is_quoted_correctly(total))]))
    print("=" * 100)
    for group, cases in all_cases:
        print(f"-- {group}")
        for label, expect_finding, found in cases:
            ok = bool(found) == expect_finding
            if not ok:
                failures.append(label)
            print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
            if not ok:
                print(f"         expected a finding={expect_finding}, got={found or 'none'}")
    print("=" * 100)
    if failures:
        for label in failures:
            print(f"FAILED: {label}")
        print(f"\n{total - len(failures)}/{total} checks passed")
        return 1
    print(f"{total}/{total} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
