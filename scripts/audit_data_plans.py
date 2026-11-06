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
  required       a creating declaration leaves out, or leaves blank on the rows it creates (not
                 ones an earlier pass created), a field that is createable, not nillable and not
                 defaulted on create
Informational (reported, never gating):
  object-missing   the object isn't in the describe (often a feature the org doesn't have)
  dead-columns     CSV values in fields that are neither createable nor updateable, so they never
                   land: usually derived fields an extraction copied, sometimes a value someone
                   meant to set (a key field used only for matching is left out)
  undefined-value  a value outside an unrestricted picklist's defined values (it loads)
  unwritten        writable fields no plan writes, per object, marked when the release diff
                   says the release added them
  release-values   picklist values the release added to a field a plan writes

Exit codes: 0 = no new gating finding · 1 = findings (new, or stale `KNOWN_FINDINGS` entries)
· 2 = tool error (no snapshot for the active release, or a `sourceRecordsFilter` the audit can't
evaluate).
"""
from __future__ import annotations

import argparse
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
GATING = ("unknown-field", "picklist", "required")
# Fields the platform sets itself, never a plan's to write.
SYSTEM_FIELDS = frozenset({"Id", "IsDeleted", "CreatedDate", "CreatedById", "LastModifiedDate",
                           "LastModifiedById", "SystemModstamp", "LastViewedDate",
                           "LastReferencedDate", "LastActivityDate"})
# Writable on almost every object and set by the platform or the org's currency, so listing them
# as fields "no plan writes" would bury the ones worth reviewing.
UNWRITTEN_NOISE = frozenset({"OwnerId", "CurrencyIsoCode"})
DESCRIBE_KEYS = ("type", "createable", "updateable", "nillable", "defaultedOnCreate",
                 "calculated", "autoNumber", "restrictedPicklist", "relationshipName", "referenceTo")

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


def active_release(manifest: Path = MANIFEST) -> str:
    m = re.search(r'^salesforce_release_active:\s*"?(\d+)"?', manifest.read_text(encoding="utf-8"),
                  re.M)
    if not m:
        raise ValueError(f"no salesforce_release_active in {manifest}")
    return m.group(1)


def default_snapshot(release: str) -> Path:
    return SCHEMA_DIR / f"{release}-plan-describe.json"


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
    for plan in layering.plan_dirs(root):
        rel = plan.relative_to(root).as_posix()
        if not prefixes or any(rel == p or rel.startswith(p + "/") for p in prefixes):
            out.append(plan)
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


def describe_org(target_org: str, objects: List[str], workers: int = 8) -> Dict[str, Any]:
    """{object: compact describe} for the objects the org has; a missing object is absent."""
    def one(obj: str):
        try:
            return obj, compact_describe(connect_request(
                "GET", f"sobjects/{obj}/describe", target_org=target_org))
        except DecisionTableClientError as exc:
            if "NOT_FOUND" in exc.error_codes or "INVALID_TYPE" in exc.error_codes:
                return obj, None
            raise
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return {o: d for o, d in pool.map(one, objects) if d is not None}


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
        return header if header in fields else None
    rel = header.split(".", 1)[0]
    return next((n for n, f in fields.items() if f.get("relationshipName") == rel), None)


def _path_problem(obj: str, segs: List[str], snapshot: Dict[str, Any]) -> Optional[str]:
    """Why the field path `segs` (`Field` or `Rel.Field`, any depth) doesn't resolve from `obj`, or
    None when it does or can't be checked: a lookup's target missing from the snapshot is left
    unchecked, and a polymorphic one resolves if any target in the snapshot has the rest."""
    fields = snapshot[obj]["fields"]
    seg = segs[0]
    if len(segs) == 1:
        return None if seg in fields or seg in SYSTEM_FIELDS else f"{obj} has no field `{seg}`"
    f = next((f for f in fields.values() if f.get("relationshipName") == seg), None)
    if f is None:
        return f"{obj} has no relationship `{seg}`"
    wanted = f.get("referenceTo") or []
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

    def add(plan, obj, check, field, detail):
        findings.append({"plan": plan, "object": obj, "check": check, "field": field,
                         "detail": detail})

    for plan in selected_plans(root, prefixes):
        rel = plan.relative_to(root).as_posix()
        export = json.loads((plan / "export.json").read_text(encoding="utf-8"))
        created_keys: Dict[str, set] = {}
        first_keys: Dict[str, List[str]] = {}
        for pass_idx, decl, obj in sorted(layering.declarations(export), key=lambda t: t[0]):
            if not layering.is_written(decl):
                continue
            desc = snapshot.get(obj)
            if desc is None:
                if rel not in missing[obj]:
                    missing[obj].append(rel)
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
                # `Field$Type` is SFDMU's polymorphic lookup: the field, resolved through Type.
                sel = sel.split("$", 1)[0]
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
            by_field: Dict[str, List[str]] = defaultdict(list)
            for col in columns:
                name = _field_of(col, fields)
                if name:
                    by_field[name].append(col)
            written_by_obj[obj].update(by_field)

            for name, cols in sorted(by_field.items()):
                f = fields[name]
                filled = [r for r in rows if any(not layering.is_null(r.get(c)) for c in cols)]
                if not filled:
                    continue
                if (not f.get("createable") and not f.get("updateable") and name not in key
                        and name not in SYSTEM_FIELDS):
                    if rel not in dead[obj][name]:
                        dead[obj][name].append(rel)
                if (f.get("type") in ("picklist", "multipicklist") and name != "CurrencyIsoCode"
                        and not f.get("orgValues")):
                    allowed = set(f.get("values") or [])
                    vals = {v for r in filled for c in cols if "." not in c
                            for v in ([x.strip() for x in (r.get(c) or "").split(";")]
                                      if f["type"] == "multipicklist" else [r.get(c) or ""])
                            if not layering.is_null(v)}
                    bad = sorted(vals - allowed)
                    if bad and f.get("restrictedPicklist"):
                        add(rel, obj, "picklist", name,
                            f"{where}: {', '.join(bad)} not among the restricted picklist's active "
                            f"values ({', '.join(sorted(allowed)) or 'none'})")
                    elif bad and allowed:
                        undefined.append({"plan": rel, "object": obj, "field": name, "values": bad})

            if op in layering.CREATES:
                created_objs.add(obj)
                # Required fields are checked on the rows this pass creates. A row a creating
                # pass of this plan already created (same key) is only patched here, by an Upsert
                # (it matches); an Insert never matches, so its rows are always new.
                # The plan's key for the object is its first creating declaration's (the layering
                # check takes its first written one, which may be an Update keyed on Id), so a
                # later pass keyed differently still meets its rows.
                plan_key = first_keys.setdefault(obj, key_list)
                made = created_keys.setdefault(obj, set())
                fresh = []
                for r in rows:
                    ident = layering.key_of(layering.row_values(plan_key, headers, r), plan_key)
                    if op == "insert" or ident is None or ident not in made:
                        fresh.append(r)
                    if ident is not None:
                        made.add(ident)
                if fresh:
                    for name, f in sorted(fields.items()):
                        if not _is_required(name, f):
                            continue
                        if name not in by_field:
                            add(rel, obj, "required", name,
                                f"{where}: {obj}.{name} is required on create (not nillable, not "
                                f"defaulted) and the plan doesn't load it")
                            continue
                        blank = sum(1 for r in fresh
                                    if all(layering.is_null(r.get(c)) for c in by_field[name]))
                        if blank:
                            add(rel, obj, "required", name,
                                f"{where}: {obj}.{name} is required on create and {blank} row(s) "
                                f"leave it blank")

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


def classify(result: Dict[str, Any], known=None):
    """(new gating findings, known ones, stale KNOWN_FINDINGS keys). An entry is stale only when
    its plan was audited and the finding is gone, so a `--plans` subset reports none for the
    plans it left out."""
    known = KNOWN_FINDINGS if known is None else known
    gating = [f for f in result["findings"] if f["check"] in GATING]
    keys = {finding_key(f) for f in gating}
    audited = set(result.get("plans", ()))
    # An object the describe lacks was never checked, so its entries can't be called stale.
    unchecked = {(plan, obj) for obj, plans in result["info"]["object-missing"].items()
                 for plan in plans}
    new = [f for f in gating if finding_key(f) not in known]
    kept = [f for f in gating if finding_key(f) in known]
    stale = sorted(k for k in known if k not in keys and k[0] in audited
                  and (k[0], k[1]) not in unchecked)
    return new, kept, stale


# --------------------------------------------------------------------------- report


def render_markdown(result: Dict[str, Any], source: str, known=None) -> str:
    known = KNOWN_FINDINGS if known is None else known
    new, kept, stale = classify(result, known)
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
            objects = describe_org(args.target_org, plan_objects(args.root))
            if args.merge:
                objects = merge_snapshots(_load_json(args.merge)["objects"], objects)
            snap = {"metadata": {"release": release,
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
            snapshot = _load_json(path)["objects"]
            source = f"snapshot {path.relative_to(REPO) if path.is_relative_to(REPO) else path}"
        diff_path = args.release_diff or default_release_diff(release)
        diff = _load_json(diff_path) if diff_path and diff_path.exists() else None
        result = audit(snapshot, args.root, args.plans, diff)
    except (OSError, ValueError, DecisionTableClientError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    new, kept, stale = classify(result)
    text = (json.dumps({"source": source, "new": new, "known": kept, "stale": [list(k) for k in stale],
                        **result}, indent=1)
            if args.json else render_markdown(result, source))
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
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
