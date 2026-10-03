"""
UX template writeback — reverse-applies active feature patches against
org-retrieved flexipages and writes the result as updated base templates.

The assembler invariant is: base + patches = deployed state.
Write-back computes:         new_base = org_state - patches.

This prevents double-application of non-idempotent patches (insert_after_xml)
on the next assembly run. The per-type reverse and refresh logic lives in
``_patch_ops``.

Requires ``ux_tool.py retrieve`` to have populated ``unpackaged/post_ux/`` with
the org's current flexipage state. Dry run by default: nothing under
``templates/`` changes unless ``apply=True`` (``ux_tool.py writeback --apply``).
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from scripts.ux._assemble import validate_selection
from scripts.ux._context import UxContext, UxOptionError
from scripts.ux._diff import org_flexipage_files
from scripts.ux._flags import (
    FLEXIPAGE_SUFFIX,
    active_patch_files,
    load_yaml,
    resolve_flexipage_sources,
)
from scripts.ux._patch_ops import (
    ABSENT,
    REMOVED,
    PagePair,
    describe_patch,
    refresh_patch,
    reverse_patch,
)
from scripts.ux._xml import indented_text, write_xml


def writeback(
    ctx: UxContext,
    org_path: Path,
    metadata_name: Optional[str] = None,
    apply: bool = False,
) -> List[Dict[str, Any]]:
    """Write back (with ``apply``) or report template changes; return per-page results.

    new_base = org_state - reverse(patches)
    """
    validate_selection("flexipages", metadata_name, ("flexipages",))
    logger = ctx.logger
    org_path = Path(org_path)
    features = ctx.features
    logger.info(f"Write-back mode: {'LIVE' if apply else 'DRY RUN'}")
    logger.info(
        "Active features: "
        + (", ".join(k for k, v in features.items() if v) or "none")
    )

    flexipages = ctx.templates_path / "flexipages"
    base_dir = flexipages / "base"
    patches_dir = flexipages / "patches"
    standalone_dir = flexipages / "standalone"
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
            logger.info(
                f"  [new page]  {fname} — exists in org but not in "
                "templates. Saving as new base template."
            )
            if apply:
                write_xml(ET.parse(str(org_dir / fname)).getroot(), base_dir / fname)
            results.append({"file": fname, "written": apply, "new": True})
            continue
        results.append(_writeback_page(
            ctx, fname, org_dir, source, patches_dir, apply,
            standalone=standalone_dir in source.parents,
        ))

    if apply:
        logger.info("\nUpdating patch files...")
        for fname in org_files:
            source = page_sources.get(fname)
            if source is not None:
                _refresh_patch_files(ctx, fname, org_dir / fname, source, patches_dir)

    written = sum(1 for r in results if r["written"])
    logger.info(
        f"\nWrite-back complete: {written} written, {len(results) - written} skipped "
        f"({'live' if apply else 'dry run'})"
    )
    return results


def _writeback_page(
    ctx: UxContext,
    fname: str,
    org_dir: Path,
    source: Path,
    patches_dir: Path,
    apply: bool,
    standalone: bool,
) -> Dict[str, Any]:
    """Reverse the active patches out of the org page and write it over ``source``,
    the page's template (a base page or an active standalone override)."""
    logger = ctx.logger
    kind = "standalone" if standalone else "base"
    root = ET.parse(str(org_dir / fname)).getroot()
    template_root = ET.parse(str(source)).getroot()
    page_stem = fname[: -len(FLEXIPAGE_SUFFIX)]

    patches: List[Tuple[str, Dict[str, Any]]] = [
        (feature, patch)
        for feature, patch_file in active_patch_files(patches_dir, page_stem, ctx.features)
        for patch in load_yaml(patch_file).get("patches", [])
    ]

    # Last-applied patch is reversed first.
    reversed_count = absent_count = 0
    for feature, patch in reversed(patches):
        result = reverse_patch(root, patch, template_root, logger)
        if result == REMOVED:
            reversed_count += 1
            logger.info(f"    reversed {patch.get('type')} from {feature}")
        elif result == ABSENT:
            absent_count += 1
            logger.info(f"    skipped {patch.get('type')} from {feature} (already absent)")
        else:
            logger.warning(
                f"    FAILED to reverse {patch.get('type')} from "
                f"{feature} — element not found in org XML"
            )

    logger.info(
        f"  [{kind}] {fname} ({source.parent.name}) — reversed "
        f"{reversed_count}/{len(patches)} patches"
        + (f" ({absent_count} already absent)" if absent_count else "")
    )

    if apply:
        write_xml(root, source)

    return {
        "file": fname,
        "written": apply,
        "patches_reversed": reversed_count,
        "patches_total": len(patches),
        "standalone": standalone,
    }


def _refresh_patch_files(
    ctx: UxContext, fname: str, org_file: Path, template: Path, patches_dir: Path,
) -> None:
    """Re-derive each active patch file for a page from the org state, so that
    the just-regenerated ``template`` + patches reproduces the org page."""
    patch_files = active_patch_files(patches_dir, fname[: -len(FLEXIPAGE_SUFFIX)], ctx.features)
    if not patch_files or not template.exists() or not org_file.exists():
        return

    base_root = ET.parse(str(template)).getroot()
    org_root = ET.parse(str(org_file)).getroot()
    page = PagePair(base_root, org_root, indented_text(base_root), indented_text(org_root))

    for feature, patch_path in patch_files:
        patch_data = load_yaml(patch_path)
        patches = patch_data.get("patches", [])
        if not patches:
            continue
        label = f"    [patch] {feature}/{fname}"
        new_patches = []
        for patch in patches:
            refreshed = refresh_patch(patch, page)
            if refreshed is None:
                ctx.logger.info(f"{label}: {describe_patch(patch)} absent in org, removing patch entry")
            else:
                new_patches.append(refreshed)
        if new_patches == patches:
            continue
        if not new_patches:
            ctx.logger.info(f"{label}: all patches removed, deleting patch file")
            patch_path.unlink()
            continue
        patch_data["patches"] = new_patches
        _write_patch_yaml(patch_path, patch_data)
        ctx.logger.info(f"{label}: updated ({len(new_patches)} patches)")


class _BlockStr(str):
    """A string YAML writes in block style (``|``)."""


def _block_repr(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


class _PatchDumper(yaml.SafeDumper):
    pass


_PatchDumper.add_representer(_BlockStr, _block_repr)


def _write_patch_yaml(path: Path, data: Dict[str, Any]) -> None:
    """Write patch YAML, with multi-line ``xml``/``anchor`` values as block strings."""
    for patch in data.get("patches", []):
        for key in ("xml", "anchor"):
            if key in patch and "\n" in str(patch[key]):
                patch[key] = _BlockStr(patch[key])
    path.write_text(
        yaml.dump(
            data, Dumper=_PatchDumper, default_flow_style=False,
            sort_keys=False, allow_unicode=True, width=120,
        ),
        encoding="utf-8",
    )
