#!/usr/bin/env python3
"""
skill_manifest.py — Cross-repo skill-manifest resolver.

Loads .claude/skill-manifest.yml from the current repo, resolves the local
filesystem paths for both Foundations and PMOS clones (via env vars or
sibling-directory fallback), and exposes lookup helpers for skills and
grounding artifacts that need to read across the repo boundary.

Design references:
  - Schema: .claude/skill-manifest.yml (this repo)
  - Pattern: .agents/artifacts/skills-consolidation-plan.md §3
  - SSOT contract: .agents/artifacts/ssot-comparison.md §6
  - Phase: 6.3 (per pmos-integration.md roadmap)

Usage:
    from scripts.ai.skill_manifest import (
        load_manifest, resolve_path, resolve_grounding,
    )

    m = load_manifest()
    qb = resolve_grounding(m, repo='foundations', key='qb_scenario')
    # qb is a Path object (or None if the Foundations clone can't be found)

    if qb:
        text = qb.read_text()

CLI usage (for diagnostics):
    python scripts/ai/skill_manifest.py --check
    python scripts/ai/skill_manifest.py --list-skills foundations
    python scripts/ai/skill_manifest.py --resolve foundations/grounding/qb_scenario
"""

from __future__ import annotations

import argparse
import importlib
import importlib.util
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

# PyYAML is optional at import time. find_spec can report a module that still
# fails to import (broken/partial install), so guard the actual import.
yaml = None
if importlib.util.find_spec("yaml") is not None:
    try:
        yaml = importlib.import_module("yaml")
    except ImportError:
        yaml = None


MANIFEST_FILENAME = ".claude/skill-manifest.yml"

PY_YAML_HELP = (
    "PyYAML is not installed, so skill_manifest.py is using its minimal fallback. "
    "The fallback supports baseline diagnostics only: file presence, high-level "
    "manifest keys, repo discovery, and simple skill path listing. For full YAML "
    "support, activate the project CumulusCI environment or install PyYAML with "
    "`pipx inject cumulusci PyYAML`, `python -m pip install PyYAML`, or "
    "`python -m pip install cumulusci`."
)


def _strip_inline_comment(value: str) -> str:
    """Remove simple YAML comments outside quoted values for fallback parsing.

    A ``#`` only starts a comment when it is at the start of the value or
    preceded by whitespace (YAML semantics). This keeps ``#`` inside unquoted
    path fragments (e.g. ``docs/foo#section``) intact.
    """
    in_single = False
    in_double = False
    for idx, char in enumerate(value):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif (
            char == "#"
            and not in_single
            and not in_double
            and (idx == 0 or value[idx - 1].isspace())
        ):
            return value[:idx].rstrip()
    return value.strip()


def _parse_scalar(value: str) -> Any:
    """Parse a tiny subset of YAML scalars used by baseline diagnostics."""
    value = _strip_inline_comment(value.strip())
    if value in ("", "null", "Null", "NULL", "~"):
        return None
    if value in ("true", "True", "TRUE"):
        return True
    if value in ("false", "False", "FALSE"):
        return False
    if value == "[]":
        return []
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(part.strip()) for part in inner.split(",")]
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    # Only coerce plain base-10 integers. Leave zero-padded codes ("007") and
    # underscore-grouped values ("1_000") as strings so they are not corrupted
    # — this matches yaml.safe_load for these forms.
    if re.fullmatch(r"-?[1-9][0-9]*|0", value):
        return int(value)
    return value


