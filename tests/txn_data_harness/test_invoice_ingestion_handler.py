"""Tests for the InvoiceIngestionHandler + CLI step wiring (PR 4).

Pins behavior on:

* The handler's static ``STEP_GRAPH`` (Draft + Posted),
* :meth:`InvoiceIngestionHandler.remaining_steps` resume math (the four
  meaningful (reached_stage, target_stage) combinations + the cross-kind
  rejection),
* :meth:`InvoiceIngestionHandler.effective_stage` -- no PST cap on
  pipeline-only accounts (ingestion's signature win),
* :meth:`InvoiceIngestionHandler.resolve` -- account + line + override
  binding, including a Product2 miss falling through to a
  description-only line,
* :meth:`InvoiceIngestionHandler.run` -- Draft + Posted manifests reach
  the right ``reached_stage`` and run the right steps,
* The handler registry surfaces the ingestion handler under
  ``SCENARIO_HANDLERS["invoice_ingestion"]``,
* :func:`config.load_scenarios` rejects PST-only knobs on ingestion
  specs and ingestion-only knobs on PST specs at parse time,
* CLI step end-to-end on a Draft -> Posted resume (the canonical
  ingestion-resume flow).
"""

from __future__ import annotations

from argparse import Namespace
from dataclasses import dataclass

import pytest

from scripts.txn_data_harness import cli as cli_mod
from scripts.txn_data_harness.config import (
    ConfigError,
    InvoiceIngestionScenarioSpec,
    InvoiceLineSpec,
    InvoiceOverrides,
    _coerce_spec,
)
from scripts.txn_data_harness.discovery import (
    Account,
    InvoiceLineProduct,
    OrgContext,
)
from scripts.txn_data_harness.handlers import (
    SCENARIO_HANDLERS,
    InvoiceIngestionHandler,
)
from scripts.txn_data_harness.handlers.invoice_ingestion import STEP_GRAPH
from scripts.txn_data_harness.lifecycle import LifecycleError
from scripts.txn_data_harness.models import (
    Manifest,
    ResolvedInvoiceIngestionSpec,
    ResolvedInvoiceLine,
    ResolvedInvoiceOverrides,
)


# ---------------------------------------------------------------------------
# Registry / STEP_GRAPH
# ---------------------------------------------------------------------------


def test_invoice_ingestion_handler_registered() -> None:
    handler = SCENARIO_HANDLERS["invoice_ingestion"]
    assert isinstance(handler, InvoiceIngestionHandler)
    assert handler.kind == "invoice_ingestion"


def test_step_graph_shape() -> None:
    # Draft ends after one step; Posted always runs both so the manifest
    # transitions invoice -> post even when ingest_invoice already landed
    # Posted (the no-op short-circuit lives in run_promote_to_posted).
    assert STEP_GRAPH["invoice"] == ["ingest_invoice"]
    assert STEP_GRAPH["post"] == ["ingest_invoice", "promote_to_posted"]
    # Ingestion has no other valid target stages -- the kind's valid_stages
    # set in config.py mirrors this graph.
    assert set(STEP_GRAPH) == {"invoice", "post"}


# ---------------------------------------------------------------------------
# remaining_steps -- the four meaningful resume combinations
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("reached", "target", "expected"),
    [
        # None -> invoice: fresh Draft run
        (None, "invoice", ["ingest_invoice"]),
        # None -> post: fresh Posted run lands both steps; the second is a
        # no-op fast path at runtime but appears in the plan so the
        # manifest stage transitions are uniform with the Draft+resume flow.
        (None, "post", ["ingest_invoice", "promote_to_posted"]),
        # invoice -> post: Draft already persisted; only post the existing id
        ("invoice", "post", ["promote_to_posted"]),
        # post -> post: terminal; nothing to do
        ("post", "post", []),
        # invoice -> invoice: already at target
        ("invoice", "invoice", []),
        # post -> invoice: stepping "back" is a no-op (never undo)
        ("post", "invoice", []),
    ],
)
def test_remaining_steps_resume_math(
    reached, target, expected
) -> None:
    handler = InvoiceIngestionHandler()
    assert handler.remaining_steps(reached, target, with_opportunity=False) == expected


