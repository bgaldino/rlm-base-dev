"""Textual application for the CCI build manager."""

from __future__ import annotations

import json
import queue
import re
import secrets
import subprocess
import threading
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from textual import events
from textual.app import App, ComposeResult, SystemCommand
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, RichLog, Static

from scripts.build_harness.tui.runner import ROOT as REPO_ROOT
from scripts.build_harness.tui.runner import load_tui_config, run_build
from scripts.build_harness.tui.state import BuildConfig, OrgShape, PrepareStepView, RunEvent, RunEventKind
from scripts.build_harness.tui.widgets.progress_format import format_step_label

SETTINGS_FILE = Path(__file__).with_name("settings.json")
COMPACT_LAYOUT_WIDTH = 120
TUI_RUNS_ROOT = REPO_ROOT / ".harness" / "tui-runs"


def _validate_alias_and_days(alias: str, days_raw: str) -> Optional[str]:
    if not alias:
        return "Org alias is required."
    if len(alias) > 60:
        return "Org alias must be 60 chars or fewer."
    try:
        days = int(days_raw)
    except ValueError:
        return "Days must be an integer."
    if days < 1 or days > 30:
        return "Days must be between 1 and 30."
    return None


def _generate_default_alias(shape_name: str) -> str:
    """Generate a valid, low-collision scratch alias."""
    normalized_shape = re.sub(r"[^a-z0-9-]", "-", shape_name.lower()).strip("-")
    normalized_shape = re.sub(r"-{2,}", "-", normalized_shape) or "org"
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"

    for _ in range(12):
        suffix = "".join(secrets.choice(alphabet) for _ in range(4))
        alias = f"{normalized_shape}-{suffix}"[:60]
        if not _alias_exists(alias):
            return alias

    # Fallback if many collisions are encountered.
    timestamp = time.strftime("%H%M%S")
    return f"{normalized_shape}-{timestamp}"[:60]


