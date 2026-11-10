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
import copy
import re
import textwrap
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from scripts.ux._assemble import validate_selection
from scripts.ux._context import UxContext, UxError, UxOptionError
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
    org_files = org_flexipage_files(org_path, metadata_name)
    if metadata_name:
        if metadata_name not in org_files:
            raise UxOptionError(f"'{metadata_name}' not found in {org_dir}.")
        org_files = [metadata_name]
    if not org_files:
        # Nothing retrieved means no org state: reporting success would hide that.
        raise UxOptionError(f"No org flexipages in {org_dir}; nothing to write back.")

    # Reverse every page before writing any, so a failed reversal leaves
    # templates and patch files untouched.
    results = []
    pending: List[Tuple[ET.Element, Path]] = []
    failures: List[str] = []
    for fname in org_files:
        source = page_sources.get(fname)
        if source is None:
            # Active standalone pages are in page_sources, so any owner here is
            # an inactive feature: saving the page as base would leak it.
            owners = sorted(p.parent.name for p in standalone_dir.glob(f"*/{fname}"))
            if owners:
                failures.append(
                    f"{fname}: belongs to the inactive standalone feature(s) "
                    f"{', '.join(owners)}; the flags do not match the org (set them with --flag)"
                )
                continue
            logger.info(
                f"  [new page]  {fname} — exists in org but not in "
                "templates. Saving as new base template."
            )
            pending.append((ET.parse(str(org_dir / fname)).getroot(), base_dir / fname))
            results.append({"file": fname, "written": apply, "new": True})
            continue
        result, root, failed = _writeback_page(
            ctx, fname, org_dir, source, patches_dir, apply,
            standalone=standalone_dir in source.parents,
        )
        results.append(result)
        pending.append((root, source))
        failures += [f"{fname}: {f}" for f in failed]

    if failures:
        raise UxError(
            f"Write-back aborted: {len(failures)} page(s) or patch(es) could not be "
            "written back, so no template or patch file was changed. Writing them "
            "anyway would bake feature content into a template:\n  "
            + "\n  ".join(failures)
        )

    if apply:
        for root, path in pending:
            write_xml(root, path)
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
) -> Tuple[Dict[str, Any], ET.Element, List[str]]:
    """Reverse the active patches out of the org page, the new content for
    ``source`` (a base page or an active standalone override).

    Return the page result, the reversed page, and a description of each patch
    that could not be reversed. Nothing is written here.
    """
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
    failed: List[str] = []
    for feature, patch in reversed(patches):
        result = reverse_patch(root, patch, template_root, logger)
        if result == REMOVED:
            reversed_count += 1
            logger.info(f"    reversed {patch.get('type')} from {feature}")
        elif result == ABSENT:
            absent_count += 1
            logger.info(f"    skipped {patch.get('type')} from {feature} (already absent)")
        else:
            failed.append(f"{feature}: {describe_patch(patch)}")
            logger.error(
                f"    FAILED to reverse {patch.get('type')} from "
                f"{feature} — element not found in org XML"
            )

    logger.info(
        f"  [{kind}] {fname} ({source.parent.name}) — reversed "
        f"{reversed_count}/{len(patches)} patches"
        + (f" ({absent_count} already absent)" if absent_count else "")
    )

    return {
        "file": fname,
        "written": apply,
        "patches_reversed": reversed_count,
        "patches_total": len(patches),
        "standalone": standalone,
    }, root, failed


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
        originals = copy.deepcopy(patches)  # the file's entries, whatever refresh_patch does
        refreshed_each: List[Optional[Dict[str, Any]]] = []
        for patch in patches:
            refreshed = refresh_patch(patch, page)
            if refreshed is None:
                ctx.logger.info(f"{label}: {describe_patch(patch)} no longer applies to the org, removing patch entry")
            refreshed_each.append(refreshed)
        new_patches = [p for p in refreshed_each if p is not None]
        if new_patches == patches:
            continue
        if not new_patches:
            ctx.logger.info(f"{label}: all patches removed, deleting patch file")
            patch_path.unlink()
            continue
        original = patch_path.read_text(encoding="utf-8")
        patch_data["patches"] = new_patches
        edited = rewrite_patch_entries(original, originals, refreshed_each, patch_data)
        if edited is None:
            ctx.logger.warning(
                f"{label}: layout not recognised, rewriting the whole file "
                "(its comments are not kept)"
            )
            _write_patch_yaml(patch_path, patch_data, original)
        else:
            patch_path.write_text(edited, encoding="utf-8")
        ctx.logger.info(f"{label}: updated ({len(new_patches)} patches)")


class _BlockStr(str):
    """A string YAML writes in block style (``|``)."""


