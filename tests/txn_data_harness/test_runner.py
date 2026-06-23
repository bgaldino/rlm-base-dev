"""Tests for Transaction Data Harness runner helpers."""

from __future__ import annotations

from datetime import date

import pytest

from scripts.txn_data_harness.config import ConfigError, ProductOption, ScenarioSpec
from scripts.txn_data_harness.lifecycle import LifecycleError
from scripts.txn_data_harness.models import (
    EndDateOverride,
    LineItem,
    Manifest,
    ResolvedOption,
    ResolvedSpec,
    Term,
)
from scripts.txn_data_harness.runner import (
    _resolve_end_date,
    _resolve_term,
    draw_lines,
    draw_start_date,
    effective_stage,
    remaining_steps,
    run_batch,
    run_scenario,
    stage_sequence,
)


def _opt(**overrides) -> ProductOption:
    """Build a minimal ProductOption with quantity=(1,1) and overrides."""
    base = dict(sku=None, quantity=(1, 1), discount=None)
    base.update(overrides)
    return ProductOption(**base)


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
        "order", "activate", "usage", "invoice", "post",
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


# ---------------------------------------------------------------------------
# _resolve_term -- fallback chain and unit-vs-PSM consistency
# ---------------------------------------------------------------------------


class TestResolveTerm:
    """The 4-step fallback chain + unit consistency rule from runner._resolve_term.

    Order: line override -> scenario default -> product.default_term ->
    Term(12, "Months"). Bare-int config promotes ``unit`` from the resolved
    PSM; explicit unit must equal the PSM unit (no implicit PBE switching).
    """

    def test_line_override_beats_scenario_and_psm_default(self, annual_term_product):
        spec = ScenarioSpec(
            account=None, products=[], target_stage="post",
            with_opportunity=False, opportunity_stage=None, count=1,
            term=Term(2, "Annual"),
        )
        opt = _opt(term=Term(3, "Annual"))
        assert _resolve_term(opt, spec, annual_term_product) == Term(3, "Annual")

    def test_scenario_default_falls_through_when_no_line_override(self, annual_term_product):
        spec = ScenarioSpec(
            account=None, products=[], target_stage="post",
            with_opportunity=False, opportunity_stage=None, count=1,
            term=Term(2, "Annual"),
        )
        assert _resolve_term(_opt(), spec, annual_term_product) == Term(2, "Annual")

    def test_psm_default_when_no_config_term(self, annual_term_product):
        spec = ScenarioSpec(
            account=None, products=[], target_stage="post",
            with_opportunity=False, opportunity_stage=None, count=1,
        )
        # annual_term_product carries pricing_term=1, pricing_term_unit="Annual".
        assert _resolve_term(_opt(), spec, annual_term_product) == Term(1, "Annual")

    def test_hardcoded_default_when_psm_has_no_term(self, term_product):
        # Strip the PSM's declared term so neither config nor product has one.
        from dataclasses import replace
        bare = replace(term_product, pricing_term=None, pricing_term_unit=None)
        spec = ScenarioSpec(
            account=None, products=[], target_stage="post",
            with_opportunity=False, opportunity_stage=None, count=1,
        )
        assert _resolve_term(_opt(), spec, bare) == Term(12, "Months")

    def test_bare_int_promotes_unit_from_psm(self, quarterly_term_product):
        """``term: 4`` on a Quarterly SOM resolves to ``Term(4, "Quarterly")``."""
        spec = ScenarioSpec(
            account=None, products=[], target_stage="post",
            with_opportunity=False, opportunity_stage=None, count=1,
        )
        opt = _opt(term=Term(4, None))
        assert _resolve_term(opt, spec, quarterly_term_product) == Term(4, "Quarterly")

    def test_bare_int_with_missing_psm_unit_raises(self, term_product):
        """Bare-int term + PSM missing ``PricingTermUnit`` must fail loud.

        A silent ``Months`` fallback would write the wrong SubscriptionTermUnit
        on a non-monthly PSM and the platform validation error would point
        miles from the cause. Force the author to pin the unit explicitly.
        """
        from dataclasses import replace
        bare = replace(term_product, pricing_term_unit=None)
        spec = ScenarioSpec(
            account=None, products=[], target_stage="post",
            with_opportunity=False, opportunity_stage=None, count=1,
        )
        opt = _opt(term=Term(4, None))
        with pytest.raises(ConfigError, match="PricingTermUnit"):
            _resolve_term(opt, spec, bare)

    def test_explicit_matching_unit_passes(self, quarterly_term_product):
        spec = ScenarioSpec(
            account=None, products=[], target_stage="post",
            with_opportunity=False, opportunity_stage=None, count=1,
        )
        opt = _opt(term=Term(4, "Quarterly"))
        assert _resolve_term(opt, spec, quarterly_term_product) == Term(4, "Quarterly")

    def test_explicit_unit_mismatch_raises(self, quarterly_term_product):
        """Quarterly PSM + ``unit: Annual`` is incoherent: the line is bound to
        a PBE whose SOM is Quarterly; sending Annual would silently desynchronize
        the line cadence from the billing engine. Author must pin a matching
        ``selling_model:`` explicitly.
        """
        spec = ScenarioSpec(
            account=None, products=[], target_stage="post",
            with_opportunity=False, opportunity_stage=None, count=1,
        )
        opt = _opt(term=Term(1, "Annual"))
        with pytest.raises(ConfigError, match="PricingTermUnit"):
            _resolve_term(opt, spec, quarterly_term_product)

    def test_evergreen_with_term_raises(self, evergreen_product):
        """Evergreen lines must reject any term config -- EndDate (and now
        SubscriptionTerm) are rejected by createOrderFromQuote."""
        spec = ScenarioSpec(
            account=None, products=[], target_stage="post",
            with_opportunity=False, opportunity_stage=None, count=1,
        )
        opt = _opt(term=Term(12, "Months"))
        with pytest.raises(ConfigError, match="Evergreen"):
            _resolve_term(opt, spec, evergreen_product)

    def test_evergreen_without_term_returns_none(self, evergreen_product):
        spec = ScenarioSpec(
            account=None, products=[], target_stage="post",
            with_opportunity=False, opportunity_stage=None, count=1,
        )
        assert _resolve_term(_opt(), spec, evergreen_product) is None

    def test_end_date_without_term_raises(self, annual_term_product):
        """``end_date`` without any term cadence (line / scenario / PSM)
        would silently fall through to ``Term(12, "Months")``; surface it
        as ConfigError instead so the author has to be explicit.
        """
        from dataclasses import replace
        # Strip the PSM's term so neither config nor product carries one.
        bare = replace(annual_term_product, pricing_term=None, pricing_term_unit=None)
        spec = ScenarioSpec(
            account=None, products=[], target_stage="post",
            with_opportunity=False, opportunity_stage=None, count=1,
        )
        opt = _opt(end_date=EndDateOverride(months=12))
        with pytest.raises(ConfigError, match="end_date requires an accompanying term"):
            _resolve_term(opt, spec, bare)