def _load_manifest_minimal(manifest_path: Path) -> dict[str, Any]:
    """Load enough manifest structure for baseline checks without PyYAML.

    This fallback intentionally does not try to be a general YAML parser. It
    recognizes the manifest's top-level metadata, repo sections, local path
    hints, simple grounding/context_files path entries, and skill ``id`` /
    ``path`` / ``purpose`` fields so diagnostics can still run in a fresh
    checkout. Complex nested YAML remains a PyYAML-only feature.
    """
    data: dict[str, Any] = {"_minimal_fallback": True}
    current_repo: str | None = None
    current_list: str | None = None
    current_skill: dict[str, Any] | None = None
    current_mapping: str | None = None
    current_mapping_key: str | None = None

    for raw_line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if indent == 0 and line.endswith(":"):
            key = line[:-1]
            if key in ("foundations", "pmos"):
                current_repo = key
                data.setdefault(key, {})
            else:
                data.setdefault(key, {})
                current_repo = None
            current_list = None
            current_skill = None
            current_mapping = None
            current_mapping_key = None
            continue

        if indent == 0 and ":" in line:
            key, value = line.split(":", 1)
            data[key] = _parse_scalar(value)
            current_repo = None
            current_list = None
            current_mapping = None
            current_mapping_key = None
            continue

        if current_repo is None:
            continue
        section = data.setdefault(current_repo, {})

        if indent == 2 and line.endswith(":"):
            key = line[:-1]
            if key in ("local_path_hints", "skills"):
                section.setdefault(key, [])
                current_list = key
                current_mapping = None
            elif key in ("grounding", "context_files"):
                section.setdefault(key, {})
                current_mapping = key
                current_list = None
            else:
                section.setdefault(key, {})
                current_list = None
                current_mapping = None
            current_skill = None
            current_mapping_key = None
            continue

        if indent == 2 and ":" in line:
            key, value = line.split(":", 1)
            section[key] = _parse_scalar(value)
            current_list = None
            current_skill = None
            current_mapping = None
            current_mapping_key = None
            continue

        if (
            current_list == "local_path_hints"
            and indent == 4
            and line.startswith("- ")
        ):
            section.setdefault("local_path_hints", []).append(_parse_scalar(line[2:]))
            continue

        if current_list == "skills" and indent == 4 and line.startswith("- "):
            current_skill = {}
            section.setdefault("skills", []).append(current_skill)
            item = line[2:]
            if ":" in item:
                key, value = item.split(":", 1)
                current_skill[key] = _parse_scalar(value)
            continue

        if (
            current_list == "skills"
            and current_skill is not None
            and indent == 6
            and ":" in line
        ):
            key, value = line.split(":", 1)
            # Baseline diagnostics only need simple scalar skill metadata.
            if key in ("id", "path", "purpose"):
                current_skill[key] = _parse_scalar(value)
            continue

        if (
            current_mapping in ("grounding", "context_files")
            and indent == 4
            and ":" in line
        ):
            key, value = line.split(":", 1)
            mapping = section.setdefault(current_mapping, {})
            parsed_value = _parse_scalar(value)
            mapping[key] = {} if parsed_value is None else parsed_value
            current_mapping_key = key
            continue

        if (
            current_mapping in ("grounding", "context_files")
            and current_mapping_key
            and indent == 6
            and ":" in line
        ):
            key, value = line.split(":", 1)
            entry = section.setdefault(current_mapping, {}).setdefault(
                current_mapping_key, {}
            )
            # Capture every scalar sub-key, not just ``path`` — structured
            # grounding entries carry multiple path-like keys (e.g. path,
            # manifest, index, or cci_reference: {tasks, flows, flags}) that
            # the old ``path``-only branch silently dropped.
            if isinstance(entry, dict):
                entry[key] = _parse_scalar(value)
            continue

    return data

# ─── Repo discovery ─────────────────────────────────────────────────────────


@dataclass
class RepoLocation:
    """Resolved local clone of one repo declared in the manifest."""

    name: str
    role: str
    path: Path | None
    candidates_tried: list[Path]
    env_var: str | None  # which env var was tried first (if any)


