"""
AssembleAndDeployUX — CumulusCI task for late-stage UX metadata assembly.

Reads base templates and feature-conditional YAML patches from the templates/
directory, assembles the final metadata for each active feature, writes the
output to unpackaged/post_ux/ (git-tracked), and optionally deploys in a
single sf project deploy start call.

Supported metadata types:
  flexipages   — patch-based XML assembly (insert_action, add_display_field,
                  add_facet_field, add_component, raw insert_after_xml)
  layouts      — copy base + conditional overrides (billing, constraints)
  applications — copy from versioned templates based on active features
  profiles     — strip-and-build: base grants + feature layout patches

Usage examples:
    cci task run assemble_and_deploy_ux --org dev-sb0
    cci task run assemble_and_deploy_ux -o deploy false --org dev-sb0
    cci task run assemble_and_deploy_ux \\
        -o metadata_name RLM_Quote_Record_Page.flexipage-meta.xml --org dev-sb0
    cci task run assemble_and_deploy_ux \\
        -o metadata_type profiles -o deploy false --org dev-sb0
"""
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import xml.etree.ElementTree as ET

try:
    import yaml
except ImportError:
    yaml = None

try:
    from cumulusci.tasks.sfdx import SFDXBaseTask
    from cumulusci.core.exceptions import TaskOptionsError, CommandException
    from cumulusci.core.keychain import BaseProjectKeychain
    from cumulusci.core.utils import process_bool_arg
except ImportError:
    SFDXBaseTask = object
    TaskOptionsError = Exception
    CommandException = Exception
    BaseProjectKeychain = object

    def process_bool_arg(val):
        if isinstance(val, bool):
            return val
        return str(val).lower() in ("true", "1", "yes")

try:
    from tasks.rlm_ux_utils import get_ux_feature_flags, resolve_flexipage_sources, PERSONAS_PROFILES
except ImportError:
    from rlm_ux_utils import get_ux_feature_flags, resolve_flexipage_sources, PERSONAS_PROFILES


# Salesforce metadata XML namespace
SF_NS = "http://soap.sforce.com/2006/04/metadata"
SF_NS_TAG = f"{{{SF_NS}}}"

# Maps full source filename suffix → canonical metadata type key
SUFFIX_TO_TYPE: Dict[str, str] = {
    ".flexipage-meta.xml": "flexipages",
    ".layout-meta.xml": "layouts",
    ".app-meta.xml": "applications",
    ".profile-meta.xml": "profiles",
    ".compactLayout-meta.xml": "objects",
    ".listView-meta.xml": "objects",
    ".object-meta.xml": "objects",
}

VALID_TYPES: Set[str] = {"all", "flexipages", "layouts", "applications", "profiles", "objects"}

# Register default namespace so ElementTree serializes without ns0: prefix
ET.register_namespace("", SF_NS)


