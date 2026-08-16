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
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

# PyYAML is optional at import time. Any import-time failure — module missing,
# a broken/partial install, a SyntaxError or runtime error in the module, or a
# find_spec error — degrades to the stdlib-only minimal fallback.
yaml = None
try:
    if importlib.util.find_spec("yaml") is not None:
        yaml = importlib.import_module("yaml")
except Exception:
    yaml = None


MANIFEST_FILENAME = ".claude/skill-manifest.yml"

PY_YAML_HELP = (
    "PyYAML is not available (not installed, or failed to import), so "
    "skill_manifest.py is using its minimal fallback. "
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
        # Inline flow list. Drop empty segments so a trailing comma ("[a, b,]")
        # matches yaml.safe_load rather than injecting a None.
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(part.strip()) for part in inner.split(",") if part.strip()]
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    # Coerce plain decimal integers (including a signed zero). Zero-padded codes
    # ("007") and underscore-grouped values ("1_000") are INTENTIONALLY kept as
    # strings to avoid corrupting identifiers; this diverges from yaml.safe_load
    # (YAML 1.1 would coerce them), but the manifest contains no such values.
    if re.fullmatch(r"-?(?:0|[1-9][0-9]*)", value):
        return int(value)
    return value


def _split_key_value(content: str) -> tuple[str, str | None]:
    """Split a ``key: value`` line at the first ``:`` that is outside quotes and
    followed by whitespace or end-of-line (YAML's mapping separator).

    Returns ``(key, value)``, or ``(content, None)`` when there is no separator
    (so a quoted key containing a colon, e.g. ``"a:b": 1``, is not split mid-key).
    """
    in_single = in_double = False
    for i, ch in enumerate(content):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == ":" and not in_single and not in_double:
            if i + 1 >= len(content) or content[i + 1] in " \t":
                return content[:i], content[i + 1:]
    return content, None


def _reject_block_scalar(value: str) -> None:
    """Raise on a YAML block-scalar indicator (``|``/``>`` with optional
    chomping/indent modifiers). The fallback cannot fold multi-line block
    scalars, so fail loudly rather than silently truncating to ``|``/``>``."""
    if re.fullmatch(r"[|>][+-]?[0-9]?", value.strip()):
        raise ValueError(
            "block scalars (| or >) are not supported by the no-PyYAML "
            "fallback; install PyYAML for full manifest parsing"
        )