def _discover_repo(
    repo_section: dict[str, Any], manifest_root: Path | None = None
) -> RepoLocation:
    """Resolve a manifest repo entry to a local Path, trying candidates in order.

    Relative hints (e.g. ``../pmos-revenue-cloud``) anchor against
    ``manifest_root`` (the directory containing ``.claude/skill-manifest.yml``),
    NOT the process cwd. This keeps ``--check`` and the documented sibling-
    directory fallback stable regardless of which subdirectory the caller is
    in (``docs/``, ``scripts/``, etc.).
    """
    hints: list[str] = repo_section.get("local_path_hints", []) or []
    candidates: list[Path] = []
    env_var: str | None = None

    for hint in hints:
        # Skip non-string hints (a malformed manifest could yield ints/lists),
        # which would otherwise raise TypeError in expanduser/expandvars.
        if not isinstance(hint, str):
            continue
        # Expand env vars and ~. If the var is unset, expandvars leaves "$FOO"
        # as-is; we filter those out below.
        expanded = os.path.expandvars(os.path.expanduser(hint))
        if "$" in expanded:
            # Unresolved var; remember which one so the diagnostic is helpful
            if env_var is None and hint.startswith("$"):
                env_var = hint.split("/")[0].lstrip("$")
            continue
        p = Path(expanded)
        if not p.is_absolute() and manifest_root is not None:
            p = (manifest_root / p).resolve()
        candidates.append(p)

    # Phase 6.3 transition: only Foundations ships the manifest today.
    # For the OTHER repo (the one whose clone we're trying to find from
    # this one's manifest), accept a directory that looks like the right repo
    # even without the manifest file — we'll know it's the right repo because
    # the manifest declared its repo name, and we can sanity-check via a
    # well-known marker (.claude/ or .cursor/).
    repo_name = repo_section.get("name", "")
    for cand in candidates:
        if not cand.is_dir():
            continue
        # Strict match: manifest already shipped here
        if (cand / MANIFEST_FILENAME).is_file():
            return RepoLocation(
                name=repo_name or "<unknown>",
                role=repo_section.get("role", "<unknown>"),
                path=cand,
                candidates_tried=candidates,
                env_var=env_var,
            )
        # Lenient match: directory exists with the expected agent surface.
        # Foundations ships .cursor/skills/; PMOS ships .claude/skills/.
        # If either is present at this candidate, treat it as the clone.
        looks_like_pmos = (cand / ".claude" / "skills").is_dir()
        looks_like_foundations = (cand / ".cursor" / "skills").is_dir()
        if (repo_name == "pmos-revenue-cloud" and looks_like_pmos) or (
            repo_name == "rlm-base-dev" and looks_like_foundations
        ):
            return RepoLocation(
                name=repo_name or "<unknown>",
                role=repo_section.get("role", "<unknown>"),
                path=cand,
                candidates_tried=candidates,
                env_var=env_var,
            )

    return RepoLocation(
        name=repo_section.get("name", "<unknown>"),
        role=repo_section.get("role", "<unknown>"),
        path=None,
        candidates_tried=candidates,
        env_var=env_var,
    )


# ─── Manifest loading ───────────────────────────────────────────────────────


def find_manifest(start: Path | None = None) -> Path:
    """Walk up from `start` (default: cwd) looking for .claude/skill-manifest.yml."""
    cwd = (start or Path.cwd()).resolve()
    for d in [cwd, *cwd.parents]:
        candidate = d / MANIFEST_FILENAME
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        f"No {MANIFEST_FILENAME} found walking up from {cwd}. "
        "Run this from inside a Foundations or PMOS clone, or set "
        "FOUNDATIONS_REPO_ROOT / PMOS_REPO_ROOT explicitly."
    )


def load_manifest(path: Path | None = None) -> dict[str, Any]:
    """Load and lightly normalize the manifest. Discovers repo locations."""
    manifest_path = path or find_manifest()
    if yaml is None:
        print(PY_YAML_HELP, file=sys.stderr)
        data = _load_manifest_minimal(manifest_path)
    else:
        with manifest_path.open("r") as f:
            data: dict[str, Any] = yaml.safe_load(f) or {}

    # Stash where we found it so callers can debug
    data["_manifest_path"] = str(manifest_path)
    manifest_root = manifest_path.parent.parent  # .claude/skill-manifest.yml -> repo root
    data["_self_repo_root"] = str(manifest_root)

    # Discover both repos' clones, anchoring relative hints to the manifest's
    # repo root (NOT process cwd) so discovery is stable from any subdirectory.
    for key in ("foundations", "pmos"):
        # An empty `foundations:`/`pmos:` section parses to None; only resolve
        # when the section is actually a mapping.
        if isinstance(data.get(key), dict):
            data[key]["_resolved"] = _discover_repo(data[key], manifest_root)

    return data