def _load_yaml(path: Path) -> Dict[str, Any]:
    if yaml is None:
        raise ImportError("PyYAML is required. Install with: pip install pyyaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _write_xml(root: ET.Element, dest: Path) -> None:
    """Write an ElementTree Element to a file with XML declaration."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(root, space="    ")
    tree = ET.ElementTree(root)
    tree.write(str(dest), encoding="unicode", xml_declaration=True)
    # ElementTree uses single quotes and writes encoding="us-ascii" in the
    # declaration when using encoding="unicode". Fix both to match Salesforce
    # convention: double quotes, UTF-8, and trailing newline.
    text = dest.read_text(encoding="utf-8")
    # Normalize the XML declaration to Salesforce convention (double quotes).
    # ET may produce: version='1.0', encoding='us-ascii'|'utf-8'|'UTF-8'
    text = text.replace("<?xml version='1.0'", '<?xml version="1.0"')
    for sq_enc in ("encoding='us-ascii'", "encoding='utf-8'", "encoding='UTF-8'"):
        if sq_enc in text:
            text = text.replace(sq_enc, 'encoding="UTF-8"')
            break
    # Re-encode quotes as &quot; inside <value> elements containing escaped
    # HTML (&lt;) or JSON ([{/{"}).  ET unescapes &quot; on parse since raw "
    # is valid in XML text, but Salesforce metadata expects &quot; in these
    # contexts (HTML attribute quotes, JSON property names/values).
    def _requote_value(m):
        content = m.group(2)
        if "&lt;" in content or content.lstrip().startswith(("[{", '{"')):
            content = content.replace('"', "&quot;")
        return m.group(1) + content + m.group(3)

    text = re.sub(r"(<value>)(.*?)(</value>)", _requote_value, text)
    if not text.endswith("\n"):
        text += "\n"
    dest.write_text(text, encoding="utf-8")


def _find_elem(parent: ET.Element, local_name: str) -> Optional[ET.Element]:
    return parent.find(f"{SF_NS_TAG}{local_name}")


def _findall_elem(parent: ET.Element, local_name: str) -> List[ET.Element]:
    return parent.findall(f"{SF_NS_TAG}{local_name}")


def _make_elem(local_name: str, text: Optional[str] = None) -> ET.Element:
    el = ET.Element(f"{SF_NS_TAG}{local_name}")
    if text is not None:
        el.text = text
    return el


def _sub_elem(parent: ET.Element, local_name: str, text: Optional[str] = None) -> ET.Element:
    el = ET.SubElement(parent, f"{SF_NS_TAG}{local_name}")
    if text is not None:
        el.text = text
    return el


# ---------------------------------------------------------------------------
# Flexipage XML patching helpers
# ---------------------------------------------------------------------------

def _get_action_values(root: ET.Element) -> List[str]:
    """Return all action values from the actionNames componentInstanceProperty."""
    for ci_props in root.iter(f"{SF_NS_TAG}componentInstanceProperties"):
        name_el = _find_elem(ci_props, "name")
        if name_el is None or name_el.text != "actionNames":
            continue
        vlist = _find_elem(ci_props, "valueList")
        if vlist is None:
            continue
        return [
            _find_elem(item, "value").text
            for item in _findall_elem(vlist, "valueListItems")
            if _find_elem(item, "value") is not None
        ]
    return []


def _patch_remove_action(root: ET.Element, action: str) -> bool:
    """Remove an action valueListItem by value. Returns True if removed."""
    for ci_props in root.iter(f"{SF_NS_TAG}componentInstanceProperties"):
        name_el = _find_elem(ci_props, "name")
        if name_el is None or name_el.text != "actionNames":
            continue
        vlist = _find_elem(ci_props, "valueList")
        if vlist is None:
            continue
        for item in _findall_elem(vlist, "valueListItems"):
            val_el = _find_elem(item, "value")
            if val_el is not None and val_el.text == action:
                vlist.remove(item)
                return True
    return False


def _patch_insert_action(root: ET.Element, anchor: str, actions: List[str]) -> bool:
    """Insert action valueListItems immediately after the anchor action.
    Skips actions already present anywhere in the list (idempotent)."""
    for ci_props in root.iter(f"{SF_NS_TAG}componentInstanceProperties"):
        name_el = _find_elem(ci_props, "name")
        if name_el is None or name_el.text != "actionNames":
            continue
        vlist = _find_elem(ci_props, "valueList")
        if vlist is None:
            continue
        children = list(vlist)
        existing = {
            _find_elem(item, "value").text
            for item in children
            if _find_elem(item, "value") is not None
        }
        for i, item in enumerate(children):
            val_el = _find_elem(item, "value")
            if val_el is not None and val_el.text == anchor:
                offset = 0
                for action in actions:
                    if action in existing:
                        continue  # already present, skip
                    new_item = _make_elem("valueListItems")
                    _sub_elem(new_item, "value", action)
                    vlist.insert(i + 1 + offset, new_item)
                    offset += 1
                return True
    return False


def _patch_add_display_field(root: ET.Element, field: str) -> bool:
    """Append a display field valueListItem to the displayFields valueList.
    Skips if the field is already present (idempotent)."""
    for ci_props in root.iter(f"{SF_NS_TAG}componentInstanceProperties"):
        name_el = _find_elem(ci_props, "name")
        if name_el is None or name_el.text != "displayFields":
            continue
        vlist = _find_elem(ci_props, "valueList")
        if vlist is None:
            continue
        existing = {
            _find_elem(item, "value").text
            for item in _findall_elem(vlist, "valueListItems")
            if _find_elem(item, "value") is not None
        }
        if field in existing:
            return True  # already present, nothing to do
        new_item = _make_elem("valueListItems")
        _sub_elem(new_item, "value", field)
        vlist.append(new_item)
        return True
    return False


def _make_field_instance_item(field_api_name: str, identifier: str) -> ET.Element:
    """Build an <itemInstances><fieldInstance>...<fieldItem>Record.FIELD</fieldItem>"""
    item = _make_elem("itemInstances")
    fi = _sub_elem(item, "fieldInstance")
    fip = _sub_elem(fi, "fieldInstanceProperties")
    _sub_elem(fip, "name", "uiBehavior")
    _sub_elem(fip, "value", "none")
    _sub_elem(fi, "fieldItem", f"Record.{field_api_name}")
    _sub_elem(fi, "identifier", identifier)
    return item


def _get_facet_field_items(root: ET.Element) -> Set[str]:
    """Collect all fieldItem values across all Facet flexiPageRegions."""
    result: Set[str] = set()
    for region in _findall_elem(root, "flexiPageRegions"):
        type_el = _find_elem(region, "type")
        if type_el is None or type_el.text != "Facet":
            continue
        for item in _findall_elem(region, "itemInstances"):
            fi = _find_elem(item, "fieldInstance")
            if fi is None:
                continue
            field_item_el = _find_elem(fi, "fieldItem")
            if field_item_el is not None and field_item_el.text:
                # Strip 'Record.' prefix for comparison
                val = field_item_el.text
                if val.startswith("Record."):
                    val = val[len("Record."):]
                result.add(val)
    return result


def _patch_add_facet_field(
    root: ET.Element,
    fields: List[str],
    after: Optional[str] = None,
    facet_label: Optional[str] = None,
) -> bool:
    """
    Insert fieldInstance itemInstances into a Facet flexiPageRegion.

    If `after` is given: find the itemInstances containing
    <fieldItem>Record.{after}</fieldItem> and insert the new items immediately
    after it within the same flexiPageRegion. Skips fields already present
    anywhere in any Facet region (idempotent).

    If only `facet_label` is given: navigate from the fieldSection label to
    its `columns` facet UUID and append to that facet region.
    """
    existing_fields = _get_facet_field_items(root)
    fields = [f for f in fields if f not in existing_fields]
    if not fields:
        return True  # all already present, nothing to do

    regions = _findall_elem(root, "flexiPageRegions")

    if after:
        for region in regions:
            items = _findall_elem(region, "itemInstances")
            for i, item in enumerate(items):
                fi = _find_elem(item, "fieldInstance")
                if fi is None:
                    continue
                field_item_el = _find_elem(fi, "fieldItem")
                if field_item_el is not None and field_item_el.text == f"Record.{after}":
                    for j, field in enumerate(fields):
                        identifier = f"Record{field}Field"
                        new_item = _make_field_instance_item(field, identifier)
                        region.insert(list(region).index(item) + 1 + j, new_item)
                    return True
        return False

    if facet_label:
        # Build a mapping: section label → columns facet UUID
        # Then find the flexiPageRegion with that UUID as its <name>
        label_to_columns: Dict[str, str] = {}
        for region in regions:
            for item in _findall_elem(region, "itemInstances"):
                ci = _find_elem(item, "componentInstance")
                if ci is None:
                    continue
                has_label_match = False
                columns_val = None
                for ci_prop in _findall_elem(ci, "componentInstanceProperties"):
                    name_el = _find_elem(ci_prop, "name")
                    val_el = _find_elem(ci_prop, "value")
                    if name_el is None or val_el is None:
                        continue
                    if name_el.text == "label" and val_el.text == facet_label:
                        has_label_match = True
                    if name_el.text == "columns":
                        columns_val = val_el.text
                if has_label_match and columns_val:
                    label_to_columns[facet_label] = columns_val

        if facet_label not in label_to_columns:
            return False

        target_uuid = label_to_columns[facet_label]
        for region in regions:
            name_el = _find_elem(region, "name")
            type_el = _find_elem(region, "type")
            if (
                name_el is not None
                and name_el.text == target_uuid
                and type_el is not None
                and type_el.text == "Facet"
            ):
                # Append before the <name> element (which is at the end)
                name_idx = list(region).index(name_el)
                for j, field in enumerate(fields):
                    identifier = f"Record{field}Field"
                    new_item = _make_field_instance_item(field, identifier)
                    region.insert(name_idx + j, new_item)
                return True

    return False


def _patch_add_component(
    root: ET.Element,
    region_name: str,
    component_name: str,
    properties: Dict[str, str],
    identifier: str,
    after_identifier: Optional[str] = None,
) -> bool:
    """
    Add a componentInstance to a named flexiPageRegion's itemInstances list.
    Inserts after `after_identifier` if given, else appends before the closing
    <name> element of the region.
    """
    regions = _findall_elem(root, "flexiPageRegions")
    for region in regions:
        name_el = _find_elem(region, "name")
        if name_el is None or name_el.text != region_name:
            continue
        items = _findall_elem(region, "itemInstances")

        new_ci = _make_elem("componentInstance")
        for prop_name, prop_val in properties.items():
            cip = _sub_elem(new_ci, "componentInstanceProperties")
            _sub_elem(cip, "name", prop_name)
            _sub_elem(cip, "value", prop_val)
        _sub_elem(new_ci, "componentName", component_name)
        _sub_elem(new_ci, "identifier", identifier)

        new_item = _make_elem("itemInstances")
        new_item.append(new_ci)

        if after_identifier:
            for i, item in enumerate(items):
                ci = _find_elem(item, "componentInstance")
                if ci is not None:
                    id_el = _find_elem(ci, "identifier")
                    if id_el is not None and id_el.text == after_identifier:
                        region.insert(list(region).index(item) + 1, new_item)
                        return True

        # Append before <name> element
        region_children = list(region)
        insert_before = region_children.index(name_el) if name_el in region_children else len(region_children)
        region.insert(insert_before, new_item)
        return True
    return False


def _patch_description(patch: Dict[str, Any]) -> str:
    """Return a short human-readable description of a patch for manifests."""
    ptype = patch.get("type", "")
    if ptype == "insert_action":
        actions = patch.get("actions", [])
        return f"insert actions: {', '.join(actions)}"
    if ptype == "remove_action":
        return f"remove action: {patch.get('action', '?')}"
    if ptype == "add_display_field":
        return f"add display field: {patch.get('field', '?')}"
    if ptype == "add_facet_field":
        fields = patch.get("fields", [])
        facet = patch.get("facet", "")
        return f"add fields to {facet}: {', '.join(fields)}"
    if ptype == "add_component":
        return f"add component: {patch.get('component', '?')}"
    if ptype == "insert_after_xml":
        anchor = patch.get("anchor", "")
        # Extract a recognizable identifier from the anchor
        for tag in ("identifier", "name", "value"):
            m = re.search(rf"<{tag}>(.*?)</{tag}>", anchor)
            if m:
                return f"insert XML after <{tag}>{m.group(1)}</{tag}>"
        return "insert XML block"
    return ptype


def _profile_patch_description(patch: Dict[str, Any]) -> str:
    """Return a short description of a profile patch for manifests."""
    ptype = patch.get("type", "")
    if ptype == "add_layout_assignment":
        return f"layout: {patch.get('layout', '?')}"
    if ptype == "add_app_visibility":
        return f"app: {patch.get('application', '?')}"
    return ptype


def _apply_flexipage_patch(root: ET.Element, patch: Dict[str, Any], logger=None) -> None:
    """Apply a single patch operation to a flexipage XML root element."""
    ptype = patch.get("type")
    log = logger.warning if logger else print

    if ptype == "remove_action":
        action = patch.get("action")
        ignore_missing = patch.get("ignore_missing", False)
        if not action:
            log(f"remove_action patch missing 'action': {patch}")
            return
        removed = _patch_remove_action(root, action)
        if not removed and not ignore_missing and logger:
            logger.warning(f"remove_action: action '{action}' not found in flexipage")

    elif ptype == "insert_action":
        anchor = patch.get("after") or patch.get("before")
        actions = patch.get("actions", [])
        if not anchor or not actions:
            log(f"insert_action patch missing 'after' or 'actions': {patch}")
            return
        ok = _patch_insert_action(root, anchor, actions)
        if not ok and logger:
            logger.warning(f"insert_action anchor '{anchor}' not found in flexipage")

    elif ptype == "add_display_field":
        field = patch.get("field")
        if not field:
            log(f"add_display_field patch missing 'field': {patch}")
            return
        ok = _patch_add_display_field(root, field)
        if not ok and logger:
            logger.warning(f"add_display_field: displayFields valueList not found")

    elif ptype == "add_facet_field":
        fields = patch.get("fields", [])
        after = patch.get("after")
        facet_label = patch.get("facet")
        if not fields:
            log(f"add_facet_field patch missing 'fields': {patch}")
            return
        ok = _patch_add_facet_field(root, fields, after=after, facet_label=facet_label)
        if not ok and logger:
            logger.warning(
                f"add_facet_field: anchor '{after or facet_label}' not found"
            )

    elif ptype == "add_component":
        region_name = patch.get("region")
        component_name = patch.get("component")
        properties = patch.get("properties", {})
        identifier = patch.get("identifier", component_name)
        after_id = patch.get("after_identifier")
        if not region_name or not component_name:
            log(f"add_component patch missing 'region' or 'component': {patch}")
            return
        ok = _patch_add_component(root, region_name, component_name, properties, identifier, after_id)
        if not ok and logger:
            logger.warning(f"add_component: region '{region_name}' not found")

    elif ptype == "insert_after_xml":
        # Text-based fallback: raw XML string inserted after anchor text
        # This is handled at the file text level, not on the ET root.
        # Caller must handle this separately.
        pass

    else:
        log(f"Unknown patch type '{ptype}': {patch}")


# ---------------------------------------------------------------------------
# Profile XML helpers
# ---------------------------------------------------------------------------

def _strip_profile_personalization(root: ET.Element) -> None:
    """Remove layoutAssignments and applicationVisibilities from a profile root."""
    to_remove = []
    for child in list(root):
        local = child.tag.replace(SF_NS_TAG, "")
        if local in ("layoutAssignments", "applicationVisibilities"):
            to_remove.append(child)
    for el in to_remove:
        root.remove(el)


def _add_layout_assignment(root: ET.Element, layout: str, record_type: Optional[str] = None) -> None:
    """Append a <layoutAssignments> element to a profile root."""
    la = _make_elem("layoutAssignments")
    _sub_elem(la, "layout", layout)
    if record_type:
        _sub_elem(la, "recordType", record_type)
    root.append(la)


def _add_app_visibility(root: ET.Element, application: str, default: bool = False) -> None:
    """Append an <applicationVisibilities> element to a profile root."""
    av = _make_elem("applicationVisibilities")
    _sub_elem(av, "application", application)
    _sub_elem(av, "default", str(default).lower())
    _sub_elem(av, "visible", "true")
    root.append(av)


# ---------------------------------------------------------------------------
# Main task class
# ---------------------------------------------------------------------------

class AssembleAndDeployUX(SFDXBaseTask):
    """
    Assembles feature-conditional UX metadata from templates and deploys it.

    Reads base templates + YAML patch files from the templates/ directory tree,
    assembles the correct variant based on active CCI feature flags, writes
    assembled SFDX-format metadata to unpackaged/post_ux/, and optionally
    deploys that directory via sf project deploy start.
    """

    keychain_class = BaseProjectKeychain
    task_options: Dict[str, Dict[str, Any]] = {
        "metadata_type": {
            "description": (
                "Which metadata type(s) to assemble. One of: all, flexipages, "
                "layouts, applications, profiles, objects. "
                "Defaults to 'all'. 'objects' covers compactLayouts and listViews."
            ),
            "required": False,
        },
        "metadata_name": {
            "description": (
                "A specific metadata item to generate, identified by its full source "
                "filename including the type suffix, e.g. "
                "'RLM_Quote_Record_Page.flexipage-meta.xml', "
                "'Admin.profile-meta.xml', "
                "'OrderItem-RLM Order Product Layout.layout-meta.xml'. "
                "The suffix disambiguates the metadata type automatically. "
                "When provided, only this item is assembled and deployed."
            ),
            "required": False,
        },
        "deploy": {
            "description": (
                "Whether to deploy the assembled output. Defaults to true. "
                "Set to false to generate output only."
            ),
            "required": False,
        },
        "output_path": {
            "description": (
                "Output directory for assembled metadata. Defaults to 'unpackaged/post_ux'."
            ),
            "required": False,
        },
    }

    def _validate_options(self):
        super()._validate_options()
        mtype = self.options.get("metadata_type", "all")
        if mtype not in VALID_TYPES:
            raise TaskOptionsError(
                f"metadata_type must be one of {sorted(VALID_TYPES)}, got: '{mtype}'"
            )
        mname = self.options.get("metadata_name")
        if mname:
            resolved = self._resolve_type_from_name(mname)
            if resolved is None:
                raise TaskOptionsError(
                    f"Cannot determine metadata type from filename: '{mname}'. "
                    f"Expected a name ending in one of: {list(SUFFIX_TO_TYPE.keys())}"
                )
            if mtype != "all" and mtype != resolved:
                raise TaskOptionsError(
                    f"metadata_type '{mtype}' conflicts with type inferred from "
                    f"metadata_name '{mname}' (inferred: '{resolved}')"
                )

    @staticmethod
    def _resolve_type_from_name(name: str) -> Optional[str]:
        for suffix, mtype in SUFFIX_TO_TYPE.items():
            if name.endswith(suffix):
                return mtype
        return None

    def _run_task(self):
        repo_root = Path(self.project_config.repo_root)
        output_path = repo_root / self.options.get("output_path", "unpackaged/post_ux")
        templates_path = repo_root / "templates"
        metadata_type = self.options.get("metadata_type", "all")
        metadata_name = self.options.get("metadata_name")
        should_deploy = process_bool_arg(self.options.get("deploy", True))

        if metadata_name:
            metadata_type = self._resolve_type_from_name(metadata_name)
            self.logger.info(f"Assembling single item: {metadata_name} (type: {metadata_type})")
        else:
            self.logger.info(f"Assembling metadata type(s): {metadata_type}")

        features = self._get_feature_flags()
        self.logger.info(f"Active features: {', '.join(k for k, v in features.items() if v) or 'none'}")

        # Clean output subdirectories for the types being assembled to prevent stale files
        # from previous runs (e.g. files that are no longer emitted due to skip rules).
        type_subdirs = {
            "flexipages": output_path / "flexipages",
            "layouts":    output_path / "layouts",
            "applications": output_path / "applications",
            "profiles":   output_path / "profiles",
            "objects":    output_path / "objects",
        }
        if metadata_name:
            # Single-item mode: only remove that one file if it exists
            resolved_type = self._resolve_type_from_name(metadata_name)
            if resolved_type and resolved_type in type_subdirs:
                stale = type_subdirs[resolved_type] / metadata_name
                if stale.exists():
                    stale.unlink()
        else:
            # Full or type-scoped assembly: remove the relevant subdirectory contents
            for t, subdir in type_subdirs.items():
                if metadata_type in ("all", t) and subdir.exists():
                    shutil.rmtree(subdir)

        manifest = {
            "assembled_at": datetime.datetime.utcnow().isoformat() + "Z",
            "feature_flags": features,
            "assembled": [],
            "skipped": [],
        }

        def should_run(t: str) -> bool:
            return metadata_type in ("all", t)

        if should_run("flexipages"):
            items, skipped = self._assemble_flexipages(
                templates_path, output_path, features, metadata_name
            )
            manifest["assembled"].extend(items)
            manifest["skipped"].extend(skipped)

        if should_run("layouts"):
            items = self._assemble_layouts(
                templates_path, output_path, features, metadata_name
            )
            manifest["assembled"].extend(items)

        if should_run("applications"):
            items = self._assemble_applications(
                templates_path, output_path, features, metadata_name
            )
            manifest["assembled"].extend(items)

        # AppSwitcher (appmenus) is no longer assembled — app launcher
        # ordering is handled dynamically by reorder_app_launcher.
        # Clean up stale appMenus dir from previous assembler versions.
        stale_appmenus = output_path / "appMenus"
        if stale_appmenus.exists():
            shutil.rmtree(stale_appmenus)
            self.logger.info("Removed stale appMenus/ directory")

        if should_run("profiles"):
            items = self._assemble_profiles(
                templates_path, output_path, features, metadata_name
            )
            manifest["assembled"].extend(items)

        if should_run("objects"):
            items = self._assemble_objects(
                templates_path, output_path, features, metadata_name
            )
            manifest["assembled"].extend(items)

        manifest_path = output_path / "assembly_manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        self.logger.info(
            f"Assembly complete. {len(manifest['assembled'])} item(s) written to {output_path}"
        )

        if should_deploy:
            if not manifest["assembled"]:
                self.logger.warning("No items assembled — skipping deploy")
                return
            self._deploy(output_path)

    def _get_feature_flags(self) -> Dict[str, bool]:
        """Read feature flags from project_config.project__custom__*."""
        return get_ux_feature_flags(self.project_config)

    # ------------------------------------------------------------------
    # Flexipages assembly
    # ------------------------------------------------------------------

    def _assemble_flexipages(
        self,
        templates_path: Path,
        output_path: Path,
        features: Dict[str, bool],
        filter_name: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
        base_dir = templates_path / "flexipages" / "base"
        patches_dir = templates_path / "flexipages" / "patches"
        standalone_dir = templates_path / "flexipages" / "standalone"
        out_dir = output_path / "flexipages"

        if not base_dir.exists():
            self.logger.warning(f"Flexipage base directory not found: {base_dir}")
            return [], []

        # Build a map of page filename → authoritative source file.
        # Seeds from base/ then overlays active standalone dirs in deploy order.
        # Order is defined in rlm_ux_utils._STANDALONE_ORDER (last writer wins).
        page_sources = resolve_flexipage_sources(base_dir, standalone_dir, features)

        # Filter to single item if requested
        if filter_name:
            if filter_name not in page_sources:
                self.logger.warning(
                    f"Flexipage '{filter_name}' not found in templates "
                    f"(base or standalone directories)"
                )
                return [], []
            page_sources = {filter_name: page_sources[filter_name]}

        # 3. For each resolved source, apply YAML patches and write to output
        assembled = []
        skipped = []
        # Patch order matches deploy-sequence (approvals before docgen before ramps)
        feature_patch_order = [
            ("quantumbit",  "quantumbit"),
            ("quantumbit",  "utils"),
            ("billing",     "billing"),
            ("billing_ui",  "billing_ui"),
            ("payments",    "payments"),
            ("quantumbit",  "approvals"),
            ("docgen",      "docgen"),
            ("tso",         "tso"),
            ("constraints", "constraints"),
            ("ramps",       "ramp_builder"),
            ("large_stx",   "large_stx"),
            ("collections", "collections"),
            ("personas",    "personas"),
        ]

        # Flexipage types that cannot be deployed via Metadata API (platform restriction)
        NON_DEPLOYABLE_TYPES = {"EmailTemplatePage"}

        for fname, src_file in sorted(page_sources.items()):
            patches_applied = []
            root = ET.parse(str(src_file)).getroot()

            # Skip types that cannot be deployed via Metadata API
            ns = "http://soap.sforce.com/2006/04/metadata"
            fp_type_el = root.find(f"{{{ns}}}type")
            if fp_type_el is None:
                fp_type_el = root.find("type")
            fp_type = fp_type_el.text.strip() if fp_type_el is not None else ""
            if fp_type in NON_DEPLOYABLE_TYPES:
                self.logger.warning(
                    f"  [flexipage] Skipping {fname} — type={fp_type} cannot be deployed via Metadata API"
                )
                skipped.append({"file": fname, "reason": "non_deployable_metadata", "type": fp_type})
                continue

            for flag, patch_feature in feature_patch_order:
                if not features.get(flag):
                    continue
                page_stem = fname.replace(".flexipage-meta.xml", "")
                patch_file = patches_dir / patch_feature / (page_stem + ".yml")
                if not patch_file.exists():
                    continue

                patch_data = _load_yaml(patch_file)
                for patch in patch_data.get("patches", []):
                    if patch.get("type") == "insert_after_xml":
                        self._apply_raw_xml_patch(root, patch)
                    else:
                        _apply_flexipage_patch(root, patch, logger=self.logger)
                    patches_applied.append(
                        {"feature": patch_feature, "patch_type": patch.get("type"),
                         "description": _patch_description(patch)}
                    )

            dest = out_dir / fname
            if patches_applied:
                _write_xml(root, dest)
            else:
                # No patches — copy source directly to preserve original
                # encoding (avoids ET entity re-encoding differences).
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src_file), str(dest))
            assembled.append(
                {
                    "type": "flexipage",
                    "name": fname,
                    "dest": str(dest.relative_to(output_path.parent.parent)),
                    "source": str(src_file.relative_to(templates_path.parent)),
                    "patches": patches_applied,
                }
            )
            self.logger.info(
                f"  [flexipage] {fname} "
                f"(src: {src_file.parent.parent.name}/{src_file.parent.name}"
                f", {len(patches_applied)} patch(es))"
            )

        return assembled, skipped

    def _apply_raw_xml_patch(self, root: ET.Element, patch: Dict[str, Any]) -> None:
        """
        Text-based XML insertion as a fallback for structures not handled by
        the semantic patch operations. Operates on the serialized string of the
        root element and re-parses back into the root. Expensive — use sparingly.
        """
        anchor = patch.get("anchor")
        xml_fragment = patch.get("xml", "")
        if not anchor or not xml_fragment:
            self.logger.warning("insert_after_xml patch missing 'anchor' or 'xml'")
            return

        ET.indent(root, space="    ")
        text = ET.tostring(root, encoding="unicode")
        if anchor not in text:
            self.logger.warning(f"insert_after_xml anchor not found: {anchor!r}")
            return
        idx = text.index(anchor) + len(anchor)
        text = text[:idx] + "\n" + xml_fragment + text[idx:]
        new_root = ET.fromstring(text)
        # Replace root children with new_root children (in-place modification)
        for child in list(root):
            root.remove(child)
        for child in list(new_root):
            root.append(child)

    # ------------------------------------------------------------------
    # Layouts assembly
    # ------------------------------------------------------------------

    def _assemble_layouts(
        self,
        templates_path: Path,
        output_path: Path,
        features: Dict[str, bool],
        filter_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        out_dir = output_path / "layouts"
        assembled = []

        source_dirs = [
            ("base", templates_path / "layouts" / "base", True),
            ("billing", templates_path / "layouts" / "billing", features.get("billing", False)),
            ("constraints", templates_path / "layouts" / "constraints", features.get("constraints", False)),
        ]

        copied_names: Set[str] = set()

        for tier_name, src_dir, active in source_dirs:
            if not active or not src_dir.exists():
                continue
            for src_file in sorted(src_dir.glob("*.layout-meta.xml")):
                fname = src_file.name
                if filter_name and fname != filter_name:
                    continue
                dest = out_dir / fname
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src_file), str(dest))
                action = "override" if fname in copied_names else "copy"
                copied_names.add(fname)
                assembled.append(
                    {
                        "type": "layout",
                        "name": fname,
                        "dest": str(dest.relative_to(output_path.parent.parent)),
                        "source_tier": tier_name,
                        "action": action,
                    }
                )
                self.logger.info(f"  [layout] {fname} ({action} from {tier_name})")

        return assembled

    # ------------------------------------------------------------------
    # Applications assembly
    # ------------------------------------------------------------------

    def _apply_app_action_overrides_patch(self, app_dest: Path, patch_file: Path) -> None:
        """Merge <actionOverrides> elements from a patch file into the assembled app XML.

        The patch file contains bare <actionOverrides> elements (no root wrapper beyond
        the XML declaration and an optional comment). After merging, all actionOverrides
        in the output file are re-sorted alphabetically by pageOrSobjectType then
        formFactor (Large before Small) to satisfy Salesforce metadata ordering.
        """
        import xml.etree.ElementTree as ET

        NS = "http://soap.sforce.com/2006/04/metadata"
        ET.register_namespace("", NS)

        # Parse the assembled app
        app_tree = ET.parse(app_dest)
        app_root = app_tree.getroot()

        # Parse patch — wrap in a temporary root so ET can parse multiple siblings
        raw = patch_file.read_text(encoding="utf-8")
        # Strip XML declaration and comments; wrap in a root element
        import re as _re
        raw_stripped = _re.sub(r"<\?xml[^?]*\?>", "", raw).strip()
        raw_stripped = _re.sub(r"<!--[^-]*-->", "", raw_stripped).strip()
        wrapped = f"<root xmlns=\"{NS}\">{raw_stripped}</root>"
        patch_root = ET.fromstring(wrapped)

        # Collect existing actionOverrides keys to avoid duplicates
        existing_keys = set()
        for ao in app_root.findall(f"{{{NS}}}actionOverrides"):
            sobjtype = (ao.findtext(f"{{{NS}}}pageOrSobjectType") or "").strip()
            ff = (ao.findtext(f"{{{NS}}}formFactor") or "").strip()
            existing_keys.add((sobjtype, ff))

        # Inject new actionOverrides that aren't already present
        added = 0
        for ao in patch_root.findall(f"{{{NS}}}actionOverrides"):
            sobjtype = (ao.findtext(f"{{{NS}}}pageOrSobjectType") or "").strip()
            ff = (ao.findtext(f"{{{NS}}}formFactor") or "").strip()
            if (sobjtype, ff) not in existing_keys:
                app_root.append(ao)
                existing_keys.add((sobjtype, ff))
                added += 1

        if added == 0:
            return

        # Re-sort all actionOverrides by (pageOrSobjectType, formFactor)
        # Large sorts before Small; missing formFactor sorts last
        ff_order = {"Large": 0, "Small": 1, "": 2}
        all_overrides = app_root.findall(f"{{{NS}}}actionOverrides")
        for ao in all_overrides:
            app_root.remove(ao)

        all_overrides.sort(key=lambda ao: (
            (ao.findtext(f"{{{NS}}}pageOrSobjectType") or "").strip().lower(),
            ff_order.get((ao.findtext(f"{{{NS}}}formFactor") or "").strip(), 2),
        ))

        # Re-insert before the first non-actionOverrides element after the overrides block
        # Find insertion index: after existing leading non-actionOverride elements
        insert_before = None
        for i, child in enumerate(list(app_root)):
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            if tag not in ("actionOverrides",) and i > 0:
                insert_before = i
                break

        if insert_before is not None:
            for idx, ao in enumerate(all_overrides):
                app_root.insert(insert_before + idx, ao)
        else:
            for ao in all_overrides:
                app_root.append(ao)

        ET.indent(app_tree, space="    ")
        app_tree.write(app_dest, encoding="utf-8", xml_declaration=True, default_namespace=NS)
        self.logger.debug(f"  [app patch] {patch_file.name}: +{added} actionOverride(s)")

    def _assemble_applications(
        self,
        templates_path: Path,
        output_path: Path,
        features: Dict[str, bool],
        filter_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Assemble application metadata from versioned templates.

        RLM_Revenue_Cloud selection priority (highest wins):
          tso > quantumbit > base

        Conditional standalone apps:
          standard__BillingConsole  — billing_ui=true wins over billing=true (priority: billing_ui > billing)
          standard__CollectionConsole, RLM_Receivables_Management — when collections=true
        """
        out_dir = output_path / "applications"
        app_base = templates_path / "applications"
        assembled = []

        # --- RLM_Revenue_Cloud (versioned selection + feature patches) ---
        rev_cloud_name = "RLM_Revenue_Cloud.app-meta.xml"
        if not filter_name or filter_name == rev_cloud_name:
            if features.get("tso"):
                src_dir = app_base / "tso"
            elif features.get("quantumbit"):
                src_dir = app_base / "quantumbit"
            else:
                src_dir = app_base / "base"

            src_file = src_dir / rev_cloud_name
            if src_file.exists():
                dest = out_dir / rev_cloud_name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src_file), str(dest))
                tier = "tso" if features.get("tso") else ("quantumbit" if features.get("quantumbit") else "base")

                # Apply feature-conditional actionOverride patches.
                # Patch files live in templates/applications/patches/{feature}/RLM_Revenue_Cloud.patch.xml
                # and contain bare <actionOverrides> elements (no root wrapper).
                # TSO template already contains all overrides; patches only run for non-TSO builds.
                patches_applied = []
                if not features.get("tso"):
                    patch_features = ["billing", "rates", "ramps"]
                    for pf in patch_features:
                        if not features.get(pf):
                            continue
                        patch_file = app_base / "patches" / pf / rev_cloud_name.replace(".app-meta.xml", ".patch.xml")
                        if not patch_file.exists():
                            continue
                        self._apply_app_action_overrides_patch(dest, patch_file)
                        patches_applied.append(pf)

                assembled.append(
                    {
                        "type": "application",
                        "name": rev_cloud_name,
                        "dest": str(dest.relative_to(output_path.parent.parent)),
                        "source_tier": tier,
                    }
                )
                patch_info = f" + patches: {', '.join(patches_applied)}" if patches_applied else ""
                self.logger.info(f"  [application] {rev_cloud_name} (from {tier}{patch_info})")
            else:
                self.logger.warning(f"RLM_Revenue_Cloud template not found at: {src_file}")

        # --- Conditional standalone apps ---
        conditional_apps = []
        if features.get("billing") or features.get("billing_ui"):
            # billing_ui=true wins over billing=true — provides the Billing Account Record Page override.
            # Guard covers either flag so billing_ui can be enabled independently of billing.
            billing_subdir = "billing_ui" if features.get("billing_ui") else "billing"
            conditional_apps.append(
                (app_base / "conditional" / billing_subdir / "standard__BillingConsole.app-meta.xml", billing_subdir)
            )
        if features.get("collections"):
            conditional_apps += [
                (app_base / "conditional" / "collections" / "standard__CollectionConsole.app-meta.xml", "collections"),
                (app_base / "conditional" / "collections" / "RLM_Receivables_Management.app-meta.xml", "collections"),
            ]

        for src_file, feature_name in conditional_apps:
            fname = src_file.name
            if filter_name and fname != filter_name:
                continue
            if not src_file.exists():
                self.logger.warning(f"Conditional app template not found: {src_file}")
                continue
            dest = out_dir / fname
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(src_file), str(dest))
            assembled.append(
                {
                    "type": "application",
                    "name": fname,
                    "dest": str(dest.relative_to(output_path.parent.parent)),
                    "source_tier": f"conditional/{feature_name}",
                }
            )
            self.logger.info(f"  [application] {fname} (conditional/{feature_name})")

        return assembled

    # ------------------------------------------------------------------
    # Profiles assembly
    # ------------------------------------------------------------------

    def _assemble_profiles(
        self,
        templates_path: Path,
        output_path: Path,
        features: Dict[str, bool],
        filter_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Build profiles via strip-and-build:
        1. Start with base profile template (full access grants)
        2. Apply feature-specific layout/app patches in order
        3. Write to output

        The base template in templates/profiles/base/ should already contain
        full layout assignments and applicationVisibilities for the base feature
        set (core QB). Feature patches add billing/constraints layouts or
        replace layout assignments for override scenarios.
        """
        profiles_base = templates_path / "profiles" / "base"
        patches_dir = templates_path / "profiles" / "patches"
        out_dir = output_path / "profiles"
        assembled = []

        if not profiles_base.exists():
            self.logger.warning(f"Profile base directory not found: {profiles_base}")
            return []

        for base_file in sorted(profiles_base.glob("*.profile-meta.xml")):
            fname = base_file.name
            if filter_name and fname != filter_name:
                continue
            if fname in PERSONAS_PROFILES and not features.get("personas"):
                self.logger.info(f"  [profile] skipping {fname} (personas feature flag is false)")
                continue

            root = ET.parse(str(base_file)).getroot()
            patches_applied = []

            patch_order = [
                ("billing", "billing"),
                ("constraints", "constraints"),
                ("prm", "prm"),
            ]
            for flag, feature_dir in patch_order:
                if not features.get(flag):
                    continue
                patch_file = patches_dir / feature_dir / (
                    base_file.stem.replace(".profile-meta", "") + ".yml"
                )
                if not patch_file.exists():
                    continue
                patch_data = _load_yaml(patch_file)
                for patch in patch_data.get("patches", []):
                    self._apply_profile_patch(root, patch)
                    patches_applied.append(
                        {"feature": feature_dir, "patch_type": patch.get("type"),
                         "description": _profile_patch_description(patch)}
                    )

            dest = out_dir / fname
            _write_xml(root, dest)
            assembled.append(
                {
                    "type": "profile",
                    "name": fname,
                    "dest": str(dest.relative_to(output_path.parent.parent)),
                    "patches": patches_applied,
                }
            )
            self.logger.info(
                f"  [profile] {fname} ({len(patches_applied)} patch(es) applied)"
            )

        return assembled

    def _assemble_objects(
        self,
        templates_path: Path,
        output_path: Path,
        features: Dict[str, bool],
        filter_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Assemble object-level UX metadata from templates/objects/{feature}/ into
        output_path/objects/{ObjectName}/{subtype}/.

        Handles three file types:
          *.object-meta.xml        — UX bindings (actionOverrides, compactLayoutAssignment)
          *.compactLayout-meta.xml — compact layout definitions
          *.listView-meta.xml      — list view definitions

        Copy order (last write wins for same filename):
          base        — always included
          billing     — when billing=true
          tso         — when tso=true
          collections — when collections=true

        filter_name matches the bare filename across any object directory.
        """
        objects_templates = templates_path / "objects"
        out_dir = output_path / "objects"
        assembled = []

        if not objects_templates.exists():
            self.logger.warning(f"Objects template directory not found: {objects_templates}")
            return []

        copy_order = [
            ("base",        True),
            ("billing",     features.get("billing", False)),
            ("tso",         features.get("tso", False)),
            ("collections", features.get("collections", False)),
        ]

        patterns = [
            "*.object-meta.xml",
            "*.compactLayout-meta.xml",
            "*.listView-meta.xml",
        ]

        for feature_dir, active in copy_order:
            if not active:
                continue
            src_root = objects_templates / feature_dir
            if not src_root.exists():
                continue

            all_files: List[Path] = []
            for pattern in patterns:
                all_files.extend(sorted(src_root.rglob(pattern)))

            for src_file in all_files:
                if filter_name and src_file.name != filter_name:
                    continue
                rel = src_file.relative_to(src_root)
                dest = out_dir / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src_file), str(dest))

                name = src_file.name
                if ".object-meta.xml" in name:
                    subtype = "CustomObject"
                elif ".compactLayout-meta.xml" in name:
                    subtype = "compactLayout"
                else:
                    subtype = "listView"

                assembled.append(
                    {
                        "type": subtype,
                        "name": name,
                        "dest": str(dest.relative_to(output_path.parent.parent)),
                        "source": f"objects/{feature_dir}",
                    }
                )
                self.logger.info(f"  [{subtype}] {rel} (from {feature_dir})")

        return assembled

    def _apply_profile_patch(self, root: ET.Element, patch: Dict[str, Any]) -> None:
        ptype = patch.get("type")
        if ptype == "add_layout_assignment":
            layout = patch.get("layout")
            record_type = patch.get("record_type")
            if layout:
                _add_layout_assignment(root, layout, record_type)

        elif ptype == "replace_layout_assignment":
            old_layout = patch.get("old_layout")
            new_layout = patch.get("new_layout")
            if old_layout and new_layout:
                for la in _findall_elem(root, "layoutAssignments"):
                    layout_el = _find_elem(la, "layout")
                    if layout_el is not None and layout_el.text == old_layout:
                        layout_el.text = new_layout
                        return

        elif ptype == "add_app_visibility":
            app = patch.get("application")
            default = patch.get("default", False)
            if app:
                _add_app_visibility(root, app, default)

        else:
            self.logger.warning(f"Unknown profile patch type '{ptype}': {patch}")

    # ------------------------------------------------------------------
    # Deploy
    # ------------------------------------------------------------------

    def _deploy(self, output_path: Path) -> None:
        """Deploy assembled metadata via sf project deploy start."""
        username = getattr(self.org_config, "username", None)
        if not username:
            raise TaskOptionsError(
                "Org config has no username. Cannot deploy without a target org."
            )

        cmd = [
            "sf",
            "project",
            "deploy",
            "start",
            "--source-dir",
            str(output_path),
            "--target-org",
            username,
            "--ignore-conflicts",
            "--json",
        ]
        self.logger.info(f"Deploying {output_path} → {username}")
        self.logger.debug(f"Deploy command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=600,
            )
        except subprocess.TimeoutExpired:
            raise CommandException("sf project deploy start timed out after 600 seconds")
        except FileNotFoundError:
            raise CommandException(
                "sf command not found. Ensure Salesforce CLI is installed and in PATH."
            )

        if result.stderr:
            self.logger.debug(f"Deploy stderr: {result.stderr[:2000]}")

        try:
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            raise CommandException(
                f"Deploy returned non-JSON output.\n"
                f"Exit code: {result.returncode}\n"
                f"Stdout: {result.stdout[:2000]}\n"
                f"Stderr: {result.stderr[:2000]}"
            )

        status = output.get("status", -1)
        deploy_result = output.get("result", {})
        deploy_status = deploy_result.get("status", "Unknown")

        if status != 0 or deploy_status not in ("Succeeded", "SucceededPartial"):
            errors = deploy_result.get("details", {}).get("componentFailures", [])


            err_msgs = [
                f"  {e.get('componentType')}/{e.get('fullName')}: {e.get('problem')}"
                for e in errors[:20]
            ]
            raise CommandException(
                f"Deployment failed (status={deploy_status}).\n"
                + "\n".join(err_msgs)
            )

        deployed_count = deploy_result.get("numberComponentsDeployed", 0)
        self.logger.info(
            f"Deployment succeeded: {deployed_count} component(s) deployed (status={deploy_status})"
        )