# ---------------------------------------------------------------------------
# _resolve_end_date -- line wins over scenario; TermDefined-only
# ---------------------------------------------------------------------------


class TestResolveEndDate:
    """``end_date`` override resolution: line beats scenario; rejected on
    non-TermDefined products at resolve time so the lifecycle never has to
    deal with an incoherent override.
    """

    def test_line_override_beats_scenario(self, annual_term_product):
        spec = ScenarioSpec(
            account=None, products=[], target_stage="post",
            with_opportunity=False, opportunity_stage=None, count=1,
            end_date=EndDateOverride(absolute=date(2027, 1, 14)),
        )
        opt = _opt(end_date=EndDateOverride(absolute=date(2028, 12, 31)))
        out = _resolve_end_date(opt, spec, annual_term_product)
        assert out is not None
        assert out.absolute == date(2028, 12, 31)

    def test_scenario_default_falls_through(self, annual_term_product):
        spec = ScenarioSpec(
            account=None, products=[], target_stage="post",
            with_opportunity=False, opportunity_stage=None, count=1,
            end_date=EndDateOverride(absolute=date(2027, 1, 14)),
        )
        out = _resolve_end_date(_opt(), spec, annual_term_product)
        assert out is not None
        assert out.absolute == date(2027, 1, 14)

    def test_none_when_neither_set(self, annual_term_product):
        spec = ScenarioSpec(
            account=None, products=[], target_stage="post",
            with_opportunity=False, opportunity_stage=None, count=1,
        )
        assert _resolve_end_date(_opt(), spec, annual_term_product) is None

    def test_evergreen_with_end_date_raises(self, evergreen_product):
        spec = ScenarioSpec(
            account=None, products=[], target_stage="post",
            with_opportunity=False, opportunity_stage=None, count=1,
        )
        opt = _opt(end_date=EndDateOverride(months=12))
        with pytest.raises(ConfigError, match="Evergreen"):
            _resolve_end_date(opt, spec, evergreen_product)


# ---------------------------------------------------------------------------
# LineItem manifest round-trip carries end_date
# ---------------------------------------------------------------------------


def test_line_item_manifest_round_trip_preserves_end_date(term_product) -> None:
    """``cli step`` resume reads LineItems back from the manifest; the
    end_date override must survive the round-trip so a resumed place picks
    the same EndDate.
    """
    line = LineItem(
        product=term_product,
        quantity=2,
        discount_percent=10.0,
        term=Term(12, "Months"),
        end_date=EndDateOverride(absolute=date(2027, 1, 14)),
    )
    record = line.to_manifest_record()
    assert record["end_date"] == {"absolute": "2027-01-14"}

    restored = LineItem.from_manifest_record(record, term_product)
    assert restored.end_date == EndDateOverride(absolute=date(2027, 1, 14))


def test_line_item_manifest_round_trip_preserves_months_offset(term_product) -> None:
    line = LineItem(
        product=term_product,
        quantity=1,
        term=Term(12, "Months"),
        end_date=EndDateOverride(months=12),
    )
    record = line.to_manifest_record()
    assert record["end_date"] == {"months": 12}

    restored = LineItem.from_manifest_record(record, term_product)
    assert restored.end_date == EndDateOverride(months=12)


def test_line_item_manifest_round_trip_omits_end_date_when_unset(term_product) -> None:
    line = LineItem(product=term_product, quantity=1, term=Term(12, "Months"))
    record = line.to_manifest_record()
    assert "end_date" not in record

    restored = LineItem.from_manifest_record(record, term_product)
    assert restored.end_date is None
