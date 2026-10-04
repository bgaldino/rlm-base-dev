"""
UX metadata assembly — CCI-free core of ``assemble_and_deploy_ux``.

Reads base templates and feature-conditional YAML patches from ``templates/``,
assembles the final metadata for the active feature flags, and writes it to
an output directory (``unpackaged/post_ux/`` by default, git-tracked).
Deploying is a separate step (``scripts/ux/_deploy.py``).

Supported metadata types:
  flexipages   — patch-based XML assembly (insert_action, add_display_field,
                  add_facet_field, add_component, raw insert_after_xml)
  layouts      — copy base + conditional overrides (billing, constraints)
  applications — copy from versioned templates based on active features
  profiles     — strip-and-build: base grants + feature layout patches
  objects      — compactLayouts, listViews and object actionOverrides

Entry points: ``python scripts/ux/ux_tool.py assemble`` and the
``assemble_and_deploy_ux`` CCI task (``tasks/rlm_ux_assembly.py``).
"""
import datetime
import json
import re
import shutil
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple
import xml.etree.ElementTree as ET

from scripts.ux._context import UxContext, UxOptionError
from scripts.ux._flags import (
    FLEXIPAGE_SUFFIX,
    LAYOUT_SUFFIX,
    PERSONAS_PROFILES,
    active_layout_tiers,
    active_patch_files,
    load_yaml,
    resolve_flexipage_sources,
)
from scripts.ux._patch_ops import apply_patch, describe_patch
from scripts.ux._xml import (
    SF_NS,
    SF_NS_TAG,
    find_elem,
    findall_elem,
    local_tag,
    make_elem,
    sub_elem,
    write_xml,
)

# Maps full source filename suffix → canonical metadata type key
SUFFIX_TO_TYPE: Dict[str, str] = {
    FLEXIPAGE_SUFFIX: "flexipages",
    LAYOUT_SUFFIX: "layouts",
    ".app-meta.xml": "applications",
    ".profile-meta.xml": "profiles",
    ".compactLayout-meta.xml": "objects",
    ".listView-meta.xml": "objects",
    ".object-meta.xml": "objects",
}

#: Written by a ``retrieve --name``: the one page in ``flexipages/`` that is org state.
RETRIEVE_SCOPE_NAME = "retrieve_scope.json"

VALID_TYPES: Set[str] = {"all", "flexipages", "layouts", "applications", "profiles", "objects"}


def _profile_patch_description(patch: Dict[str, Any]) -> str:
    """Return a short description of a profile patch for manifests."""
    ptype = patch.get("type", "")
    if ptype == "add_layout_assignment":
        return f"layout: {patch.get('layout', '?')}"
    if ptype == "add_app_visibility":
        return f"app: {patch.get('application', '?')}"
    return ptype


# ---------------------------------------------------------------------------
# Profile XML helpers
# ---------------------------------------------------------------------------

def _add_layout_assignment(root: ET.Element, layout: str, record_type: Optional[str] = None) -> None:
    """Append a <layoutAssignments> element to a profile root."""
    la = make_elem("layoutAssignments")
    sub_elem(la, "layout", layout)
    if record_type:
        sub_elem(la, "recordType", record_type)
    root.append(la)


def _add_app_visibility(root: ET.Element, application: str, default: bool = False) -> None:
    """Append an <applicationVisibilities> element to a profile root."""
    av = make_elem("applicationVisibilities")
    sub_elem(av, "application", application)
    sub_elem(av, "default", str(default).lower())
    sub_elem(av, "visible", "true")
    root.append(av)


# ---------------------------------------------------------------------------
# Selection
# ---------------------------------------------------------------------------


def resolve_type_from_name(name: str) -> Optional[str]:
    """Metadata type key for a full source filename, or None if unrecognised."""
    for suffix, mtype in SUFFIX_TO_TYPE.items():
        if name.endswith(suffix):
            return mtype
    return None


