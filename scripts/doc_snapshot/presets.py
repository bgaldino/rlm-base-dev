"""Load ``presets.yaml`` and turn a preset plus CLI overrides into options.

PyYAML is imported lazily (inside ``load_presets``) so the snapshot modules and
their offline tests stay importable under a bare stdlib interpreter.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

from scripts.doc_snapshot._core import OptionsError, SnapshotError

PRESETS_PATH = Path(__file__).resolve().parent / "presets.yaml"

# Preset kinds, as they appear under a release in presets.yaml.
KINDS = ("help", "dev_guide")

# Dropped when bootstrapping a new release: both are facts about a captured
# corpus (a verified count floor, a pinned atlas version), not about the root.
_BOOTSTRAP_DROP = ("expect_min_articles", "doc_version")


def load_presets(path: Optional[Path] = None) -> Dict[str, Any]:
    """Parse and sanity-check the preset file; returns its ``releases`` map."""
    try:
        import yaml
    except ImportError:
        raise SnapshotError(
            "PyYAML is required to read presets. Install it with: "
            "python -m pip install -r scripts/doc_snapshot/requirements.txt"
        )
    path = path or PRESETS_PATH
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    releases = data.get("releases")
    if not isinstance(releases, dict):
        raise OptionsError(f"{path}: top-level 'releases' mapping is missing")

    normalized: Dict[str, Any] = {}
    for release, block in releases.items():
        release = str(release)
        if not isinstance(block, dict) or not block.get("release_name"):
            raise OptionsError(f"{path}: release {release} needs a release_name")
        for kind in KINDS:
            presets = block.get(kind) or {}
            if not isinstance(presets, dict):
                raise OptionsError(f"{path}: {release}.{kind} must be a mapping")
            for key, preset in presets.items():
                if not isinstance(preset, dict):
                    raise OptionsError(
                        f"{path}: {release}.{kind}.{key} must be a mapping"
                    )
        normalized[release] = block
    return normalized


def iter_presets(
    releases: Dict[str, Any], release: Optional[str] = None
) -> Iterator[Tuple[str, str, str, Dict[str, Any]]]:
    """Yield ``(release, kind, key, preset)`` in file order."""
    for rel, block in releases.items():
        if release is not None and rel != str(release):
            continue
        for kind in KINDS:
            for key, preset in (block.get(kind) or {}).items():
                yield rel, kind, str(key), preset


def preset_keys(releases: Dict[str, Any], release: str, kind: str) -> List[str]:
    block = releases.get(str(release)) or {}
    return [str(k) for k in (block.get(kind) or {})]


def resolve(
    releases: Dict[str, Any],
    release: str,
    kind: str,
    key: Optional[str],
    overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build snapshotter options: release defaults < preset < overrides.

    ``key`` may name no preset (or be None) for an ad hoc run; the caller's
    overrides must then supply whatever the snapshotter requires, and the
    snapshotter's own validation reports anything missing. Overrides whose
    value is None are ignored, so unset CLI flags never mask a preset value.
    """
    release = str(release)
    block = releases.get(release) or {}
    presets = block.get(kind) or {}
    options: Dict[str, Any] = {"release_version": release}
    if block.get("release_name"):
        options["release_name"] = block["release_name"]

    if key is not None and key in presets:
        options.update(presets[key])
        if kind == "help":
            options.setdefault("area", key)
    elif key is not None and not overrides_complete(kind, overrides):
        known = ", ".join(presets) or "none"
        needed = ("--root-article-id and --prefix" if kind == "help" else "--deliverable")
        raise OptionsError(
            f"no {kind} preset {key!r} for release {release} (known: {known}). "
            f"Pass {needed} for an ad hoc run."
        )
    elif key is not None and kind == "help":
        options["area"] = key

    for name, value in (overrides or {}).items():
        if value is not None:
            options[name] = value
    return options


def overrides_complete(kind: str, overrides: Optional[Dict[str, Any]]) -> bool:
    """True when the overrides alone describe a run (no preset needed)."""
    overrides = overrides or {}
    if kind == "help":
        return bool(overrides.get("root_article_id") and overrides.get("article_id_prefix"))
    # The deliverable has a default, but an unknown key must not fall back to it:
    # a mistyped `--guide` would otherwise snapshot (or refresh) the RLM guide.
    return bool(overrides.get("deliverable"))


# ---------------------------------------------------------------------------
# Bootstrap — add a release block by copying another one
# ---------------------------------------------------------------------------


def bootstrap_block(
    releases: Dict[str, Any], source: str, target: str, release_name: str
) -> str:
    """Render a ``releases.<target>`` YAML block copied from ``source``.

    Root IDs and prefixes carry over unverified; ``expect_min_articles`` and
    ``doc_version`` are dropped, and release numbers inside ``output_dir`` are
    rewritten. Returned as text so appending it keeps the file's comments.
    """
    source, target = str(source), str(target)
    if source not in releases:
        raise OptionsError(f"no release {source} in presets (known: {', '.join(releases)})")
    if target in releases:
        raise OptionsError(f"release {target} already exists in presets")
    if not release_name:
        raise OptionsError("a release name is required, e.g. \"Spring '27\"")

    src_block = releases[source]
    lines = [
        "",
        "  # -------------------------------------------------------------------------",
        f"  # {release_name} ({target}) — bootstrapped from {source}.",
        "  #",
        f"  # Root IDs and prefixes are copied from {source} and UNVERIFIED for {target}.",
        "  # Run `--mode discover` per area, check each \"Discovered N\" line, then add",
        "  # expect_min_articles floors (and dev-guide doc_version pins) once captured.",
        "  # -------------------------------------------------------------------------",
        f"  {_scalar(target)}:",
        f"    release_name: {_scalar(release_name)}",
    ]
    for kind in KINDS:
        presets = src_block.get(kind) or {}
        if not presets:
            continue
        lines.append(f"    {kind}:")
        for key, preset in presets.items():
            body = []
            for name, value in preset.items():
                if name in _BOOTSTRAP_DROP:
                    continue
                if name == "output_dir":
                    value = _retarget_output_dir(str(value), source, target)
                body.extend(_emit(name, value, indent=8))
            # A bare `key:` would load as null, which load_presets() rejects.
            lines.append(f"      {key}:" if body else f"      {key}: {{}}")
            lines.extend(body)
    return "\n".join(lines) + "\n"


def append_block(text: str, path: Optional[Path] = None) -> Path:
    path = path or PRESETS_PATH
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(text)
    return path


def _retarget_output_dir(output_dir: str, source: str, target: str) -> str:
    return re.sub(
        rf"(^|/)salesforce/{re.escape(source)}(/|$)",
        rf"\g<1>salesforce/{target}\g<2>",
        output_dir,
    )


def _scalar(value: Any) -> str:
    # JSON scalars are valid YAML flow scalars; always quote strings so
    # release numbers stay strings and apostrophes need no escaping.
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(str(value), ensure_ascii=False)


def _emit(name: str, value: Any, indent: int) -> List[str]:
    pad = " " * indent
    if isinstance(value, (list, tuple)):
        return [f"{pad}{name}:"] + [f"{pad}  - {_scalar(v)}" for v in value]
    return [f"{pad}{name}: {_scalar(value)}"]
