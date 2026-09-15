"""Validate (and optionally populate) source-org externalId key fields before extraction.

SFDMU data plans key their objects on externalId fields.  If those key fields are
null or non-unique in the source org, an extraction produces broken composite keys
(blank components, duplicate rows).  This task is the pre-extraction guard: for the
plan's "key-target" objects — those whose externalId is composed entirely of direct
fields (the object's own logical key, e.g. Product2.StockKeepingUnit, UsageResource.Code,
UnitOfMeasure.UnitCode, RateCard.Name;Type) — it reports null and duplicate keys, and
can populate null single-field keys (StockKeepingUnit / *.Code / *.UnitCode) by deriving
a unique value from a basis field (generalizes scripts/apex/.../uniq_sku logic).

Objects whose externalId traverses relationships (e.g. RateCardEntry's
Product.StockKeepingUnit;RateCard.Name;...) are NOT validated here — their keys live on
the parent objects, which ARE validated when those parents appear as plan objects.

Read-only by default.  ``--populate true`` writes derived values to the org (null keys
only; existing values are never renamed).  ``--fail_on_issues`` (default: true when not
populating) makes the task exit non-zero if any key issue remains, so it can gate a flow.
"""
import json
import os
import re
import sys
from collections import Counter
from typing import Any, Dict, List, Optional

# Bootstrap the repo's scripts/ dir onto sys.path so the shared SFDMU parsing
# primitives (`sfdmu_export`) resolve when this task module is imported by CCI.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import sfdmu_export  # noqa: E402  (after the path bootstrap above)

try:
    from cumulusci.tasks.salesforce import BaseSalesforceApiTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseSalesforceApiTask = object
    TaskOptionsError = Exception

EXPORT_JSON_FILENAME = "export.json"
_SLUG_RE = re.compile(r"[^A-Z0-9]+")

# Auto-populate config for objects whose single direct key field can be derived.
# basis: ordered source fields to derive a value from (first non-blank wins).
# sync:  fields to also set to the derived value (e.g. Product2.ProductCode == SKU).
# Objects not listed use the default: field = the lone direct key, basis = [Name].
POPULATE_CONFIG: Dict[str, Dict[str, Any]] = {
    "Product2": {"field": "StockKeepingUnit", "basis": ["ProductCode", "Name"], "sync": ["ProductCode"]},
}


def _slug(value: str) -> str:
    """Uppercase slug of a value: non-alphanumerics → '-', trimmed. Mirrors uniq_sku.apex."""
    s = _SLUG_RE.sub("-", (value or "").upper()).strip("-")
    return s or "KEY"


def _present(value) -> bool:
    """True if a key value is actually populated. A boolean False or numeric 0 is a
    valid key value, so test for None/empty-string specifically (not falsiness)."""
    return value is not None and value != ""


def collect_key_target_objects(export_json: dict) -> Dict[str, List[List[str]]]:
    """Return {object: [distinct direct-key field-sets]} for objects whose externalId is all-direct.

    A multi-pass plan can declare the same object with different direct-key externalIds in
    different passes — e.g. `Name` in the top-level `objects` pass (unshifted as pass 1 by
    ``normalize_object_sets``) and `Code` in an `objectSets` pass. Each distinct key-field set
    is returned and validated on its own, so a null/duplicate in a later declaration's key is
    not silently missed by collapsing every declaration to the first. Identical field-sets are
    de-duplicated (first-seen order preserved) to avoid redundant source-org queries.

    Objects with any relationship-traversal externalId component are skipped (their
    keys are validated through their parent objects).
    """
    object_sets = sfdmu_export.normalize_object_sets(export_json)
    targets: Dict[str, List[List[str]]] = {}
    for oset in object_sets:
        for obj in oset.get("objects", []):
            # JS truthiness: SFDMU reads `excluded` in JS, where `[]`/`{}` are truthy
            # and skip the declaration. Python's plain `if` would read them as live and
            # query/populate keys for an object SFDMU never loads (pack 168 now walks
            # the prepended top-level pass here too).
            if sfdmu_export.is_js_truthy(obj.get("excluded")):
                continue
            # Shared parser: case-insensitive, subquery-aware, and returns "" (not a
            # raise) on a non-string/malformed query — the newly-included top-level pass
            # (pack 168) must be validated without aborting on a lowercase `from`.
            name = sfdmu_export.extract_object_name(obj.get("query", ""))
            external_id = obj.get("externalId", "")
            # A non-string externalId (a hand-edited list/dict, now reachable via the
            # top-level pass) is truthy but would raise on `.split(";")` — skip it.
            if not name or not isinstance(external_id, str) or not external_id or external_id == "Id":
                continue
            comps = [c.strip() for c in external_id.split(";") if c.strip()]
            if not comps or any("." in c for c in comps):
                continue  # relationship-keyed: validated via parent objects
            variants = targets.setdefault(name, [])
            if comps not in variants:
                variants.append(comps)
    return targets


