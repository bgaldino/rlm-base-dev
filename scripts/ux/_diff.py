"""
UX drift diff — compares org state against what current templates assemble to.

``org_path`` (default ``unpackaged/post_ux/``) holds the org's flexipages, as
written by ``ux_tool.py retrieve``. The diff assembles flexipages from
``templates/`` into a temporary directory and reports added, removed,
modified and repositioned flexiPageRegions per page. It modifies no files
other than the report it writes (``drift_report.json`` by default).
"""
import json
import re
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional

from scripts.ux._assemble import SF_NS_TAG, UxAssembler, _find_elem, _findall_elem, validate_selection
from scripts.ux._context import UxContext, UxOptionError
from scripts.ux._flags import FLEXIPAGE_SUFFIX


def drift_count(report: Dict[str, Any]) -> int:
    """Number of pages that differ (drifted, org-only or templates-only)."""
    s = report["summary"]
    return s["drifted"] + s["org_only"] + s["templates_only"]


def org_flexipage_files(org_path: Path) -> List[str]:
    """Names of the org-state flexipages under ``org_path``; raise if there are none."""
    org_dir = Path(org_path) / "flexipages"
    names = sorted(f.name for f in org_dir.glob(f"*{FLEXIPAGE_SUFFIX}"))
    if not names:
        raise UxOptionError(
            f"No org flexipages in {org_dir}. Run `ux_tool.py retrieve` first."
        )
    return names


class UxDiff:
    """Diffs org flexipages against the assembler output from current templates."""

    def __init__(self, ctx: UxContext):
        self.ctx = ctx
        self.logger = ctx.logger

    def run(
        self,
        org_path: Path,
        metadata_name: Optional[str] = None,
        report_file: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Diff, log, write the JSON report and return it."""
        validate_selection("flexipages", metadata_name, ("flexipages",))
        org_path = Path(org_path)
        org_flexipage_files(org_path)
        report_path = Path(report_file) if report_file else org_path / "drift_report.json"
        features = self.ctx.features
        self.logger.info(
            "Active features: "
            + (", ".join(k for k, v in features.items() if v) or "none")
        )

        with tempfile.TemporaryDirectory(prefix="rlm_ux_diff_") as tmpdir:
            tmp_path = Path(tmpdir)
            self.logger.info("Assembling flexipages from templates for comparison...")
            self._assemble_to_temp(tmp_path, metadata_name)
            report = self._diff_flexipages(org_path, tmp_path, metadata_name)

        self._log_report(report)

        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        self.logger.info(f"Drift report written to: {report_path}")

        n_drifted = drift_count(report)
        if n_drifted == 0:
            self.logger.info("No drift detected — templates are in sync with org state.")
        else:
            self.logger.warning(
                f"{n_drifted} page(s) have drift. Review templates/, run "
                "`ux_tool.py writeback`, then reassemble and deploy."
            )
        return report

    def _assemble_to_temp(self, tmp_path: Path, filter_name: Optional[str]) -> None:
        """Run the assembler's flexipage logic into tmp_path."""
        assembled, skipped = UxAssembler(self.ctx)._assemble_flexipages(
            self.ctx.templates_path, tmp_path, self.ctx.features, filter_name,
        )
        self.logger.info(
            f"  Assembled {len(assembled)} flexipage(s) from templates "
            f"({len(skipped)} skipped as non-deployable)."
        )

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
            {f.name for f in org_dir.glob(f"*{FLEXIPAGE_SUFFIX}")}
            if org_dir.exists()
            else set()
        )
        asm_files: set = (
            {f.name for f in asm_dir.glob(f"*{FLEXIPAGE_SUFFIX}")}
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
                    "run `ux_tool.py retrieve` first)"
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

    # Union in order: org regions first, then template-only ones.
    all_names_ordered = list(dict.fromkeys(org_order + asm_order))
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

            parts = [
                part for part, changed in (
                    ("content_modified", content_changed),
                    ("position_changed", position_changed),
                ) if changed
            ]
            region_diffs.append(
                {
                    "name": name,
                    "label": org_by_name[name].get("label", ""),
                    "status": "+".join(parts) or "in_sync",
                    "org_position": org_pos,
                    "asm_position": asm_pos,
                }
            )

    return {"regions": region_diffs}


def _extract_regions(root: ET.Element) -> List[Dict[str, Any]]:
    """Return all flexiPageRegion elements with name, type, label, and xml."""
    regions = []
    for region in _findall_elem(root, "flexiPageRegions"):
        name_el = _find_elem(region, "name")
        type_el = _find_elem(region, "type")
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
        for el in region.iter(f"{SF_NS_TAG}componentName")
        if el.text
    ]
    if component_names:
        # Use last component after colon for brevity (e.g. flexipage:tab → tab)
        short = component_names[0].rsplit(":", 1)[-1]
        return short
    return name


def _normalize_xml(element: ET.Element) -> str:
    """Canonical string for XML comparison — strips whitespace-only text nodes."""
    return re.sub(r">\s+<", "><", ET.tostring(element, encoding="unicode")).strip()

