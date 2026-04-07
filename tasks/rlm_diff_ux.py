"""
DiffUXTemplates — Compares unpackaged/post_ux/ (org state captured by
retrieve_ux_from_org) against what the assembler would produce from current
templates/. Reports added, removed, modified, and repositioned flexiPageRegions.

Does not modify any files. Run retrieve_ux_from_org first to populate
unpackaged/post_ux/ with the org's current state.

Usage examples:
    cci task run diff_ux_templates
    cci task run diff_ux_templates \\
        -o metadata_name RLM_Order_Record_Page.flexipage-meta.xml
    cci task run diff_ux_templates -o report_file /tmp/drift.json
"""
import copy
import json
import re
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception

try:
    from tasks.rlm_ux_assembly import AssembleAndDeployUX
except ImportError:
    AssembleAndDeployUX = None  # type: ignore


_SF_NS = "http://soap.sforce.com/2006/04/metadata"
_NS_TAG = f"{{{_SF_NS}}}"


class DiffUXTemplates(BaseTask):
    """
    Diffs unpackaged/post_ux/ (org state) against the assembler output from
    current templates, reporting UX drift per flexiPageRegion.

    Requires retrieve_ux_from_org to have been run first (or post_ux to have
    been manually updated with org-retrieved files).
    """

    task_options = {
        "metadata_name": {
            "description": (
                "Specific file to diff, e.g. "
                "'RLM_Order_Record_Page.flexipage-meta.xml'. "
                "Diffs all flexipages when omitted."
            ),
            "required": False,
        },
        "metadata_type": {
            "description": (
                "Metadata type to diff. Currently supports 'flexipages'. "
                "Defaults to 'flexipages'."
            ),
            "required": False,
        },
        "org_path": {
            "description": (
                "Directory containing org-retrieved metadata (output of "
                "retrieve_ux_from_org). Defaults to 'unpackaged/post_ux'."
            ),
            "required": False,
        },
        "report_file": {
            "description": (
                "Path to write drift_report.json. "
                "Defaults to 'unpackaged/post_ux/drift_report.json'."
            ),
            "required": False,
        },
    }

    def _validate_options(self):
        super()._validate_options()
        if AssembleAndDeployUX is None:
            raise TaskOptionsError(
                "tasks.rlm_ux_assembly could not be imported — "
                "ensure it is present in the tasks/ directory."
            )
        mtype = self.options.get("metadata_type", "flexipages")
        if mtype not in ("flexipages",):
            raise TaskOptionsError(
                f"metadata_type must be 'flexipages', got: '{mtype}'"
            )
        mname = self.options.get("metadata_name")
        if mname and not mname.endswith(".flexipage-meta.xml"):
            raise TaskOptionsError(
                f"metadata_name must end in '.flexipage-meta.xml', got: '{mname}'"
            )

    def _run_task(self):
        repo_root = Path(self.project_config.repo_root)
        org_path = repo_root / self.options.get("org_path", "unpackaged/post_ux")
        metadata_name = self.options.get("metadata_name")
        report_file = self.options.get(
            "report_file", str(org_path / "drift_report.json")
        )
        templates_path = repo_root / "templates"

        features = self._get_features()
        self.logger.info(
            "Active features: "
            + (
                ", ".join(k for k, v in features.items() if v)
                or "none"
            )
        )

        with tempfile.TemporaryDirectory(prefix="rlm_ux_diff_") as tmpdir:
            tmp_path = Path(tmpdir)
            self.logger.info(
                "Assembling flexipages from templates for comparison..."
            )
            self._assemble_to_temp(templates_path, tmp_path, features, metadata_name)
            report = self._diff_flexipages(org_path, tmp_path, metadata_name)

        self._log_report(report)

        report_path = Path(report_file)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        # Strip non-serialisable xml field before writing
        _strip_xml_fields(report)
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        self.logger.info(f"Drift report written to: {report_path}")

        n_drifted = (
            report["summary"]["drifted"]
            + report["summary"]["org_only"]
            + report["summary"]["templates_only"]
        )
        if n_drifted == 0:
            self.logger.info(
                "No drift detected — templates are in sync with org state."
            )
        else:
            self.logger.warning(
                f"{n_drifted} page(s) have drift. "
                "Review templates/ then run assemble_and_deploy_ux."
            )

    # ------------------------------------------------------------------
    # Feature flags
    # ------------------------------------------------------------------

    def _get_features(self) -> Dict[str, bool]:
        """Read feature flags via AssembleAndDeployUX._get_feature_flags."""
        return AssembleAndDeployUX._get_feature_flags(self)  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # Assembly
    # ------------------------------------------------------------------

    def _assemble_to_temp(
        self,
        templates_path: Path,
        tmp_path: Path,
        features: Dict[str, bool],
        filter_name: Optional[str],
    ) -> None:
        """Run the assembler's flexipage logic into tmp_path."""
        adapter = _AssemblerAdapter(self)
        result = AssembleAndDeployUX._assemble_flexipages(
            adapter,  # type: ignore[arg-type]
            templates_path,
            tmp_path,
            features,
            filter_name,
        )
        assembled, skipped = result if isinstance(result, tuple) else (result, [])
        self.logger.info(
            f"  Assembled {len(assembled)} flexipage(s) from templates "
            f"({len(skipped)} skipped as non-deployable)."
        )

    # ------------------------------------------------------------------
    # Diff
    # ------------------------------------------------------------------

    def _diff_flexipages(
        self,
        org_path: Path,
        tmp_path: Path,
        filter_name: Optional[str],
    ) -> Dict[str, Any]:
        """Compare org flexipages against assembled-from-templates flexipages."""
        org_dir = org_path / "flexipages"
        asm_dir = tmp_path / "flexipages"

        org_files: set = (
            {f.name for f in org_dir.glob("*.flexipage-meta.xml")}
            if org_dir.exists()
            else set()
        )
        asm_files: set = (
            {f.name for f in asm_dir.glob("*.flexipage-meta.xml")}
            if asm_dir.exists()
            else set()
        )

        if filter_name:
            org_files &= {filter_name}
            asm_files &= {filter_name}

        report: Dict[str, Any] = {
            "pages": [],
            "summary": {
                "in_sync": 0,
                "drifted": 0,
                "org_only": 0,
                "templates_only": 0,
            },
        }

        for fname in sorted(org_files | asm_files):
            in_org = fname in org_files
            in_asm = fname in asm_files

            if in_org and not in_asm:
                report["pages"].append(
                    {
                        "file": fname,
                        "status": "org_only",
                        "note": "Exists in org but not produced by current templates.",
                        "regions": [],
                    }
                )
                report["summary"]["org_only"] += 1
                continue

            if in_asm and not in_org:
                report["pages"].append(
                    {
                        "file": fname,
                        "status": "templates_only",
                        "note": "Produced by templates but not found in org state.",
                        "regions": [],
                    }
                )
                report["summary"]["templates_only"] += 1
                continue

            page_report = _diff_flexipage_file(org_dir / fname, asm_dir / fname)
            page_report["file"] = fname

            has_drift = any(
                r["status"] != "in_sync" for r in page_report["regions"]
            )
            page_report["status"] = "drifted" if has_drift else "in_sync"
            if has_drift:
                report["summary"]["drifted"] += 1
            else:
                report["summary"]["in_sync"] += 1

            report["pages"].append(page_report)

        return report

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def _log_report(self, report: Dict[str, Any]) -> None:
        for page in report["pages"]:
            fname = page["file"]
            status = page["status"]

            if status == "in_sync":
                self.logger.info(f"  [in sync]  {fname}")
                continue

            self.logger.info(f"  [drift]    {fname}")

            if status == "org_only":
                self.logger.info(
                    "               (page exists in org but not in templates)"
                )
                continue
            if status == "templates_only":
                self.logger.info(
                    "               (page in templates but not in org state — "
                    "run retrieve_ux_from_org first)"
                )
                continue

            for region in page.get("regions", []):
                rstatus = region["status"]
                if rstatus == "in_sync":
                    continue
                label = f" ({region['label']})" if region.get("label") else ""
                pos_info = ""
                if region.get("org_position") is not None and region.get("asm_position") is not None:
                    if region["org_position"] != region["asm_position"]:
                        pos_info = (
                            f" [org pos {region['org_position']} "
                            f"vs templates pos {region['asm_position']}]"
                        )
                self.logger.info(
                    f"    {rstatus.upper():30s}  {region['name']}{label}{pos_info}"
                )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


