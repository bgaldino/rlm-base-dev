#!/usr/bin/env python3
"""Audit the SFDMU data plans against a release's object describe (todo 321).

A plan that loads isn't audited for a release: it can select a field the release removed, carry a
value a restricted picklist no longer allows, write a field the platform won't write (so the value
is silently dropped), or leave out a field the release made required. This checks every tracked
plan's written declarations against `sobject describe`, from a live org or from a saved snapshot.

  python scripts/audit_data_plans.py snapshot --target-org <sf alias or username> \\
      [--merge scripts/erd/schema_diff/<release>-plan-describe.json] --out <snapshot.json>
  python scripts/audit_data_plans.py audit [--target-org <sf alias> | --snapshot <snapshot.json>] \\
      [--plans qb/en-US ...] [--release-diff <diff.json>] [--out report.md] [--json]

`snapshot` and a live `audit` are read-only. Without `--target-org` or `--snapshot`, `audit` reads
the committed snapshot for the active release (`salesforce_release_active` in
`.claude/skill-manifest.yml`), which is how `pr_gate` runs it. `--merge` adds another org's
objects, fields and picklist values to an existing snapshot, for objects one org shape lacks.

Gating findings (each fails the run unless `KNOWN_FINDINGS` lists it, with its reason):
  unknown-field  the query selects, or the externalId names, a field the object doesn't have, or a
                 relationship path (any depth, followed through the snapshot) that doesn't resolve
  picklist       a value outside a restricted picklist's active values (CurrencyIsoCode is the
                 org's currency set, so it's skipped)
  required       a creating declaration leaves out, or leaves blank on the rows it creates, a
                 field that is createable, not nillable and not defaulted on create. An Upsert row
                 whose externalId value an earlier creating pass already created (a row the
                 platform rejects for a required field or restricted picklist value isn't) only
                 patches it, and a repeat of a key in one pass counts once; Insert rows always create
  object-missing the object isn't in the describe, so its declarations aren't audited (a feature
                 the org lacks); gating so an unaudited object is triaged, not silently passed
Informational (reported, never gating):
  dead-columns     CSV values in fields that are neither createable nor updateable, so they never
                   land: usually derived fields an extraction copied, sometimes a value someone
                   meant to set (a key field used only for matching is left out)
  undefined-value  a value outside an unrestricted picklist's defined values (it loads)
  unwritten        writable fields no plan writes, per object, marked when the release diff
                   says the release added them
  release-values   picklist values the release added to a field a plan writes

Exit codes: 0 = no new gating finding · 1 = findings (new, or stale `KNOWN_FINDINGS` entries)
· 2 = tool error (no snapshot for the active release, or one recorded for another release or API
version, a report that can't be written, a `--plans` prefix that matches no plan, or a
`sourceRecordsFilter` the audit can't evaluate).
Only required-field and restricted-picklist rejections are modeled; a row the platform rejects for
another reason (length, lookup target, a validation rule) is still treated as created.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "scripts" / "ai"))
import check_sfdmu_layering as layering  # noqa: E402
import sfdmu_export  # noqa: E402
from scripts.decision_tables._client import DecisionTableClientError, connect_request  # noqa: E402

SFDMU = REPO / "datasets" / "sfdmu"
SCHEMA_DIR = REPO / "scripts" / "erd" / "schema_diff"
MANIFEST = REPO / ".claude" / "skill-manifest.yml"
GATING = ("unknown-field", "picklist", "required", "object-missing")
# On every object, so a plan naming it needs no describe entry. `LastActivityDate` and the like are
# on some objects only, so they are checked against the describe.
ALWAYS_PRESENT = frozenset({"Id"})
# Fields the platform sets itself, never a plan's to write: left out of the dead-column, required
# and unwritten reports.
SYSTEM_FIELDS = ALWAYS_PRESENT | frozenset({
    "IsDeleted", "CreatedDate", "CreatedById", "LastModifiedDate", "LastModifiedById",
    "SystemModstamp", "LastViewedDate", "LastReferencedDate", "LastActivityDate"})
# Writable on almost every object and set by the platform or the org's currency, so listing them
# as fields "no plan writes" would bury the ones worth reviewing.
UNWRITTEN_NOISE = frozenset({"OwnerId", "CurrencyIsoCode"})
DESCRIBE_KEYS = ("type", "createable", "updateable", "nillable", "defaultedOnCreate",
                 "calculated", "autoNumber", "restrictedPicklist", "relationshipName", "referenceTo")

# A `picklist` entry stands only for the values triaged here: a different bad value in the same
# field is a new finding, and the entry goes stale once the triaged ones are gone.
TRIAGED_VALUES: Dict[Tuple[str, str, str, str], frozenset] = {
    ("qb/en-US/qb-clm", "ObjectStateValue", "picklist", "ReferenceRecordAccessType"):
        frozenset({"ReadOnly"}),
}

# (plan, object, check, field): why it stands. Each entry is a finding the 264 audit triaged and
# kept (todo 321); a fix removes its entry, and an entry that no longer matches is reported stale.
KNOWN_FINDINGS: Dict[Tuple[str, str, str, str], str] = {
    # AttributePicklist.Code is a B2B Commerce field, absent from Revenue Cloud orgs (todo 319);
    # SFDMU drops it, so the plans load. Drop the column with the next pcm change (todo 345).
    **{(plan, "AttributePicklist", "unknown-field", "Code"):
       "B2B Commerce field, absent on RLM orgs; SFDMU drops it (todo 345)"
       for plan in ("qb/en-US/qb-pcm", "qb/ja/qb-pcm", "q3/en-US/q3-pcm", "mfg/en-US/mfg-pcm")},
    # Deployed by deploy_post_prm, which runs only with prm_exp_bundle and tso (todo 345).
    **{(plan, "ChannelProgramLevel", "unknown-field", field):
       "deployed only with prm_exp_bundle and tso; without them SFDMU drops the column (todo 345)"
       for plan in ("qb/en-US/qb-prm", "qb/en-US/qb-prm-pricing")
       for field in ("RLM_Deal_Expiration_Days__c", "RLM_Minimum_Deal_Size__c")},
    # qb-clm fails to load with clm_data on (120 rows across 7 objects rejected on a fresh 264
    # build, todo 346).
    ("qb/en-US/qb-clm", "DocumentClauseSet", "required", "Category"):
        "all 20 rows rejected on 264 with clm_data on (todo 346)",
    ("qb/en-US/qb-clm", "ObjectStateValue", "picklist", "ReferenceRecordAccessType"):
        "`ReadOnly` is not a value (`Read Only` is); fails with clm_data on (todo 346)",
    # qb-accounting has no load task yet; its BillingBatchFilterCriteria key is a copy-paste of the
    # previous object's (todo 341, which makes the plan loadable with portable keys).
    ("qb/en-US/qb-accounting", "BillingBatchFilterCriteria", "unknown-field", "JournalEntryRuleName"):
        "externalId copied from GeneralLedgerJrnlEntryRule; not a field here; no load task (todo 341)",
    # Not on a qb org: AAF and rebates are mfg features. Audit them against a snapshot merged from
    # an org that has them (todo 332 rebuilds mfg).
    **{(plan, obj, "object-missing", ""):
       "mfg-only object, not in the qb-org describe; merge a snapshot from an mfg org (todo 332)"
       for plan, objs in (("mfg/en-US/mfg-aaf", ("AdvAccountForecastFact", "AdvAcctForecastSetPartner")),
                          ("mfg/en-US/mfg-rebates", ("ProgramRebateType", "ProgramRebateTypeBenefit",
                                                     "RebateProgram", "RebateProgramMember",
                                                     "RebateProgramPayoutPeriod")))
       for obj in objs},
    # mfg is rebuilt in the mfg-264-series; these go to its rebase list (todo 332).
    ("mfg/en-US/mfg-guidedselling", "AssessmentQuestion", "unknown-field", "ShouldExcludeFromMetadata"):
        "not on a 264 org (absent from the 262 and 264 ERD snapshots too); mfg rebase (todo 332)",
    ("mfg/en-US/mfg-guidedselling", "AssessmentQuestion", "unknown-field", "ShouldHideInDesigner"):
        "not on a 264 org (absent from the 262 and 264 ERD snapshots too); mfg rebase (todo 332)",
    ("mfg/en-US/mfg-guidedselling", "AssessmentQuestionVersion", "unknown-field", "ExternalAsmtContentVersion"):
        "not on a 264 org (absent from the 262 and 264 ERD snapshots too); mfg rebase (todo 332)",
    ("mfg/en-US/mfg-guidedselling", "OmniProcessElement", "required", "OmniProcessId"):
        "4 rows have #N/A for OmniProcess.UniqueName (an extraction gap); mfg rebase (todo 332)",
}


def _manifest_value(pattern: str, name: str, manifest: Path) -> str:
    m = re.search(pattern, manifest.read_text(encoding="utf-8"), re.M)
    if not m:
        raise ValueError(f"no {name} in {manifest}")
    return m.group(1)


def active_release(manifest: Path = MANIFEST) -> str:
    return _manifest_value(r'^salesforce_release_active:\s*"?(\d+)"?', "salesforce_release_active",
                           manifest)


def default_snapshot(release: str) -> Path:
    return SCHEMA_DIR / f"{release}-plan-describe.json"


def check_snapshot_metadata(snap: Dict[str, Any], path: Any, release: str, api_version: str) -> None:
    """Refuse a snapshot not captured for the active release at the active API version: a stale
    schema would pass a plan the release would break, or fail one it fixed."""
    objects = snap.get("objects") if isinstance(snap, dict) else None
    if not isinstance(objects, dict) or not all(
            isinstance(o, dict) and isinstance(o.get("fields"), dict) for o in objects.values()):
        raise ValueError(f"{path} isn't a describe snapshot (`objects` must map each object to its "
                         f"`fields`); recapture it (`snapshot`)")
    meta = snap.get("metadata") or {}
    for key, want in (("release", release), ("api_version", api_version)):
        if meta.get(key) != want:
            raise ValueError(f"{path} records {key} {meta.get(key)!r}, not the active {want!r}; "
                             f"recapture it (`snapshot`) before auditing against it")


def default_release_diff(release: str) -> Optional[Path]:
    found = sorted(SCHEMA_DIR.glob(f"*-vs-{release}-diff.json"))
    return found[-1] if found else None


# --------------------------------------------------------------------------- plans


def plan_objects(root: Path = SFDMU, prefixes: Iterable[str] = ()) -> List[str]:
    """Every object any tracked plan (under `prefixes`, when given) declares."""
    objs = set()
    for plan in selected_plans(root, prefixes):
        export = json.loads((plan / "export.json").read_text(encoding="utf-8"))
        objs.update(obj for _, _, obj in layering.declarations(export))
    return sorted(objs)


def selected_plans(root: Path, prefixes: Iterable[str]) -> List[Path]:
    prefixes = [p.strip("/") for p in prefixes]
    out = []
    hit = set()
    for plan in layering.plan_dirs(root):
        rel = plan.relative_to(root).as_posix()
        matched = [p for p in prefixes if rel == p or rel.startswith(p + "/")]
        if not prefixes or matched:
            out.append(plan)
            hit.update(matched)
    # A prefix that names no plan audits nothing for it and would pass; a typo must not.
    if unmatched := [p for p in prefixes if p not in hit]:
        raise ValueError(f"--plans {', '.join(unmatched)} matches no tracked plan under {root}")
    if not out:
        raise ValueError(f"no tracked plan under {root}; an audit of nothing would pass")
    return out


# --------------------------------------------------------------------------- describe


# Some picklists list org records by Id: DocumentClauseSet.Category's values are the org's
# categories (15-character Ids), and ProcedurePlanDefinitionVersion.ContextDefinition mixes the
# standard context names with custom definitions' 18-character Ids. Others list object names, some
# of them 15 or 18 alphanumerics (`Pricebook2Share`), so an 18-character Id needs its case
# checksum, and a 15-character one Id's shape: a 3-character key prefix, then a run of zeros
# (the pod and reserved characters) before the record number.
_ID18 = re.compile(r"^[a-zA-Z0-9]{15}[A-Z0-5]{3}$")
_ID15 = re.compile(r"^[a-zA-Z0-9]{3}[a-zA-Z0-9]{2}0{3,}[a-zA-Z0-9]+$")
_CHECKSUM = "ABCDEFGHIJKLMNOPQRSTUVWXYZ012345"


def _is_record_id(value: str) -> bool:
    """An 18-character Salesforce Id whose last three characters are the checksum of the case of
    the first fifteen (each encodes which of five characters are upper-case), or a 15-character
    one with an Id's zero run."""
    if len(value) == 15:
        return bool(_ID15.match(value)) and any(c.isdigit() for c in value[:3] + value[8:])
    if not _ID18.match(value):
        return False
    for i in range(3):
        chunk = value[i * 5:(i + 1) * 5]
        bits = sum(1 << j for j, c in enumerate(chunk) if "A" <= c <= "Z")
        if value[15 + i] != _CHECKSUM[bits]:
            return False
    return True