def _load_manifest_minimal(text: str) -> dict[str, Any]:
    """Parse the manifest without PyYAML, via a generic indent-based parser.

    Accepts the already-read manifest text (the caller reads it, so I/O errors
    are handled in one place). It supports the block-YAML subset the manifest
    uses — nested mappings, block lists (``- item``), inline flow lists
    (``[a, b]``), scalars (str/int/bool/null), quoted strings, and ``#``
    comments — and for that structure reproduces ``yaml.safe_load``. It is NOT a
    general YAML parser: anchors/aliases, merge keys, block scalars (``|``/``>``)
    and flow maps are unsupported (the manifest uses none of them). For the
    current manifest the output is verified to equal ``yaml.safe_load``.
    """
    # Tokenize: (indent, content) for non-blank, non-comment-only lines, with
    # trailing inline comments stripped (respecting quotes) so a line like
    # `key:   # note` is seen as an empty-valued key, not a scalar.
    tokens: list[tuple[int, str]] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        content = _strip_inline_comment(stripped)
        if not content:
            continue
        tokens.append((len(raw) - len(raw.lstrip(" ")), content))

    pos = [0]  # boxed index so the nested parsers can advance it

    def parse_block(indent: int) -> Any:
        if pos[0] >= len(tokens):
            return None
        content = tokens[pos[0]][1]
        if content == "-" or content.startswith("- "):
            return parse_list(indent)
        return parse_map(indent)

    def parse_map(indent: int) -> dict[str, Any]:
        result: dict[str, Any] = {}
        while pos[0] < len(tokens):
            cur_indent, content = tokens[pos[0]]
            if cur_indent != indent or content.startswith("- "):
                break
            key_raw, val_raw = _split_key_value(content)
            key = key_raw.strip()
            if len(key) >= 2 and key[0] == key[-1] and key[0] in "\"'":
                key = key[1:-1]  # unquote a quoted mapping key
            pos[0] += 1
            val = (val_raw or "").strip()
            if val == "":
                child_indent = tokens[pos[0]][0] if pos[0] < len(tokens) else -1
                result[key] = parse_block(child_indent) if child_indent > indent else None
            else:
                _reject_block_scalar(val)
                result[key] = _parse_scalar(val)
        return result

    def parse_list(indent: int) -> list[Any]:
        result: list[Any] = []
        while pos[0] < len(tokens):
            cur_indent, content = tokens[pos[0]]
            if cur_indent != indent or not (content == "-" or content.startswith("- ")):
                break
            item = content[1:].strip()
            # A mapping list item ("- key: value") starts a mapping whose keys
            # sit at indent + 2 (the columns after "- "). Quote-aware detection
            # via _split_key_value handles quoted keys that contain a colon.
            _, item_val = _split_key_value(item)
            if item_val is not None:
                tokens[pos[0]] = (indent + 2, item)
                result.append(parse_map(indent + 2))
            else:
                pos[0] += 1
                result.append(_parse_scalar(item))
        return result

    data = parse_block(0)
    return data if isinstance(data, dict) else {}

# ─── Repo discovery ─────────────────────────────────────────────────────────


@dataclass
class RepoLocation:
    """Resolved local clone of one repo declared in the manifest."""

    name: str
    role: str
    path: Path | None
    candidates_tried: list[Path]
    env_var: str | None  # which env var was tried first (if any)
    # Identity of the accepted candidate relative to the declared repo_url:
    #   "verified-remote" — git remote matches repo_url
    #   "verified-self"   — the candidate IS the repo containing this manifest
    #                       AND carries this section's repo-specific surface
    #                       (remote not consulted)
    #   "unverified"      — structural match (strict or lenient) accepted, but
    #                       no remote/URL comparison was possible
    #   "unknown"         — no candidate accepted
    identity: str = "unknown"
    # Candidates that structurally matched but were REJECTED because their git
    # remote names a different repo than the manifest's repo_url. Each entry is
    # (path, remote_url). A stale clone of a departed maintainer's repo lands
    # here instead of silently winning discovery — the P0 failure class.
    rejected: list[tuple[Path, str]] = field(default_factory=list)