class _AssemblerAdapter:
    """
    Minimal stand-in that provides the attributes AssembleAndDeployUX instance
    methods expect, so they can be called as unbound functions without needing
    a fully-initialised CCI task.
    """

    def __init__(self, parent_task: Any) -> None:
        self.project_config = parent_task.project_config
        self.logger = parent_task.logger

    def _apply_raw_xml_patch(self, root: ET.Element, patch: Dict[str, Any]) -> None:
        AssembleAndDeployUX._apply_raw_xml_patch(
            self,  # type: ignore[arg-type]
            root,
            patch,
        )


def _diff_flexipage_file(
    org_file: Path, asm_file: Path
) -> Dict[str, Any]:
    """Diff a single flexipage XML at the flexiPageRegion level."""
    org_root = ET.parse(str(org_file)).getroot()
    asm_root = ET.parse(str(asm_file)).getroot()

    org_regions = _extract_regions(org_root)
    asm_regions = _extract_regions(asm_root)

    org_order = [r["name"] for r in org_regions]
    asm_order = [r["name"] for r in asm_regions]
    org_by_name = {r["name"]: r for r in org_regions}
    asm_by_name = {r["name"]: r for r in asm_regions}

    all_names_ordered = _merge_ordered(org_order, asm_order)
    region_diffs: List[Dict[str, Any]] = []

    for name in all_names_ordered:
        in_org = name in org_by_name
        in_asm = name in asm_by_name

        if in_org and not in_asm:
            region_diffs.append(
                {
                    "name": name,
                    "label": org_by_name[name].get("label", ""),
                    "status": "added_in_org",
                    "org_position": org_order.index(name),
                    "asm_position": None,
                }
            )
        elif in_asm and not in_org:
            region_diffs.append(
                {
                    "name": name,
                    "label": asm_by_name[name].get("label", ""),
                    "status": "removed_from_org",
                    "org_position": None,
                    "asm_position": asm_order.index(name),
                }
            )
        else:
            org_pos = org_order.index(name)
            asm_pos = asm_order.index(name)
            content_changed = _normalize_xml(org_by_name[name]["xml"]) != _normalize_xml(
                asm_by_name[name]["xml"]
            )
            position_changed = org_pos != asm_pos

            if content_changed or position_changed:
                parts = []
                if content_changed:
                    parts.append("content_modified")
                if position_changed:
                    parts.append("position_changed")
                region_diffs.append(
                    {
                        "name": name,
                        "label": org_by_name[name].get("label", ""),
                        "status": "+".join(parts),
                        "org_position": org_pos,
                        "asm_position": asm_pos,
                    }
                )
            else:
                region_diffs.append(
                    {
                        "name": name,
                        "label": org_by_name[name].get("label", ""),
                        "status": "in_sync",
                        "org_position": org_pos,
                        "asm_position": asm_pos,
                    }
                )

    return {"regions": region_diffs}