def validate_selection(
    metadata_type: str = "all",
    metadata_name: Optional[str] = None,
    supported: Iterable[str] = VALID_TYPES,
) -> str:
    """Return the type to process (inferred from ``metadata_name`` when given).

    Raise UxOptionError for a type outside ``supported``, an unrecognised name,
    or a name whose type conflicts with ``metadata_type``.
    """
    supported = set(supported)
    if metadata_type not in supported:
        raise UxOptionError(
            f"metadata_type must be one of {sorted(supported)}, got: '{metadata_type}'"
        )
    if metadata_name:
        # A bare filename only: retrieve and writeback join it onto output and
        # template directories, so a path component could escape them.
        if metadata_name != Path(metadata_name).name or "\\" in metadata_name:
            raise UxOptionError(
                f"metadata_name must be a bare filename, not a path: '{metadata_name}'"
            )
        resolved = resolve_type_from_name(metadata_name)
        if resolved is None:
            raise UxOptionError(
                f"Cannot determine metadata type from filename: '{metadata_name}'. "
                f"Expected a name ending in one of: {list(SUFFIX_TO_TYPE.keys())}"
            )
        if metadata_type != "all" and metadata_type != resolved:
            raise UxOptionError(
                f"metadata_type '{metadata_type}' conflicts with type inferred from "
                f"metadata_name '{metadata_name}' (inferred: '{resolved}')"
            )
        if resolved not in supported:
            raise UxOptionError(
                f"'{metadata_name}' is a {resolved} file; expected one of {sorted(supported - {'all'})}"
            )
        return resolved
    return metadata_type