def _alias_exists(alias: str) -> bool:
    """Check if CCI already has this org alias registered."""
    try:
        result = subprocess.run(
            ["cci", "org", "info", alias],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        # If we cannot validate, avoid blocking alias generation.
        return False
    return result.returncode == 0


def _load_tui_settings() -> Dict[str, object]:
    """Load optional TUI settings from local settings.json."""
    if not SETTINGS_FILE.exists():
        return {}
    try:
        payload = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _save_tui_settings(settings: Dict[str, object]) -> Optional[str]:
    """Persist local TUI settings and return an error message on failure."""
    try:
        SETTINGS_FILE.write_text(f"{json.dumps(settings, indent=2)}\n", encoding="utf-8")
    except OSError as exc:
        return str(exc)
    return None


def _parse_theme_mode(settings: Dict[str, object]) -> str:
    raw = str(settings.get("theme_mode", "auto")).strip().lower()
    return raw if raw in {"auto", "light", "dark"} else "auto"


def _parse_persistent_logging(settings: Dict[str, object]) -> bool:
    raw = settings.get("persistent_logging", True)
    if isinstance(raw, bool):
        return raw
    normalized = str(raw).strip().lower()
    if normalized in {"0", "false", "no", "off"}:
        return False
    if normalized in {"1", "true", "yes", "on"}:
        return True
    return True


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_git_sha() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


class PersistentRunLogger:
    """Write TUI run artifacts to disk for later comparison/debugging."""

    def __init__(self, config: BuildConfig, settings_snapshot: Dict[str, object]) -> None:
        self._lock = threading.Lock()
        self._closed = False
        self._config = config
        self._started_at = _utc_now_iso()
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.run_id = f"tui-{stamp}-{config.org_alias}"
        self.run_dir = TUI_RUNS_ROOT / self.run_id
        self.run_dir.mkdir(parents=True, exist_ok=True)

        self.events_path = self.run_dir / "events.jsonl"
        self.output_path = self.run_dir / "command-output.log"
        self.summary_path = self.run_dir / "run_summary.json"
        self.manifest_path = self.run_dir / "run_manifest.json"

        manifest = {
            "run_id": self.run_id,
            "source": "tui",
            "started_at": self._started_at,
            "repo_root": str(REPO_ROOT),
            "git_sha": _safe_git_sha(),
            "config": {
                "org_shape": config.org_shape,
                "org_alias": config.org_alias,
                "days": config.days,
                "flag_overrides": dict(config.flag_overrides),
            },
            "settings": dict(settings_snapshot),
        }
        self.manifest_path.write_text(f"{json.dumps(manifest, indent=2)}\n", encoding="utf-8")

    def record_event(self, event: RunEvent) -> None:
        payload: Dict[str, Any] = {
            "timestamp": _utc_now_iso(),
            "kind": event.kind.value,
            "payload": event.payload,
        }
        with self._lock:
            if self._closed:
                return
            with self.events_path.open("a", encoding="utf-8") as handle:
                handle.write(f"{json.dumps(payload, sort_keys=True)}\n")
            if event.kind == RunEventKind.COMMAND_OUTPUT:
                line = str(event.payload.get("line", ""))
                if line:
                    with self.output_path.open("a", encoding="utf-8") as handle:
                        handle.write(f"{line}\n")

    def finalize(
        self,
        *,
        status: str,
        total_steps: int,
        completed_steps: int,
        elapsed_seconds: float,
        terminal_payload: Dict[str, object],
    ) -> None:
        with self._lock:
            if self._closed:
                return
            summary = {
                "run_id": self.run_id,
                "status": status,
                "started_at": self._started_at,
                "finished_at": _utc_now_iso(),
                "config": {
                    "org_shape": self._config.org_shape,
                    "org_alias": self._config.org_alias,
                    "days": self._config.days,
                    "flag_overrides": dict(self._config.flag_overrides),
                },
                "progress": {
                    "completed_steps": completed_steps,
                    "total_steps": total_steps,
                    "elapsed_seconds": round(elapsed_seconds, 3),
                },
                "terminal_event_payload": terminal_payload,
                "artifacts": {
                    "events": self.events_path.name,
                    "command_output": self.output_path.name,
                    "manifest": self.manifest_path.name,
                },
            }
            self.summary_path.write_text(f"{json.dumps(summary, indent=2)}\n", encoding="utf-8")
            self._closed = True


class OrgSelectionScreen(Screen[None]):
    """Wizard step 1: choose org shape."""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="wizard-panel"):
            yield Static("Step 1 of 4: Select Scratch Org Shape", classes="section-title")
            yield DataTable(id="shape-table")
            with Horizontal(id="wizard-actions"):
                yield Button("Next", id="next-button", variant="success")
                yield Static("", id="layout-indicator")
                yield Static("", id="actions-spacer")
                yield Button("Exit", id="exit-button", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#shape-table", DataTable)
        table.cursor_type = "row"
        table.add_columns("shape", "config_file", "default_days")
        default_row = 0
        for idx, shape in enumerate(self.app.org_shapes):
            if shape.name == self.app.default_org_shape:
                default_row = idx
            table.add_row(shape.name, shape.config_file, str(shape.days), key=shape.name)
        table.move_cursor(row=default_row, column=0)
        self._apply_responsive_layout()

    def on_resize(self, _: events.Resize) -> None:
        self._apply_responsive_layout()

    def _apply_responsive_layout(self) -> None:
        table = self.query_one("#shape-table", DataTable)
        actions = self.query_one("#wizard-actions", Horizontal)
        indicator = self.query_one("#layout-indicator", Static)
        compact = self.app.is_compact_layout()
        # Keep at least a few visible rows even in short terminals.
        table.styles.height = max(6, self.app.size.height - 14)
        actions.set_class(compact, "wizard-actions-compact")
        indicator.update("Compact Layout")
        indicator.set_class(compact, "layout-indicator-visible")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit-button":
            self.app.exit()
            return
        if event.button.id != "next-button":
            return
        table = self.query_one("#shape-table", DataTable)
        row_index = table.cursor_row
        if row_index is None:
            self.notify("Select an org shape first.", severity="warning")
            return
        row = table.get_row_at(row_index)
        self.app.selected_shape = str(row[0])
        selected = next((shape for shape in self.app.org_shapes if shape.name == self.app.selected_shape), None)
        if selected:
            self.app.alias = _generate_default_alias(selected.name)
            self.app.days = selected.days
        self.app.push_screen(AliasDaysScreen())


class AliasDaysScreen(Screen[None]):
    """Wizard step 2: set alias and days."""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="wizard-panel"):
            yield Static("Step 2 of 4: Alias and Scratch Duration", classes="section-title")
            yield Label("Org alias")
            yield Input(id="alias-input", placeholder="e.g. dev-myfeature")
            yield Label("Scratch org days")
            yield Input(id="days-input")
            yield Static("", id="alias-days-error")
            with Horizontal(id="wizard-actions"):
                yield Button("Back", id="back-button")
                yield Button("Next", id="next-button", variant="success")
                yield Static("", id="layout-indicator")
                yield Static("", id="actions-spacer")
                yield Button("Exit", id="exit-button", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#alias-input", Input).value = self.app.alias
        self.query_one("#days-input", Input).value = str(self.app.days)
        self._apply_responsive_layout()

    def on_resize(self, _: events.Resize) -> None:
        self._apply_responsive_layout()

    def _apply_responsive_layout(self) -> None:
        actions = self.query_one("#wizard-actions", Horizontal)
        indicator = self.query_one("#layout-indicator", Static)
        compact = self.app.is_compact_layout()
        actions.set_class(compact, "wizard-actions-compact")
        indicator.update("Compact Layout")
        indicator.set_class(compact, "layout-indicator-visible")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit-button":
            self.app.exit()
            return
        if event.button.id == "back-button":
            self.app.pop_screen()
            return
        if event.button.id != "next-button":
            return

        alias = self.query_one("#alias-input", Input).value.strip()
        days_raw = self.query_one("#days-input", Input).value.strip()
        error = _validate_alias_and_days(alias, days_raw)
        if error:
            self.query_one("#alias-days-error", Static).update(error)
            return

        self.app.alias = alias
        self.app.days = int(days_raw)
        self.app.push_screen(FlagOverridesScreen())


class FlagOverridesScreen(Screen[None]):
    """Wizard step 3: choose runtime flag overrides and start run."""

    def __init__(self) -> None:
        super().__init__()
        self.flag_values: Dict[str, bool] = {}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="wizard-panel"):
            yield Static("Step 3 of 4: Runtime Flag Overrides", classes="section-title")
            with VerticalScroll(id="flag-scroll"):
                yield Static("Toggle switches to set runtime-only overrides.", id="flags-help")
                for group_name, flags in self.app.flag_groups:
                    yield Static(group_name, classes="section-title")
                    for name in flags:
                        default = self.app.bool_flags[name]
                        override = self.app.flag_overrides.get(name, default)
                        with Horizontal(classes="flag-row"):
                            yield Button(
                                "ON ●" if override else "○ OFF",
                                id=f"flag-toggle-{name}",
                                classes="flag-toggle flag-toggle-on" if override else "flag-toggle flag-toggle-off",
                            )
                            yield Label(name, classes="flag-name")
                            comment = self.app.flag_comments.get(name, "")
                            if comment:
                                yield Static(f" - {comment}", classes="flag-inline-comment")
            with Horizontal(id="wizard-actions"):
                yield Button("Back", id="back-button")
                yield Button("Start Build", id="start-button", variant="success")
                yield Static("", id="layout-indicator")
                yield Static("", id="actions-spacer")
                yield Button("Exit", id="exit-button", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        self.flag_values = {
            name: self.app.flag_overrides.get(name, default) for name, default in self.app.bool_flags.items()
        }
        self._apply_responsive_layout()

    def on_resize(self, _: events.Resize) -> None:
        self._apply_responsive_layout()

    def _apply_responsive_layout(self) -> None:
        actions = self.query_one("#wizard-actions", Horizontal)
        indicator = self.query_one("#layout-indicator", Static)
        compact = self.app.is_compact_layout()
        actions.set_class(compact, "wizard-actions-compact")
        indicator.update("Compact Layout")
        indicator.set_class(compact, "layout-indicator-visible")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id or ""
        if button_id.startswith("flag-toggle-"):
            flag_name = button_id.replace("flag-toggle-", "", 1)
            current = self.flag_values.get(flag_name, False)
            updated = not current
            self.flag_values[flag_name] = updated
            event.button.label = "ON ●" if updated else "○ OFF"
            event.button.set_class(updated, "flag-toggle-on")
            event.button.set_class(not updated, "flag-toggle-off")
            return

        if event.button.id == "exit-button":
            self.app.exit()
            return
        if event.button.id == "back-button":
            self.app.pop_screen()
            return
        if event.button.id != "start-button":
            return

        overrides: Dict[str, bool] = {}
        for flag_name, current_value in self.flag_values.items():
            default = self.app.bool_flags.get(flag_name)
            if default is not None and current_value != default:
                overrides[flag_name] = bool(current_value)
        self.app.flag_overrides = overrides
        self.app.start_build_and_show_output()


class OutputScreen(Screen[None]):
    """Wizard step 4: execution output with live progress."""

    def __init__(self, *, config: BuildConfig) -> None:
        super().__init__()
        self.config = config
        self.step_views: Dict[int, PrepareStepView] = {}
        self._step_column_keys: tuple[object, ...] = ()
        self._running_step_started_at: Dict[int, float] = {}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="output-panel"):
            yield Static("Step 4 of 4: Build Output", classes="section-title")
            yield Static("Starting...", id="run-status")
            yield Static("", id="run-banner")
            yield Static("Total Elapsed: 0.0s", id="elapsed")
            yield Static("Current: startup", id="current-step")
            yield DataTable(id="step-table")
            yield RichLog(id="log", wrap=True, highlight=True, markup=False)
            with Horizontal(id="wizard-actions"):
                yield Button("Stop Build", id="stop-button", variant="warning")
                yield Static("", id="layout-indicator")
                yield Static("", id="actions-spacer")
                yield Button("Exit", id="exit-button", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#step-table", DataTable)
        table.cursor_type = "row"
        self._step_column_keys = table.add_columns("step", "target", "status", "duration", "detail")
        self.set_interval(0.2, self._refresh_elapsed)
        self._apply_responsive_layout()
        self._set_stop_button_mode(is_running=True)

    def on_resize(self, _: events.Resize) -> None:
        self._apply_responsive_layout()

    def _apply_responsive_layout(self) -> None:
        table = self.query_one("#step-table", DataTable)
        log = self.query_one("#log", RichLog)
        banner = self.query_one("#run-banner", Static)
        actions = self.query_one("#wizard-actions", Horizontal)
        indicator = self.query_one("#layout-indicator", Static)
        compact = self.app.is_compact_layout()
        banner_height = 3 if banner.has_class("banner-visible") else 0
        available = max(8, self.app.size.height - 16 - banner_height)
        table_height = min(12, max(3, available // 3))
        log_height = available - table_height
        if log_height < 3:
            deficit = 3 - log_height
            table_height = max(3, table_height - deficit)
            log_height = available - table_height
        table.styles.height = table_height
        log.styles.height = log_height
        actions.set_class(compact, "wizard-actions-compact")
        indicator.update("Compact Layout")
        indicator.set_class(compact, "layout-indicator-visible")

    def _refresh_elapsed(self) -> None:
        sampled_now = time.monotonic()
        elapsed = self.app.elapsed_seconds(sampled_now=sampled_now)
        self.query_one("#elapsed", Static).update(f"Total Elapsed: {self._format_duration(elapsed)}")
        self._refresh_running_step_durations(sampled_now=sampled_now)

    @staticmethod
    def _format_duration(seconds_total: float) -> str:
        if seconds_total < 60:
            return f"{seconds_total:.1f}s"
        minutes = int(seconds_total // 60)
        seconds = int(seconds_total % 60)
        return f"{minutes}m {seconds:02d}s"

    def _refresh_running_step_durations(self, *, sampled_now: float) -> None:
        if not self._running_step_started_at or len(self._step_column_keys) < 4:
            return
        table = self.query_one("#step-table", DataTable)
        duration_key = self._step_column_keys[3]
        for step_number, started_at in list(self._running_step_started_at.items()):
            view = self.step_views.get(step_number)
            if view is None or view.status != "running":
                self._running_step_started_at.pop(step_number, None)
                continue
            elapsed = max(0.0, sampled_now - started_at)
            view.duration_seconds = elapsed
            try:
                table.update_cell(f"step-{step_number}", duration_key, self._format_duration(elapsed))
            except Exception:
                continue

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit-button":
            if self.app.is_run_active():
                self.app.push_screen(ExitConfirmScreen())
            else:
                self.app.exit()
            return
        if event.button.id == "stop-button":
            if self.app.is_run_active():
                self.app.request_stop()
                return
            self.app.start_new_build_flow()
            return

    def handle_event(self, event: RunEvent) -> None:
        log = self.query_one("#log", RichLog)
        status = self.query_one("#run-status", Static)
        current = self.query_one("#current-step", Static)
        table = self.query_one("#step-table", DataTable)
        payload = event.payload

        if event.kind == RunEventKind.RUN_STARTED:
            status.update(f"Running (0/{int(payload.get('total_steps', 0))})")
            self._set_stop_button_mode(is_running=True)
            log.write(
                f"Build started: shape={self.config.org_shape} alias={self.config.org_alias} days={self.config.days}"
            )
            return

        if event.kind == RunEventKind.COMMAND_STARTED:
            current.update(f"Current: {payload.get('step_label', 'command')}")
            log.write(f"$ {payload.get('command', '')}")
            return

        if event.kind == RunEventKind.COMMAND_OUTPUT:
            line = payload.get("line", "")
            if line:
                log.write(str(line))
            return

        if event.kind in {
            RunEventKind.STEP_STARTED,
            RunEventKind.STEP_SKIPPED,
            RunEventKind.STEP_SUCCEEDED,
            RunEventKind.STEP_FAILED,
        }:
            self._handle_step_event(event.kind, payload, table, current, status)
            return

        if event.kind == RunEventKind.RUN_SUCCEEDED:
            status.update(self.app.status_label_success())
            log.write(str(payload.get("message", "Build completed.")))
            self._show_run_banner("BUILD SUCCEEDED", "banner-success")
            self._set_stop_button_mode(is_running=False)
            return

        if event.kind == RunEventKind.RUN_FAILED:
            status.update("Failed")
            failure = payload.get("failure_signature", "")
            message = payload.get("message", "Run failed.")
            log.write(f"{message} :: {failure}" if failure else str(message))
            traceback_text = str(payload.get("traceback", "")).strip()
            if traceback_text:
                for line in traceback_text.splitlines():
                    log.write(line)
            self._show_run_banner("BUILD FAILED", "banner-failed")
            self._set_stop_button_mode(is_running=False)
            return

        if event.kind == RunEventKind.RUN_CANCELLED:
            status.update("Cancelled")
            log.write(str(payload.get("message", "Run cancelled.")))
            self._show_run_banner("BUILD CANCELLED", "banner-cancelled")
            self._set_stop_button_mode(is_running=False)
            return

    def _handle_step_event(
        self,
        kind: RunEventKind,
        payload: Dict[str, object],
        table: DataTable,
        current: Static,
        status: Static,
    ) -> None:
        if kind == RunEventKind.STEP_STARTED:
            step_number = int(payload["step_number"])
            self._running_step_started_at[step_number] = time.monotonic()
            self._upsert_step(
                table,
                PrepareStepView(
                    step_number=step_number,
                    target_type=str(payload["target_type"]),
                    target_name=str(payload["target_name"]),
                    when=payload.get("when"),
                    status="running",
                ),
            )
            current.update(
                f"Current: {format_step_label(int(payload['step_number']), str(payload['target_type']), str(payload['target_name']))}"
            )
            status.update(self.app.status_label_running())
            return

        step_number = int(payload["step_number"])
        if kind == RunEventKind.STEP_SKIPPED:
            self._upsert_step(
                table,
                PrepareStepView(
                    step_number=step_number,
                    target_type=str(payload["target_type"]),
                    target_name=str(payload["target_name"]),
                    when=payload.get("when"),
                    status="skipped",
                    detail="when=false",
                ),
            )
            self._set_step_status(table, step_number, "skipped", 0.0, "when=false")
            self.app.update_progress(int(payload.get("completed_steps", 0)))
            status.update(self.app.status_label_running())
            return

        if kind == RunEventKind.STEP_SUCCEEDED:
            duration = float(payload.get("duration_seconds", 0.0))
            self._set_step_status(table, step_number, "success", duration, "")
            self.app.update_progress(int(payload.get("completed_steps", 0)))
            status.update(self.app.status_label_running())
            return

        if kind == RunEventKind.STEP_FAILED:
            duration = float(payload.get("duration_seconds", 0.0))
            detail = str(payload.get("failure_signature", "failed"))
            self._set_step_status(table, step_number, "failed", duration, detail)

    def _upsert_step(self, table: DataTable, view: PrepareStepView) -> None:
        if view.step_number in self.step_views:
            self._set_step_status(table, view.step_number, view.status, view.duration_seconds, view.detail)
            return
        self.step_views[view.step_number] = view
        table.add_row(
            str(view.step_number),
            f"{view.target_type}:{view.target_name}",
            view.status,
            f"{view.duration_seconds:.1f}s",
            view.detail,
            key=f"step-{view.step_number}",
        )
        self._scroll_step_table_to_bottom(table)

    def _scroll_step_table_to_bottom(self, table: DataTable) -> None:
        if table.row_count <= 0:
            return
        try:
            table.move_cursor(row=table.row_count - 1, column=0)
        except Exception:
            return

    def _show_run_banner(self, text: str, style_class: str) -> None:
        banner = self.query_one("#run-banner", Static)
        banner.update(text)
        banner.set_class(True, "banner-visible")
        banner.set_class(style_class == "banner-success", "banner-success")
        banner.set_class(style_class == "banner-failed", "banner-failed")
        banner.set_class(style_class == "banner-cancelled", "banner-cancelled")
        self._apply_responsive_layout()

    def _set_stop_button_mode(self, *, is_running: bool) -> None:
        button = self.query_one("#stop-button", Button)
        if is_running:
            button.label = "Stop Build"
            button.disabled = False
            button.set_class(False, "new-build-button")
            return
        button.label = "New Build"
        button.disabled = False
        button.set_class(True, "new-build-button")

    def _set_step_status(
        self,
        table: DataTable,
        step_number: int,
        status: str,
        duration_seconds: float,
        detail: str,
    ) -> None:
        view = self.step_views.get(step_number)
        if view is None:
            return
        key = f"step-{step_number}"
        view.status = status
        view.duration_seconds = duration_seconds
        view.detail = detail
        if status != "running":
            self._running_step_started_at.pop(step_number, None)
        if len(self._step_column_keys) < 5:
            return
        status_key = self._step_column_keys[2]
        duration_key = self._step_column_keys[3]
        detail_key = self._step_column_keys[4]
        try:
            table.update_cell(key, status_key, status)
            table.update_cell(key, duration_key, f"{duration_seconds:.1f}s")
            table.update_cell(key, detail_key, detail)
        except Exception:
            # Keep run alive even if table state drifts during long-running updates.
            return


class ExitConfirmScreen(Screen[None]):
    """Prompt for optional scratch delete when exiting an active run."""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="wizard-panel"):
            yield Static("Build In Progress", classes="section-title")
            yield Static(
                "A build is still running. Exit now and optionally delete the scratch org?",
                id="exit-confirm-message",
            )
            with Horizontal(id="wizard-actions"):
                yield Button("Back", id="back-button")
                yield Static("", id="layout-indicator")
                yield Static("", id="actions-spacer")
                yield Button("Keep Org and Exit", id="keep-exit-button", variant="warning")
                yield Button("Delete Org and Exit", id="delete-exit-button", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        self._apply_responsive_layout()

    def on_resize(self, _: events.Resize) -> None:
        self._apply_responsive_layout()

    def _apply_responsive_layout(self) -> None:
        actions = self.query_one("#wizard-actions", Horizontal)
        indicator = self.query_one("#layout-indicator", Static)
        compact = self.app.is_compact_layout()
        actions.set_class(compact, "wizard-actions-compact")
        indicator.update("Compact Layout")
        indicator.set_class(compact, "layout-indicator-visible")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back-button":
            self.app.pop_screen()
            return
        if event.button.id == "keep-exit-button":
            self.app.stop_and_exit(delete_org=False)
            return
        if event.button.id == "delete-exit-button":
            self.app.stop_and_exit(delete_org=True)
            return


class BuildManagerApp(App[None]):
    """Interactive terminal application to create and build scratch orgs."""

    TITLE = "CCI Build Manager"
    SUB_TITLE = "Scratch Org + prepare_rlm_org"
    BINDINGS = [
        ("ctrl+x", "safe_exit", "Quit"),
        ("escape", "safe_exit", "Quit"),
    ]
    CSS = """
    .theme-light Screen {
        layout: vertical;
        background: #e5eff8;
        color: #001639;
    }
    .theme-light #wizard-panel, .theme-light #output-panel {
        height: 1fr;
        border: heavy #0176d3;
        background: #f8fbff;
        color: #001639;
        padding: 1;
    }
    #shape-table {
        height: 1fr;
        min-height: 6;
        margin: 1 0;
    }
    .theme-light #flag-scroll {
        height: 1fr;
        border: round #8fa8c2;
        background: #f4f8fc;
        color: #001639;
        padding: 0 1;
        margin: 1 0;
    }
    #step-table {
        height: 1fr;
        min-height: 4;
        margin: 1 0;
    }
    .theme-light #log {
        height: 1fr;
        border: round #8fa8c2;
        background: #eef4fb;
        color: #001639;
        margin-top: 1;
    }
    #run-banner {
        display: none;
        height: 3;
        content-align: center middle;
        text-style: bold;
        margin: 1 0;
    }
    #run-banner.banner-visible {
        display: block;
    }
    .theme-light #run-banner.banner-success {
        background: #2e844a;
        color: #ffffff;
        border: round #2e844a;
    }
    .theme-light #run-banner.banner-failed {
        background: #ba0517;
        color: #ffffff;
        border: round #ba0517;
    }
    .theme-light #run-banner.banner-cancelled {
        background: #dd7a01;
        color: #ffffff;
        border: round #dd7a01;
    }
    #wizard-actions {
        height: auto;
        margin-top: 1;
    }
    #layout-indicator {
        color: #015ba7;
        text-style: bold;
        display: none;
    }
    #layout-indicator.layout-indicator-visible {
        display: block;
        width: 16;
    }
    #wizard-actions.wizard-actions-compact {
        layout: vertical;
    }
    #wizard-actions.wizard-actions-compact Button {
        width: 1fr;
        margin-bottom: 1;
    }
    #wizard-actions.wizard-actions-compact #actions-spacer {
        display: none;
    }
    #actions-spacer {
        width: 1fr;
    }
    .theme-light Button {
        background: #f4f8fc;
        color: #001639;
        border: round #0176d3;
    }
    .theme-light Button:hover {
        background: #d8ecff;
    }
    .theme-light Button.-success {
        background: #0176d3;
        color: #ffffff;
        border: round #0176d3;
    }
    .theme-light Button.-warning {
        background: #dd7a01;
        color: #ffffff;
        border: round #dd7a01;
    }
    .theme-light Button.new-build-button {
        background: #0176d3;
        color: #ffffff;
        border: round #0176d3;
    }
    .theme-light Button.-error {
        background: #ba0517;
        color: #ffffff;
        border: round #ba0517;
    }
    .theme-light DataTable {
        background: #f8fbff;
        color: #001639;
    }
    .theme-light DataTable > .datatable--header {
        background: #cfe9ff;
        color: #001639;
        text-style: bold;
    }
    .theme-light Input {
        background: #ffffff;
        color: #001639;
        border: round #8fa8c2;
    }
    .theme-light Label {
        color: #001639;
    }
    .flag-row {
        height: auto;
        margin-bottom: 1;
        align: left middle;
    }
    .flag-toggle {
        width: 10;
        min-width: 10;
        margin-right: 1;
        border: round #8fa8c2;
        text-style: bold;
        content-align: center middle;
    }
    .flag-name {
        width: 18;
        min-width: 18;
    }
    .flag-inline-comment {
        color: #16325c;
    }
    .theme-light .flag-inline-comment {
        color: #16325c;
    }
    .theme-light .flag-toggle {
        background: #ffffff;
        color: #0176d3;
        border: round #8fa8c2;
    }
    .theme-light .flag-toggle:hover {
        background: #d8ecff;
    }
    .theme-light .flag-toggle:focus {
        border: round #0176d3;
    }
    .theme-light .flag-toggle.flag-toggle-on {
        background: #0176d3;
        color: #ffffff;
        border: round #0176d3;
    }
    .theme-light .flag-toggle.flag-toggle-off {
        background: #ffffff;
        color: #0176d3;
    }
    .theme-light .section-title {
        text-style: bold;
        margin: 0 0 1 0;
        color: #001639;
    }
    .theme-dark Screen {
        layout: vertical;
        background: #0b1626;
        color: #d8e6ff;
    }
    .theme-dark #wizard-panel, .theme-dark #output-panel {
        height: 1fr;
        border: heavy #1b96ff;
        background: #10233d;
        color: #eaf2ff;
        padding: 1;
    }
    .theme-dark #flag-scroll {
        height: 1fr;
        border: round #3b5a80;
        background: #142b47;
        color: #d8e6ff;
        padding: 0 1;
        margin: 1 0;
    }
    .theme-dark #log {
        height: 1fr;
        border: round #3b5a80;
        background: #0f2137;
        color: #eaf2ff;
        margin-top: 1;
    }
    .theme-dark #run-banner.banner-success {
        background: #2e844a;
        color: #ffffff;
        border: round #2e844a;
    }
    .theme-dark #run-banner.banner-failed {
        background: #ba0517;
        color: #ffffff;
        border: round #ba0517;
    }
    .theme-dark #run-banner.banner-cancelled {
        background: #dd7a01;
        color: #ffffff;
        border: round #dd7a01;
    }
    .theme-dark #layout-indicator {
        color: #7dc2ff;
    }
    .theme-dark Button {
        background: #18324f;
        color: #eaf2ff;
        border: round #4ba6ff;
    }
    .theme-dark Button:hover {
        background: #23476e;
    }
    .theme-dark Button.-success {
        background: #1b96ff;
        color: #001639;
        border: round #1b96ff;
    }
    .theme-dark Button.-warning {
        background: #f3b47a;
        color: #291500;
        border: round #f3b47a;
    }
    .theme-dark Button.new-build-button {
        background: #1b96ff;
        color: #001639;
        border: round #1b96ff;
    }
    .theme-dark Button.-error {
        background: #ff6f7f;
        color: #2b0a0d;
        border: round #ff6f7f;
    }
    .theme-dark DataTable {
        background: #10233d;
        color: #eaf2ff;
    }
    .theme-dark DataTable > .datatable--header {
        background: #1f456c;
        color: #f3f8ff;
        text-style: bold;
    }
    .theme-dark Input {
        background: #0f2137;
        color: #eaf2ff;
        border: round #4a6f98;
    }
    .theme-dark Label {
        color: #d8e6ff;
    }
    .theme-dark .flag-comment {
        color: #adc9ef;
    }
    .theme-dark .flag-inline-comment {
        color: #adc9ef;
    }
    .theme-dark .flag-toggle {
        background: #18324f;
        color: #7dc2ff;
        border: round #4a6f98;
    }
    .theme-dark .flag-toggle:hover {
        background: #23476e;
    }
    .theme-dark .flag-toggle:focus {
        border: round #1b96ff;
    }
    .theme-dark .flag-toggle.flag-toggle-on {
        background: #1b96ff;
        color: #001639;
        border: round #1b96ff;
    }
    .theme-dark .flag-toggle.flag-toggle-off {
        background: #18324f;
        color: #7dc2ff;
    }
    .theme-dark .section-title {
        text-style: bold;
        margin: 0 0 1 0;
        color: #f3f8ff;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.org_shapes: List[OrgShape] = []
        self.bool_flags: Dict[str, bool] = {}
        self.flag_groups: List[tuple[str, List[str]]] = []
        self.flag_comments: Dict[str, str] = {}
        self.settings: Dict[str, object] = {}
        self.persistent_logging_enabled: bool = True
        self.theme_mode: str = "auto"
        self.default_org_shape: str = ""
        self.selected_shape: str = ""
        self.alias: str = ""
        self.days: int = 1
        self.flag_overrides: Dict[str, bool] = {}

        self._event_queue: "queue.Queue[RunEvent]" = queue.Queue()
        self._stop_event = threading.Event()
        self._runner_thread: Optional[threading.Thread] = None
        self._run_started_monotonic: Optional[float] = None
        self._run_finished_monotonic: Optional[float] = None
        self._completed_steps = 0
        self._total_steps = 0
        self._running_step_numbers: set[int] = set()
        self._output_screen: Optional[OutputScreen] = None
        self._run_logger: Optional[PersistentRunLogger] = None
        self._active_org_alias: str = ""
        self._org_created_in_run = False
        self._unexpected_runner_exit_reported = False

    def on_mount(self) -> None:
        self.settings = _load_tui_settings()
        default_shape_raw = str(self.settings.get("default_org_shape", "")).strip()
        self.theme_mode = _parse_theme_mode(self.settings)
        self.persistent_logging_enabled = _parse_persistent_logging(self.settings)
        self._apply_theme_mode()

        shapes, bool_flags, _, flag_groups, flag_comments = load_tui_config()
        self.org_shapes = shapes
        self.bool_flags = bool_flags
        self.flag_groups = flag_groups
        self.flag_comments = flag_comments
        known_shapes = {shape.name for shape in shapes}
        self.default_org_shape = default_shape_raw if default_shape_raw in known_shapes else ""
        self.set_interval(0.2, self._drain_events)
        self.push_screen(OrgSelectionScreen())

    def _apply_theme_mode(self) -> None:
        self.set_class(False, "theme-light")
        self.set_class(False, "theme-dark")
        if self.theme_mode == "light":
            self.set_class(True, "theme-light")
            return
        if self.theme_mode == "dark":
            self.set_class(True, "theme-dark")
            return
        is_dark_mode = "-dark-mode" in self.classes or "dark" in self.pseudo_classes
        self.set_class(True, "theme-dark" if is_dark_mode else "theme-light")

    def is_compact_layout(self) -> bool:
        return self.size.width < COMPACT_LAYOUT_WIDTH

    def start_build_and_show_output(self) -> None:
        if self._runner_thread and self._runner_thread.is_alive():
            return
        if not self.selected_shape:
            self.notify("No org shape selected.", severity="error")
            return
        error = _validate_alias_and_days(self.alias.strip(), str(self.days))
        if error:
            self.notify(error, severity="error")
            return

        self._run_started_monotonic = None
        self._run_finished_monotonic = None
        self._completed_steps = 0
        self._total_steps = 0
        self._running_step_numbers.clear()
        self._stop_event.clear()
        self._org_created_in_run = False
        self._unexpected_runner_exit_reported = False
        self._run_logger = None

        config = BuildConfig(
            org_shape=self.selected_shape,
            org_alias=self.alias.strip(),
            days=self.days,
            flag_overrides=dict(self.flag_overrides),
        )
        if self.persistent_logging_enabled:
            try:
                self._run_logger = PersistentRunLogger(config=config, settings_snapshot=self.settings)
            except Exception as exc:
                self.notify(f"Failed to initialize persistent run logging: {exc}", severity="warning")
                self._run_logger = None

        output = OutputScreen(config=config)
        self._output_screen = output
        self.push_screen(output)
        self._active_org_alias = config.org_alias

        def _emit(event: RunEvent) -> None:
            if self._run_logger is not None:
                try:
                    self._run_logger.record_event(event)
                except Exception as exc:
                    self._event_queue.put(
                        RunEvent(
                            kind=RunEventKind.COMMAND_OUTPUT,
                            payload={
                                "phase": "logger",
                                "step_number": -1,
                                "line": f"[harness] persistent log write failed: {exc}",
                            },
                        )
                    )
                    self._run_logger = None
            self._event_queue.put(event)

        def _runner() -> None:
            try:
                run_build(config=config, stop_event=self._stop_event, emit=_emit)
            except Exception as exc:
                _emit(
                    RunEvent(
                        kind=RunEventKind.RUN_FAILED,
                        payload={
                            "message": "Build runner crashed with an unexpected exception.",
                            "failure_signature": str(exc),
                            "traceback": traceback.format_exc(),
                        },
                    )
                )

        self._runner_thread = threading.Thread(target=_runner, daemon=True)
        self._runner_thread.start()

    def request_stop(self) -> None:
        self._stop_event.set()

    def is_run_active(self) -> bool:
        return self._runner_thread is not None and self._runner_thread.is_alive()

    def stop_and_exit(self, *, delete_org: bool) -> None:
        self.request_stop()
        if self._runner_thread is not None:
            self._runner_thread.join(timeout=5)
        if delete_org and self._active_org_alias:
            self._delete_scratch_org(self._active_org_alias)
        self.exit()

    def action_safe_exit(self) -> None:
        if self.is_run_active():
            self.push_screen(ExitConfirmScreen())
            return
        self.exit()

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        """Register custom app actions in the command palette."""
        yield from super().get_system_commands(screen)
        yield SystemCommand(
            "Set Default Org",
            "Persist the highlighted/current org shape as default",
            self.action_set_default_org,
        )

    def action_set_default_org(self) -> None:
        org_shape = self._get_current_org_shape_for_default()
        if not org_shape:
            self.notify(
                "No org shape available to set. Go to Step 1 and highlight an org shape.",
                severity="warning",
            )
            return
        self.default_org_shape = org_shape
        self.settings["default_org_shape"] = org_shape
        error = _save_tui_settings(self.settings)
        if error:
            self.notify(f"Failed to save default org shape: {error}", severity="error")
            return
        self.notify(f"Default org shape set to '{org_shape}'.")

    def _get_current_org_shape_for_default(self) -> Optional[str]:
        screen = self.screen
        if isinstance(screen, OrgSelectionScreen):
            table = screen.query_one("#shape-table", DataTable)
            row_index = table.cursor_row
            if row_index is not None:
                row = table.get_row_at(row_index)
                return str(row[0])
        if self.selected_shape:
            return self.selected_shape
        return None

    def elapsed_seconds(self, *, sampled_now: Optional[float] = None) -> float:
        if self._run_started_monotonic is None:
            return 0.0
        if self._run_finished_monotonic is not None:
            return max(0.0, self._run_finished_monotonic - self._run_started_monotonic)
        now = sampled_now if sampled_now is not None else time.monotonic()
        return now - self._run_started_monotonic

    def start_new_build_flow(self) -> None:
        """Return from output screen to step 1 for a fresh run."""
        if self.is_run_active():
            return
        self._output_screen = None
        self._active_org_alias = ""
        self._org_created_in_run = False
        self._run_logger = None
        self._run_started_monotonic = None
        self._run_finished_monotonic = None
        self._completed_steps = 0
        self._total_steps = 0
        self._running_step_numbers.clear()
        self.flag_overrides = {}
        self.selected_shape = ""
        self.alias = ""
        self._unexpected_runner_exit_reported = False

        safety_counter = 0
        while not isinstance(self.screen, OrgSelectionScreen) and safety_counter < 10:
            self.pop_screen()
            safety_counter += 1

        if not isinstance(self.screen, OrgSelectionScreen):
            self.push_screen(OrgSelectionScreen())

    def update_progress(self, completed_steps: int) -> None:
        self._completed_steps = completed_steps

    def status_label_running(self) -> str:
        running_numerator = self._completed_steps + len(self._running_step_numbers)
        if self._total_steps > 0:
            running_numerator = min(running_numerator, self._total_steps)
        return f"Running ({running_numerator}/{self._total_steps})"

    def status_label_success(self) -> str:
        return f"Success ({self._completed_steps}/{self._total_steps})"

    def _drain_events(self) -> None:
        while True:
            try:
                event = self._event_queue.get_nowait()
            except queue.Empty:
                if self._emit_unexpected_runner_exit_event():
                    continue
                return
            if event.kind == RunEventKind.RUN_STARTED:
                self._run_started_monotonic = time.monotonic()
                self._run_finished_monotonic = None
                self._total_steps = int(event.payload.get("total_steps", 0))
                self._completed_steps = 0
                self._running_step_numbers.clear()
            if event.kind == RunEventKind.STEP_STARTED:
                step_number = int(event.payload.get("step_number", -1))
                if step_number > 0:
                    self._running_step_numbers.add(step_number)
            if event.kind in {RunEventKind.STEP_SKIPPED, RunEventKind.STEP_SUCCEEDED, RunEventKind.STEP_FAILED}:
                step_number = int(event.payload.get("step_number", -1))
                if step_number > 0:
                    self._running_step_numbers.discard(step_number)
            if event.kind == RunEventKind.COMMAND_FINISHED:
                phase = str(event.payload.get("phase", ""))
                step_number = int(event.payload.get("step_number", -1))
                exit_code = int(event.payload.get("exit_code", 1))
                if phase == "create_org" and step_number == 0 and exit_code == 0:
                    self._org_created_in_run = True
            if event.kind in {RunEventKind.RUN_SUCCEEDED, RunEventKind.RUN_FAILED, RunEventKind.RUN_CANCELLED}:
                if self._run_finished_monotonic is None:
                    self._run_finished_monotonic = time.monotonic()
                status = {
                    RunEventKind.RUN_SUCCEEDED: "success",
                    RunEventKind.RUN_FAILED: "failed",
                    RunEventKind.RUN_CANCELLED: "cancelled",
                }[event.kind]
                self._finalize_run_logger(status=status, terminal_payload=event.payload)
                if event.kind == RunEventKind.RUN_FAILED and self._org_created_in_run and self._active_org_alias:
                    alias = self._active_org_alias
                    self.notify(f"Build failed. Cleaning up scratch org '{alias}'...", severity="warning")
                    self._delete_scratch_org(alias)
                self._active_org_alias = ""
                self._org_created_in_run = False
            if self._output_screen is not None:
                self._output_screen.handle_event(event)

    def _emit_unexpected_runner_exit_event(self) -> bool:
        if self._unexpected_runner_exit_reported:
            return False
        if self._runner_thread is None or self._runner_thread.is_alive():
            return False
        if self._run_started_monotonic is None or self._run_finished_monotonic is not None:
            return False

        self._unexpected_runner_exit_reported = True
        self._event_queue.put(
            RunEvent(
                kind=RunEventKind.RUN_FAILED,
                payload={
                    "message": "Build runner stopped unexpectedly before completion.",
                    "failure_signature": "runner_thread_exited_without_terminal_event",
                },
            )
        )
        return True

    def _finalize_run_logger(self, *, status: str, terminal_payload: Dict[str, object]) -> None:
        if self._run_logger is None:
            return
        elapsed = self.elapsed_seconds()
        try:
            self._run_logger.finalize(
                status=status,
                total_steps=self._total_steps,
                completed_steps=self._completed_steps,
                elapsed_seconds=elapsed,
                terminal_payload=terminal_payload,
            )
        except Exception as exc:
            self.notify(f"Failed to finalize persistent run log: {exc}", severity="warning")
        finally:
            self._run_logger = None

    def _delete_scratch_org(self, alias: str) -> None:
        try:
            result = subprocess.run(
                ["cci", "org", "scratch_delete", alias, "--no-prompt"],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
            )
        except Exception as exc:  # pragma: no cover
            self.notify(f"Failed to run scratch_delete for {alias}: {exc}", severity="error")
            return

        if result.returncode == 0:
            self.notify(f"Deleted scratch org '{alias}'.")
            return

        combined = (result.stdout or "") + "\n" + (result.stderr or "")
        lines = [line.strip() for line in combined.splitlines() if line.strip()]
        tail = lines[-1] if lines else ""
        message = f"scratch_delete failed for '{alias}'"
        if tail:
            message = f"{message}: {tail}"
        self.notify(message, severity="warning")