def _git_remote_url(path: Path) -> str | None:
    """Return the clone's ``remote.origin.url``, or None if unreadable.

    Uses ``git -C <path> config --get remote.origin.url`` so worktrees and
    gitfile indirection are handled by git itself. Any failure (not a git
    repo, git not installed, no origin remote) returns None — the caller
    treats that as "identity unverifiable", never as an error.
    """
    try:
        res = subprocess.run(
            ["git", "-C", str(path), "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    url = res.stdout.strip()
    return url or None


def _normalize_repo_url(url: str) -> tuple[str, str] | None:
    """Reduce a git URL to ``(host, owner/repo)`` for identity comparison.

    Handles https://host/owner/repo(.git), ssh://git@host/owner/repo(.git),
    and scp-style git@host:owner/repo(.git). Returns None if the URL doesn't
    parse into host + two path segments.
    """
    u = url.strip().rstrip("/")
    if u.endswith(".git"):
        u = u[: -len(".git")]
    m = re.match(r"^(?:ssh://)?git@([^:/]+)[:/](.+)$", u)
    if m:
        host, rest = m.group(1), m.group(2)
    else:
        m = re.match(r"^[a-z+]+://([^/]+)/(.+)$", u)
        if not m:
            return None
        host, rest = m.group(1), m.group(2)
    parts = [p for p in rest.split("/") if p]
    if len(parts) < 2:
        return None
    return (host.lower(), "/".join(parts[-2:]).lower())


def _urls_equivalent(a: str, b: str) -> bool | None:
    """Compare two git URLs after normalization.

    Returns True (same repo), False (provably DIFFERENT repos), or None when
    either URL does not normalize (local-path or ``file://`` remotes, exotic
    schemes). None means "cannot compare" — callers must treat it as
    unverifiable, never as a mismatch: rejecting a legitimate clone because
    its remote is a local mirror would be a false positive.
    """
    na, nb = _normalize_repo_url(a), _normalize_repo_url(b)
    if na is None or nb is None:
        return None
    return na == nb


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
    declared_url = repo_section.get("repo_url", "") or ""
    rejected: list[tuple[Path, str]] = []

    def _identity_of(cand: Path) -> str | None:
        """Classify a structurally-matching candidate against repo_url.

        Returns "verified", "unverified", or None (= REJECT: the clone's
        remote provably names a different repo). Structural matching alone
        is what let a departed maintainer's stale clone win discovery and
        silently supply outdated grounding — the P0 failure class — so a
        readable remote that disagrees with the declared repo_url disqualifies
        the candidate outright.
        """
        if manifest_root is not None and cand.resolve() == manifest_root.resolve():
            # The repo containing this manifest is trivially itself — but only
            # for the section that actually DESCRIBES this repo. The manifest
            # is designed to ship identically in both repos, so containment
            # alone cannot say which section it satisfies: a PMOS hint pointed
            # at this Foundations checkout would otherwise be accepted as a
            # "verified" PMOS clone. Require the section's repo-specific agent
            # surface; on mismatch, fall through to remote comparison, which
            # rejects a provably different repo.
            self_is_this_section = (
                repo_name == "pmos-revenue-cloud"
                and (cand / ".claude" / "skills").is_dir()
            ) or (
                repo_name == "rlm-base-dev"
                and (cand / ".cursor" / "skills").is_dir()
            )
            if self_is_this_section:
                return "verified-self"
        remote = _git_remote_url(cand)
        if remote is None or not declared_url:
            return "unverified"
        same = _urls_equivalent(remote, declared_url)
        if same is None:
            # Readable remote, but not comparable (local-path/file:// mirror,
            # exotic scheme). Not a provable mismatch — fall back to the
            # documented unverified acceptance rather than rejecting.
            return "unverified"
        if same:
            return "verified-remote"
        rejected.append((cand, remote))
        return None

    for cand in candidates:
        if not cand.is_dir():
            continue
        # Strict match: manifest already shipped here
        if (cand / MANIFEST_FILENAME).is_file():
            identity = _identity_of(cand)
            if identity is None:
                continue
            return RepoLocation(
                name=repo_name or "<unknown>",
                role=repo_section.get("role", "<unknown>"),
                path=cand,
                candidates_tried=candidates,
                env_var=env_var,
                identity=identity,
                rejected=rejected,
            )
        # Lenient match: directory exists with the expected agent surface.
        # Foundations ships .cursor/skills/; PMOS ships .claude/skills/.
        # If either is present at this candidate, treat it as the clone.
        looks_like_pmos = (cand / ".claude" / "skills").is_dir()
        looks_like_foundations = (cand / ".cursor" / "skills").is_dir()
        if (repo_name == "pmos-revenue-cloud" and looks_like_pmos) or (
            repo_name == "rlm-base-dev" and looks_like_foundations
        ):
            identity = _identity_of(cand)
            if identity is None:
                continue
            return RepoLocation(
                name=repo_name or "<unknown>",
                role=repo_section.get("role", "<unknown>"),
                path=cand,
                candidates_tried=candidates,
                env_var=env_var,
                identity=identity,
                rejected=rejected,
            )

    return RepoLocation(
        name=repo_section.get("name", "<unknown>"),
        role=repo_section.get("role", "<unknown>"),
        path=None,
        candidates_tried=candidates,
        env_var=env_var,
        rejected=rejected,
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
    # Read once, with a guard, so an unreadable manifest produces a clear
    # diagnostic (not a traceback) in both the PyYAML and fallback paths.
    try:
        manifest_text = manifest_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise SystemExit(f"skill_manifest.py: cannot read {manifest_path}: {exc}")
    if yaml is None:
        print(PY_YAML_HELP, file=sys.stderr)
        try:
            data = _load_manifest_minimal(manifest_text)
        except Exception as exc:
            # Mirror the PyYAML branch: any fallback parse failure (e.g. an
            # over-nested manifest, or an unsupported block scalar) becomes a
            # clean diagnostic rather than a raw traceback.
            raise SystemExit(f"skill_manifest.py: cannot parse {manifest_path}: {exc}")
    else:
        try:
            data: dict[str, Any] = yaml.safe_load(manifest_text) or {}
        except yaml.YAMLError as exc:
            raise SystemExit(f"skill_manifest.py: cannot parse {manifest_path}: {exc}")
        if not isinstance(data, dict):
            data = {}

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
        for rej_path, rej_remote in resolved.rejected:
            print(
                f"  [WARN]  {key}: REJECTED candidate {rej_path} — its git remote "
                f"({rej_remote}) names a different repo than the declared repo_url. "
                f"A stale/foreign clone at a hint path must not win discovery; "
                f"remove or re-clone it."
            )
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
            if resolved.identity == "verified-remote":
                print("          identity: verified (git remote matches repo_url)")
            elif resolved.identity == "verified-self":
                print(
                    "          identity: verified (this clone contains this "
                    "manifest and the section's repo surface; remote not "
                    "consulted)"
                )
            else:
                print(
                    "          identity: UNVERIFIED — no remote/URL comparison "
                    "was possible (unreadable git remote, undeclared repo_url, "
                    "or a remote form that does not normalize, e.g. a "
                    "local-path/file:// mirror); structural match accepted. "
                    "Confirm this clone is the declared repo."
                )
            if key == "pmos":
                skills_dir = resolved.path / ".claude" / "skills"
                if skills_dir.is_dir():
                    n = sum(
                        1
                        for d in skills_dir.iterdir()
                        if d.is_dir() and (d / "SKILL.md").is_file()
                    )
                    print(f"          skills on disk: {n} (measured, not hand-kept)")

    return 0 if _audit_foundations(manifest) and overall_ok else 1


#: Where a repo-relative path can start. Anything outside this is prose, not a path.
_PATH_ROOTS = (
    ".agents/", ".claude/", ".cursor/", ".github/", "config/", "datasets/", "docs/",
    "force-app/", "orgs/", "postman/", "robot/", "scripts/", "tasks/", "templates/",
    "unpackaged/",
)
#: Root-level files the manifest legitimately names. Without these, a typo in a
#: declared root file passed the audit because it matched no _PATH_ROOTS prefix.
_ROOT_FILES = ("AGENTS.md", "CLAUDE.md", "REVIEW.md", "README.md", "cumulusci.yml")


def _path_like_values(node: Any, where: str):
    """Yield (location, value) for every string in a manifest subtree that names a
    repo path. Recursive on purpose — see the caller."""
    if isinstance(node, dict):
        # ⚠ An entry that declares itself absent used to skip its WHOLE subtree, which
        # also skipped the paths it still actively claims. The prior-GA entry is exactly
        # that shape: status not_captured, and `partial:
        # docs/salesforce/260/feature-index.md` — a file that does exist and is offered
        # to consumers. Deleting or misspelling it passed --check while the audit printed
        # "all paths resolve".
        #
        # The skip bought nothing anyway: an entry declaring itself absent has its
        # path/manifest keys REMOVED from the YAML (the prior-GA comment says to restore
        # them once captured), so there was never an absent path here to protect. Keep
        # walking — what a not_captured entry still names, it still has to have.
        for key, value in node.items():
            yield from _path_like_values(value, f"{where}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _path_like_values(value, f"{where}[{index}]")
    elif isinstance(node, str) and (node.startswith(_PATH_ROOTS) or node in _ROOT_FILES):
        yield where, node


def _audit_foundations(manifest: dict[str, Any]) -> bool:
    """Resolve what the Foundations section CLAIMS against the working tree.

    ⚠ Clone discovery succeeding says nothing about whether the manifest is true.
    Before this audit existed, ``--check`` printed OK for two months while two
    skills present since April and May went unadvertised, the postman collection
    filenames named files that had never existed, and the prior-GA help corpus
    pointed at a directory never committed on any branch. A check that cannot
    fail is not a check.

    PMOS is deliberately not audited: its clone is optional and usually absent,
    so every path would miss for a reason that is not drift.
    """
    section = manifest.get("foundations", {})
    resolved: RepoLocation | None = section.get("_resolved")
    if resolved is None or resolved.path is None:
        return True  # nothing to audit against; the clone check already reported it
    root = Path(resolved.path)

    problems: list[str] = []

    def exists(rel: str) -> bool:
        # ⚠ A template ({release}) cannot be resolved to ONE path, but that is not a
        # reason to accept it unchecked — and it used to be: `"{" in rel or ...`
        # short-circuited to True, so `docs/enablement/{release}/never-existed.md`
        # passed and the audit still printed "all paths resolve". Unfalsifiable is
        # exactly the defect this function's own docstring was written about, one
        # level deeper: a check that cannot fail is not a check.
        #
        # A template cannot be resolved, but it CAN be falsified: expand each
        # placeholder to a glob and require at least one real match. That still
        # catches a renamed or deleted filename, which is the drift that actually
        # happens; it deliberately does not verify every release has one.
        if "{" in rel:
            pattern = re.sub(r"\{[^}]*\}", "*", rel)
            if pattern.startswith(("/", "~")):  # Path.glob rejects absolute patterns
                return False
            return any(root.glob(pattern.rstrip("/")))
        return (root / rel).exists()

    declared = {s.get("id") for s in section.get("skills", []) or []}
    for entry in section.get("skills", []) or []:
        for rel in [entry.get("path")] + list(entry.get("sub_skills") or []) + list(
            entry.get("tooling") or []
        ):
            if rel and not exists(rel):
                problems.append(f"skill {entry.get('id')}: missing {rel}")

    on_disk = {p.parent.name for p in sorted(root.glob(".cursor/skills/*/SKILL.md"))}
    for name in sorted(on_disk - declared):
        problems.append(f"{name}: has a SKILL.md but is not declared — agents cannot discover it")

    # ⚠ Every path-shaped value in the WHOLE section, found by walking — not a
    # hand-listed set of field names, and not one subtree.
    #
    # Twice now this has been narrower than its own claim. First it checked only
    # path/manifest/index plus a postman list, missing `postman_environment` — added in
    # the very same change. Then it walked `grounding` only, so skill fields like
    # `auto_generated_subfiles` and `governs`, and declared root files such as
    # AGENTS.md, still went unaudited while the output said "all paths resolve".
    # The lesson both times: scope the walk to the claim, or weaken the claim.
    for where, rel in _path_like_values(section, "foundations"):
        if not exists(rel):
            problems.append(f"{where}: missing {rel}")

    print()
    if problems:
        print(f"  [ERROR] foundations manifest does not match the working tree "
              f"({len(problems)} problem(s)):")
        for problem in problems:
            print(f"          - {problem}")
        return False
    print(f"  [OK    ] foundations manifest matches the working tree "
          f"({len(declared)} skills declared, all paths resolve)")
    return True


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
