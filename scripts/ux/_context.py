"""Shared run context and error type for the UX tooling.

``UxContext`` carries everything the assembler, retriever, diff and writeback
need from their caller. The CLI (``ux_tool.py``) builds it from
``cumulusci.yml`` plus ``--flag`` overrides; the CCI wrapper
(``tasks/rlm_ux_assembly.py``) builds it from ``project_config``. Nothing in
this package imports CumulusCI.
"""
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

DEFAULT_API_VERSION = "68.0"


class UxError(RuntimeError):
    """A UX assemble/retrieve/diff/writeback/deploy step failed."""


class UxOptionError(UxError):
    """An invalid option (metadata type, metadata name, flag) was given."""


@dataclass
class UxContext:
    repo_root: Path
    features: Dict[str, bool]
    api_version: str = DEFAULT_API_VERSION
    logger: logging.Logger = field(default_factory=lambda: logging.getLogger("rlm_ux"))

    def __post_init__(self) -> None:
        self.repo_root = Path(self.repo_root)

    @property
    def templates_path(self) -> Path:
        return self.repo_root / "templates"

    def resolve(self, path) -> Path:
        """Resolve a repo-relative path (absolute paths pass through)."""
        return self.repo_root / path
