"""State models for the build manager TUI."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Dict, Optional


class RunEventKind(StrEnum):
    """Canonical event kinds exchanged between runner and UI."""

    RUN_STARTED = "run_started"
    RUN_SUCCEEDED = "run_succeeded"
    RUN_FAILED = "run_failed"
    RUN_CANCELLED = "run_cancelled"
    COMMAND_STARTED = "command_started"
    COMMAND_OUTPUT = "command_output"
    COMMAND_FINISHED = "command_finished"
    STEP_STARTED = "step_started"
    STEP_SKIPPED = "step_skipped"
    STEP_SUCCEEDED = "step_succeeded"
    STEP_FAILED = "step_failed"


@dataclass
class OrgShape:
    """Scratch org shape metadata loaded from cumulusci.yml."""

    name: str
    config_file: str
    days: int = 1


@dataclass
class BuildConfig:
    """Runtime build configuration gathered from UI inputs."""

    org_shape: str
    org_alias: str
    days: int
    flag_overrides: Dict[str, bool] = field(default_factory=dict)


@dataclass
class PrepareStepView:
    """UI model for each top-level prepare_rlm_org step."""

    step_number: int
    target_type: str
    target_name: str
    when: Optional[str]
    status: str = "pending"
    duration_seconds: float = 0.0
    exit_code: int = 0
    detail: str = ""


@dataclass
class RunEvent:
    """Structured event emitted by the background runner."""

    kind: RunEventKind
    payload: Dict[str, Any] = field(default_factory=dict)
