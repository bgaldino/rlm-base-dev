"""Tests for scripts.build_harness.tui.app safety behaviors."""

from __future__ import annotations

from scripts.build_harness.tui import app
from scripts.build_harness.tui.state import BuildConfig


def _config(alias: str = "ent-tui-a3f9") -> BuildConfig:
    return BuildConfig(org_shape="ent", org_alias=alias, days=30, flag_overrides={})


def test_validate_alias_rejects_path_separators_and_traversal() -> None:
    assert app._validate_alias_and_days("../escape", "7") is not None
    assert app._validate_alias_and_days("ent/tui", "7") is not None
    assert app._validate_alias_and_days(r"ent\\tui", "7") is not None


def test_persistent_run_logger_sanitizes_alias_fragment(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(app, "TUI_RUNS_ROOT", tmp_path / ".harness" / "tui-runs")
    logger = app.PersistentRunLogger(
        config=_config(alias="../unsafe/alias"),
        settings_snapshot={},
        effective_flags={},
    )
    # Run id/path must remain inside the configured output root.
    assert ".." not in logger.run_id
    assert "/" not in logger.run_id
    assert logger.run_dir.resolve().is_relative_to((tmp_path / ".harness" / "tui-runs").resolve())


def test_stop_and_exit_deletes_only_orgs_created_in_run(monkeypatch) -> None:
    manager = app.BuildManagerApp()
    manager._active_org_alias = "existing-org"
    manager._org_created_in_run = False
    deleted_aliases: list[str] = []
    exits: list[bool] = []
    notices: list[str] = []
    monkeypatch.setattr(manager, "_delete_scratch_org", lambda alias: deleted_aliases.append(alias))
    monkeypatch.setattr(manager, "exit", lambda: exits.append(True))
    monkeypatch.setattr(manager, "notify", lambda message, **_kwargs: notices.append(str(message)))

    manager.stop_and_exit(delete_org=True)

    assert deleted_aliases == []
    assert any("Skipping delete" in message for message in notices)
    assert exits == [True]