def compact_describe(describe: Dict[str, Any]) -> Dict[str, Any]:
    """The describe attributes the audit reads, by field: org-independent. A picklist with record
    Ids among its values (a list of org records) keeps only its other values and is marked
    `orgValues`, so the snapshot carries no org identity and the audit doesn't check values that
    differ per org."""
    fields = {}
    for f in describe.get("fields", []):
        entry = {k: f.get(k) for k in DESCRIBE_KEYS}
        if f.get("type") in ("picklist", "multipicklist"):
            values = [v["value"] for v in f.get("picklistValues", []) if v.get("active", True)]
            if any(_is_record_id(v) for v in values):
                entry["orgValues"] = True
                values = [v for v in values if not _is_record_id(v)]
            entry["values"] = sorted(values)
        fields[f["name"]] = entry
    return {"fields": fields}


def active_api_version(manifest: Path = MANIFEST) -> str:
    """`api_version_active` as `68.0`, the version the describe requests must use."""
    return _manifest_value(r'^api_version_active:\s*"?v?(\d+\.\d+)"?', "api_version_active", manifest)


def describe_org(target_org: str, objects: List[str], workers: int = 8,
                 api_version: Optional[str] = None) -> Dict[str, Any]:
    """{object: compact describe} for the objects the org has; a missing object is absent."""
    api_version = api_version or active_api_version()

    def one(obj: str):
        try:
            return obj, compact_describe(connect_request(
                "GET", f"sobjects/{obj}/describe", target_org=target_org,
                api_version=api_version))
        except DecisionTableClientError as exc:
            if "NOT_FOUND" in exc.error_codes or "INVALID_TYPE" in exc.error_codes:
                return obj, None
            raise
    with ThreadPoolExecutor(max_workers=workers) as pool:
        found = {o: d for o, d in pool.map(one, objects) if d is not None}
    if objects and not found:
        raise ValueError(f"the org returned no describe for any of {len(objects)} objects at API "
                         f"{api_version}: wrong alias, or an org older than that API version")
    return found