# ─── Lookup helpers ─────────────────────────────────────────────────────────


def resolve_repo_root(manifest: dict[str, Any], repo: str) -> Path | None:
    """Return the local Path for the named repo's clone, or None if not found."""
    section = manifest.get(repo)
    if not section:
        return None
    resolved: RepoLocation | None = section.get("_resolved")
    if resolved is None or resolved.path is None:
        return None
    return resolved.path


def resolve_path(
    manifest: dict[str, Any], repo: str, relative_path: str
) -> Path | None:
    """Resolve a manifest-relative path to an absolute Path, if the clone exists."""
    root = resolve_repo_root(manifest, repo)
    if root is None:
        return None
    return root / relative_path


def resolve_grounding(
    manifest: dict[str, Any], repo: str, key: str
) -> Path | dict[str, Path] | None:
    """Look up a grounding artifact by key (e.g. 'qb_scenario') and resolve it.

    Returns a single ``Path`` for entries with a single ``path:`` value (or a
    bare string). Returns a ``dict[str, Path]`` for STRUCTURED entries that
    expose multiple paths under named sub-keys (e.g.
    ``cci_reference: {tasks: ..., flows: ..., flags: ...}``) — the dict maps
    each sub-key whose value looks like a filesystem path to its resolved
    absolute ``Path``. Returns ``None`` if the key is missing or the entry
    contains no resolvable paths.

    Callers expecting a single Path should check ``isinstance(result, Path)``
    before treating it as one.
    """
    section = manifest.get(repo, {})
    grounding = section.get("grounding") or section.get("context_files") or {}
    entry = grounding.get(key)
    if entry is None:
        return None
    if isinstance(entry, str):
        return resolve_path(manifest, repo, entry)
    if isinstance(entry, dict):
        if "path" in entry and isinstance(entry["path"], str):
            return resolve_path(manifest, repo, entry["path"])
        # Structured entry: collect every value that looks like a relative
        # filesystem path (string containing '/' or ending in a known
        # extension). Skip metadata fields (counts, status, etc.).
        resolved: dict[str, Path] = {}
        for sub_key, sub_val in entry.items():
            if not isinstance(sub_val, str):
                continue
            if "/" not in sub_val and not sub_val.endswith((
                ".md", ".json", ".yml", ".yaml", ".py", ".txt"
            )):
                continue
            p = resolve_path(manifest, repo, sub_val)
            if p is not None:
                resolved[sub_key] = p
        return resolved or None
    return None


def list_skills(manifest: dict[str, Any], repo: str) -> list[dict[str, Any]]:
    """Return the list of skill entries for a given repo."""
    return list(manifest.get(repo, {}).get("skills", []) or [])


def find_skill(
    manifest: dict[str, Any], repo: str, skill_id: str
) -> dict[str, Any] | None:
    """Find a skill entry by id within the named repo."""
    for entry in list_skills(manifest, repo):
        if entry.get("id") == skill_id:
            return entry
    return None


def resolve_skill(
    manifest: dict[str, Any], repo: str, skill_id: str
) -> Path | None:
    """Resolve a skill SKILL.md to an absolute Path."""
    entry = find_skill(manifest, repo, skill_id)
    if entry is None:
        return None
    rel = entry.get("path")
    if not rel:
        return None
    return resolve_path(manifest, repo, rel)


# ─── Diagnostics CLI ────────────────────────────────────────────────────────


