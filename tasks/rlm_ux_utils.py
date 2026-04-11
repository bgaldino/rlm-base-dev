"""
Shared utilities for UX metadata assembly, retrieval, and writeback tasks.

Centralises the standalone flexipage feature-directory order and feature-flag
reader so that rlm_ux_assembly.py, rlm_writeback_ux.py, and
rlm_retrieve_ux.py all stay in sync when new standalone feature dirs are added.
"""
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from cumulusci.core.utils import process_bool_arg
except ImportError:
    def process_bool_arg(val):  # type: ignore[misc]
        if isinstance(val, bool):
            return val
        return str(val).lower() in ("true", "1", "yes")


#: All feature flags that gate UX metadata assembly / retrieval.
UX_KNOWN_FLAGS: List[str] = [
    "qb", "billing", "billing_ui", "tax", "rating", "rates", "clm", "dro",
    "guidedselling", "ramps", "tso", "prm", "agents", "docgen",
    "payments", "constraints", "analytics", "procedureplans",
    "collections", "badger",
]

#: Standalone flexipage dirs in deploy order (last writer wins).
#: Each entry is (directory_name, flag_key).
#: Order matches the prepare_rlm_org deploy sequence.
#: Manufacturing is intentionally excluded here — it is only appended when
#: manufacturing_mode=True is passed to resolve_flexipage_sources (i.e. when
#: called from prepare_mfg_ux, which runs after manufacturing metadata is deployed).
_STANDALONE_ORDER: List[Tuple[str, str]] = [
    ("payments",       "payments"),
    ("billing",        "billing"),
    ("billing_ui",     "billing_ui"),
    ("quantumbit",     "qb"),
    ("tso",            "tso"),
    ("constraints",    "constraints"),
    ("utils",          "qb"),           # utils deploys with qb flow
    ("docgen",         "docgen"),
    ("approvals",      "qb"),           # approvals deploys with qb flow
    ("collections",    "collections"),
]

#: Manufacturing standalone entry — appended only when manufacturing_mode=True.
_MANUFACTURING_STANDALONE: Tuple[str, str] = ("manufacturing", "badger")


def get_ux_feature_flags(project_config) -> Dict[str, bool]:
    """Read UX-relevant feature flags from project_config.project__custom__*."""
    custom = getattr(project_config, "project__custom", {}) or {}
    flags: Dict[str, bool] = {}
    for flag in UX_KNOWN_FLAGS:
        val = custom.get(flag, False)
        flags[flag] = process_bool_arg(val) if isinstance(val, (str, bool)) else bool(val)
    return flags


def resolve_flexipage_sources(
    base_dir: Path,
    standalone_dir: Path,
    features: Dict[str, bool],
    manufacturing_mode: bool = False,
) -> Dict[str, Path]:
    """
    Build a filename → source-path map for all active flexipages.

    Seeds from ``base_dir/``, then overlays each active standalone feature
    directory in deploy order (last writer wins, matching prepare_rlm_org).

    Manufacturing standalone content is only included when ``manufacturing_mode=True``.
    This flag is set exclusively by ``prepare_mfg_ux``, which runs inside
    ``prepare_badger_flow`` after all manufacturing metadata has been deployed.
    It must NOT be set when running ``prepare_ux`` (step 29 of ``prepare_rlm_org``),
    because the SalesAgreement object, Order.SalesAgreementId field, and related
    manufacturing resources do not exist yet at that point.
    """
    sources: Dict[str, Path] = {}

    for f in sorted(base_dir.glob("*.flexipage-meta.xml")):
        sources[f.name] = f

    order = list(_STANDALONE_ORDER)
    if manufacturing_mode:
        order.append(_MANUFACTURING_STANDALONE)

    for feature_dir, flag_key in order:
        if not features.get(flag_key, False):
            continue
        src_dir = standalone_dir / feature_dir
        if not src_dir.exists():
            continue
        for src_file in sorted(src_dir.glob("*.flexipage-meta.xml")):
            sources[src_file.name] = src_file

    return sources