def merge_snapshots(base: Dict[str, Any], extra: Dict[str, Any]) -> Dict[str, Any]:
    """`base` plus `extra`'s objects, fields and picklist values; `base` wins on attributes."""
    merged = json.loads(json.dumps(base))
    for obj, desc in extra.items():
        target = merged.setdefault(obj, {"fields": {}})["fields"]
        for name, f in desc["fields"].items():
            if name not in target:
                target[name] = f
                continue
            if "values" in f:
                target[name]["values"] = sorted(set(target[name].get("values", [])) | set(f["values"]))
            if f.get("orgValues"):
                # Either org listing records by Id makes the field org-dependent.
                target[name]["orgValues"] = True
    return merged


# --------------------------------------------------------------------------- audit


def _field_of(header: str, fields: Dict[str, Any]) -> Optional[str]:
    """The object field a CSV column writes: itself, or the lookup a `Rel.X` column goes through."""
    if header.startswith("$$"):
        return None
    if "." not in header:
        header = header.partition("$")[0]  # `AssignedToId$User` is the field `AssignedToId`
        return header if header in fields else None
    rel = header.split(".", 1)[0].partition("$")[0]  # `Who$Contact.Name` is the lookup `Who`
    return next((n for n, f in fields.items() if f.get("relationshipName") == rel), None)


