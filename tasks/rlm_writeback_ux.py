"""
WriteBackUXTemplates — Reverse-applies active feature patches against
org-retrieved flexipages and writes the result as updated base templates.

The assembler invariant is: base + patches = deployed state.
Write-back computes:         new_base = org_state - patches.

This prevents double-application of non-idempotent patches (insert_after_xml)
on the next assembly run.

Requires retrieve_ux_from_org to have populated unpackaged/post_ux/ with the
org's current flexipage state.

Usage examples:
    cci task run writeback_ux_templates --org drotest              # dry-run (default)
    cci task run writeback_ux_templates -o dry_run false --org drotest
    cci task run writeback_ux_templates \
        -o metadata_name RLM_Order_Record_Page.flexipage-meta.xml \
        -o dry_run false --org drotest
"""
import copy
import json
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    from cumulusci.core.tasks import BaseTask
    from cumulusci.core.exceptions import TaskOptionsError
except ImportError:
    BaseTask = object
    TaskOptionsError = Exception

try:
    import yaml
except ImportError:
    yaml = None

try:
    from tasks.rlm_ux_assembly import (
        AssembleAndDeployUX,
        SF_NS,
        SF_NS_TAG,
        _find_elem,
        _findall_elem,
        _load_yaml,
        _write_xml,
    )
except ImportError:
    AssembleAndDeployUX = None
    SF_NS = "http://soap.sforce.com/2006/04/metadata"
    SF_NS_TAG = f"{{{SF_NS}}}"

ET.register_namespace("", SF_NS)