def _extract_regions(root: ET.Element) -> List[Dict[str, Any]]:
    """Return all flexiPageRegion elements with name, type, label, and xml."""
    regions = []
    for region in root.findall(f"{_NS_TAG}flexiPageRegions"):
        name_el = region.find(f"{_NS_TAG}name")
        type_el = region.find(f"{_NS_TAG}type")
        name = (name_el.text or "").strip() if name_el is not None else ""
        rtype = (type_el.text or "").strip() if type_el is not None else ""
        # Provide a human-readable label for well-known names
        label = _region_label(name, rtype, region)
        regions.append({"name": name, "type": rtype, "label": label, "xml": region})
    return regions


def _region_label(name: str, rtype: str, region: ET.Element) -> str:
    """Return a descriptive label for a flexiPageRegion."""
    # Named regions (header, main, maintabs, etc.) use their name directly
    if rtype == "Region":
        return name
    # Facets: look for a componentName to use as label
    component_names = [
        el.text.strip()
        for el in region.iter(f"{_NS_TAG}componentName")
        if el.text
    ]
    if component_names:
        # Use last component after colon for brevity (e.g. flexipage:tab → tab)
        short = component_names[0].rsplit(":", 1)[-1]
        return short
    return name


def _normalize_xml(element: ET.Element) -> str:
    """Canonical string for XML comparison — strips whitespace-only text nodes."""
    clone = copy.deepcopy(element)
    return re.sub(r">\s+<", "><", ET.tostring(clone, encoding="unicode")).strip()


def _merge_ordered(a: List[str], b: List[str]) -> List[str]:
    """Merge two ordered lists preserving relative order; items in a come first."""
    seen: set = set()
    result = []
    for item in a:
        if item not in seen:
            result.append(item)
            seen.add(item)
    for item in b:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result


def _strip_xml_fields(obj: Any) -> None:
    """Recursively remove any 'xml' key holding an ET.Element (not JSON-serialisable)."""
    if isinstance(obj, dict):
        obj.pop("xml", None)
        for v in obj.values():
            _strip_xml_fields(v)
    elif isinstance(obj, list):
        for item in obj:
            _strip_xml_fields(item)