def _cli_check(manifest: dict[str, Any]) -> int:
    """Verify both repos can be located; print a status report.

    A repo section may declare ``optional: true`` in the manifest. Absent
    optional clones are reported as ``[INFO]`` lines and DO NOT fail the
    check (exit 0); only absent required clones fail. This matches the
    PMOS-as-optional contract documented in ``pmos-integration/SKILL.md``
    and the manifest's PMOS section header.
    """
    print(f"Manifest: {manifest['_manifest_path']}")
    print(f"Manifest version: {manifest.get('manifest_version', '?')}")
    print(f"Last verified: {manifest.get('last_verified', '?')}")
    print()

    overall_ok = True
    for key in ("foundations", "pmos"):
        section = manifest.get(key, {})
        resolved: RepoLocation | None = section.get("_resolved")
        is_optional = bool(section.get("optional", False))
        if resolved is None:
            # Section missing entirely. Always fatal even for "optional" repos,
            # because the manifest itself is malformed.
            print(f"  [ERROR] {key}: section missing in manifest")
            overall_ok = False
            continue
        if resolved.path is None:
            if is_optional:
                print(
                    f"  [INFO]  {key} ({resolved.name}): clone not found "
                    f"(optional — degrading gracefully)"
                )
                print(f"          tried: {[str(p) for p in resolved.candidates_tried]}")
                if resolved.env_var:
                    print(f"          to enable, set env var: {resolved.env_var}")
                # Do not flip overall_ok for optional misses.
            else:
                print(f"  [ERROR] {key} ({resolved.name}): required clone not found")
                print(f"          tried: {[str(p) for p in resolved.candidates_tried]}")
                if resolved.env_var:
                    print(f"          consider setting env var: {resolved.env_var}")
                overall_ok = False
        else:
            tag = "OK-OPT" if is_optional else "OK"
            print(f"  [{tag:6s}] {key}: {resolved.path}")
    return 0 if overall_ok else 1


def _cli_list_skills(manifest: dict[str, Any], repo: str) -> int:
    skills = list_skills(manifest, repo)
    if not skills:
        print(f"No skills declared for repo '{repo}'", file=sys.stderr)
        return 1
    for entry in skills:
        sid = entry.get("id", "<unnamed>")
        purpose = entry.get("purpose", "")
        path_rel = entry.get("path", "")
        resolved = resolve_skill(manifest, repo, sid)
        status = "OK" if resolved and resolved.is_file() else "MISSING"
        print(f"  [{status:7s}] {sid:30s} {purpose}")
        print(f"             {path_rel}")
    return 0


def _cli_resolve(manifest: dict[str, Any], spec: str) -> int:
    """Resolve a path spec: {repo}/{kind}/{key}.

    e.g. foundations/grounding/qb_scenario
         foundations/skills/release-enablement
         pmos/context_files/capabilities
    """
    parts = spec.split("/", 2)
    if len(parts) < 3:
        print(
            "spec must be {repo}/{kind}/{key} (e.g. foundations/grounding/qb_scenario)",
            file=sys.stderr,
        )
        return 2
    repo, kind, key = parts
    if kind in ("grounding", "context_files"):
        result = resolve_grounding(manifest, repo, key)
    elif kind == "skills":
        result = resolve_skill(manifest, repo, key)
    elif kind == "path":
        result = resolve_path(manifest, repo, key)
    else:
        print(f"unknown kind '{kind}'; use grounding|skills|path", file=sys.stderr)
        return 2
    if result is None:
        print(f"could not resolve {spec}", file=sys.stderr)
        return 1
    if isinstance(result, dict):
        # Structured grounding entry — print one line per sub-key, exit
        # non-zero if any of them don't exist.
        all_exist = True
        for sub_key, sub_path in sorted(result.items()):
            exists = sub_path.exists()
            all_exist = all_exist and exists
            print(f"{sub_key}: {sub_path}{'' if exists else '  (MISSING)'}")
        return 0 if all_exist else 1
    print(result)
    return 0 if result.exists() else 1


def main(argv: Iterable[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Cross-repo skill-manifest resolver (Foundations side)."
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="verify clone discovery")
    g.add_argument(
        "--list-skills",
        choices=["foundations", "pmos"],
        help="list declared skills for a repo",
    )
    g.add_argument(
        "--resolve",
        metavar="SPEC",
        help="resolve a path spec, e.g. foundations/grounding/qb_scenario",
    )
    p.add_argument(
        "--manifest",
        type=Path,
        help="explicit manifest path (default: walk up from cwd)",
    )
    args = p.parse_args(list(argv) if argv is not None else None)

    manifest = load_manifest(args.manifest)

    if args.check:
        return _cli_check(manifest)
    if args.list_skills:
        return _cli_list_skills(manifest, args.list_skills)
    if args.resolve:
        return _cli_resolve(manifest, args.resolve)
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