def test_remaining_steps_ignores_with_opportunity_flag() -> None:
    """Ingestion has no Opportunity step; the flag is honored only for
    protocol parity with the PST handler. A True value must NOT smuggle an
    opportunity step into the plan."""
    handler = InvoiceIngestionHandler()
    assert handler.remaining_steps(None, "post", with_opportunity=True) == [
        "ingest_invoice",
        "promote_to_posted",
    ]


def test_remaining_steps_rejects_pst_target_stage() -> None:
    """A PST-only ``--to-stage`` against an ingestion manifest must fail
    loudly. The CLI relies on this to surface cross-kind misuse before any
    org write."""
    handler = InvoiceIngestionHandler()
    with pytest.raises(ValueError, match="not in STEP_GRAPH"):
        handler.remaining_steps(None, "activate", with_opportunity=False)


def test_remaining_steps_rejects_pst_reached_stage() -> None:
    """Mirror: a PST-shaped ``reached_stage`` (e.g. 'order') on an ingestion
    handler is a cross-kind manifest mismatch -- reject."""
    handler = InvoiceIngestionHandler()
    with pytest.raises(ValueError, match="not a valid ingestion stage"):
        handler.remaining_steps("order", "post", with_opportunity=False)


# ---------------------------------------------------------------------------
# effective_stage -- no PST cap for ingestion
# ---------------------------------------------------------------------------


def test_effective_stage_does_not_cap_pipeline_account() -> None:
    """PST caps non-billing accounts at ``order``; ingestion accepts them.
    This is the whole reason the ingestion path exists."""
    handler = InvoiceIngestionHandler()
    pipeline = Account(id="001PIPE", name="Global Media", billing_account_id=None)
    assert handler.effective_stage("post", pipeline) == "post"
    assert handler.effective_stage("invoice", pipeline) == "invoice"


# ---------------------------------------------------------------------------
# resolve -- account + line + override binding
# ---------------------------------------------------------------------------


def _ingestion_spec(
    account: str = "Infinitech",
    target: str = "post",
    lines=None,
    invoice=None,
    count: int = 1,
) -> InvoiceIngestionScenarioSpec:
    return InvoiceIngestionScenarioSpec(
        account=account,
        invoice_lines=lines or [
            InvoiceLineSpec(
                name="Cloud License",
                sku="QB-LIC-CLOUD",
                quantity=2,
                unit_price=450.0,
            ),
        ],
        target_stage=target,
        count=count,
        invoice=invoice,
    )


def _empty_org_context() -> OrgContext:
    return OrgContext(
        pricebook_id="pb",
        pricebook_name="Standard",
        legal_entity_id=None,
        legal_entity_name=None,
        opportunity_stage=None,
        billing_ready_accounts=[],
        products=[],
    )


def test_resolve_binds_account_and_lines(fake_client) -> None:
    # resolve_account: account row + BillingAccount lookup
    fake_client.query_responses.append([{"Id": "001A", "Name": "Infinitech"}])
    fake_client.query_responses.append([{"Id": "BA-1"}])
    # resolve_invoice_line_product: SKU hit -> product binding
    fake_client.query_responses.append(
        [{"Id": "01tCLOUD", "Name": "Cloud License", "StockKeepingUnit": "QB-LIC-CLOUD"}]
    )
    spec = _ingestion_spec()
    handler = InvoiceIngestionHandler()
    resolved = handler.resolve(fake_client, _empty_org_context(), spec)

    assert isinstance(resolved, ResolvedInvoiceIngestionSpec)
    assert resolved.account.id == "001A"
    assert resolved.account.name == "Infinitech"
    assert resolved.effective_stage == "post"
    assert len(resolved.invoice_lines) == 1
    line = resolved.invoice_lines[0]
    assert isinstance(line.product, InvoiceLineProduct)
    assert line.product.id == "01tCLOUD"
    assert line.sku == "QB-LIC-CLOUD"
    assert line.taxable is False  # Phase 1 invariant


