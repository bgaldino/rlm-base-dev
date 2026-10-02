"""Feature flags and flexipage source resolution for the UX tooling.

Single source of truth for the UX feature-flag list and the standalone
flexipage directory order, shared by assembly, retrieve, diff and writeback.
Flags come from ``project.custom`` in ``cumulusci.yml``; the CLI layers
runtime overrides on top (``--flag name=value``), and the CCI wrapper passes
``project_config.project__custom``.
"""
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

try:
    import yaml
except ImportError:
    yaml = None

from scripts.ux._context import DEFAULT_API_VERSION, UxOptionError


#: All feature flags that gate UX metadata assembly / retrieval.
UX_KNOWN_FLAGS: List[str] = [
    "quantumbit", "billing", "billing_ui", "tax", "rating", "rates", "clm", "dro",
    "guidedselling", "tso", "prm", "agents", "docgen",
    "payments", "constraints", "analytics", "procedureplans", "large_stx",
    "collections", "personas", "prm_pricing",
]

#: Profile templates only assembled when the personas feature flag is true.
PERSONAS_PROFILES: List[str] = [
    "RLM Sales Representative.profile-meta.xml",
]

#: LWC identifier for the Sales Transaction Line Editor component in Quote flexipages.
SALES_TXN_LINE_EDITOR_IDENTIFIER = "runtime_rca_salesTxnLineTable"

#: Standalone flexipage dirs in deploy order (last writer wins).
#: Each entry is (directory_name, flag_key).
#: Order matches the prepare_rlm_org deploy sequence.
_STANDALONE_ORDER: List[Tuple[str, str]] = [
    ("payments",    "payments"),
    ("billing",     "billing"),
    ("billing_ui",  "billing_ui"),
    ("quantumbit",  "quantumbit"),
    ("tso",         "tso"),
    ("constraints", "constraints"),
    ("utils",       "quantumbit"),  # utils deploys with quantumbit flow
    ("docgen",      "docgen"),
    ("approvals",   "quantumbit"),  # approvals deploys with quantumbit flow
    ("collections", "collections"),
    ("prm_pricing", "prm_pricing"),
]


def to_bool(val: Any) -> bool:
    """Coerce a flag value the way CumulusCI's process_bool_arg does."""
    if isinstance(val, bool):
        return val
    if val is None:
        return False
    return str(val).strip().lower() in ("true", "1", "yes", "y", "on")


def features_from_custom(custom: Optional[Mapping[str, Any]]) -> Dict[str, bool]:
    """Read the UX-relevant flags from a ``project.custom`` mapping."""
    custom = custom or {}
    flags: Dict[str, bool] = {}
    for flag in UX_KNOWN_FLAGS:
        val = custom.get(flag, False)
        flags[flag] = to_bool(val) if isinstance(val, (str, bool)) else bool(val)
    return flags


def load_project_config(repo_root: Path) -> Tuple[Dict[str, Any], str]:
    """Return ``(project.custom, project.package.api_version)`` from cumulusci.yml."""
    if yaml is None:
        raise UxOptionError("PyYAML is required. Install with: pip install pyyaml")
    path = Path(repo_root) / "cumulusci.yml"
    if not path.exists():
        raise UxOptionError(f"cumulusci.yml not found at {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    project = data.get("project") or {}
    custom = project.get("custom") or {}
    api_version = str((project.get("package") or {}).get("api_version") or DEFAULT_API_VERSION)
    return custom, api_version


def parse_flag_overrides(values: Iterable[str]) -> Dict[str, bool]:
    """Parse ``name=value`` overrides; reject names the UX tooling does not know."""
    overrides: Dict[str, bool] = {}
    for raw in values or []:
        name, sep, value = raw.partition("=")
        name = name.strip()
        if not sep or not name:
            raise UxOptionError(f"--flag expects name=true|false, got: '{raw}'")
        if name not in UX_KNOWN_FLAGS:
            raise UxOptionError(
                f"Unknown UX feature flag '{name}'. Known flags: {', '.join(UX_KNOWN_FLAGS)}"
            )
        overrides[name] = to_bool(value)
    return overrides


def flags_from_manifest(manifest_path: Path) -> Dict[str, bool]:
    """Read the feature flags recorded by a previous assembly run."""
    path = Path(manifest_path)
    if not path.exists():
        raise UxOptionError(f"Assembly manifest not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise UxOptionError(f"Assembly manifest is not valid JSON: {path} ({exc})") from exc
    recorded = data.get("feature_flags") or {}
    return {k: to_bool(v) for k, v in recorded.items() if k in UX_KNOWN_FLAGS}


def resolve_features(
    repo_root: Path,
    overrides: Optional[Mapping[str, bool]] = None,
    manifest_path: Optional[Path] = None,
) -> Tuple[Dict[str, bool], str]:
    """Resolve UX flags: cumulusci.yml defaults, then the manifest, then overrides."""
    custom, api_version = load_project_config(repo_root)
    features = features_from_custom(custom)
    if manifest_path is not None:
        features.update(flags_from_manifest(manifest_path))
    features.update(overrides or {})
    return features, api_version


def resolve_flexipage_sources(
    base_dir: Path,
    standalone_dir: Path,
    features: Dict[str, bool],
) -> Dict[str, Path]:
    """
    Build a filename → source-path map for all active flexipages.

    Seeds from ``base_dir/``, then overlays each active standalone feature
    directory in deploy order (last writer wins, matching prepare_rlm_org).
    """
    sources: Dict[str, Path] = {}

    for f in sorted(base_dir.glob("*.flexipage-meta.xml")):
        sources[f.name] = f

    for feature_dir, flag_key in _STANDALONE_ORDER:
        if not features.get(flag_key, False):
            continue
        src_dir = standalone_dir / feature_dir
        if not src_dir.exists():
            continue
        for src_file in sorted(src_dir.glob("*.flexipage-meta.xml")):
            sources[src_file.name] = src_file

    return sources
