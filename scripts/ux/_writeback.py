"""
UX template writeback — reverse-applies active feature patches against
org-retrieved flexipages and writes the result as updated base templates.

The assembler invariant is: base + patches = deployed state.
Write-back computes:         new_base = org_state - patches.

This prevents double-application of non-idempotent patches (insert_after_xml)
on the next assembly run.

Requires ``ux_tool.py retrieve`` to have populated ``unpackaged/post_ux/`` with
the org's current flexipage state. Dry run by default: nothing under
``templates/`` changes unless ``dry_run=False`` (``ux_tool.py writeback --apply``).
"""
import copy
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    import yaml
except ImportError:
    yaml = None

from scripts.ux._assemble import (
    SF_NS,
    SF_NS_TAG,
    _action_name,
    _find_elem,
    _findall_elem,
    _get_facet_field_items,
    _local_tag,
    _write_xml,
    validate_selection,
)
from scripts.ux._context import UxContext, UxOptionError
from scripts.ux._diff import org_flexipage_files
from scripts.ux._flags import (
    FLEXIPAGE_SUFFIX,
    SALES_TXN_LINE_EDITOR_IDENTIFIER,
    active_patch_files,
    load_yaml,
    resolve_flexipage_sources,
)

ET.register_namespace("", SF_NS)