def read_manifest(path: Path) -> Dict[str, Any]:
    """A previous assembly manifest, or {} when it is missing or unreadable."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def deploy_sources(output_path: Path, manifest: Dict[str, Any]) -> Optional[List[Path]]:
    """What a deploy of ``output_path`` may send, from its latest manifest: None
    (the whole directory) after a full assembly; after a filtered one, only the
    files it assembled, since everything else is left over from older runs."""
    if not manifest or manifest.get("incomplete") or "scope" not in manifest:
        raise UxOptionError(
            f"{output_path} has no completed assembly manifest. Run assemble before deploying."
        )
    scope = manifest["scope"]
    if scope.get("type") == "all" and not scope.get("name"):
        return None
    return [Path(output_path).parent.parent / item["dest"] for item in manifest.get("assembled", [])]


class UxAssembler:
    """
    Assembles feature-conditional UX metadata from templates.

    Reads base templates + YAML patch files from the templates/ directory tree,
    assembles the correct variant for ``ctx.features``, and writes assembled
    SFDX-format metadata to the output directory.
    """

    def __init__(self, ctx: UxContext):
        self.ctx = ctx
        self.logger = ctx.logger

    def run(
        self,
        output_path: Path,
        metadata_type: str = "all",
        metadata_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Assemble into ``output_path``; write and return the assembly manifest."""
        metadata_type = validate_selection(metadata_type, metadata_name)
        output_path = Path(output_path)
        templates_path = self.ctx.templates_path

        if metadata_name:
            self.logger.info(f"Assembling single item: {metadata_name} (type: {metadata_type})")
        else:
            self.logger.info(f"Assembling metadata type(s): {metadata_type}")

        features = dict(self.ctx.features)
        self.logger.info(f"Active features: {', '.join(k for k, v in features.items() if v) or 'none'}")

        manifest_path = output_path / "assembly_manifest.json"
        previous = read_manifest(manifest_path)
        # Until this run completes, the output is neither the old assembly nor
        # the new one: no command may trust or deploy it.
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps({"incomplete": True}), encoding="utf-8")

        # Clean output subdirectories for the types being assembled to prevent stale files
        # from previous runs (e.g. files that are no longer emitted due to skip rules).
        type_subdirs = {
            "flexipages": output_path / "flexipages",
            "layouts":    output_path / "layouts",
            "applications": output_path / "applications",
            "profiles":   output_path / "profiles",
            "objects":    output_path / "objects",
        }
        # Single-item mode removes only that file, keeping its content in case
        # the item turns out to be unavailable and the run is rolled back.
        stale: Optional[Path] = None
        stale_content: Optional[bytes] = None
        if metadata_name:
            if metadata_type in type_subdirs:
                stale = type_subdirs[metadata_type] / metadata_name
                if stale.exists():
                    stale_content = stale.read_bytes()
                    stale.unlink()
        else:
            # Full or type-scoped assembly: remove the relevant subdirectory contents
            for t, subdir in type_subdirs.items():
                if metadata_type in ("all", t) and subdir.exists():
                    shutil.rmtree(subdir)

        manifest = {
            "assembled_at": datetime.datetime.now(datetime.timezone.utc)
            .replace(tzinfo=None).isoformat() + "Z",
            "feature_flags": features,
            "scope": {"type": metadata_type, "name": metadata_name},
            "assembled": [],
            "skipped": [],
        }

        def should_run(t: str) -> bool:
            return metadata_type in ("all", t)

        try:
            if should_run("flexipages"):
                items, skipped = self._assemble_flexipages(
                    templates_path, output_path, features, metadata_name
                )
                if not metadata_name:
                    # Every flexipage is now assembled, so none is scoped org
                    # state. A --name run rewrites one page and leaves the scope.
                    (output_path / RETRIEVE_SCOPE_NAME).unlink(missing_ok=True)
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

            if metadata_name and not (manifest["assembled"] or manifest["skipped"]):
                raise UxOptionError(f"'{metadata_name}' not found in templates.")
        except UxOptionError:
            if metadata_name and not manifest["assembled"]:
                # An unknown or unavailable name wrote nothing: put back the file
                # it cleared, and the previous manifest still describes the output.
                if stale_content is not None:
                    stale.write_bytes(stale_content)
                if previous:
                    manifest_path.write_text(json.dumps(previous, indent=2, ensure_ascii=False), encoding="utf-8")
                else:
                    manifest_path.unlink()
            raise

        if metadata_name or metadata_type not in ("all", "flexipages"):
            # The flexipages in the output keep the previous run's flags. Unless
            # those match, the drift commands must not trust this manifest.
            if previous.get("partial") or previous.get("feature_flags") != features:
                manifest["partial"] = True
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        self.logger.info(
            f"Assembly complete. {len(manifest['assembled'])} item(s) written to {output_path}"
        )
        return manifest

    # ------------------------------------------------------------------
    # Flexipages assembly
    # ------------------------------------------------------------------

    def assemble_flexipages(
        self, output_path: Path, filter_name: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
        """Assemble only flexipages into ``output_path``; return (assembled, skipped)."""
        return self._assemble_flexipages(
            self.ctx.templates_path, Path(output_path), self.ctx.features, filter_name,
        )

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
        # Order is defined in _flags._STANDALONE_ORDER (last writer wins).
        page_sources = resolve_flexipage_sources(base_dir, standalone_dir, features)

        # Filter to single item if requested
        if filter_name:
            if filter_name not in page_sources:
                raise UxOptionError(
                    f"Flexipage '{filter_name}' not found in templates "
                    "(base or active standalone directories)."
                )
            page_sources = {filter_name: page_sources[filter_name]}

        # 3. For each resolved source, apply YAML patches and write to output
        assembled = []
        skipped = []
        # Flexipage types that cannot be deployed via Metadata API (platform restriction)
        NON_DEPLOYABLE_TYPES = {"EmailTemplatePage"}

        for fname, src_file in sorted(page_sources.items()):
            patches_applied = []
            root = ET.parse(str(src_file)).getroot()

            # Skip types that cannot be deployed via Metadata API
            fp_type_el = find_elem(root, "type")
            if fp_type_el is None:
                fp_type_el = root.find("type")
            fp_type = fp_type_el.text.strip() if fp_type_el is not None else ""
            if fp_type in NON_DEPLOYABLE_TYPES:
                self.logger.warning(
                    f"  [flexipage] Skipping {fname} — type={fp_type} cannot be deployed via Metadata API"
                )
                skipped.append({"file": fname, "reason": "non_deployable_metadata", "type": fp_type})
                continue

            page_stem = fname[: -len(FLEXIPAGE_SUFFIX)]
            for patch_feature, patch_file in active_patch_files(patches_dir, page_stem, features):
                patch_data = load_yaml(patch_file)
                for patch in patch_data.get("patches", []):
                    apply_patch(root, patch, self.logger)
                    patches_applied.append(
                        {"feature": patch_feature, "patch_type": patch.get("type"),
                         "description": describe_patch(patch)}
                    )

            dest = out_dir / fname
            if patches_applied:
                write_xml(root, dest)
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

        copied_names: Set[str] = set()

        for tier_name, src_dir in active_layout_tiers(templates_path, features):
            for src_file in sorted(src_dir.glob(f"*{LAYOUT_SUFFIX}")):
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
        # Parse the assembled app
        app_tree = ET.parse(app_dest)
        app_root = app_tree.getroot()

        # Parse patch — wrap in a temporary root so ET can parse multiple siblings
        raw = patch_file.read_text(encoding="utf-8")
        # Strip XML declaration and comments; wrap in a root element
        raw_stripped = re.sub(r"<\?xml[^?]*\?>", "", raw).strip()
        raw_stripped = re.sub(r"<!--[^-]*-->", "", raw_stripped).strip()
        wrapped = f"<root xmlns=\"{SF_NS}\">{raw_stripped}</root>"
        patch_root = ET.fromstring(wrapped)

        # Collect existing actionOverrides keys to avoid duplicates
        existing_keys = set()
        for ao in app_root.findall(f"{SF_NS_TAG}actionOverrides"):
            sobjtype = (ao.findtext(f"{SF_NS_TAG}pageOrSobjectType") or "").strip()
            ff = (ao.findtext(f"{SF_NS_TAG}formFactor") or "").strip()
            existing_keys.add((sobjtype, ff))

        # Inject new actionOverrides that aren't already present
        added = 0
        for ao in patch_root.findall(f".//{SF_NS_TAG}actionOverrides"):
            sobjtype = (ao.findtext(f"{SF_NS_TAG}pageOrSobjectType") or "").strip()
            ff = (ao.findtext(f"{SF_NS_TAG}formFactor") or "").strip()
            if (sobjtype, ff) not in existing_keys:
                app_root.append(ao)
                existing_keys.add((sobjtype, ff))
                added += 1

        if added == 0:
            return

        # Re-sort all actionOverrides by (pageOrSobjectType, formFactor)
        # Large sorts before Small; missing formFactor sorts last
        ff_order = {"Large": 0, "Small": 1, "": 2}
        all_overrides = app_root.findall(f"{SF_NS_TAG}actionOverrides")
        for ao in all_overrides:
            app_root.remove(ao)

        all_overrides.sort(key=lambda ao: (
            (ao.findtext(f"{SF_NS_TAG}pageOrSobjectType") or "").strip().lower(),
            ff_order.get((ao.findtext(f"{SF_NS_TAG}formFactor") or "").strip(), 2),
        ))

        # Re-insert before the first non-actionOverrides element after the overrides block
        # Find insertion index: after existing leading non-actionOverride elements
        insert_before = None
        for i, child in enumerate(list(app_root)):
            if local_tag(child) != "actionOverrides":
                insert_before = i
                break

        if insert_before is not None:
            for idx, ao in enumerate(all_overrides):
                app_root.insert(insert_before + idx, ao)
        else:
            for ao in all_overrides:
                app_root.append(ao)

        ET.indent(app_tree, space="    ")
        app_tree.write(app_dest, encoding="utf-8", xml_declaration=True, default_namespace=SF_NS)
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
                    patch_features = ["billing", "payments", "rates", "prm_pricing"]
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
                patch_data = load_yaml(patch_file)
                for patch in patch_data.get("patches", []):
                    self._apply_profile_patch(root, patch)
                    patches_applied.append(
                        {"feature": feature_dir, "patch_type": patch.get("type"),
                         "description": _profile_patch_description(patch)}
                    )

            dest = out_dir / fname
            write_xml(root, dest)
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
                for la in findall_elem(root, "layoutAssignments"):
                    layout_el = find_elem(la, "layout")
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
