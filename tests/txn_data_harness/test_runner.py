"""Tests for Transaction Data Harness runner helpers."""

from __future__ import annotations

from datetime import date

from scripts.txn_data_harness.config import ScenarioSpec
from scripts.txn_data_harness.lifecycle import LifecycleError
from scripts.txn_data_harness.models import Manifest, ResolvedOption, ResolvedSpec
from scripts.txn_data_harness.runner import (
    draw_lines,
    draw_start_date,
    effective_stage,
    remaining_steps,
    run_batch,
    run_scenario,
    stage_sequence,
)


def _spec(count: int = 1, target_stage: str = "post") -> ScenarioSpec:
    return ScenarioSpec(
        account="Infinitech",
        products=[],
        target_stage=target_stage,
        with_opportunity=False,
        opportunity_stage=None,
        count=count,
    )


def test_effective_stage_caps_non_billing_account_at_order(pipeline_account) -> None:
    assert effective_stage("post", pipeline_account) == "order"
    assert effective_stage("activate", pipeline_account) == "order"
    assert effective_stage("quote", pipeline_account) == "quote"


def test_effective_stage_preserves_billable_target(billable_account) -> None:
    assert effective_stage("post", billable_account) == "post"


def test_stage_sequence_handles_opportunity_only() -> None:
    assert stage_sequence("opportunity", with_opportunity=False) == ["opportunity"]


def test_stage_sequence_can_prepend_opportunity() -> None:
    assert stage_sequence("order", with_opportunity=True) == [
        "opportunity", "quote", "order",
    ]


def test_draw_start_date_picks_within_range(monkeypatch) -> None:
    monkeypatch.setattr("scripts.txn_data_harness.runner.random.randint", lambda _lo, _hi: 2)
    assert draw_start_date((date(2026, 1, 1), date(2026, 1, 5))) == date(2026, 1, 3)


def test_draw_lines_always_returns_at_least_one_line(monkeypatch, term_product) -> None:
    option = ResolvedOption(
        product=term_product,
        quantity=(2, 2),
        discount=(10, 10),
        period_boundary="Anniversary",
        billing_frequency="Monthly",
    )
    monkeypatch.setattr("scripts.txn_data_harness.runner.random.random", lambda: 0.99)
    monkeypatch.setattr("scripts.txn_data_harness.runner.random.choice", lambda items: items[0])
    lines = draw_lines([option])

    assert len(lines) == 1
    assert lines[0].quantity == 2
    assert lines[0].discount_percent == 10
    assert lines[0].period_boundary == "Anniversary"
    assert lines[0].billing_frequency == "Monthly"


def test_remaining_steps_fresh_run_uses_full_sequence() -> None:
    assert remaining_steps(None, "order", with_opportunity=False) == [
        "quote", "order",
    ]
    assert remaining_steps(None, "order", with_opportunity=True) == [
        "opportunity", "quote", "order",
    ]


def test_remaining_steps_resumes_after_reached_stage() -> None:
    assert remaining_steps("quote", "post", with_opportunity=False) == [
        "order", "activate", "invoice", "post",
    ]


def test_remaining_steps_empty_when_already_at_target() -> None:
    assert remaining_steps("post", "post", with_opportunity=False) == []
    assert remaining_steps("invoice", "order", with_opportunity=False) == []


def _resolved_account_and_lines(billable_account, term_product):
    line = draw_lines([ResolvedOption(product=term_product, quantity=(1, 1), discount=None)])
    return billable_account, line