def _path_problem(obj: str, segs: List[str], snapshot: Dict[str, Any]) -> Optional[str]:
    """Why the field path `segs` (`Field` or `Rel.Field`, any depth) doesn't resolve from `obj`, or
    None when it does or can't be checked: a lookup's target missing from the snapshot is left
    unchecked. A segment `Rel$Type` is SFDMU's polymorphic lookup resolved through `Type`, so the rest
    is checked against that target only; without one, a polymorphic lookup resolves if any target in
    the snapshot has the rest. On the last segment `$Type` names the lookup field itself, which must reference it."""
    fields = snapshot[obj]["fields"]
    seg, _, typed = segs[0].partition("$")
    if len(segs) == 1:
        if seg not in fields:
            return None if seg in ALWAYS_PRESENT else f"{obj} has no field `{seg}`"
        targets = fields[seg].get("referenceTo") or []
        if typed and targets and typed.lower() not in (t.lower() for t in targets):
            return f"`{seg}` doesn't reference `{typed}`"
        return None
    f = next((f for f in fields.values() if f.get("relationshipName") == seg), None)
    if f is None:
        return f"{obj} has no relationship `{seg}`"
    wanted = f.get("referenceTo") or []
    if typed:
        wanted = [t for t in wanted if t.lower() == typed.lower()]  # object names ignore case
        if not wanted:
            return f"`{seg}` doesn't reference `{typed}`"
    targets = [t for t in wanted if t in snapshot]
    if not targets:
        return None
    problems = [_path_problem(t, segs[1:], snapshot) for t in targets]
    # A polymorphic lookup with a target the snapshot lacks may resolve there.
    return None if None in problems or len(targets) < len(wanted) else problems[0]


def _is_required(name: str, f: Dict[str, Any]) -> bool:
    return (bool(f.get("createable")) and not f.get("nillable") and not f.get("defaultedOnCreate")
            and f.get("type") != "boolean" and name not in SYSTEM_FIELDS)