class UxWriteback:
    """
    Reverse-applies active feature patches against org-retrieved flexipages
    and writes the result as updated base templates.

    new_base = org_state - reverse(patches)
    """

    def __init__(self, ctx: UxContext):
        self.ctx = ctx
        self.logger = ctx.logger

    def run(
        self,
        org_path: Path,
        metadata_name: Optional[str] = None,
        dry_run: bool = True,
    ) -> List[Dict[str, Any]]:
        """Write back (or, with ``dry_run``, report) template changes; return per-item results."""
        validate_selection("flexipages", metadata_name, ("flexipages",))
        org_path = Path(org_path)
        templates_path = self.ctx.templates_path
        features = self.ctx.features
        self.logger.info(
            f"Write-back mode: {'DRY RUN' if dry_run else 'LIVE'}"
        )
        self.logger.info(
            "Active features: "
            + (", ".join(k for k, v in features.items() if v) or "none")
        )

        results = self._writeback_flexipages(
            templates_path, org_path, features, metadata_name, dry_run,
        )

        # Summary
        written = sum(1 for r in results if r.get("written"))
        skipped = sum(1 for r in results if not r.get("written"))
        self.logger.info(
            f"\nWrite-back complete: {written} written, {skipped} skipped "
            f"({'dry run' if dry_run else 'live'})"
        )
        return results

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
    ) -> List[Dict[str, Any]]:
        base_dir = templates_path / "flexipages" / "base"
        patches_dir = templates_path / "flexipages" / "patches"
        standalone_dir = templates_path / "flexipages" / "standalone"
        org_dir = org_path / "flexipages"

        page_sources = resolve_flexipage_sources(base_dir, standalone_dir, features)

        org_files = org_flexipage_files(org_path)
        if metadata_name:
            if metadata_name not in org_files:
                raise UxOptionError(f"'{metadata_name}' not found in {org_dir}.")
            org_files = [metadata_name]

        results = []
        for fname in org_files:
            source = page_sources.get(fname)
            if source is None:
                self.logger.info(
                    f"  [new page]  {fname} — exists in org but not in "
                    "templates. Saving as new base template."
                )
                results.append(self._handle_new_page(fname, org_dir, base_dir, dry_run))
                continue
            results.append(self._writeback_page(
                fname, org_dir, source, patches_dir, features, dry_run,
                standalone=standalone_dir in source.parents,
            ))

        if not dry_run:
            self._update_all_patches(
                org_dir, patches_dir,
                features, org_files, page_sources,
            )

        return results

    # ------------------------------------------------------------------
    # Page source resolution (mirrors assembler logic)
    # ------------------------------------------------------------------

    def _writeback_page(
        self,
        fname: str,
        org_dir: Path,
        source: Path,
        patches_dir: Path,
        features: Dict[str, bool],
        dry_run: bool,
        standalone: bool,
    ) -> Dict[str, Any]:
        """Reverse the active patches out of the org page and write it over ``source``,
        the page's template (a base page or an active standalone override)."""
        kind = "standalone" if standalone else "base"
        root = ET.parse(str(org_dir / fname)).getroot()
        template_root = ET.parse(str(source)).getroot()
        page_stem = fname[: -len(FLEXIPAGE_SUFFIX)]

        patches_to_reverse: List[Tuple[str, Dict[str, Any]]] = [
            (patch_feature, patch)
            for patch_feature, patch_file in active_patch_files(patches_dir, page_stem, features)
            for patch in load_yaml(patch_file).get("patches", [])
        ]

        # Reverse patches in reverse order (last-applied reversed first)
        reversed_count = 0
        absent_count = 0
        for feature, patch in reversed(patches_to_reverse):
            result = _reverse_patch(root, patch, self.logger, template_root)
            if result == "removed":
                reversed_count += 1
                self.logger.info(f"    reversed {patch.get('type')} from {feature}")
            elif result == "absent":
                absent_count += 1
                self.logger.info(
                    f"    skipped {patch.get('type')} from {feature} (already absent)"
                )
            else:
                self.logger.warning(
                    f"    FAILED to reverse {patch.get('type')} from "
                    f"{feature} — element not found in org XML"
                )

        self.logger.info(
            f"  [{kind}] {fname} ({source.parent.name}) — reversed "
            f"{reversed_count}/{len(patches_to_reverse)} patches"
            + (f" ({absent_count} already absent)" if absent_count else "")
        )

        if not dry_run:
            _write_xml(root, source)

        return {
            "file": fname,
            "written": not dry_run,
            "patches_reversed": reversed_count,
            "patches_total": len(patches_to_reverse),
            "standalone": standalone,
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
        patches_dir: Path,
        features: Dict[str, bool],
        org_files: List[str],
        page_sources: Dict[str, Path],
    ) -> None:
        """Update patch YAML files so base + patches reproduces org state."""
        self.logger.info("\nUpdating patch files...")

        for fname in org_files:
            source = page_sources.get(fname)
            if source is None:
                continue
            page_stem = fname[: -len(FLEXIPAGE_SUFFIX)]
            org_file = org_dir / fname
            # Compare against the page's template (base or standalone), which
            # writeback has just regenerated.
            base_file = source
            if not base_file.exists() or not org_file.exists():
                continue

            patch_files = active_patch_files(patches_dir, page_stem, features)
            if not patch_files:
                continue

            # Serialize base and org for text-level comparison
            base_root = ET.parse(str(base_file)).getroot()
            ET.indent(base_root, space="    ")
            base_text = ET.tostring(base_root, encoding="unicode")

            org_root = ET.parse(str(org_file)).getroot()
            ET.indent(org_root, space="    ")
            org_text = ET.tostring(org_root, encoding="unicode")

            for patch_feature, patch_path in patch_files:
                self._update_patch_file(
                    fname, base_text, org_text, base_root, org_root,
                    patch_path, patch_feature,
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
    ) -> None:
        """Update a single patch YAML file by extracting current org content."""
        patch_data = load_yaml(patch_path)
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
                if new_xml is not None and not _same_xml_fragment(
                    new_xml, patch.get("xml", "")
                ):
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
                if new_actions is not None:
                    if not new_actions:
                        patch["_remove"] = True
                    else:
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

            elif ptype == "add_sales_txn_line_editor_field":
                new_fields = self._extract_sales_txn_line_editor_fields(
                    org_root, patch
                )
                if new_fields is not None:
                    if not new_fields:
                        patch["_remove"] = True
                    elif "fields" in patch:
                        patch["fields"] = new_fields
                    elif len(new_fields) == 1:
                        patch["field"] = new_fields[0]
                    else:
                        patch.pop("field", None)
                        patch["fields"] = new_fields
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
            patch_path.unlink()
            return

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
    ) -> Optional[List[Any]]:
        """Patch actions still present in the org; None when all of them are."""
        current_actions = patch.get("actions", [])
        org_actions = set(_get_action_names(org_root))

        # Keep only those patch actions that exist in the org. Entries are a
        # bare name or a {name, visibility} dict; a survivor keeps its shape.
        surviving = [a for a in current_actions if _action_name(a) in org_actions]
        if surviving == current_actions:
            return None  # No change needed
        return surviving

    def _extract_facet_fields(
        self,
        base_root: ET.Element,
        org_root: ET.Element,
        patch: Dict[str, Any],
    ) -> Optional[List[str]]:
        """Extract facet fields present in org but not in base."""
        patch_fields = patch.get("fields", [])

        # Field items across every Facet region of base and org
        base_fields = set(_get_facet_field_items(base_root))
        org_fields = _get_facet_field_items(org_root)

        # Patch fields = in org but not in base
        extra = [f for f in org_fields if f not in base_fields]
        # Only return the subset that overlaps with the original patch fields
        # (other patches may also add fields to this facet)
        relevant = [f for f in extra if f in patch_fields]
        return relevant

    def _extract_sales_txn_line_editor_fields(
        self,
        org_root: ET.Element,
        patch: Dict[str, Any],
    ) -> Optional[List[str]]:
        """Keep only patched Line Editor fields still present in the org state."""
        patch_fields = _patch_field_values(patch)
        if not patch_fields:
            return None

        component_identifier = patch.get(
            "component_identifier", SALES_TXN_LINE_EDITOR_IDENTIFIER
        )
        prop_name = patch.get("property", "displayFields")
        org_items = _get_component_value_list_items(
            org_root, component_identifier, prop_name
        )
        if org_items is None:
            # Component/property/valueList not found in the org state — cannot
            # determine which fields survive, so leave the patch unchanged rather
            # than dropping all of its fields (the org may use a different
            # component identifier or property name).
            return None
        org_fields = set(org_items)
        surviving = [field for field in patch_fields if field in org_fields]
        if surviving == patch_fields:
            return None
        return surviving

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


