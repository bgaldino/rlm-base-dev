"""Textual application for the CCI build manager."""

from __future__ import annotations

import json
import queue
import subprocess
import threading
import time
from pathlib import Path
from typing import Dict, List, Optional

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, RichLog, Static, Switch

from scripts.build_harness.tui.runner import ROOT as REPO_ROOT
from scripts.build_harness.tui.runner import load_tui_config, run_build
from scripts.build_harness.tui.state import BuildConfig, OrgShape, PrepareStepView, RunEvent, RunEventKind
from scripts.build_harness.tui.widgets.progress_format import format_step_label

SETTINGS_FILE = Path(__file__).with_name("settings.json")


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


def _load_tui_settings() -> Dict[str, object]:
    """Load optional TUI settings from local settings.json."""
    if not SETTINGS_FILE.exists():
        return {}
    try:
        payload = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return payload if isinstance(payload, dict) else {}


class OrgSelectionScreen(Screen[None]):
    """Wizard step 1: choose org shape."""

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="wizard-panel"):
            yield Static("Step 1 of 4: Select Scratch Org Shape", classes="section-title")
            yield DataTable(id="shape-table")
            with Horizontal(id="wizard-actions"):
                yield Button("Next", id="next-button", variant="success")
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
            self.app.alias = f"{selected.name}-local"
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
                yield Static("", id="actions-spacer")
                yield Button("Exit", id="exit-button", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#alias-input", Input).value = self.app.alias
        self.query_one("#days-input", Input).value = str(self.app.days)

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
                        state = "ON" if override else "OFF"
                        with Horizontal(classes="flag-row"):
                            yield Static(state, id=f"flag-state-{name}", classes=f"flag-state-{state.lower()}")
                            yield Switch(value=override, id=f"flag-switch-{name}")
                            yield Label(name)
                        comment = self.app.flag_comments.get(name, "")
                        if comment:
                            yield Static(comment, classes="flag-comment")
            with Horizontal(id="wizard-actions"):
                yield Button("Back", id="back-button")
                yield Button("Start Build", id="start-button", variant="success")
                yield Static("", id="actions-spacer")
                yield Button("Exit", id="exit-button", variant="error")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit-button":
            self.app.exit()
            return
        if event.button.id == "back-button":
            self.app.pop_screen()
            return
        if event.button.id != "start-button":
            return

        overrides: Dict[str, bool] = {}
        for switch in self.query(Switch):
            if switch.id is None or not switch.id.startswith("flag-switch-"):
                continue
            flag_name = switch.id.replace("flag-switch-", "", 1)
            default = self.app.bool_flags.get(flag_name)
            if default is not None and switch.value != default:
                overrides[flag_name] = bool(switch.value)
        self.app.flag_overrides = overrides
        self.app.start_build_and_show_output()

    def on_switch_changed(self, event: Switch.Changed) -> None:
        switch_id = event.switch.id
        if switch_id is None or not switch_id.startswith("flag-switch-"):
            return
        flag_name = switch_id.replace("flag-switch-", "", 1)
        state_widget = self.query_one(f"#flag-state-{flag_name}", Static)
        if event.value:
            state_widget.update("ON")
            state_widget.set_class(True, "flag-state-on")
            state_widget.set_class(False, "flag-state-off")
        else:
            state_widget.update("OFF")
            state_widget.set_class(False, "flag-state-on")
            state_widget.set_class(True, "flag-state-off")


class OutputScreen(Screen[None]):
    """Wizard step 4: execution output with live progress."""

    def __init__(self, *, config: BuildConfig) -> None:
        super().__init__()
        self.config = config
        self.step_views: Dict[int, PrepareStepView] = {}

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Vertical(id="output-panel"):
            yield Static("Step 4 of 4: Build Output", classes="section-title")
            yield Static("Starting...", id="run-status")
            yield Static("Elapsed: 0.0s", id="elapsed")
            yield Static("Current: startup", id="current-step")
            yield DataTable(id="step-table")
            yield RichLog(id="log", wrap=True, highlight=True, markup=False)
            with Horizontal(id="wizard-actions"):
                yield Button("Stop Build", id="stop-button", variant="warning")
                yield Static("", id="actions-spacer")
                yield Button("Exit", id="exit-button", variant="error")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#step-table", DataTable)
        table.cursor_type = "row"
        table.add_columns("step", "target", "status", "duration", "detail")
        self.set_interval(0.2, self._refresh_elapsed)

    def _refresh_elapsed(self) -> None:
        self.query_one("#elapsed", Static).update(f"Elapsed: {self.app.elapsed_seconds():.1f}s")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "exit-button":
            if self.app.is_run_active():
                self.app.push_screen(ExitConfirmScreen())
            else:
                self.app.exit()
            return
        if event.button.id == "stop-button":
            self.app.request_stop()

    def handle_event(self, event: RunEvent) -> None:
        log = self.query_one("#log", RichLog)
        status = self.query_one("#run-status", Static)
        current = self.query_one("#current-step", Static)
        table = self.query_one("#step-table", DataTable)
        payload = event.payload

        if event.kind == RunEventKind.RUN_STARTED:
            status.update(f"Running (0/{int(payload.get('total_steps', 0))})")
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
            self.query_one("#stop-button", Button).disabled = True
            return

        if event.kind == RunEventKind.RUN_FAILED:
            status.update("Failed")
            failure = payload.get("failure_signature", "")
            message = payload.get("message", "Run failed.")
            log.write(f"{message} :: {failure}" if failure else str(message))
            self.query_one("#stop-button", Button).disabled = True
            return

        if event.kind == RunEventKind.RUN_CANCELLED:
            status.update("Cancelled")
            log.write(str(payload.get("message", "Run cancelled.")))
            self.query_one("#stop-button", Button).disabled = True
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
            self._upsert_step(
                table,
                PrepareStepView(
                    step_number=int(payload["step_number"]),
                    target_type=str(payload["target_type"]),
                    target_name=str(payload["target_name"]),
                    when=payload.get("when"),
                    status="running",
                ),
            )
            current.update(
                f"Current: {format_step_label(int(payload['step_number']), str(payload['target_type']), str(payload['target_name']))}"
            )
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
        table.update_cell(key, "status", status)
        table.update_cell(key, "duration", f"{duration_seconds:.1f}s")
        table.update_cell(key, "detail", detail)


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
                yield Static("", id="actions-spacer")
                yield Button("Keep Org and Exit", id="keep-exit-button", variant="warning")
                yield Button("Delete Org and Exit", id="delete-exit-button", variant="error")
        yield Footer()

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
    CSS = """
    Screen {
        layout: vertical;
    }
    #wizard-panel, #output-panel {
        height: 1fr;
        border: heavy $primary;
        padding: 1;
    }
    #shape-table {
        height: 16;
        margin: 1 0;
    }
    #flag-scroll {
        height: 1fr;
        border: round $surface;
        padding: 0 1;
        margin: 1 0;
    }
    #step-table {
        height: 12;
        margin: 1 0;
    }
    #log {
        height: 1fr;
        border: round $surface;
        margin-top: 1;
    }
    #wizard-actions {
        height: auto;
        margin-top: 1;
    }
    #actions-spacer {
        width: 1fr;
    }
    .flag-row {
        height: auto;
        margin-bottom: 1;
    }
    .flag-comment {
        margin: -1 0 1 11;
        color: $text-muted;
    }
    .flag-state-on {
        width: 5;
        content-align: center middle;
        text-style: bold;
        color: $success;
    }
    .flag-state-off {
        width: 5;
        content-align: center middle;
        text-style: bold;
        color: $error;
    }
    .section-title {
        text-style: bold;
        margin: 0 0 1 0;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.org_shapes: List[OrgShape] = []
        self.bool_flags: Dict[str, bool] = {}
        self.flag_groups: List[tuple[str, List[str]]] = []
        self.flag_comments: Dict[str, str] = {}
        self.settings: Dict[str, object] = {}
        self.default_org_shape: str = ""
        self.selected_shape: str = ""
        self.alias: str = ""
        self.days: int = 1
        self.flag_overrides: Dict[str, bool] = {}

        self._event_queue: "queue.Queue[RunEvent]" = queue.Queue()
        self._stop_event = threading.Event()
        self._runner_thread: Optional[threading.Thread] = None
        self._run_started_monotonic: Optional[float] = None
        self._completed_steps = 0
        self._total_steps = 0
        self._output_screen: Optional[OutputScreen] = None
        self._active_org_alias: str = ""

    def on_mount(self) -> None:
        self.settings = _load_tui_settings()
        default_shape_raw = str(self.settings.get("default_org_shape", "")).strip()

        shapes, bool_flags, _, flag_groups, flag_comments = load_tui_config()
        self.org_shapes = shapes
        self.bool_flags = bool_flags
        self.flag_groups = flag_groups
        self.flag_comments = flag_comments
        known_shapes = {shape.name for shape in shapes}
        self.default_org_shape = default_shape_raw if default_shape_raw in known_shapes else ""
        self.set_interval(0.2, self._drain_events)
        self.push_screen(OrgSelectionScreen())

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
        self._completed_steps = 0
        self._total_steps = 0
        self._stop_event.clear()

        config = BuildConfig(
            org_shape=self.selected_shape,
            org_alias=self.alias.strip(),
            days=self.days,
            flag_overrides=dict(self.flag_overrides),
        )
        output = OutputScreen(config=config)
        self._output_screen = output
        self.push_screen(output)
        self._active_org_alias = config.org_alias

        def _runner() -> None:
            run_build(config=config, stop_event=self._stop_event, emit=self._event_queue.put)

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

    def elapsed_seconds(self) -> float:
        if self._run_started_monotonic is None:
            return 0.0
        return time.monotonic() - self._run_started_monotonic

    def update_progress(self, completed_steps: int) -> None:
        self._completed_steps = completed_steps

    def status_label_running(self) -> str:
        return f"Running ({self._completed_steps}/{self._total_steps})"

    def status_label_success(self) -> str:
        return f"Success ({self._completed_steps}/{self._total_steps})"

    def _drain_events(self) -> None:
        while True:
            try:
                event = self._event_queue.get_nowait()
            except queue.Empty:
                return
            if event.kind == RunEventKind.RUN_STARTED:
                self._run_started_monotonic = time.monotonic()
                self._total_steps = int(event.payload.get("total_steps", 0))
                self._completed_steps = 0
            if event.kind in {RunEventKind.RUN_SUCCEEDED, RunEventKind.RUN_FAILED, RunEventKind.RUN_CANCELLED}:
                self._active_org_alias = ""
            if self._output_screen is not None:
                self._output_screen.handle_event(event)

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