def test_resolve_falls_through_on_sku_miss(fake_client) -> None:
    """An SKU that doesn't match an active Product2 yields a description-only
    line (the ingestion API accepts unproducted lines)."""
    fake_client.query_responses.append([{"Id": "001A", "Name": "Infinitech"}])
    fake_client.query_responses.append([])  # no BillingAccount
    fake_client.query_responses.append([])  # SKU miss
    spec = _ingestion_spec(
        target="invoice",
        lines=[InvoiceLineSpec(name="Custom Service", sku="MISSING-SKU",
                               quantity=1, unit_price=100.0)],
    )
    resolved = InvoiceIngestionHandler().resolve(
        fake_client, _empty_org_context(), spec
    )
    line = resolved.invoice_lines[0]
    assert line.product is None
    assert line.sku == "MISSING-SKU"
    # account resolves but is pipeline-only -- ingestion is fine with that
    assert resolved.account.is_billing_ready is False


def test_resolve_uses_default_account_when_unpinned(fake_client) -> None:
    """No account in spec + no billing-ready accounts in ctx ->
    discover_any_accounts picks the first Account in the org."""
    # discover_any_accounts: list Accounts, then BillingAccount stitch
    fake_client.query_responses.append([{"Id": "001X", "Name": "Acme"}])
    fake_client.query_responses.append([])  # no BillingAccount
    # SKU lookup for the spec's line
    fake_client.query_responses.append([])  # SKU miss

    spec = _ingestion_spec(account=None)
    resolved = InvoiceIngestionHandler().resolve(
        fake_client, _empty_org_context(), spec
    )
    assert resolved.account.id == "001X"
    assert resolved.account.name == "Acme"


def test_resolve_carries_invoice_overrides(fake_client) -> None:
    from datetime import date
    fake_client.query_responses.append([{"Id": "001A", "Name": "Infinitech"}])
    fake_client.query_responses.append([{"Id": "BA-1"}])
    fake_client.query_responses.append([])  # SKU miss on the line

    overrides = InvoiceOverrides(
        invoice_date=date(2026, 3, 1),
        due_date=date(2026, 3, 31),
        currency="USD",
        description="Q1 standalone billing test",
    )
    spec = _ingestion_spec(
        invoice=overrides,
        lines=[InvoiceLineSpec(name="Setup", quantity=1, unit_price=500.0)],
    )
    resolved = InvoiceIngestionHandler().resolve(
        fake_client, _empty_org_context(), spec
    )
    assert isinstance(resolved.invoice_overrides, ResolvedInvoiceOverrides)
    assert resolved.invoice_overrides.invoice_date == date(2026, 3, 1)
    assert resolved.invoice_overrides.currency == "USD"
    # Phase 1 invariant survives the resolve step.
    assert resolved.invoice_overrides.should_calculate_tax is False


# ---------------------------------------------------------------------------
# run -- drive a scenario through the lifecycle
# ---------------------------------------------------------------------------


def _build_resolved(account: Account, target: str = "post") -> ResolvedInvoiceIngestionSpec:
    return ResolvedInvoiceIngestionSpec(
        spec=InvoiceIngestionScenarioSpec(
            account=account.name,
            invoice_lines=[InvoiceLineSpec(name="Plan", quantity=1, unit_price=100.0)],
            target_stage=target,
            count=1,
        ),
        account=account,
        invoice_lines=[
            ResolvedInvoiceLine(name="Plan", quantity=1, unit_price=100.0)
        ],
        invoice_overrides=None,
        effective_stage=target,
    )


def test_run_drafts_an_invoice(monkeypatch, fake_client, billable_account) -> None:
    """A scenario targeting ``invoice`` runs ingest_invoice once and stops."""
    called: list[str] = []

    def fake_ingest(client, account, lines, run_id, *, status, invoice_spec, timeout):
        called.append(status)
        return "1nvDRAFT", None, ["iln1"]

    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.ingest_invoice", fake_ingest
    )
    # promote_to_posted shouldn't be called on a Draft target -- guard it.
    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.post_invoice",
        lambda *a, **kw: pytest.fail("post_invoice must not run for target=invoice"),
    )
    manifest = InvoiceIngestionHandler().run(
        client=fake_client,
        ctx=_empty_org_context(),
        run_id="DEMO-DRAFT",
        resolved=_build_resolved(billable_account, target="invoice"),
        poll_timeout=1,
        max_retries=0,
    )
    assert called == ["Draft"]
    assert manifest.kind == "invoice_ingestion"
    assert manifest.reached_stage == "invoice"
    assert manifest.invoice_id == "1nvDRAFT"
    assert manifest.account_id == billable_account.id
    assert manifest.error is None