def test_run_scenario_retries_transient_then_succeeds(
    monkeypatch, org_context, billable_account, term_product
) -> None:
    account, lines = _resolved_account_and_lines(billable_account, term_product)
    monkeypatch.setattr("scripts.txn_data_harness.runner.write_manifest", lambda m, *a, **k: None)

    calls = {"n": 0}

    def flaky_run_steps(step_names, ctx, manifest):
        calls["n"] += 1
        if calls["n"] == 1:
            manifest.reached_stage = "quote"  # checkpoint partial progress
            raise LifecycleError("activate", "request timed out")
        manifest.reached_stage = "post"
        return manifest

    monkeypatch.setattr("scripts.txn_data_harness.runner.run_steps", flaky_run_steps)
    sleeps: list[float] = []

    manifest = run_scenario(
        client=object(), ctx=org_context, run_id="R-1", target_stage="post",
        account=account, lines=lines, with_opportunity=False, poll_timeout=1,
        max_retries=2, sleep=sleeps.append,
    )

    assert calls["n"] == 2
    assert manifest.attempts == 2
    assert manifest.error is None
    assert manifest.failure_class is None
    assert manifest.reached_stage == "post"
    assert len(sleeps) == 1  # one backoff between the two attempts


def test_run_scenario_does_not_retry_deterministic(
    monkeypatch, org_context, billable_account, term_product
) -> None:
    account, lines = _resolved_account_and_lines(billable_account, term_product)
    monkeypatch.setattr("scripts.txn_data_harness.runner.write_manifest", lambda m, *a, **k: None)

    calls = {"n": 0}

    def failing_run_steps(step_names, ctx, manifest):
        calls["n"] += 1
        raise LifecycleError("order", "quote_id is required before order")

    monkeypatch.setattr("scripts.txn_data_harness.runner.run_steps", failing_run_steps)
    sleeps: list[float] = []

    manifest = run_scenario(
        client=object(), ctx=org_context, run_id="R-1", target_stage="post",
        account=account, lines=lines, with_opportunity=False, poll_timeout=1,
        max_retries=2, sleep=sleeps.append,
    )

    assert calls["n"] == 1  # failed fast, no retry
    assert manifest.attempts == 1
    assert manifest.failure_class == "deterministic"
    assert "is required before" in manifest.error
    assert sleeps == []


def test_run_scenario_exhausts_retry_budget(
    monkeypatch, org_context, billable_account, term_product
) -> None:
    account, lines = _resolved_account_and_lines(billable_account, term_product)
    monkeypatch.setattr("scripts.txn_data_harness.runner.write_manifest", lambda m, *a, **k: None)

    def always_transient(step_names, ctx, manifest):
        raise LifecycleError("activate", "request timed out")

    monkeypatch.setattr("scripts.txn_data_harness.runner.run_steps", always_transient)
    sleeps: list[float] = []

    manifest = run_scenario(
        client=object(), ctx=org_context, run_id="R-1", target_stage="post",
        account=account, lines=lines, with_opportunity=False, poll_timeout=1,
        max_retries=2, sleep=sleeps.append,
    )

    # 1 initial + 2 retries = 3 attempts, 2 backoffs.
    assert manifest.attempts == 3
    assert manifest.failure_class == "transient"
    assert manifest.error is not None
    assert len(sleeps) == 2


def test_run_batch_emits_start_and_completion_callbacks(
    monkeypatch, billable_account, term_product
) -> None:
    resolved = ResolvedSpec(
        spec=_spec(count=2),
        account=billable_account,
        options=[ResolvedOption(product=term_product, quantity=(1, 1), discount=None)],
        effective_stage="post",
    )
    started = []
    completed = []

    def fake_run_scenario(_client, _ctx, run_id, *_args, **_kwargs):
        return Manifest(run_id=run_id, reached_stage="post")

    monkeypatch.setattr("scripts.txn_data_harness.runner.run_scenario", fake_run_scenario)

    result = run_batch(
        client=object(),
        ctx=object(),
        resolved=[resolved],
        concurrency=5,
        poll_timeout=1,
        on_start=lambda base, total, workers: started.append((base, total, workers)),
        on_complete=lambda done, total, manifest, _path: completed.append(
            (done, total, manifest.run_id)
        ),
    )

    assert result.total == 2
    assert result.failures == 0
    assert started[0][1:] == (2, 2)
    assert [item[0] for item in completed] == [1, 2]