# ---------------------------------------------------------------------------
# Reverse-patch operations
# ---------------------------------------------------------------------------


def _reverse_patch(
    root: ET.Element,
    patch: Dict[str, Any],
    logger=None,
    template_root: Optional[ET.Element] = None,
) -> str:
    """Apply the inverse of a single patch operation.

    ``template_root`` is the page's current template. An insert_action patch
    skips actions the template already has, so its reverse must keep them.

    Returns:
        "removed" — element found and removed
        "absent"  — element already absent (idempotent success,
                     e.g. another patch's reverse already removed it)
        "failed"  — reverse could not be applied
    """
    ptype = patch.get("type")

    if ptype == "insert_action":
        keep = set(_get_action_names(template_root)) if template_root is not None else set()
        return "removed" if _reverse_insert_action(root, patch, keep) else "absent"

    if ptype == "remove_action":
        # No-op: if a patch removes an action from the base, the base
        # already has it. The org state won't have it (it was removed),
        # so there's nothing to re-add during reverse.
        return "removed"

    if ptype == "add_display_field":
        return "removed" if _reverse_add_display_field(root, patch) else "absent"

    if ptype == "add_sales_txn_line_editor_field":
        return (
            "removed"
            if _reverse_add_sales_txn_line_editor_field(root, patch)
            else "absent"
        )

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


def _reverse_insert_action(
    root: ET.Element, patch: Dict[str, Any], keep: Iterable[str] = ()
) -> bool:
    """Remove the actions an insert_action patch inserted; True if any were removed.

    Mirrors the forward patch: it targets the actionNames list holding the
    ``after`` anchor and never inserts an action already present, so names in
    ``keep`` (the template's own actions) are left alone.
    """
    names = {_action_name(a) for a in patch.get("actions", [])} - set(keep)
    anchor = patch.get("after")
    for ci_props in root.iter(f"{SF_NS_TAG}componentInstanceProperties"):
        name_el = _find_elem(ci_props, "name")
        if name_el is None or name_el.text != "actionNames":
            continue
        vlist = _find_elem(ci_props, "valueList")
        if vlist is None:
            continue
        items = [
            (item, _find_elem(item, "value"))
            for item in _findall_elem(vlist, "valueListItems")
        ]
        if anchor and not any(v is not None and v.text == anchor for _, v in items):
            continue
        removed = [item for item, v in items if v is not None and v.text in names]
        for item in removed:
            vlist.remove(item)
        return bool(removed)
    return False


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


def _reverse_add_sales_txn_line_editor_field(
    root: ET.Element, patch: Dict[str, Any]
) -> bool:
    """Remove fields added to a Sales Transaction Line Editor valueList."""
    fields = _patch_field_values(patch)
    if not fields:
        return True

    component_identifier = patch.get(
        "component_identifier", SALES_TXN_LINE_EDITOR_IDENTIFIER
    )
    prop_name = patch.get("property", "displayFields")
    return _remove_component_value_list_items(
        root, component_identifier, prop_name, fields
    )


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

    # Case 4: any other element (e.g. a <visibilityRule> inserted after a
    # component's <identifier>) — remove a structurally identical sibling of
    # the anchor element.
    handled = {"flexiPageRegions", "itemInstances", "valueListItems"}
    others = [el for el in wrapper if _local_tag(el) not in handled]
    if others and _remove_anchor_siblings(root, patch.get("anchor", ""), others):
        removed_any = True

    return True if removed_any else None