def test_run_posts_an_invoice_with_short_circuit_promote(
    monkeypatch, fake_client, billable_account
) -> None:
    """target=post: ingest_invoice lands Posted, promote_to_posted is a
    no-op fast-path (manifest already at reached_stage='post')."""
    statuses: list[str] = []

    def fake_ingest(client, account, lines, run_id, *, status, invoice_spec, timeout):
        statuses.append(status)
        return "1nvPOSTED", "INV-0001", ["iln1"]

    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.ingest_invoice", fake_ingest
    )
    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.post_invoice",
        lambda *a, **kw: pytest.fail("post_invoice should not run -- already Posted"),
    )
    manifest = InvoiceIngestionHandler().run(
        client=fake_client,
        ctx=_empty_org_context(),
        run_id="DEMO-POST",
        resolved=_build_resolved(billable_account, target="post"),
        poll_timeout=1,
        max_retries=0,
    )
    assert statuses == ["Posted"]
    assert manifest.reached_stage == "post"
    assert manifest.invoice_id == "1nvPOSTED"
    assert manifest.invoice_number == "INV-0001"


def test_run_records_lifecycle_error_without_raising(
    monkeypatch, fake_client, billable_account
) -> None:
    """A LifecycleError from a step lands on the manifest as failure_class
    but doesn't propagate out of ``run`` (parity with PST run_scenario)."""
    def boom(*a, **kw):
        raise LifecycleError("ingest_invoice", "kaboom")

    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.ingest_invoice", boom
    )
    manifest = InvoiceIngestionHandler().run(
        client=fake_client,
        ctx=_empty_org_context(),
        run_id="DEMO-FAIL",
        resolved=_build_resolved(billable_account, target="invoice"),
        poll_timeout=1,
        max_retries=0,
    )
    assert manifest.error
    assert "kaboom" in manifest.error
    assert manifest.reached_stage is None


# ---------------------------------------------------------------------------
# Config parser: cross-kind PST-only knob rejection
# ---------------------------------------------------------------------------


def test_coerce_spec_rejects_pst_only_field_on_ingestion() -> None:
    merged = {
        "kind": "invoice_ingestion",
        "target_stage": "post",
        "account": "Infinitech",
        "invoice_lines": [{"name": "API", "quantity": 1, "unit_price": 10}],
        # PST-only field
        "products": [{"sku": "QB-API-FLEX", "quantity": 1}],
    }
    with pytest.raises(ConfigError, match="'products' is not valid for kind 'invoice_ingestion'"):
        _coerce_spec(merged, "test")


def test_coerce_spec_rejects_with_opportunity_on_ingestion() -> None:
    merged = {
        "kind": "invoice_ingestion",
        "target_stage": "post",
        "account": "Infinitech",
        "invoice_lines": [{"name": "API", "quantity": 1, "unit_price": 10}],
        "with_opportunity": True,
    }
    with pytest.raises(ConfigError, match="with_opportunity"):
        _coerce_spec(merged, "test")


def test_coerce_spec_rejects_taxable_line_on_posted() -> None:
    merged = {
        "kind": "invoice_ingestion",
        "target_stage": "post",
        "account": "Infinitech",
        "invoice_lines": [
            {"name": "API", "quantity": 1, "unit_price": 10, "taxable": True}
        ],
    }
    with pytest.raises(ConfigError, match="taxable: true"):
        _coerce_spec(merged, "test")


def test_coerce_spec_rejects_ingestion_target_outside_kind_stages() -> None:
    """``activate`` is PST-only; the kind-specific stage allowlist must
    catch it before construction."""
    merged = {
        "kind": "invoice_ingestion",
        "target_stage": "activate",
        "account": "Infinitech",
        "invoice_lines": [{"name": "API", "quantity": 1, "unit_price": 10}],
    }
    with pytest.raises(ConfigError, match="not valid for kind 'invoice_ingestion'"):
        _coerce_spec(merged, "test")


def test_coerce_spec_returns_ingestion_dataclass() -> None:
    merged = {
        "kind": "invoice_ingestion",
        "target_stage": "post",
        "account": "Infinitech",
        "invoice_lines": [
            {"name": "API", "quantity": 1.0, "unit_price": 10.0},
        ],
    }
    spec = _coerce_spec(merged, "test")
    assert isinstance(spec, InvoiceIngestionScenarioSpec)
    assert spec.target_stage == "post"
    assert len(spec.invoice_lines) == 1