def audit(snapshot: Dict[str, Any], root: Path = SFDMU, prefixes: Iterable[str] = (),
          release_diff: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """{"findings": [...], "info": {...}}; each finding is a dict with plan, object, check, field,
    detail. Gating checks are in `GATING`."""
    findings: List[Dict[str, Any]] = []
    missing: Dict[str, List[str]] = defaultdict(list)
    bad_filters: List[str] = []
    undefined: List[Dict[str, Any]] = []
    dead: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
    written_by_obj: Dict[str, set] = defaultdict(set)
    created_objs = set()

    def add(plan, obj, check, field, detail, values=None):
        findings.append({"plan": plan, "object": obj, "check": check, "field": field,
                         "detail": detail, **({"values": values} if values else {})})

    for plan in selected_plans(root, prefixes):
        rel = plan.relative_to(root).as_posix()
        export = json.loads((plan / "export.json").read_text(encoding="utf-8"))
        plan_keys: Dict[str, List[str]] = {}
        key_cache: Dict[Any, List[Any]] = {}
        created_rows: Dict[str, List[Any]] = {}  # object -> [(headers, rows)] of its creating passes
        for pass_idx, decl, obj in sorted(layering.declarations(export), key=lambda t: t[0]):
            if not layering.is_written(decl):
                continue
            desc = snapshot.get(obj)
            if desc is None:
                if rel not in missing[obj]:
                    missing[obj].append(rel)
                    # Unchecked is not clean: the object passes only by being triaged.
                    add(rel, obj, "object-missing", "",
                        f"{obj} isn't in the describe, so none of its declarations are audited")
                continue
            fields = desc["fields"]
            op = sfdmu_export.resolve_operation(decl.get("operation", "Readonly"))
            key_list = layering.key_parts(decl.get("externalId", ""))
            key = set(key_list)
            where = f"pass {pass_idx + 1}"

            # The fields the query selects, and the `externalId` components SFDMU queries whether or
            # not the query names them.
            checked = set()
            for sel, source in ([(s, "the query selects") for s in
                                 sfdmu_export.parse_select_fields(decl.get("query", ""))]
                                + [(k, "its externalId names") for k in key_list]):
                if sel.lower() == "all" or sel.startswith("$$"):
                    continue
                if sel in checked:
                    continue
                checked.add(sel)
                problem = _path_problem(obj, sel.split("."), snapshot)
                if problem:
                    add(rel, obj, "unknown-field", sel, f"{where}: {source} `{sel}`, but {problem}")

            headers, rows = layering.read_rows(layering.csv_for(plan, export, pass_idx, obj))
            try:
                keep = layering.row_filter(decl.get("sourceRecordsFilter"), headers)
            except layering.UnsupportedFilter as exc:
                # Not a skip: the declaration's rows would go unchecked and the audit pass. Every
                # one is collected and raised together once the plans are read.
                bad_filters.append(f"{rel} {where} {obj}: sourceRecordsFilter `{exc}` isn't a "
                                   f"form the audit evaluates (`[col] LIKE 'x'`, `col = 'x'`, "
                                   f"`col <> 'x'`)")
                continue
            if keep is not None:
                rows = [r for r in rows if keep(r)]
            columns = layering.written_columns(decl, headers)
            # A written `Rel.Field` column, and each part of a composite `Rel.$$A$B` one, reaches
            # a parent field the query's `RelId` doesn't name, so it is checked like a selected one.
            for col in columns:
                if col.startswith("$$"):  # the key column: its parts are the externalId's
                    continue
                for path in (layering.composite_names(col) or [col]):
                    if path in checked:
                        continue
                    checked.add(path)
                    problem = _path_problem(obj, path.split("."), snapshot)
                    if problem:
                        add(rel, obj, "unknown-field", path,
                            f"{where}: the CSV writes `{path}`, but {problem}")
            by_field: Dict[str, List[str]] = defaultdict(list)
            for col in columns:
                name = _field_of(col, fields)
                if name:
                    by_field[name].append(col)
            written_by_obj[obj].update(by_field)
            bad_picklist_rows = set()  # ids of rows the platform rejects for a restricted picklist value

            known = set()
            skipped = set()  # ids of rows a `skipExistingRecords` pass leaves alone
            if op in layering.CREATES:
                # Required fields are checked on the rows this pass creates. An Upsert row that
                # matches, on this declaration's externalId, a row an earlier creating pass of the
                # plan created is only patched here; an Insert never matches, so its rows are new.
                earlier = created_rows.setdefault(obj, [])
                if sfdmu_export.is_js_truthy(decl.get("deleteOldData")):
                    # The object's records are deleted before this pass loads, so an earlier
                    # pass's rows are gone and can't be what a later Upsert patches.
                    earlier.clear()
                    for k in [k for k in key_cache if k[0] == obj]:
                        del key_cache[k]
                # Only the columns this declaration writes reach the org; a CSV cell it doesn't select
                # can't identify a record.
                written = list(columns)
                # An undeclared externalId falls back to the plan's first creating key.
                first_key = plan_keys.setdefault(obj, key_list)
                ident_key = key_list or first_key
                if op != "insert" and ident_key:
                    # Earlier passes' rows read by this declaration's key, which they may not have
                    # been keyed on (`Code` then `Name;Code`); only passes not yet read are added.
                    seen = key_cache.setdefault((obj, tuple(ident_key)), [0, set()])
                    for h, rs in earlier[seen[0]:]:
                        for r in rs:
                            v = layering.row_values(ident_key, h, r)
                            # A pass that doesn't carry every key field can't be matched by it.
                            if all(f in v for f in ident_key) and (k := layering.key_of(v, ident_key)):
                                seen[1].add(k)
                    seen[0] = len(earlier)
                    known = set(seen[1])
                    if re.search(r"\bWHERE\b", decl.get("query") or "", re.I):
                        # SFDMU matches an Upsert row against the target records the query returns, so
                        # a WHERE limits which earlier rows it can patch. The audit doesn't evaluate
                        # the clause, so it assumes no match and checks the row as a create.
                        known = set()
                if (op == "upsert" and ident_key
                        and sfdmu_export.is_js_truthy(decl.get("skipExistingRecords"))):
                    # SFDMU leaves a matched record alone, so the row's values never load: they
                    # aren't value-checked, and a bad one there can't reject anything.
                    for r in rows:
                        v = layering.row_values(ident_key, written, r)
                        if all(f in v for f in ident_key) and layering.key_of(v, ident_key) in known:
                            skipped.add(id(r))

            for name, cols in sorted(by_field.items()):
                f = fields[name]
                filled = [r for r in rows if id(r) not in skipped
                          and any(not layering.is_null(r.get(c)) for c in cols)]
                if not filled:
                    continue
                if (not f.get("createable") and not f.get("updateable") and name not in key
                        and name not in SYSTEM_FIELDS):
                    if rel not in dead[obj][name]:
                        dead[obj][name].append(rel)
                    continue  # SFDMU drops the column, so its values are never loaded or checked
                if (f.get("type") in ("picklist", "multipicklist") and name != "CurrencyIsoCode"
                        and not f.get("orgValues")):
                    allowed = set(f.get("values") or [])
                    vals = {v for r in filled for c in cols if "." not in c
                            for v in ([x.strip() for x in (r.get(c) or "").split(";")]
                                      if f["type"] == "multipicklist" else [r.get(c) or ""])
                            if not layering.is_null(v)}
                    bad = sorted(vals - allowed)
                    if bad and f.get("restrictedPicklist"):
                        bad_picklist_rows.update(
                            id(r) for r in filled for c in cols if "." not in c
                            for v in ([x.strip() for x in (r.get(c) or "").split(";")]
                                      if f["type"] == "multipicklist" else [r.get(c) or ""])
                            if not layering.is_null(v) and v not in allowed)
                        add(rel, obj, "picklist", name,
                            f"{where}: {', '.join(bad)} not among the restricted picklist's active "
                            f"values ({', '.join(sorted(allowed)) or 'none'})", values=bad)
                    elif bad and allowed:
                        undefined.append({"plan": rel, "object": obj, "field": name, "values": bad})

            if op in layering.CREATES:
                created_objs.add(obj)
                required = [n for n, f in sorted(fields.items()) if _is_required(n, f)]

                def rejected_row(r):
                    # The platform rejects a create that lacks, or leaves blank, a required field, or
                    # carries a value a restricted picklist doesn't list.
                    return id(r) in bad_picklist_rows or any(
                        n not in by_field or all(layering.is_null(r.get(c)) for c in by_field[n])
                        for n in required)

                if op == "insert" or not ident_key:
                    fresh = list(rows)
                else:
                    fresh = []
                    for r in rows:
                        v = layering.row_values(ident_key, written, r)
                        ident = layering.key_of(v, ident_key) if all(f in v for f in ident_key) else None
                        if ident is None or ident not in known:
                            fresh.append(r)
                            if ident is not None and not rejected_row(r):
                                known.add(ident)  # a repeat of it in this pass patches the row created
                # ids of rows the platform would reject for a required field or picklist value. A
                # row that only patches is rejected for a bad picklist value too: its other columns
                # don't land, so they add nothing a later pass can match.
                rejected = {id(r) for r in rows if id(r) in bad_picklist_rows}
                if fresh:
                    for name, f in sorted(fields.items()):
                        if not _is_required(name, f):
                            continue
                        if name not in by_field:
                            add(rel, obj, "required", name,
                                f"{where}: {obj}.{name} is required on create (not nillable, not "
                                f"defaulted) and the plan doesn't load it")
                            rejected.update(id(r) for r in fresh)
                            continue
                        blanks = [r for r in fresh
                                  if all(layering.is_null(r.get(c)) for c in by_field[name])]
                        if blanks:
                            add(rel, obj, "required", name,
                                f"{where}: {obj}.{name} is required on create and {len(blanks)} "
                                f"row(s) leave it blank")
                            rejected.update(id(r) for r in blanks)
                # A rejected row isn't persisted, so a later pass on its key creates it rather than
                # patching it. (Describe can overstate `required`; such a field is triaged in
                # KNOWN_FINDINGS, and the later pass's finding for it is the same entry.)
                # A row a skipExistingRecords pass leaves alone writes nothing, so it adds no key either.
                # A column in a field that is neither createable nor updateable is dropped by SFDMU,
                # so its value never lands and can't identify a record for a later pass (a key, like `Id`,
                # is exempt: it names a record that exists).
                landed = [c for c in written
                          if (nm := _field_of(c, fields)) is None
                          or fields[nm].get("createable") or fields[nm].get("updateable")
                          or nm in key or nm in SYSTEM_FIELDS]  # an `Id` key names a record
                earlier.append((landed, [r for r in rows
                                         if id(r) not in rejected and id(r) not in skipped]))

    if bad_filters:
        raise ValueError("; ".join(bad_filters))
    added_fields, added_values = _release_changes(release_diff)
    unwritten = {}
    for obj in sorted(created_objs):
        fields = snapshot[obj]["fields"]
        names = sorted(n for n, f in fields.items()
                       if (f.get("createable") or f.get("updateable")) and not f.get("calculated")
                       and n not in SYSTEM_FIELDS and n not in UNWRITTEN_NOISE
                       and n not in written_by_obj[obj]
                       and not n.endswith("__c"))
        if names:
            unwritten[obj] = [{"field": n, "new": n in added_fields.get(obj, ())} for n in names]
    release_values = [{"object": obj, "field": name, "added": vals}
                      for (obj, name), vals in sorted(added_values.items())
                      if name in written_by_obj.get(obj, ()) and obj in snapshot
                      and name in snapshot[obj]["fields"]
                      and (snapshot[obj]["fields"][name].get("createable")
                           or snapshot[obj]["fields"][name].get("updateable"))]
    return {"findings": findings,
            "plans": [p.relative_to(root).as_posix() for p in selected_plans(root, prefixes)],
            "info": {"object-missing": dict(sorted(missing.items())),
                     "dead-columns": {o: dict(sorted(v.items())) for o, v in sorted(dead.items())},
                     "undefined-value": undefined, "unwritten": unwritten,
                     "release-values": release_values}}


def _release_changes(diff: Optional[Dict[str, Any]]):
    added_fields: Dict[str, set] = {}
    added_values: Dict[Tuple[str, str], List[str]] = {}
    for obj, d in ((diff or {}).get("object_diffs") or {}).items():
        added_fields[obj] = {a if isinstance(a, str) else a.get("name") for a in d.get("added", [])}
        for change in d.get("picklist_changed", []):
            if change.get("added"):
                added_values[(obj, change["field"])] = list(change["added"])
    return added_fields, added_values


def finding_key(f: Dict[str, Any]) -> Tuple[str, str, str, str]:
    return (f["plan"], f["object"], f["check"], f["field"])


def classify(result: Dict[str, Any], known=None, triaged=None):
    """(new gating findings, known ones, stale KNOWN_FINDINGS keys). An entry is stale only when
    its plan was audited and the finding is gone, so a `--plans` subset reports none for the
    plans it left out. A `picklist` finding is known only when every offending value is among the
    entry's `triaged` values (`TRIAGED_VALUES` for the committed entries, none for a custom
    `known`)."""
    if known is None:
        known, triaged = KNOWN_FINDINGS, TRIAGED_VALUES if triaged is None else triaged
    triaged = triaged or {}

    def is_known(f):
        key = finding_key(f)
        if key not in known:
            return False
        if f["check"] != "picklist":
            return True
        values = set(f.get("values", ()))
        return bool(values) and values <= triaged.get(key, frozenset())

    gating = [f for f in result["findings"] if f["check"] in GATING]
    audited = set(result.get("plans", ()))
    # An object the describe lacks was never checked, so its entries can't be called stale.
    unchecked = {(plan, obj) for obj, plans in result["info"]["object-missing"].items()
                 for plan in plans}
    new = [f for f in gating if not is_known(f)]
    kept = [f for f in gating if is_known(f)]
    found = {finding_key(f) for f in gating}
    # A picklist entry that triages a value no longer found is stale: a regression would pass again.
    seen_values: Dict[Tuple[str, str, str, str], set] = {}
    for f in kept:
        if f["check"] == "picklist":
            seen_values.setdefault(finding_key(f), set()).update(f.get("values", ()))
    partial = {k for k, vals in triaged.items() if k in seen_values and vals - seen_values[k]}
    stale = sorted(k for k in known if (k not in found or k in partial) and k[0] in audited
                   and (k[0], k[1]) not in unchecked)
    return new, kept, stale


# --------------------------------------------------------------------------- report


def render_markdown(result: Dict[str, Any], source: str, known=None, triaged=None) -> str:
    new, kept, stale = classify(result, known, triaged)
    known = KNOWN_FINDINGS if known is None else known
    info = result["info"]
    out = [f"# Data-plan release audit", "", f"Source: {source}", "",
           f"- New gating findings: {len(new)}",
           f"- Known (triaged in `KNOWN_FINDINGS`): {len(kept)}",
           f"- Stale `KNOWN_FINDINGS` entries: {len(stale)}",
           f"- Objects not in the describe: {len(info['object-missing'])}", ""]

    def table(rows, with_reason=False):
        head = "| Plan | Object | Check | Field | Detail |" + (" Reason |" if with_reason else "")
        lines = [head, "|" + "---|" * (6 if with_reason else 5)]
        for f in sorted(rows, key=finding_key):
            cells = [f["plan"], f["object"], f["check"], f["field"], f["detail"]]
            if with_reason:
                cells.append(known[finding_key(f)])
            lines.append("| " + " | ".join(c.replace("|", "\\|") for c in cells) + " |")
        return lines

    if new:
        out += ["## New gating findings", "", *table(new), ""]
    if stale:
        out += ["## Stale KNOWN_FINDINGS entries", "",
                *[f"- `{k}`: no longer found; remove it" for k in stale], ""]
    if kept:
        out += ["## Known findings", "", *table(kept, with_reason=True), ""]
    if info["object-missing"]:
        out += ["## Objects not in the describe", "",
                "Often a feature the org doesn't have; audit those plans on an org that has it.", ""]
        out += [f"- {obj}: {', '.join(plans)}" for obj, plans in info["object-missing"].items()]
        out.append("")
    if info["dead-columns"]:
        out += ["## Columns that never land", "",
                "Values in fields that are neither createable nor updateable. Usually derived "
                "fields an extraction copied; check none is a value the plan means to set.", ""]
        for obj, by_field in info["dead-columns"].items():
            out.append(f"- {obj}: " + "; ".join(f"{n} ({', '.join(p)})" for n, p in by_field.items()))
        out.append("")
    if info["undefined-value"]:
        out += ["## Values outside an unrestricted picklist's defined values", "",
                "They load; decide whether to add the value to the org's picklist or change it.", ""]
        out += [f"- {u['plan']} {u['object']}.{u['field']}: {', '.join(u['values'])}"
                for u in info["undefined-value"]]
        out.append("")
    if info["release-values"]:
        out += ["## Picklist values the release added to fields the plans write", ""]
        out += [f"- {r['object']}.{r['field']}: {', '.join(r['added'])}"
                for r in info["release-values"]]
        out.append("")
    if info["unwritten"]:
        out += ["## Writable fields no plan writes", "",
                "Per object a plan creates; **new** marks a field the release diff says was added. "
                "Candidates to review, not defects.", ""]
        for obj, names in info["unwritten"].items():
            shown = ", ".join(f"**{n['field']}** (new)" if n["new"] else n["field"] for n in names)
            out.append(f"- {obj} ({len(names)}): {shown}")
        out.append("")
    return "\n".join(out)


# --------------------------------------------------------------------------- CLI


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("snapshot", help="save the describe of every object the plans declare")
    sp.add_argument("--target-org", required=True, help="sf CLI alias or username (not CCI)")
    sp.add_argument("--merge", type=Path, help="an existing snapshot to add this org's objects to")
    sp.add_argument("--out", type=Path, required=True)
    au = sub.add_parser("audit", help="audit the plans against a describe")
    src = au.add_mutually_exclusive_group()
    src.add_argument("--target-org", help="sf CLI alias or username (not CCI)")
    src.add_argument("--snapshot", type=Path)
    au.add_argument("--plans", nargs="*", default=[],
                    help="plan path prefixes under datasets/sfdmu (default: every tracked plan)")
    au.add_argument("--release-diff", type=Path,
                    help="a scripts/erd/schema_diff/*-vs-*-diff.json (default: the active release's)")
    au.add_argument("--out", type=Path, help="write the report here (default: stdout)")
    au.add_argument("--json", action="store_true", help="write JSON instead of markdown")
    for p in (sp, au):
        p.add_argument("--root", type=Path, default=SFDMU, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    try:
        release = active_release()
        if args.cmd == "snapshot":
            api_version = active_api_version()
            base = _load_json(args.merge) if args.merge else None
            if base:
                check_snapshot_metadata(base, args.merge, release, api_version)
            objects = describe_org(args.target_org, plan_objects(args.root), api_version=api_version)
            if base:
                objects = merge_snapshots(base["objects"], objects)
            snap = {"metadata": {"release": release, "api_version": api_version,
                                 "captured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                 "source": "sobject describe of every object a tracked plan declares",
                                 "object_count": len(objects)},
                    "objects": dict(sorted(objects.items()))}
            args.out.write_text(json.dumps(snap, indent=1, sort_keys=True) + "\n", encoding="utf-8")
            print(f"wrote {args.out}: {len(objects)} object(s)")
            return 0

        if args.target_org:
            snapshot = describe_org(args.target_org, plan_objects(args.root, args.plans))
            source = f"live describe of {args.target_org}"
        else:
            path = args.snapshot or default_snapshot(release)
            if not path.exists():
                print(f"error: no describe snapshot at {path}. Capture one for release {release} "
                      f"(see the schema-validation skill, release-data-plan-audit.md)",
                      file=sys.stderr)
                return 2
            loaded = _load_json(path)
            check_snapshot_metadata(loaded, path, release, active_api_version())
            snapshot = loaded["objects"]
            source = f"snapshot {path.relative_to(REPO) if path.is_relative_to(REPO) else path}"
        diff_path = args.release_diff or default_release_diff(release)
        diff = _load_json(diff_path) if diff_path and diff_path.exists() else None
        result = audit(snapshot, args.root, args.plans, diff)
    except (OSError, ValueError, csv.Error, DecisionTableClientError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    new, kept, stale = classify(result)
    text = (json.dumps({"source": source, "new": new, "known": kept, "stale": [list(k) for k in stale],
                        **result}, indent=1)
            if args.json else render_markdown(result, source))
    if args.out:
        try:
            args.out.write_text(text + "\n", encoding="utf-8")
        except OSError as exc:
            # A report that can't be written is a tool error, not a clean (0) or failing (1) audit.
            print(f"error: can't write the report to {args.out}: {exc}", file=sys.stderr)
            return 2
    else:
        print(text)
    for f in new:
        print(f"{f['check']}: {f['plan']} {f['object']}.{f['field']}: {f['detail']}", file=sys.stderr)
    for k in stale:
        print(f"stale: {k} is in KNOWN_FINDINGS but no longer found; remove it", file=sys.stderr)
    print(f"{len(new)} new gating finding(s), {len(kept)} known, {len(stale)} stale. "
          f"{'FAIL' if new or stale else 'PASS'}", file=sys.stderr)
    return 1 if new or stale else 0


if __name__ == "__main__":
    sys.exit(main())