_SIMPLE_ELEMENT_RE = re.compile(r"^\s*<(\w+)>([^<]*)</\1>\s*$")


def _remove_anchor_siblings(
    root: ET.Element, anchor: str, fragment_elements: List[ET.Element]
) -> bool:
    """Remove each fragment element from the parent of the anchor element.

    Only anchors that are one complete simple element (``<tag>text</tag>``)
    can be located in the tree; other anchors are left alone, so nothing is
    removed on a guess.
    """
    match = _SIMPLE_ELEMENT_RE.match(anchor or "")
    if not match:
        return False
    anchor_tag, anchor_text = match.group(1), match.group(2).strip()
    wanted = [_normalize_xml(el) for el in fragment_elements]

    removed_any = False
    for parent in root.iter():
        children = list(parent)
        if not any(
            _local_tag(c) == anchor_tag and (c.text or "").strip() == anchor_text
            for c in children
        ):
            continue
        for target in wanted:
            for child in children:
                if child in parent and _normalize_xml(child) == target:
                    parent.remove(child)
                    removed_any = True
                    break
    return removed_any


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


def _same_xml_fragment(a: str, b: str) -> bool:
    """True when two XML fragments differ only in whitespace/indentation."""
    try:
        wrapped = [
            ET.fromstring(f'<wrapper xmlns="{SF_NS}">{x}</wrapper>') for x in (a, b)
        ]
    except ET.ParseError:
        return a.strip() == b.strip()
    return _normalize_xml(wrapped[0]) == _normalize_xml(wrapped[1])


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


def _patch_field_values(patch: Dict[str, Any]) -> List[str]:
    """Normalize a patch that accepts either `field` or `fields`."""
    fields = patch.get("fields")
    if fields:
        return [field for field in fields if field]
    field = patch.get("field")
    return [field] if field else []


def _get_component_value_list_items(
    root: ET.Element,
    component_identifier: str,
    prop_name: str,
) -> Optional[List[str]]:
    """Return valueList values for a property on a specific component identifier.

    Returns ``None`` when the component identifier, the property, or its
    ``valueList`` cannot be located ("cannot determine" — distinct from a
    valueList that exists but is empty, which returns ``[]``). Callers must treat
    ``None`` as "leave unchanged", not "the org has no fields", so a patch is not
    silently dropped when the org uses a different component identifier/property.
    """
    for ci in root.iter(f"{SF_NS_TAG}componentInstance"):
        id_el = _find_elem(ci, "identifier")
        if id_el is None or id_el.text != component_identifier:
            continue

        for ci_props in _findall_elem(ci, "componentInstanceProperties"):
            name_el = _find_elem(ci_props, "name")
            if name_el is None or name_el.text != prop_name:
                continue
            vlist = _find_elem(ci_props, "valueList")
            if vlist is None:
                return None
            return [
                val_el.text
                for item in _findall_elem(vlist, "valueListItems")
                for val_el in [_find_elem(item, "value")]
                if val_el is not None and val_el.text
            ]

    return None


def _remove_component_value_list_items(
    root: ET.Element,
    component_identifier: str,
    prop_name: str,
    values: List[str],
) -> bool:
    """Remove matching valueListItems from a property on a specific component."""
    values_to_remove = set(values)
    removed_any = False

    for ci in root.iter(f"{SF_NS_TAG}componentInstance"):
        id_el = _find_elem(ci, "identifier")
        if id_el is None or id_el.text != component_identifier:
            continue

        for ci_props in _findall_elem(ci, "componentInstanceProperties"):
            name_el = _find_elem(ci_props, "name")
            if name_el is None or name_el.text != prop_name:
                continue
            vlist = _find_elem(ci_props, "valueList")
            if vlist is None:
                return False
            for item in list(_findall_elem(vlist, "valueListItems")):
                val_el = _find_elem(item, "value")
                if val_el is not None and val_el.text in values_to_remove:
                    vlist.remove(item)
                    removed_any = True
            return removed_any

    return removed_any


def _component_exists_in_org(root: ET.Element, identifier: str) -> bool:
    """Check if a component with given identifier exists in the tree."""
    for ci in root.iter(f"{SF_NS_TAG}componentInstance"):
        id_el = _find_elem(ci, "identifier")
        if id_el is not None and id_el.text == identifier:
            return True
    return False