def test_coerce_spec_ingestion_default_target_stage_is_post() -> None:
    """A bare ``kind: invoice_ingestion`` without an explicit target_stage
    defaults to Posted (parity with PST defaulting to ``post``)."""
    merged = {
        "kind": "invoice_ingestion",
        "account": "Infinitech",
        "invoice_lines": [{"name": "API", "quantity": 1, "unit_price": 10}],
    }
    spec = _coerce_spec(merged, "test")
    assert spec.target_stage == "post"


# ---------------------------------------------------------------------------
# CLI step end-to-end: Draft -> Posted resume
# ---------------------------------------------------------------------------


@dataclass
class _FakeClientFactory:
    """Pre-baked stub for SfRestClient.from_alias used by ``cli step``.

    The CLI rebuilds discovery against the org; we short-circuit that
    by patching ``discover`` to return an empty OrgContext. The fake
    client itself doesn't need to do much: ``promote_to_posted`` reads
    the existing invoice id from the manifest and calls
    :func:`lifecycle.post_invoice`, which we also patch.
    """

    fake: object

    def from_alias(self, *_a, **_kw):
        return self.fake


def test_cli_step_resumes_draft_to_posted(
    monkeypatch, tmp_path, fake_client, billable_account
) -> None:
    """``cli step --to-stage post`` on a Draft ingestion manifest runs
    only ``promote_to_posted`` (the resume math the test in
    ``remaining_steps`` pins is the same logic the CLI relies on)."""
    from scripts.txn_data_harness import manifests as manifests_mod

    # Point the on-disk manifest store at the tmpdir.
    monkeypatch.setattr(manifests_mod, "MANIFEST_DIR", tmp_path)

    draft = Manifest(
        run_id="DEMO-RESUME",
        kind="invoice_ingestion",
        account_id=billable_account.id,
        account_name=billable_account.name,
        invoice_id="1nvDRAFT",
        reached_stage="invoice",
    )
    manifests_mod.write_manifest(draft, manifest_dir=tmp_path)

    # Patch SfRestClient.from_alias + discovery + lifecycle. The CLI's
    # discovery path queries the org for pricebook/legal entity/etc.;
    # we substitute an empty context since ingestion doesn't need any
    # of them. resolve_account returns the billing-ready Account so the
    # CLI's downstream call shape matches.
    monkeypatch.setattr(
        cli_mod.SfRestClient, "from_alias", lambda *_a, **_kw: fake_client
    )
    monkeypatch.setattr(
        cli_mod, "resolve_account", lambda *_a, **_kw: billable_account
    )
    monkeypatch.setattr(
        cli_mod, "discover", lambda *_a, **_kw: _empty_org_context()
    )

    posted: dict = {}

    def fake_post(client, invoice_id, run_id, timeout):
        posted["invoice_id"] = invoice_id
        posted["run_id"] = run_id
        return "INV-PROMOTED"

    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.post_invoice", fake_post
    )
    # Guard: ingest_invoice MUST NOT run on a Draft->Posted resume. The
    # resume math pins this to a one-step plan: just promote_to_posted.
    monkeypatch.setattr(
        "scripts.txn_data_harness.steps.lifecycle.ingest_invoice",
        lambda *a, **kw: pytest.fail(
            "ingest_invoice must not run on Draft->Posted resume"
        ),
    )

    args = Namespace(
        org="rlm-base__test",
        api_version="67.0",
        transport="requests",
        manifest=str(tmp_path / "DEMO-RESUME.json"),
        account=None,
        product=None,
        opportunity_stage=None,
        with_opportunity=False,
        to_stage="post",
        poll_timeout=1,
        config=None,
        count=None,
        target_stage=None,
        concurrency=1,
        max_retries=0,
        no_probe=False,
        keep_probes=False,
        verbose=0,
    )
    # Capture and redirect the CLI's bare write_manifest() calls into tmp_path.
    # The CLI invokes write_manifest with no manifest_dir argument, which binds
    # the module-level default at function-def time -- monkeypatching
    # ``manifests_mod.MANIFEST_DIR`` after the fact does not retarget already-
    # captured defaults. Wrap the symbol the CLI imported instead.
    captured: list = []

    def capture_write(m):
        captured.append(m)
        return manifests_mod.write_manifest(m, manifest_dir=tmp_path)

    monkeypatch.setattr(cli_mod, "write_manifest", capture_write)

    rc = cli_mod._cmd_step(args)
    assert rc == 0
    assert posted == {"invoice_id": "1nvDRAFT", "run_id": "DEMO-RESUME"}

    # The final manifest write lands at reached_stage='post' with the assigned
    # invoice number; the Draft id is reused, not regenerated.
    final = captured[-1]
    assert final.reached_stage == "post"
    assert final.invoice_number == "INV-PROMOTED"
    assert final.invoice_id == "1nvDRAFT"