def _block_repr(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


class _PatchDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        # Indent list items under their key (``key:\n  - item``), as the
        # hand-written patch files do, rather than PyYAML's flush-left default.
        return super().increase_indent(flow, False)


class _QuotedStr(str):
    """A string YAML writes double-quoted, as the patch file it goes into does."""


def _quoted_repr(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


class _FlushPatchDumper(yaml.SafeDumper):
    """PyYAML's own layout, list items flush with their key, for files written that way."""


for _dumper in (_PatchDumper, _FlushPatchDumper):
    _dumper.add_representer(_BlockStr, _block_repr)
    _dumper.add_representer(_QuotedStr, _quoted_repr)

_QUOTED_KEY = re.compile(r'^[ \t]*(?:- )?([A-Za-z_][\w-]*):[ \t]+"', re.M)
_QUOTED_ITEM = re.compile(r'^[ \t]*- "', re.M)


def _in_file_style(value: Any, text: str) -> Any:
    """``value`` with its strings styled as the patch file ``text`` writes them.

    The hand-written files quote by key: ``after``, ``field`` and list items are
    double-quoted, ``type`` and ``component`` are not. A string under a key that
    the file quotes, or a list item where the file quotes its items, is written
    double-quoted, so a re-rendered entry does not change quoting it never meant
    to. Multi-line ``xml``/``anchor`` values stay block strings.
    """
    quoted_keys = set(_QUOTED_KEY.findall(text))
    quote_items = bool(_QUOTED_ITEM.search(text))

    def style(v: Any, key: Optional[str], in_list: bool) -> Any:
        if isinstance(v, dict):
            return {k: style(x, k, False) for k, x in v.items()}
        if isinstance(v, list):
            return [style(x, key, True) for x in v]
        if isinstance(v, str):
            if "\n" in v:
                return _BlockStr(v) if key in ("xml", "anchor") else v
            if (quote_items if in_list else key in quoted_keys):
                return _QuotedStr(v)
        return v

    return style(value, None, False)


def _dump(data: Any, flush: bool = False) -> str:
    """YAML for ``data``; ``flush`` writes list items flush with their key."""
    return yaml.dump(
        data, Dumper=_FlushPatchDumper if flush else _PatchDumper, default_flow_style=False,
        sort_keys=False, allow_unicode=True, width=120,
    )


def _write_patch_yaml(path: Path, data: Dict[str, Any], text: str = "") -> None:
    """Write a whole patch file: multi-line ``xml``/``anchor`` values as block
    strings, other strings quoted the way ``text`` (the file it replaces) quotes them."""
    data = dict(data)
    data["patches"] = [_in_file_style(p, text) for p in data.get("patches", [])]
    path.write_text(_dump(data), encoding="utf-8")


_PATCHES_KEY = re.compile(r"^patches:[ \t]*(#.*)?$")


def _rstrip_blank(lines: List[str]) -> List[str]:
    end = len(lines)
    while end and not lines[end - 1].strip():
        end -= 1
    return lines[:end]


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _entry_spans(lines: List[str]) -> Optional[Tuple[List[Tuple[int, int, int]], int]]:
    """Locate each entry of the top-level ``patches:`` list in ``lines``.

    Return ``([(start, item, end), ...], indent)``: an entry spans
    ``lines[start:end]``, where ``start`` takes in the comment lines directly
    above its ``- `` line (``item``), at or left of the entries' indent, so a
    removed entry takes its own comment with it. Comments deeper inside an entry
    stay part of it. None when the file does not have that shape.
    """
    key = next((i for i, line in enumerate(lines) if _PATCHES_KEY.match(line.rstrip("\n"))), None)
    if key is None:
        return None
    end = len(lines)
    for i in range(key + 1, len(lines)):
        text = lines[i].rstrip("\n")
        # A flush-left item (``- type:`` at column 0, PyYAML's default) is still
        # the list; any other unindented line is the next top-level key.
        if text.strip() and not text.startswith((" ", "\t", "#", "- ")):
            end = i
            break
    first = next((i for i in range(key + 1, end) if lines[i].lstrip(" ").startswith("- ")), None)
    if first is None:
        return None
    indent = _indent_of(lines[first])
    marker = " " * indent + "- "
    items = [i for i in range(key + 1, end) if lines[i].startswith(marker)]

    def is_entry_comment(line: str) -> bool:
        return line.lstrip(" ").startswith("#") and _indent_of(line) <= indent

    starts = []
    for item in items:
        start = item
        while start - 1 > key and is_entry_comment(lines[start - 1]):
            start -= 1
        starts.append(start)
    spans = [
        (start, item, starts[n + 1] if n + 1 < len(starts) else end)
        for n, (start, item) in enumerate(zip(starts, items))
    ]
    return spans, indent


_KEY = re.compile(r"[A-Za-z_][\w-]*:")


def _indented(rendered: str, pad: int) -> List[str]:
    return [" " * pad + line if line.strip("\n") else line
            for line in rendered.splitlines(keepends=True)]


def _key_chunks(body: List[str], indent: int) -> Optional[List[Tuple[str, List[str], int]]]:
    """Split one entry's lines into ``(key, lines, key_line)`` per top-level key.

    The first key sits on the ``- `` line; the rest start at ``indent + 2``.
    Comment lines directly above a key, no deeper than it, go with that key.
    None when the entry does not have that shape.
    """
    at = indent + 2
    if not (body and body[0].startswith(" " * indent + "- ") and _KEY.match(body[0][at:])):
        return None
    heads = [0] + [i for i in range(1, len(body))
                   if body[i].startswith(" " * at) and _KEY.match(body[i][at:])]
    starts = []
    for head in heads:
        start = head
        while start - 1 > 0 and body[start - 1].lstrip(" ").startswith("#") \
                and _indent_of(body[start - 1]) <= at and start - 1 not in heads:
            start -= 1
        starts.append(start)
    chunks = []
    for n, (start, head) in enumerate(zip(starts, heads)):
        stop = starts[n + 1] if n + 1 < len(starts) else len(body)
        key = _KEY.match(body[head][at:]).group(0)[:-1]
        chunks.append((key, body[start:stop], head - start))
    return chunks


def _as_mapping(chunk: List[str], key_line: int, indent: int) -> Any:
    """Load one key's lines as a mapping, with the entry's ``- `` turned into spaces."""
    lines = list(chunk)
    line = lines[key_line]
    if line[indent:indent + 2] == "- ":
        lines[key_line] = line[:indent] + "  " + line[indent + 2:]
    return yaml.safe_load(textwrap.dedent("".join(lines)))


def _changed_entry(
    body: List[str], indent: int, before: Dict[str, Any], after: Dict[str, Any], text: str,
) -> List[str]:
    """The new lines for one changed entry.

    Each key whose value is unchanged keeps its exact lines, comments and odd
    indentation included, and only changed or new keys are rendered, in the
    file's quoting. When the entry's keys cannot be told apart, the whole entry
    is rendered instead.
    """
    flush = indent == 0  # the file writes its lists flush with their key

    def whole() -> List[str]:
        return _indented(_dump([_in_file_style(after, text)], flush), indent)

    chunks = _key_chunks(body, indent)
    if chunks is None or [k for k, _, _ in chunks] != list(before):
        return whole()
    by_key = {}
    for key, chunk, key_line in chunks:
        try:
            if _as_mapping(chunk, key_line, indent) != {key: before[key]}:
                return whole()
        except yaml.YAMLError:
            return whole()
        by_key[key] = (chunk, key_line)
    out: List[str] = []
    for n, (key, value) in enumerate(after.items()):
        if key in by_key and before[key] == value:
            chunk, key_line = by_key[key]
            piece = list(chunk)
        else:
            lead = by_key[key][0][: by_key[key][1]] if key in by_key else []
            piece = lead + _indented(_dump(_in_file_style({key: value}, text), flush), indent + 2)
            key_line = len(lead)
        line = piece[key_line]
        piece[key_line] = line[:indent] + ("- " if n == 0 else "  ") + line[indent + 2:]
        out.extend(piece)
    return out


def rewrite_patch_entries(
    text: str,
    old: List[Dict[str, Any]],
    refreshed: List[Optional[Dict[str, Any]]],
    expected: Dict[str, Any],
) -> Optional[str]:
    """Edit only the changed entries of patch file ``text`` in place.

    ``refreshed[n]`` is the new value of ``old[n]``, or None to drop it. An
    unchanged entry keeps its exact text, a dropped one goes with the comments
    directly above it, and a changed one is re-rendered in place under those
    comments. The rest of the file is untouched, so a writeback's diff shows
    only what changed. Return None when the file's layout is not recognised or
    the result would not load as ``expected``; the caller then rewrites it whole.
    """
    lines = text.splitlines(keepends=True)
    found = _entry_spans(lines)
    if found is None:
        return None
    spans, indent = found
    if len(spans) != len(old) or len(refreshed) != len(old):
        return None
    out = lines[: spans[0][0]]
    for (start, item, end), before, after in zip(spans, old, refreshed):
        chunk = lines[start:end]
        try:
            # Proves the span is this entry, and nothing more, before reusing it.
            if yaml.safe_load("".join(chunk)) != [before]:
                return None
        except yaml.YAMLError:
            return None
        if after is None:
            continue
        if after == before:
            out.extend(chunk)
            continue
        out.extend(lines[start:item])
        body = _rstrip_blank(lines[item:end])
        out.extend(_changed_entry(body, indent, before, after, text))
        # Keep the blank lines that separated it from the next entry.
        out.extend(lines[item + len(body):end])
    out.extend(lines[spans[-1][2]:])
    edited = "".join(out)
    try:
        if yaml.safe_load(edited) != expected:
            return None
    except yaml.YAMLError:
        return None
    return edited