class ValidateSourceDataKeys(BaseSalesforceApiTask):
    """Validate/populate a plan's source-org externalId key fields prior to extraction."""

    task_options: Dict[str, Dict[str, Any]] = {
        "pathtoexportjson": {
            "description": "Directory containing the export.json whose key fields to validate.",
            "required": True,
        },
        "populate": {
            "description": (
                "If true, populate null single-field keys (StockKeepingUnit / *.Code / "
                "*.UnitCode) with unique derived values (writes to the org). Existing values "
                "are never renamed. Default false (report only)."
            ),
            "required": False,
        },
        "fail_on_issues": {
            "description": (
                "If true, raise (non-zero exit) when key issues remain after the run, so the "
                "task can gate a flow. Default: true when not populating, false when populating."
            ),
            "required": False,
        },
    }

    def _bool(self, name: str, default: bool) -> bool:
        val = self.options.get(name)
        if val is None:
            return default
        return str(val).strip().lower() not in {"0", "false", "no", ""}

    def _query_all(self, soql: str) -> List[dict]:
        res = self.sf.query(soql)
        records = list(res.get("records", []))
        while not res.get("done", True):
            res = self.sf.query_more(res["nextRecordsUrl"], identifier_is_url=True)
            records.extend(res.get("records", []))
        return records

    def _run_task(self) -> None:
        plan_dir = self.options["pathtoexportjson"]
        export_path = os.path.join(plan_dir, EXPORT_JSON_FILENAME)
        if not os.path.isfile(export_path):
            raise TaskOptionsError(f"export.json not found: {export_path}")
        with open(export_path, encoding="utf-8") as f:
            export_json = json.load(f)

        populate = self._bool("populate", False)
        fail_on_issues = self._bool("fail_on_issues", not populate)

        targets = collect_key_target_objects(export_json)
        if not targets:
            self.logger.info("No all-direct-key objects to validate in this plan.")
            return

        n_decls = sum(len(v) for v in targets.values())
        self.logger.info(
            f"Validating source keys for {len(targets)} object(s) "
            f"({n_decls} key declaration(s)) in {plan_dir} (populate={populate})"
        )
        total_issues = 0
        for obj in sorted(targets):
            for keyfields in targets[obj]:
                total_issues += self._validate_object(obj, keyfields, populate)

        if total_issues:
            msg = f"Source-key validation found {total_issues} unresolved key issue(s)."
            if fail_on_issues:
                raise TaskOptionsError(msg + " Re-run with --populate true to remediate null keys.")
            self.logger.warning(msg)
        else:
            self.logger.info("All source keys are present and unique.")

    def _validate_object(self, obj: str, keyfields: List[str], populate: bool) -> int:
        # POPULATE_CONFIG is object-wide but targets one specific key field
        # (e.g. Product2 -> StockKeepingUnit). A multi-pass plan may validate the
        # same object on a different direct key (e.g. ProductCode); applying the
        # config there would populate StockKeepingUnit and clear the issue count
        # while the requested key stayed null. Only honor the config for the
        # declaration whose key IS the config's field; otherwise fall back to the
        # default (populate the requested key itself from Name).
        cfg = POPULATE_CONFIG.get(obj)
        if cfg and cfg.get("field") not in keyfields:
            cfg = None
        select = ["Id"] + list(keyfields)
        extras = (cfg["basis"] + cfg.get("sync", [])) if cfg else (
            ["Name"] if (len(keyfields) == 1 and keyfields[0] != "Name") else []
        )
        for field in extras:
            if field not in select:
                select.append(field)

        try:
            records = self._query_all(f"SELECT {', '.join(select)} FROM {obj}")
        except Exception as exc:  # field may not exist on this object; retry minimal
            self.logger.warning(f"{obj}: query with {select} failed ({exc}); retrying key-only")
            records = self._query_all(f"SELECT {', '.join(['Id'] + list(keyfields))} FROM {obj}")

        null_counts = {kf: sum(1 for r in records if not _present(r.get(kf))) for kf in keyfields}
        complete = [tuple(str(r.get(k)) for k in keyfields) for r in records
                    if all(_present(r.get(k)) for k in keyfields)]
        dups = [k for k, c in Counter(complete).items() if c > 1]

        n_null = sum(null_counts.values())
        label = "+".join(keyfields)
        if n_null or dups:
            detail = ", ".join(f"{kf}={null_counts[kf]} null" for kf in keyfields if null_counts[kf])
            dup_detail = f"{len(dups)} duplicate key(s)" if dups else ""
            self.logger.warning(
                f"  {obj} [{label}] ({len(records)} records): "
                + " | ".join(p for p in [detail, dup_detail] if p)
            )
        else:
            self.logger.info(f"  {obj} [{label}] ({len(records)} records): OK")

        if populate and n_null:
            return self._populate_nulls(obj, keyfields, records, cfg) + len(dups)
        return n_null + len(dups)

    def _populate_nulls(self, obj: str, keyfields: List[str], records: List[dict],
                        cfg: Optional[dict]) -> int:
        field = (cfg or {}).get("field") or keyfields[0]
        if len(keyfields) != 1 or field == "Name":
            self.logger.warning(
                f"  {obj}: cannot auto-populate composite/Name key {keyfields}; report only."
            )
            # Report-only: count nulls across ALL key components (matching the caller's
            # honest n_null), not just the first — otherwise a composite key with nulls
            # only in a trailing component would return 0 and clear the gate while the key
            # stayed broken.
            return sum(1 for r in records for k in keyfields if not _present(r.get(k)))

        basis = (cfg or {}).get("basis", ["Name"])
        sync = (cfg or {}).get("sync", [])
        used = {str(r[field]) for r in records if _present(r.get(field))}
        updates: List[dict] = []
        for r in sorted((r for r in records if not _present(r.get(field))), key=lambda x: x["Id"]):
            base = next((_slug(str(r[b])) for b in basis if r.get(b)), None) or _slug(obj)
            cand, n = base, 2
            while cand in used:
                cand, n = f"{base}-{n}", n + 1
            used.add(cand)
            rec = {"Id": r["Id"], field: cand}
            for s in sync:
                rec[s] = cand
            updates.append(rec)

        if not updates:
            return 0
        self.logger.info(f"  {obj}: populating {len(updates)} null {field}"
                         + (f" (+sync {sync})" if sync else "") + " ...")
        results = getattr(self.sf.bulk, obj).update(updates)
        failures = [x for x in results if not x.get("success")]
        if failures:
            self.logger.error(f"  {obj}: {len(failures)} update failure(s): {failures[:3]}")
            return len(failures)
        self.logger.info(f"  {obj}: populated {len(updates)} {field} value(s).")
        return 0