def test_cli_step_rejects_pst_stage_against_ingestion_manifest(
    monkeypatch, tmp_path, fake_client, billable_account
) -> None:
    """A user accidentally passing ``--to-stage activate`` against an
    ingestion manifest must fail loudly (cross-kind step rejection)."""
    from scripts.txn_data_harness import manifests as manifests_mod

    monkeypatch.setattr(manifests_mod, "MANIFEST_DIR", tmp_path)
    draft = Manifest(
        run_id="DEMO-XKIND",
        kind="invoice_ingestion",
        account_id=billable_account.id,
        account_name=billable_account.name,
        invoice_id="1nvX",
        reached_stage="invoice",
    )
    manifests_mod.write_manifest(draft, manifest_dir=tmp_path)
    monkeypatch.setattr(
        cli_mod.SfRestClient, "from_alias", lambda *_a, **_kw: fake_client
    )
    monkeypatch.setattr(
        cli_mod, "resolve_account", lambda *_a, **_kw: billable_account
    )
    monkeypatch.setattr(
        cli_mod, "discover", lambda *_a, **_kw: _empty_org_context()
    )

    args = Namespace(
        org="rlm-base__test",
        api_version="67.0",
        transport="requests",
        manifest=str(tmp_path / "DEMO-XKIND.json"),
        account=None,
        product=None,
        opportunity_stage=None,
        with_opportunity=False,
        to_stage="activate",  # PST-only stage
        poll_timeout=1,
        config=None,
        count=None,
        target_stage=None,
        concurrency=1,
        max_retries=0,
        no_probe=False,
        keep_probes=False,
        verbose=0,
    )
    with pytest.raises(ValueError, match="STEP_GRAPH"):
        cli_mod._cmd_step(args)


def test_cli_step_unknown_manifest_kind_rejects(
    monkeypatch, tmp_path, fake_client, billable_account
) -> None:
    """A manifest from a newer harness (unknown kind) must fail loudly
    instead of silently routing through the PST handler."""
    from scripts.txn_data_harness import manifests as manifests_mod

    monkeypatch.setattr(manifests_mod, "MANIFEST_DIR", tmp_path)
    bogus = Manifest(
        run_id="DEMO-BOGUS",
        kind="future_kind_xyz",
        account_id=billable_account.id,
        account_name=billable_account.name,
    )
    # write_manifest -> to_dict -> all fields including the unknown kind.
    manifests_mod.write_manifest(bogus, manifest_dir=tmp_path)
    monkeypatch.setattr(
        cli_mod.SfRestClient, "from_alias", lambda *_a, **_kw: fake_client
    )
    monkeypatch.setattr(
        cli_mod, "resolve_account", lambda *_a, **_kw: billable_account
    )
    monkeypatch.setattr(
        cli_mod, "discover", lambda *_a, **_kw: _empty_org_context()
    )

    args = Namespace(
        org="rlm-base__test",
        api_version="67.0",
        transport="requests",
        manifest=str(tmp_path / "DEMO-BOGUS.json"),
        account=None,
        product=None,
        opportunity_stage=None,
        with_opportunity=False,
        to_stage="post",
        poll_timeout=1,
        config=None,
        count=None,
        target_stage=None,
        concurrency=1,
        max_retries=0,
        no_probe=False,
        keep_probes=False,
        verbose=0,
    )
    with pytest.raises(LifecycleError, match="has no registered handler"):
        cli_mod._cmd_step(args)