class WriteBackUXTemplates(BaseTask):
    """
    Reverse-applies active feature patches against org-retrieved flexipages
    and writes the result as updated base templates.

    new_base = org_state - reverse(patches)
    """

    task_options = {
        "metadata_name": {
            "description": (
                "Specific file to write back, e.g. "
                "'RLM_Order_Record_Page.flexipage-meta.xml'. "
                "Processes all flexipages when omitted."
            ),
            "required": False,
        },
        "metadata_type": {
            "description": (
                "Metadata type to process: 'all', 'flexipages', or "
                "'layouts'. Defaults to 'all'."
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
        "dry_run": {
            "description": (
                "When true (default), logs what would change but does not "
                "write base templates. Set false to apply."
            ),
            "required": False,
        },
        "backup": {
            "description": (
                "When true (default), copies existing base templates to "
                "*.bak before overwriting. Only applies when dry_run is false."
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
        mtype = self.options.get("metadata_type", "all")
        if mtype not in ("all", "flexipages", "layouts"):
            raise TaskOptionsError(
                f"metadata_type must be 'all', 'flexipages', or 'layouts', "
                f"got: '{mtype}'"
            )

    def _run_task(self):
        repo_root = Path(self.project_config.repo_root)
        org_path = repo_root / self.options.get("org_path", "unpackaged/post_ux")
        templates_path = repo_root / "templates"
        metadata_name = self.options.get("metadata_name")
        dry_run = str(self.options.get("dry_run", "true")).lower() in (
            "true", "1", "yes",
        )
        backup = str(self.options.get("backup", "true")).lower() in (
            "true", "1", "yes",
        )

        features = self._get_features()
        self.logger.info(
            f"Write-back mode: {'DRY RUN' if dry_run else 'LIVE'}"
        )
        self.logger.info(
            "Active features: "
            + (", ".join(k for k, v in features.items() if v) or "none")
        )

        mtype = self.options.get("metadata_type", "all")
        results = []

        if mtype in ("all", "flexipages"):
            results.extend(self._writeback_flexipages(
                templates_path, org_path, features, metadata_name,
                dry_run, backup,
            ))

        if mtype in ("all", "layouts"):
            results.extend(self._writeback_layouts(
                templates_path, org_path, features, metadata_name,
                dry_run, backup,
            ))

        # Summary
        written = sum(1 for r in results if r.get("written"))
        skipped = sum(1 for r in results if not r.get("written"))
        self.logger.info(
            f"\nWrite-back complete: {written} written, {skipped} skipped "
            f"({'dry run' if dry_run else 'live'})"
        )

    # ------------------------------------------------------------------
    # Flexipages writeback
    # ------------------------------------------------------------------

    def _writeback_flexipages(
        self,
        templates_path: Path,
        org_path: Path,
        features: Dict[str, bool],
        metadata_name: Optional[str],
        dry_run: bool,
        backup: bool,
    ) -> List[Dict[str, Any]]:
        base_dir = templates_path / "flexipages" / "base"
        patches_dir = templates_path / "flexipages" / "patches"
        standalone_dir = templates_path / "flexipages" / "standalone"
        org_dir = org_path / "flexipages"

        if not org_dir.exists():
            self.logger.error(
                f"Org flexipages directory not found: {org_dir}. "
                "Run retrieve_ux_from_org first."
            )
            return []

        page_sources = self._resolve_page_sources(
            base_dir, standalone_dir, features
        )

        org_files = sorted(
            f.name for f in org_dir.glob("*.flexipage-meta.xml")
        )
        if metadata_name and metadata_name.endswith(".flexipage-meta.xml"):
            org_files = [f for f in org_files if f == metadata_name]

        if not org_files:
            self.logger.warning("No org-retrieved flexipages to process.")
            return []

        feature_patch_order = [
            ("qb", "quantumbit"),
            ("qb", "utils"),
            ("billing", "billing"),
            ("billing_ui", "billing_ui"),
            ("payments", "payments"),
            ("qb", "approvals"),
            ("docgen", "docgen"),
            ("tso", "tso"),
            ("constraints", "constraints"),
            ("ramps", "ramp_builder"),
            ("collections", "collections"),
        ]

        results = []
        for fname in org_files:
            source = page_sources.get(fname)
            if source is None:
                self.logger.info(
                    f"  [new page]  {fname} — exists in org but not in "
                    "templates. Saving as new base template."
                )
                result = self._handle_new_page(
                    fname, org_dir, base_dir, dry_run
                )
                results.append(result)
                continue

            source_is_standalone = "standalone" in str(source)
            if source_is_standalone:
                self.logger.info(
                    f"  [standalone] {fname} — source is a standalone "
                    f"override ({source.parent.name}), writing back to "
                    "standalone source."
                )
                result = self._writeback_standalone(
                    fname, org_dir, source, patches_dir,
                    feature_patch_order, features, dry_run, backup,
                )
                results.append(result)
                continue

            result = self._writeback_base(
                fname, org_dir, base_dir, patches_dir,
                feature_patch_order, features, dry_run, backup,
            )
            results.append(result)

        if not dry_run:
            self._update_all_patches(
                org_dir, base_dir, patches_dir,
                feature_patch_order, features, org_files, page_sources,
                backup,
            )

        if not dry_run:
            self._verify_writeback(
                templates_path, org_path, features, metadata_name
            )

        return results

    # ------------------------------------------------------------------
    # Layouts writeback
    # ------------------------------------------------------------------

    def _writeback_layouts(
        self,
        templates_path: Path,
        org_path: Path,
        features: Dict[str, bool],
        metadata_name: Optional[str],
        dry_run: bool,
        backup: bool,
    ) -> List[Dict[str, Any]]:
        org_dir = org_path / "layouts"

        if not org_dir.exists():
            self.logger.info("No org-retrieved layouts to process.")
            return []

        # Layout tier resolution: last-wins (same as assembler)
        layout_tiers = [
            ("base", templates_path / "layouts" / "base", True),
            ("billing", templates_path / "layouts" / "billing",
             features.get("billing", False)),
            ("constraints", templates_path / "layouts" / "constraints",
             features.get("constraints", False)),
        ]

        # Build source map: fname → (tier_name, path)
        layout_sources: Dict[str, Tuple[str, Path]] = {}
        for tier_name, tier_dir, active in layout_tiers:
            if not active or not tier_dir.exists():
                continue
            for f in tier_dir.glob("*.layout-meta.xml"):
                layout_sources[f.name] = (tier_name, f)

        org_files = sorted(
            f.name for f in org_dir.glob("*.layout-meta.xml")
        )
        if metadata_name and metadata_name.endswith(".layout-meta.xml"):
            org_files = [f for f in org_files if f == metadata_name]

        if not org_files:
            self.logger.warning("No org-retrieved layouts to process.")
            return []

        results = []
        for fname in org_files:
            org_file = org_dir / fname
            source_info = layout_sources.get(fname)

            if source_info is None:
                # New layout — save to base
                dest = templates_path / "layouts" / "base" / fname
                self.logger.info(
                    f"  [layout:new] {fname} — saving to base"
                )
                if not dry_run:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(org_file), str(dest))
                results.append({"file": fname, "written": not dry_run,
                                "new": True})
                continue

            tier_name, dest_file = source_info
            self.logger.info(
                f"  [layout:{tier_name}] {fname} — updating template"
            )
            if not dry_run:
                if backup and dest_file.exists():
                    shutil.copy2(str(dest_file), str(dest_file) + ".bak")
                shutil.copy2(str(org_file), str(dest_file))
            results.append({"file": fname, "written": not dry_run,
                            "tier": tier_name})

        return results

    # ------------------------------------------------------------------
    # Page source resolution (mirrors assembler logic)
    # ------------------------------------------------------------------

    def _resolve_page_sources(
        self,
        base_dir: Path,
        standalone_dir: Path,
        features: Dict[str, bool],
    ) -> Dict[str, Path]:
        page_sources: Dict[str, Path] = {}

        if base_dir.exists():
            for f in sorted(base_dir.glob("*.flexipage-meta.xml")):
                page_sources[f.name] = f

        standalone_copy_order = [
            ("payments", features.get("payments", False)),
            ("billing", features.get("billing", False)),
            ("billing_ui", features.get("billing_ui", False)),
            ("quantumbit", features.get("qb", False)),
            ("tso", features.get("tso", False)),
            ("constraints", features.get("constraints", False)),
            ("utils", features.get("qb", False)),
            ("docgen", features.get("docgen", False)),
            ("approvals", features.get("qb", False)),
            ("collections", features.get("collections", False)),
        ]
        for feature_dir, active in standalone_copy_order:
            if not active:
                continue
            src_dir = standalone_dir / feature_dir
            if not src_dir.exists():
                continue
            for src_file in sorted(src_dir.glob("*.flexipage-meta.xml")):
                page_sources[src_file.name] = src_file

        return page_sources

    # ------------------------------------------------------------------
    # Write-back: base templates
    # ------------------------------------------------------------------

    def _writeback_base(
        self,
        fname: str,
        org_dir: Path,
        base_dir: Path,
        patches_dir: Path,
        feature_patch_order: List[Tuple[str, str]],
        features: Dict[str, bool],
        dry_run: bool,
        backup: bool,
    ) -> Dict[str, Any]:
        org_file = org_dir / fname
        dest_file = base_dir / fname
        page_stem = fname.replace(".flexipage-meta.xml", "")

        # Parse org XML
        root = ET.parse(str(org_file)).getroot()

        # Collect patches in forward order, then reverse
        patches_to_reverse: List[Tuple[str, Dict[str, Any]]] = []
        for flag, patch_feature in feature_patch_order:
            if not features.get(flag):
                continue
            patch_file = patches_dir / patch_feature / (page_stem + ".yml")
            if not patch_file.exists():
                continue
            patch_data = _load_yaml(patch_file)
            for patch in patch_data.get("patches", []):
                patches_to_reverse.append((patch_feature, patch))

        if not patches_to_reverse:
            self.logger.info(
                f"  [base]     {fname} — no active patches, "
                "copying org state directly to base."
            )
            if not dry_run:
                if backup and dest_file.exists():
                    shutil.copy2(str(dest_file), str(dest_file) + ".bak")
                _write_xml(root, dest_file)
            return {"file": fname, "written": not dry_run, "patches_reversed": 0}

        # Reverse patches in reverse order (last-applied reversed first)
        reversed_count = 0
        absent_count = 0
        for feature, patch in reversed(patches_to_reverse):
            result = _reverse_patch(root, patch, self.logger)
            if result == "removed":
                reversed_count += 1
                self.logger.info(
                    f"    reversed {patch.get('type')} from {feature}"
                )
            elif result == "absent":
                absent_count += 1
                self.logger.info(
                    f"    skipped {patch.get('type')} from {feature} "
                    "(already absent — duplicate fallback)"
                )
            else:
                self.logger.warning(
                    f"    FAILED to reverse {patch.get('type')} from "
                    f"{feature} — element not found in org XML"
                )

        self.logger.info(
            f"  [base]     {fname} — reversed {reversed_count}/"
            f"{len(patches_to_reverse)} patches"
            + (f" ({absent_count} duplicate fallback skips)" if absent_count else "")
        )

        if not dry_run:
            if backup and dest_file.exists():
                shutil.copy2(str(dest_file), str(dest_file) + ".bak")
            _write_xml(root, dest_file)

        return {
            "file": fname,
            "written": not dry_run,
            "patches_reversed": reversed_count,
            "patches_total": len(patches_to_reverse),
        }

    # ------------------------------------------------------------------
    # Write-back: standalone overrides
    # ------------------------------------------------------------------

    def _writeback_standalone(
        self,
        fname: str,
        org_dir: Path,
        source: Path,
        patches_dir: Path,
        feature_patch_order: List[Tuple[str, str]],
        features: Dict[str, bool],
        dry_run: bool,
        backup: bool,
    ) -> Dict[str, Any]:
        """Write back a standalone override page, reversing any patches."""
        org_file = org_dir / fname
        page_stem = fname.replace(".flexipage-meta.xml", "")

        root = ET.parse(str(org_file)).getroot()

        # Standalone pages can also have patches applied on top
        patches_to_reverse: List[Tuple[str, Dict[str, Any]]] = []
        for flag, patch_feature in feature_patch_order:
            if not features.get(flag):
                continue
            patch_file = patches_dir / patch_feature / (page_stem + ".yml")
            if not patch_file.exists():
                continue
            patch_data = _load_yaml(patch_file)
            for patch in patch_data.get("patches", []):
                patches_to_reverse.append((patch_feature, patch))

        reversed_count = 0
        for feature, patch in reversed(patches_to_reverse):
            result = _reverse_patch(root, patch, self.logger)
            if result in ("removed", "absent"):
                reversed_count += 1

        if not dry_run:
            if backup and source.exists():
                shutil.copy2(str(source), str(source) + ".bak")
            _write_xml(root, source)

        return {
            "file": fname,
            "written": not dry_run,
            "patches_reversed": reversed_count,
            "standalone": True,
        }

    # ------------------------------------------------------------------
    # New page (org-only)
    # ------------------------------------------------------------------

    def _handle_new_page(
        self,
        fname: str,
        org_dir: Path,
        base_dir: Path,
        dry_run: bool,
    ) -> Dict[str, Any]:
        org_file = org_dir / fname
        dest_file = base_dir / fname
        if not dry_run:
            root = ET.parse(str(org_file)).getroot()
            _write_xml(root, dest_file)
        return {"file": fname, "written": not dry_run, "new": True}

    # ------------------------------------------------------------------
    # Patch YAML update
    # ------------------------------------------------------------------

    def _update_all_patches(
        self,
        org_dir: Path,
        base_dir: Path,
        patches_dir: Path,
        feature_patch_order: List[Tuple[str, str]],
        features: Dict[str, bool],
        org_files: List[str],
        page_sources: Dict[str, Path],
        backup: bool,
    ) -> None:
        """Update patch YAML files so base + patches reproduces org state."""
        self.logger.info("\nUpdating patch files...")

        for fname in org_files:
            source = page_sources.get(fname)
            if source is None:
                continue
            source_is_standalone = "standalone" in str(source)

            page_stem = fname.replace(".flexipage-meta.xml", "")
            org_file = org_dir / fname
            # The source file for comparison — either the base or standalone
            if source_is_standalone:
                base_file = source
            else:
                base_file = base_dir / fname

            if not base_file.exists() or not org_file.exists():
                continue

            # Collect active patch files for this page
            active_patch_files: List[Tuple[str, str, Path]] = []
            for flag, patch_feature in feature_patch_order:
                if not features.get(flag):
                    continue
                pf = patches_dir / patch_feature / (page_stem + ".yml")
                if pf.exists():
                    active_patch_files.append((flag, patch_feature, pf))

            if not active_patch_files:
                continue

            # Serialize base and org for text-level comparison
            base_root = ET.parse(str(base_file)).getroot()
            ET.indent(base_root, space="    ")
            base_text = ET.tostring(base_root, encoding="unicode")

            org_root = ET.parse(str(org_file)).getroot()
            ET.indent(org_root, space="    ")
            org_text = ET.tostring(org_root, encoding="unicode")

            for flag, patch_feature, patch_path in active_patch_files:
                self._update_patch_file(
                    fname, base_text, org_text, base_root, org_root,
                    patch_path, patch_feature, backup,
                )

    def _update_patch_file(
        self,
        fname: str,
        base_text: str,
        org_text: str,
        base_root: ET.Element,
        org_root: ET.Element,
        patch_path: Path,
        patch_feature: str,
        backup: bool,
    ) -> None:
        """Update a single patch YAML file by extracting current org content."""
        patch_data = _load_yaml(patch_path)
        patches = patch_data.get("patches", [])
        if not patches:
            return

        updated = False
        for patch in patches:
            ptype = patch.get("type")

            if ptype == "insert_after_xml":
                new_xml = self._extract_insert_after_xml(
                    base_text, org_text, patch
                )
                if new_xml is not None and new_xml != patch.get("xml", ""):
                    patch["xml"] = new_xml
                    updated = True
                elif new_xml is None:
                    # Anchor found but no inserted content — patch region
                    # was removed from org. Mark for removal.
                    self.logger.info(
                        f"    [patch] {patch_feature}/{fname}: "
                        f"insert_after_xml content absent in org, "
                        f"removing patch entry"
                    )
                    patch["_remove"] = True
                    updated = True

            elif ptype == "insert_action":
                new_actions = self._extract_insert_actions(
                    base_root, org_root, patch
                )
                if new_actions is not None and new_actions != patch.get("actions", []):
                    patch["actions"] = new_actions
                    updated = True

            elif ptype == "add_display_field":
                # Single field — check if it exists in org
                field = patch.get("field", "")
                if not _field_exists_in_org(org_root, "displayFields", field):
                    self.logger.info(
                        f"    [patch] {patch_feature}/{fname}: "
                        f"display field '{field}' absent in org, "
                        f"removing patch entry"
                    )
                    patch["_remove"] = True
                    updated = True

            elif ptype == "add_facet_field":
                new_fields = self._extract_facet_fields(
                    base_root, org_root, patch
                )
                if new_fields is not None and new_fields != patch.get("fields", []):
                    if not new_fields:
                        patch["_remove"] = True
                    else:
                        patch["fields"] = new_fields
                    updated = True

            elif ptype == "add_component":
                # Check if component exists in org
                identifier = patch.get("identifier", patch.get("component", ""))
                if not _component_exists_in_org(org_root, identifier):
                    self.logger.info(
                        f"    [patch] {patch_feature}/{fname}: "
                        f"component '{identifier}' absent in org, "
                        f"removing patch entry"
                    )
                    patch["_remove"] = True
                    updated = True

        if not updated:
            return

        # Remove entries marked for deletion
        patches = [p for p in patches if not p.get("_remove")]

        if not patches:
            self.logger.info(
                f"    [patch] {patch_feature}/{fname}: all patches removed, "
                f"deleting patch file"
            )
            if backup:
                shutil.copy2(str(patch_path), str(patch_path) + ".bak")
            patch_path.unlink()
            return

        # Write updated YAML
        if backup:
            shutil.copy2(str(patch_path), str(patch_path) + ".bak")

        # Clean up internal markers
        for p in patches:
            p.pop("_remove", None)

        patch_data["patches"] = patches
        self._write_patch_yaml(patch_path, patch_data)
        self.logger.info(
            f"    [patch] {patch_feature}/{fname}: updated "
            f"({len(patches)} patches)"
        )

    def _extract_insert_after_xml(
        self,
        base_text: str,
        org_text: str,
        patch: Dict[str, Any],
    ) -> Optional[str]:
        """Extract the XML content that the org has after the anchor.

        Compares what follows the anchor in org vs base to isolate the
        inserted content. The org has: anchor + patch_content + base_continuation.
        We find where base_continuation starts in the org to extract patch_content.

        Returns:
            str  — the extracted XML fragment (may differ from current patch)
            None — anchor not found or no inserted content
        """
        anchor = patch.get("anchor", "")
        if not anchor:
            return None

        if anchor not in org_text or anchor not in base_text:
            return None

        org_pos = org_text.index(anchor) + len(anchor)
        base_pos = base_text.index(anchor) + len(anchor)

        base_after = base_text[base_pos:]
        org_after = org_text[org_pos:]

        if not base_after.strip():
            return None

        # Find a unique sync marker in the base continuation.
        # Generic tags like <flexiPageRegions> appear multiple times,
        # so we need a multi-line chunk that matches exactly once in org.
        sync_chunk = _find_sync_marker(base_after, org_text)

        if not sync_chunk:
            return None

        sync_idx = org_after.find(sync_chunk)
        if sync_idx < 0:
            return None

        # Everything between anchor and sync point = inserted content
        inserted = org_after[:sync_idx].strip("\n")

        if not inserted.strip():
            return None

        return inserted + "\n"

    def _extract_insert_actions(
        self,
        base_root: ET.Element,
        org_root: ET.Element,
        patch: Dict[str, Any],
    ) -> Optional[List[str]]:
        """Check if patch actions exist in org; return updated list or None."""
        current_actions = patch.get("actions", [])
        org_actions = set(_get_action_names(org_root))

        # Keep only those patch actions that exist in the org
        surviving = [a for a in current_actions if a in org_actions]
        if surviving == current_actions:
            return None  # No change needed
        return surviving if surviving else None

    def _extract_facet_fields(
        self,
        base_root: ET.Element,
        org_root: ET.Element,
        patch: Dict[str, Any],
    ) -> Optional[List[str]]:
        """Extract facet fields present in org but not in base."""
        facet_label = patch.get("facet", "")
        patch_fields = patch.get("fields", [])

        # Get field items from both base and org for the target facet
        base_fields = _get_facet_field_items(base_root, facet_label)
        org_fields = _get_facet_field_items(org_root, facet_label)

        # Patch fields = in org but not in base
        extra = [f for f in org_fields if f not in base_fields]
        # Only return the subset that overlaps with the original patch fields
        # (other patches may also add fields to this facet)
        relevant = [f for f in extra if f in patch_fields]
        return relevant

    @staticmethod
    def _write_patch_yaml(path: Path, data: Dict[str, Any]) -> None:
        """Write patch YAML preserving readability."""
        if yaml is None:
            raise ImportError("PyYAML is required for patch YAML writing")

        class _BlockStr(str):
            pass

        def _block_repr(dumper, data):
            if "\n" in data:
                return dumper.represent_scalar(
                    "tag:yaml.org,2002:str", data, style="|"
                )
            return dumper.represent_scalar("tag:yaml.org,2002:str", data)

        dumper = yaml.Dumper
        dumper.add_representer(_BlockStr, _block_repr)

        # Convert xml and anchor values to block strings
        for patch in data.get("patches", []):
            for key in ("xml", "anchor"):
                if key in patch and "\n" in str(patch[key]):
                    patch[key] = _BlockStr(patch[key])

        path.write_text(
            yaml.dump(
                data, Dumper=dumper, default_flow_style=False,
                sort_keys=False, allow_unicode=True, width=120,
            ),
            encoding="utf-8",
        )

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    def _verify_writeback(
        self,
        templates_path: Path,
        org_path: Path,
        features: Dict[str, bool],
        filter_name: Optional[str],
    ) -> None:
        """Re-assemble from updated templates and diff against org state."""
        self.logger.info("\nVerifying write-back (re-assemble + diff)...")

        with tempfile.TemporaryDirectory(prefix="rlm_wb_verify_") as tmpdir:
            tmp_path = Path(tmpdir)
            adapter = _AssemblerAdapter(self)
            result = AssembleAndDeployUX._assemble_flexipages(
                adapter, templates_path, tmp_path, features, filter_name,
            )
            assembled, skipped = (
                result if isinstance(result, tuple) else (result, [])
            )

            org_dir = org_path / "flexipages"
            asm_dir = tmp_path / "flexipages"
            drift_count = 0

            for entry in assembled:
                fname = entry["name"]
                asm_file = asm_dir / fname
                org_file = org_dir / fname

                if not org_file.exists():
                    continue

                asm_xml = _normalize_xml(
                    ET.parse(str(asm_file)).getroot()
                )
                org_xml = _normalize_xml(
                    ET.parse(str(org_file)).getroot()
                )

                if asm_xml != org_xml:
                    drift_count += 1
                    self.logger.warning(
                        f"  [verify] DRIFT REMAINS: {fname}"
                    )
                else:
                    self.logger.info(f"  [verify] OK: {fname}")

            if drift_count == 0:
                self.logger.info(
                    "Verification passed — templates reproduce org state."
                )
            else:
                self.logger.warning(
                    f"Verification found {drift_count} page(s) with "
                    "remaining drift. Review templates manually."
                )

    # ------------------------------------------------------------------
    # Feature flags
    # ------------------------------------------------------------------

    def _get_features(self) -> Dict[str, bool]:
        return AssembleAndDeployUX._get_feature_flags(self)


# ---------------------------------------------------------------------------
# Adapter for calling assembler methods
# ---------------------------------------------------------------------------


class _AssemblerAdapter:
    """
    Minimal stand-in providing attributes that AssembleAndDeployUX instance
    methods expect.
    """

    def __init__(self, parent_task: Any) -> None:
        self.project_config = parent_task.project_config
        self.logger = parent_task.logger

    def _apply_raw_xml_patch(
        self, root: ET.Element, patch: Dict[str, Any]
    ) -> None:
        AssembleAndDeployUX._apply_raw_xml_patch(self, root, patch)


# ---------------------------------------------------------------------------
# Reverse-patch operations
# ---------------------------------------------------------------------------


def _reverse_patch(
    root: ET.Element, patch: Dict[str, Any], logger=None
) -> str:
    """Apply the inverse of a single patch operation.

    Returns:
        "removed" — element found and removed
        "absent"  — element already absent (idempotent success,
                     e.g. another patch's reverse already removed it)
        "failed"  — reverse could not be applied
    """
    ptype = patch.get("type")

    if ptype == "insert_action":
        return "removed" if _reverse_insert_action(root, patch) else "absent"

    if ptype == "remove_action":
        # No-op: if a patch removes an action from the base, the base
        # already has it. The org state won't have it (it was removed),
        # so there's nothing to re-add during reverse.
        return "removed"

    if ptype == "add_display_field":
        return "removed" if _reverse_add_display_field(root, patch) else "absent"

    if ptype == "add_facet_field":
        return "removed" if _reverse_add_facet_field(root, patch) else "absent"

    if ptype == "add_component":
        return "removed" if _reverse_add_component(root, patch) else "absent"

    if ptype == "insert_after_xml":
        result = _reverse_insert_after_xml(root, patch, logger)
        if result is True:
            return "removed"
        elif result is None:
            return "absent"  # elements not found (possibly removed from org)
        else:
            return "failed"

    if logger:
        logger.warning(f"Unknown patch type for reverse: '{ptype}'")
    return "failed"


def _reverse_insert_action(root: ET.Element, patch: Dict[str, Any]) -> bool:
    """Remove actions that were inserted by an insert_action patch."""
    actions = patch.get("actions", [])
    if not actions:
        return True

    removed_any = False
    for ci_props in root.iter(f"{SF_NS_TAG}componentInstanceProperties"):
        name_el = _find_elem(ci_props, "name")
        if name_el is None or name_el.text != "actionNames":
            continue
        vlist = _find_elem(ci_props, "valueList")
        if vlist is None:
            continue
        for action in actions:
            for item in _findall_elem(vlist, "valueListItems"):
                val_el = _find_elem(item, "value")
                if val_el is not None and val_el.text == action:
                    vlist.remove(item)
                    removed_any = True
                    break
        return True  # found the actionNames list
    return removed_any


def _reverse_add_display_field(
    root: ET.Element, patch: Dict[str, Any]
) -> bool:
    """Remove a display field that was added by an add_display_field patch."""
    field = patch.get("field")
    if not field:
        return True

    for ci_props in root.iter(f"{SF_NS_TAG}componentInstanceProperties"):
        name_el = _find_elem(ci_props, "name")
        if name_el is None or name_el.text != "displayFields":
            continue
        vlist = _find_elem(ci_props, "valueList")
        if vlist is None:
            continue
        for item in _findall_elem(vlist, "valueListItems"):
            val_el = _find_elem(item, "value")
            if val_el is not None and val_el.text == field:
                vlist.remove(item)
                return True
    return False


def _reverse_add_facet_field(
    root: ET.Element, patch: Dict[str, Any]
) -> bool:
    """Remove field instances that were added by an add_facet_field patch."""
    fields = patch.get("fields", [])
    if not fields:
        return True

    target_items = set(f"Record.{f}" for f in fields)
    removed_any = False

    for region in _findall_elem(root, "flexiPageRegions"):
        type_el = _find_elem(region, "type")
        if type_el is None or type_el.text != "Facet":
            continue
        for item in list(_findall_elem(region, "itemInstances")):
            fi = _find_elem(item, "fieldInstance")
            if fi is None:
                continue
            field_item_el = _find_elem(fi, "fieldItem")
            if (
                field_item_el is not None
                and field_item_el.text in target_items
            ):
                region.remove(item)
                removed_any = True

    return removed_any


def _reverse_add_component(
    root: ET.Element, patch: Dict[str, Any]
) -> bool:
    """Remove a component that was added by an add_component patch."""
    identifier = patch.get("identifier", patch.get("component", ""))
    if not identifier:
        return True

    region_name = patch.get("region")

    for region in _findall_elem(root, "flexiPageRegions"):
        name_el = _find_elem(region, "name")
        if region_name and (
            name_el is None or name_el.text != region_name
        ):
            continue
        for item in list(_findall_elem(region, "itemInstances")):
            ci = _find_elem(item, "componentInstance")
            if ci is None:
                continue
            id_el = _find_elem(ci, "identifier")
            if id_el is not None and id_el.text == identifier:
                region.remove(item)
                return True

    return False


def _reverse_insert_after_xml(
    root: ET.Element, patch: Dict[str, Any], logger=None
):
    """
    Remove elements that were added by an insert_after_xml patch.

    Parses the XML fragment from the patch, extracts identifiable elements
    (region names, component identifiers, field identifiers, action values),
    and removes matching elements from the tree.

    Returns:
        True  — elements found and removed
        None  — elements not found (e.g. removed from org)
        False — parse error or other failure
    """
    xml_fragment = patch.get("xml", "")
    if not xml_fragment:
        return True

    # Parse the fragment to identify what it added
    # Wrap in a root element so it parses as valid XML
    try:
        wrapper = ET.fromstring(
            f'<wrapper xmlns="{SF_NS}">{xml_fragment}</wrapper>'
        )
    except ET.ParseError:
        if logger:
            logger.warning(
                "insert_after_xml reverse: could not parse XML fragment"
            )
        return False

    removed_any = False

    # Case 1: Fragment contains flexiPageRegions — remove by <name>
    fragment_regions = _findall_elem(wrapper, "flexiPageRegions")
    if fragment_regions:
        fragment_region_names = set()
        for fr in fragment_regions:
            name_el = _find_elem(fr, "name")
            if name_el is not None and name_el.text:
                fragment_region_names.add(name_el.text)

        for region in list(_findall_elem(root, "flexiPageRegions")):
            name_el = _find_elem(region, "name")
            if (
                name_el is not None
                and name_el.text in fragment_region_names
            ):
                root.remove(region)
                removed_any = True

    # Case 2: Fragment contains itemInstances — remove by identifier
    fragment_items = _findall_elem(wrapper, "itemInstances")
    if fragment_items:
        fragment_identifiers = set()
        for fi in fragment_items:
            ci = _find_elem(fi, "componentInstance")
            if ci is not None:
                id_el = _find_elem(ci, "identifier")
                if id_el is not None and id_el.text:
                    fragment_identifiers.add(id_el.text)
            # Also check for fieldInstance identifiers
            field_inst = _find_elem(fi, "fieldInstance")
            if field_inst is not None:
                id_el = _find_elem(field_inst, "identifier")
                if id_el is not None and id_el.text:
                    fragment_identifiers.add(id_el.text)

        if fragment_identifiers:
            for region in _findall_elem(root, "flexiPageRegions"):
                for item in list(_findall_elem(region, "itemInstances")):
                    ci = _find_elem(item, "componentInstance")
                    if ci is not None:
                        id_el = _find_elem(ci, "identifier")
                        if (
                            id_el is not None
                            and id_el.text in fragment_identifiers
                        ):
                            region.remove(item)
                            removed_any = True
                            continue
                    fi = _find_elem(item, "fieldInstance")
                    if fi is not None:
                        id_el = _find_elem(fi, "identifier")
                        if (
                            id_el is not None
                            and id_el.text in fragment_identifiers
                        ):
                            region.remove(item)
                            removed_any = True

    # Case 3: Fragment contains valueListItems — remove by value
    fragment_values = _findall_elem(wrapper, "valueListItems")
    if fragment_values and not fragment_regions and not fragment_items:
        # Only process as standalone valueListItems if there are no
        # regions or items (otherwise the values are nested inside them
        # and were already handled above)
        target_values = set()
        for fv in fragment_values:
            val_el = _find_elem(fv, "value")
            if val_el is not None and val_el.text:
                target_values.add(val_el.text)

        if target_values:
            for ci_props in root.iter(
                f"{SF_NS_TAG}componentInstanceProperties"
            ):
                vlist = _find_elem(ci_props, "valueList")
                if vlist is None:
                    continue
                for item in list(_findall_elem(vlist, "valueListItems")):
                    val_el = _find_elem(item, "value")
                    if (
                        val_el is not None
                        and val_el.text in target_values
                    ):
                        vlist.remove(item)
                        removed_any = True

    return True if removed_any else None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_sync_marker(text: str, org_text: str) -> Optional[str]:
    """Find a multi-line chunk from *text* (base continuation) that uniquely
    locates where base content resumes in *org_text*.

    Strategy: walk forward through base continuation lines, accumulating a
    multi-line chunk. Once the chunk contains a unique identifier tag AND
    matches exactly once in the org text, return it.
    """
    unique_tag_re = re.compile(
        r"<(?:name|identifier|componentName|fieldItem)>"
    )
    lines = text.split("\n")
    non_blank = [(i, lines[i]) for i in range(len(lines)) if lines[i].strip()]

    if not non_blank:
        return None

    # Build progressively longer chunks starting from the first non-blank line
    for end_idx in range(len(non_blank)):
        chunk_lines = [lines[i] for i, _ in non_blank[: end_idx + 1]]
        chunk = "\n".join(chunk_lines)
        has_unique = bool(unique_tag_re.search(chunk))

        if has_unique and chunk.strip():
            # Check it matches exactly once in the org
            count = org_text.count(chunk)
            if count == 1:
                return chunk
            # If not unique, keep growing

    # Fallback: use the longest chunk we built even without unique tag
    if non_blank:
        for end_idx in range(min(5, len(non_blank)), 0, -1):
            chunk_lines = [lines[i] for i, _ in non_blank[:end_idx]]
            chunk = "\n".join(chunk_lines)
            if chunk.strip() and org_text.count(chunk) == 1:
                return chunk

    return None


def _normalize_xml(element: ET.Element) -> str:
    """Canonical string for XML comparison — strips whitespace-only text."""
    clone = copy.deepcopy(element)
    ET.indent(clone, space="    ")
    return re.sub(
        r">\s+<", "><", ET.tostring(clone, encoding="unicode")
    ).strip()


def _get_action_names(root: ET.Element) -> List[str]:
    """Extract all action values from actionNames valueLists."""
    actions = []
    for ci_props in root.iter(f"{SF_NS_TAG}componentInstanceProperties"):
        name_el = _find_elem(ci_props, "name")
        if name_el is None or name_el.text != "actionNames":
            continue
        vlist = _find_elem(ci_props, "valueList")
        if vlist is None:
            continue
        for item in _findall_elem(vlist, "valueListItems"):
            val_el = _find_elem(item, "value")
            if val_el is not None and val_el.text:
                actions.append(val_el.text)
    return actions


def _get_facet_field_items(root: ET.Element, facet_label: str) -> List[str]:
    """Extract field names from a facet region, stripping 'Record.' prefix."""
    fields = []
    for region in _findall_elem(root, "flexiPageRegions"):
        type_el = _find_elem(region, "type")
        if type_el is None or type_el.text != "Facet":
            continue
        # Check if this facet matches the label (by looking at tab titles
        # that reference it, or by checking field content)
        for item in _findall_elem(region, "itemInstances"):
            fi = _find_elem(item, "fieldInstance")
            if fi is None:
                continue
            field_item_el = _find_elem(fi, "fieldItem")
            if field_item_el is not None and field_item_el.text:
                fname = field_item_el.text
                if fname.startswith("Record."):
                    fname = fname[7:]
                fields.append(fname)
    return fields


def _field_exists_in_org(
    root: ET.Element, prop_name: str, field_value: str
) -> bool:
    """Check if a field value exists in a named componentInstanceProperties valueList."""
    for ci_props in root.iter(f"{SF_NS_TAG}componentInstanceProperties"):
        name_el = _find_elem(ci_props, "name")
        if name_el is None or name_el.text != prop_name:
            continue
        vlist = _find_elem(ci_props, "valueList")
        if vlist is None:
            continue
        for item in _findall_elem(vlist, "valueListItems"):
            val_el = _find_elem(item, "value")
            if val_el is not None and val_el.text == field_value:
                return True
    return False


def _component_exists_in_org(root: ET.Element, identifier: str) -> bool:
    """Check if a component with given identifier exists in the tree."""
    for ci in root.iter(f"{SF_NS_TAG}componentInstance"):
        id_el = _find_elem(ci, "identifier")
        if id_el is not None and id_el.text == identifier:
            return True
    return False
