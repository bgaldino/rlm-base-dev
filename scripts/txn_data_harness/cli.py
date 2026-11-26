"""Subcommand CLI for composable Transaction Data Harness operations."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional

import requests

from . import generate
from .auth import SfApiError, SfCliError, SfRestClient
from .cli_args import add_connection_args, add_generate_args, add_resume_args
from .config import (
    ConfigError,
    check_settlement_stage,
    load_scenarios,
    settlement_from_dict,
)
from .discovery import DiscoveryError, discover, resolve_account, resolve_product
from .failure import classify_exception
from .lifecycle import LifecycleError, SettlementError
from .manifests import (
    MANIFEST_DIR,
    list_manifests,
    load_manifest,
    manifest_path,
    parse_retention,
    prune_old_runs,
    resolve_manifest_path,
    summarize_manifest,
    write_manifest,
)
from .handlers import SCENARIO_HANDLERS
from .models import STAGES_QUOTE, STAGES_SETTLEMENT, LineItem
from .report import build_batch_report, render_markdown
from .runner import draw_lines
from .steps import StepContext, execute_step
from . import verify as billing_verify


def _generate_argv(args: argparse.Namespace, *, dry_run: bool = False) -> list[str]:
    argv = ["--org", args.org]
    for flag in ("config", "target_stage", "account", "product", "opportunity_stage",
                 "api_version", "transport"):
        value = getattr(args, flag, None)
        if value is not None:
            argv += [f"--{flag.replace('_', '-')}", str(value)]
    for flag in ("count", "concurrency", "poll_timeout", "max_retries"):
        value = getattr(args, flag, None)
        if value is not None:
            argv += [f"--{flag.replace('_', '-')}", str(value)]
    if getattr(args, "with_opportunity", False):
        argv.append("--with-opportunity")
    if getattr(args, "no_probe", False):
        argv.append("--no-probe")
    if getattr(args, "keep_probes", False):
        argv.append("--keep-probes")
    if dry_run:
        argv.append("--dry-run")
    verbosity = getattr(args, "verbose", 0) or 0
    if verbosity:
        argv.append("-" + ("v" * verbosity))
    return argv


def _cmd_plan(args: argparse.Namespace) -> int:
    return generate.main(_generate_argv(args, dry_run=True))


def _cmd_run(args: argparse.Namespace) -> int:
    return generate.main(_generate_argv(args))


def _cmd_inspect(args: argparse.Namespace) -> int:
    if args.latest:
        manifests = list_manifests()
        if not manifests:
            print("No manifests found.", file=sys.stderr)
            return 1
        manifest = load_manifest(str(manifests[0]))
    else:
        manifest = load_manifest(args.manifest)
    summary = summarize_manifest(manifest)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(_format_inspect_text(summary))
    return 0


def _format_inspect_text(summary: dict) -> str:
    """Render a compact human-readable manifest summary."""
    ids = summary.get("ids") or {}
    lines = [
        f"Run: {summary.get('run_id')}",
        f"Kind: {summary.get('kind')}",
        f"Account: {summary.get('account')}",
        f"Reached stage: {summary.get('reached_stage') or '(none)'}",
        f"Attempts: {summary.get('attempts')}",
    ]
    if summary.get("error"):
        lines.append(f"Error: {summary.get('error')}")
    if summary.get("invoice_number"):
        lines.append(f"Invoice number: {summary.get('invoice_number')}")
    link = summary.get("invoice_order_link") or {}
    if link.get("status") == "failed":
        detail = f": {link.get('error')}" if link.get("error") else ""
        lines.append(f"Invoice order link: failed{detail}")
    for label, value in ids.items():
        if value:
            lines.append(f"{label}: {value}")
    lines.append(f"Manifest: {summary.get('path')}")
    return "\n".join(lines)


def _lines_from_manifest(client: SfRestClient, manifest, currency=None) -> list[LineItem]:
    """Rebuild ``LineItem``s from a manifest, including any resolved usage spec.

    ``LineItem.to_manifest_record`` writes the resolved usage targets (with
    UsageResource + UoM ids) so we don't need a second discovery pass for the
    common case of resuming an ``activate`` run to ``usage``.
    """
    lines: list[LineItem] = []
    for rec in manifest.lines:
        sku = rec.get("sku")
        if not sku and not rec.get("product_id"):
            continue
        lines.append(
            LineItem.from_manifest_record(rec, resolve_product(
                client, sku, selling_model=rec.get("selling_model"),
                currency=rec.get("currency", currency),
                pricebook_entry_id=rec.get("pricebook_entry_id"),
                product_id=rec.get("product_id")))
        )
    return lines


_FLOW_NAME_RE = re.compile(r"^[A-Za-z0-9_]+$")


def _cmd_rate(args: argparse.Namespace) -> int:
    """Kick off the org-wide usage rating/billing orchestration.

    Invokes ``RLM_UsageOrchestrationController.startOrchestration(<flow>)``
    via anonymous Apex (``sf apex run``). The job is asynchronous, runs ~15
    minutes, and rates every usage product in the org -- run it ONCE per batch
    of generated usage data, not per scenario.
    """
    flow = args.flow_name
    if not _FLOW_NAME_RE.match(flow):
        print(
            f"ERROR: --flow-name must match [A-Za-z0-9_]+ (got {flow!r})",
            file=sys.stderr,
        )
        return 1
    snippet = f"RLM_UsageOrchestrationController.startOrchestration('{flow}');\n"
    with tempfile.NamedTemporaryFile(
        "w", suffix=".apex", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(snippet)
        tmp_path = tmp.name
    try:
        print(
            f"Kicking off usage orchestration flow '{flow}' against org "
            f"'{args.org}'. The job is async and rates ALL usage products in "
            f"the org (~15 minutes). Monitor progress in Setup -> Monitor "
            f"Workflow Services."
        )
        proc = subprocess.run(
            ["sf", "apex", "run", "--target-org", args.org, "--file", tmp_path],
            capture_output=True, text=True,
        )
    finally:
        Path(tmp_path).unlink(missing_ok=True)
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr, end="")
        return proc.returncode
    return 0


def _cmd_step(args: argparse.Namespace) -> int:
    client = SfRestClient.from_alias(
        args.org, api_version=args.api_version, transport=args.transport
    )
    manifest = load_manifest(args.manifest)
    account = _resolve_step_account(client, args, manifest)
    ctx = discover(
        client,
        account_name=account.name,
        sku=args.product,
        opportunity_stage=args.opportunity_stage,
    )

    # Look up the handler by the manifest's persisted kind. Reject an unknown
    # kind loudly -- a manifest carrying a kind no registered handler knows
    # about is almost certainly a config typo or a future-format manifest
    # from a newer harness; quietly defaulting to PST would run the wrong
    # lifecycle against the wrong stage graph.
    if manifest.kind not in SCENARIO_HANDLERS:
        raise LifecycleError(
            "step",
            f"manifest kind '{manifest.kind}' has no registered handler "
            f"(known: {', '.join(sorted(SCENARIO_HANDLERS))})",
        )
    handler = SCENARIO_HANDLERS[manifest.kind]

    target = handler.effective_stage(args.to_stage, account)
    # Resume math is the handler's job -- it owns the kind's step graph.
    # PST's :func:`runner.remaining_steps` rejects an out-of-domain
    # ``reached_stage`` via ``STAGES.index`` (raises ValueError); the
    # ingestion handler's :meth:`remaining_steps` raises ValueError on
    # the same mismatch. Either way a cross-kind mistake fails loudly
    # before we touch the org.
    steps = handler.remaining_steps(
        manifest.reached_stage, target, args.with_opportunity
    )
    # --config is checked before anything else, so it is never ignored -- not
    # even on a manifest that already reached the target.
    settlement = _settlement_for_step(args, manifest, client)
    if getattr(args, "application_level", None):
        if args.to_stage != "payment_applied":
            raise LifecycleError(
                "step", "--application-level applies only to --to-stage payment_applied "
                "(the level decides where the payment is applied)",
            )
        if not steps:
            raise LifecycleError(
                "step", f"--application-level: manifest {manifest.run_id} already reached "
                f"{manifest.reached_stage}; nothing would run with it",
            )
    if not steps:
        # Nothing runs, so nothing changes: an earlier error stays. Only a
        # step that runs and succeeds clears error / failure_class.
        print(json.dumps(summarize_manifest(manifest), indent=2))
        return 0

    step_ctx = _build_step_context(
        args, handler, client, ctx, account, manifest, settlement=settlement
    )

    try:
        for step in steps:
            # Handlers may expose public stage names that map to different
            # internal step ids in STEP_REGISTRY (for example order_draft ->
            # order_from_quote/order_direct on PST kinds). The full batch runner
            # does this translation before dispatch; mirror it here for resume.
            internal_step = (
                handler._internal_step(step)
                if hasattr(handler, "_internal_step")
                else step
            )
            manifest = execute_step(internal_step, step_ctx, manifest)
            # The write that records the stage reached also clears an earlier
            # failure (one write: a kill cannot leave a stale error behind).
            manifest.error = None
            manifest.failure_class = None
            write_manifest(manifest)
    except Exception as exc:  # noqa: BLE001 -- record any failure, then re-raise
        # SfApiError (a 5xx, or a refusal outside a settlement call) and
        # transport errors land here as well as LifecycleError.
        manifest.error = (
            str(exc) if isinstance(exc, LifecycleError) else f"{type(exc).__name__}: {exc}"
        )
        manifest.failure_class = classify_exception(exc)
        write_manifest(manifest)
        raise
    print(json.dumps(summarize_manifest(manifest), indent=2))
    return 0


def _resolve_step_account(client: SfRestClient, args: argparse.Namespace, manifest):
    """The account a ``cli step`` resume runs against.

    The manifest's ``account_id`` is used when it has one (looked up by Id, so
    a rename or a duplicate name cannot redirect a resume). ``--account``
    must then name that account: names are not unique, so it is accepted when
    the manifest's Id is among the accounts with that name; otherwise it is
    refused before anything is written.
    """
    from .discovery import account_ids_named

    if args.account and manifest.account_id:
        ids = account_ids_named(client, args.account)
        if manifest.account_id not in ids:
            raise LifecycleError(
                "step",
                f"--account '{args.account}' resolves to {', '.join(ids) or 'no account'}, "
                f"but manifest {manifest.run_id} belongs to account {manifest.account_id} "
                f"('{manifest.account_name}'); omit --account to use the manifest's",
            )
    elif args.account:
        return resolve_account(client, args.account)
    if manifest.account_id:
        return resolve_account(
            client, manifest.account_name or manifest.account_id,
            account_id=manifest.account_id,
        )
    if not manifest.account_name:
        raise DiscoveryError(
            "step requires --account when the manifest has no account_name"
        )
    return resolve_account(client, manifest.account_name)


_UNSET = object()


def _build_step_context(
    args: argparse.Namespace,
    handler,
    client: SfRestClient,
    ctx,
    account,
    manifest,
    settlement=_UNSET,
) -> StepContext:
    """Build the per-kind StepContext for a ``cli step`` invocation.

    PST resumes need the LineItem set: either rebuilt from the manifest (if
    a prior stage already serialized lines) or freshly drawn from a config
    file passed via ``--config``. Ingestion resumes don't need lines from
    config -- the InvoiceLine records persist on the Invoice itself, so
    ``ingest_invoice`` is already done by the time we hit ``promote_to_posted``
    and the remaining step (post the existing Draft) only needs the invoice id.
    """
    if settlement is _UNSET:
        settlement = _settlement_for_step(args, manifest, client)
    if handler.kind == "invoice_ingestion":
        return StepContext(
            client=client,
            org_context=ctx,
            run_id=manifest.run_id,
            account=account,
            lines=[],
            with_opportunity=False,
            poll_timeout=args.poll_timeout,
            checkpoint=write_manifest,
            target_stage=args.to_stage,
            invoice_lines=[],
            invoice_spec=None,
            settlement=settlement,
            application_level_override=getattr(args, "application_level", None),
        )

    # Persisted selection wins; do not run unrelated default discovery first.
    lines = _lines_from_manifest(client, manifest, account.currency_iso_code)
    if not lines:
        try:
            specs = load_scenarios(args)
            resolved = [handler.resolve(client, ctx, s) for s in specs]
            lines = draw_lines(resolved[0].options) if resolved else []
        except ConfigError:
            lines = []
    if lines:
        from dataclasses import replace
        currencies = {line.product.currency_iso_code for line in lines}
        if len(currencies) > 1:
            raise ConfigError("Manifest lines must use the same currency")
        account = replace(account, currency_iso_code=lines[0].product.currency_iso_code)
    if not lines and args.to_stage not in {"invoice_draft", "invoice_posted", *STAGES_SETTLEMENT}:
        raise LifecycleError(
            "step", "no manifest lines or config product lines to use"
        )
    return StepContext(
        client=client,
        org_context=ctx,
        run_id=manifest.run_id,
        account=account,
        lines=lines,
        with_opportunity=args.with_opportunity,
        poll_timeout=args.poll_timeout,
        checkpoint=write_manifest,
        target_stage=args.to_stage,
        settlement=settlement,
        application_level_override=getattr(args, "application_level", None),
    )


def _settlement_for_step(args: argparse.Namespace, manifest, client=None):
    """Settlement options for a ``cli step`` resume.

    Only a settlement target (``credit_applied`` / ``payment_applied``) reads
    them. The block is fixed once recorded on the manifest (the first
    settlement step records it): the recorded block is used, and a
    ``--config`` that differs from it is refused, naming the keys (changed
    options = a new run). ``--config`` supplies the block only when the
    manifest has none; it is evaluated against ``--to-stage``, not the file's
    own ``target_stage``. A settlement target with no options at all fails
    here, before any org write.
    """
    to_stage = getattr(args, "to_stage", None)
    if to_stage not in STAGES_SETTLEMENT:
        return None
    config = getattr(args, "config", None)
    if manifest.settlement is not None:
        recorded = settlement_from_dict(manifest.settlement)
        if config:
            wanted = _config_settlement(args, manifest, client)
            diffs = _settlement_diff(recorded.to_dict() if recorded else {},
                                     wanted.to_dict())
            if diffs:
                raise SettlementError(
                    "step",
                    f"--config's settlement block differs from the one recorded on "
                    f"manifest {manifest.run_id} in {', '.join(diffs)}. The recorded "
                    "block is fixed: drop --config to resume with it, or start a new "
                    "run for different options",
                )
        if (
            to_stage == "payment_applied"
            and (recorded is None or recorded.payment is None)
            and manifest.reached_stage != "payment_applied"
        ):
            # Refuse before any step runs: the credit stage would otherwise
            # write first and the payment stage refuse only afterwards.
            raise SettlementError(
                "step",
                f"--to-stage payment_applied: manifest {manifest.run_id}'s recorded "
                "settlement block has no 'payment' and is fixed; stop at "
                "credit_applied, or start a new run whose block has 'payment'",
            )
        return None
    if not config:
        raise SettlementError(
            "step",
            f"--to-stage {to_stage} needs settlement options: the manifest has none; pass "
            f"--config with a scenario of kind '{manifest.kind}' for account "
            f"'{manifest.account_name}' with a 'settlement:' block",
        )
    return _config_settlement(args, manifest, client)


def _config_settlement(args: argparse.Namespace, manifest, client):
    """The one ``settlement:`` block ``--config`` holds for this manifest."""
    from .discovery import account_ids_named

    ids_by_name: dict[str, list[str]] = {}

    def same_account(name: str) -> bool:
        if not manifest.account_name or name == manifest.account_name:
            return True
        if client is None or not manifest.account_id:
            return False
        if name not in ids_by_name:
            ids_by_name[name] = account_ids_named(client, name)
        return manifest.account_id in ids_by_name[name]

    matches = []
    for spec in load_scenarios(args, settlement_stage=args.to_stage):
        settlement = getattr(spec, "settlement", None)
        if settlement is None or spec.kind != manifest.kind:
            continue
        if spec.account and not same_account(spec.account):
            continue
        if settlement not in matches:
            matches.append(settlement)
    if len(matches) == 1:
        # The --to-stage check runs on the matching scenario only.
        check_settlement_stage(matches[0], args.to_stage, "--config")
        return matches[0]
    if len(matches) > 1:
        raise SettlementError(
            "step",
            f"--config has {len(matches)} different settlement blocks for kind "
            f"'{manifest.kind}' / account '{manifest.account_name}'; pass a config "
            "with one matching scenario",
        )
    raise SettlementError(
        "step",
        f"--config has no scenario of kind '{manifest.kind}' for account "
        f"'{manifest.account_name}' ({manifest.account_id}) with a 'settlement:' block",
    )


def _settlement_diff(a, b, prefix: str = "") -> list[str]:
    """Dotted keys whose values differ between two settlement dicts."""
    keys = []
    for key in sorted(set(a or {}) | set(b or {})):
        va, vb = (a or {}).get(key), (b or {}).get(key)
        name = f"{prefix}{key}"
        if isinstance(va, dict) and isinstance(vb, dict):
            keys.extend(_settlement_diff(va, vb, f"{name}."))
        elif va != vb:
            keys.append(name)
    return keys


def _cmd_report(args: argparse.Namespace) -> int:
    """Rebuild and print a batch report from manifests already on disk.

    A batch's manifests are either the bare ``<base_run_id>`` (single-scenario
    run) or ``<base_run_id>-NNN`` (fan-out). Match those exactly rather than any
    stem sharing the prefix, so sibling batches whose ids share a leading string
    don't bleed together. The ``-report`` file is excluded so re-reporting is
    idempotent.
    """
    base = args.base_run_id
    paths = [
        p for p in list_manifests()
        if (p.stem == base or p.stem.startswith(f"{base}-"))
        and not p.stem.endswith("-report")
    ]
    if not paths:
        print(f"No manifests found for base run id '{base}'.", file=sys.stderr)
        return 1
    manifests = [load_manifest(str(p)) for p in paths]
    report = build_batch_report(manifests, base_run_id=base)
    if args.markdown:
        print(render_markdown(report))
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def _verify_ids(args: argparse.Namespace) -> tuple[list[str], list[str]]:
    """Collect invoice and payment ids from manifests and/or explicit flags."""
    invoice_ids = billing_verify.split_ids(args.invoice_ids, "--invoice-ids")
    payment_ids = billing_verify.split_ids(args.payment_ids, "--payment-ids")
    paths = [resolve_manifest_path(m) for m in (args.manifest or [])]
    if args.latest:
        manifests = list_manifests()
        if not manifests:
            raise billing_verify.VerifyError("No manifests found.")
        paths.append(manifests[0])
    empty = []
    for path in paths:
        inv, pay = billing_verify.ids_from_manifest(path)
        if not inv and not pay:
            empty.append(str(path))
        invoice_ids += [i for i in inv if i not in invoice_ids]
        payment_ids += [p for p in pay if p not in payment_ids]
    if not invoice_ids and not payment_ids:
        if empty:
            raise billing_verify.VerifyError(
                f"manifest {', '.join(empty)} names no invoice or payment id; "
                f"pass --invoice-ids instead"
            )
        raise billing_verify.VerifyError(
            "verify needs --manifest, --latest, --invoice-ids or --payment-ids"
        )
    for path in empty:
        print(f"WARNING: manifest {path} names no invoice or payment id", file=sys.stderr)
    return invoice_ids, payment_ids


def _cmd_verify(args: argparse.Namespace) -> int:
    """Read-only billing checks.

    Exit 0 when nothing fails, 1 when any check fails, 2 when the input or a
    Salesforce request is bad, or the ``sf`` CLI cannot run (no report). With
    ``--json`` an error prints ``{"ok": false, "error": ...}`` on stdout too.
    """
    try:
        invoice_ids, payment_ids = _verify_ids(args)
        client = SfRestClient.from_alias(
            args.org, api_version=args.api_version, transport=args.transport
        )
        records = billing_verify.fetch_records(client, invoice_ids, payment_ids)
        report = billing_verify.run_checks(records, args.expect_level)
    except Exception as exc:  # noqa: BLE001 - read-only command: any error is exit 2
        # Exit 1 means a check failed, so no error may reach main() (which maps
        # ValueError to 1) or escape as a traceback.
        message = _error_message(exc)
        print(f"ERROR: {message}", file=sys.stderr)
        if args.json:
            _emit(json.dumps({"ok": False, "error": message}, indent=2))
        return 2
    _emit(json.dumps(report, indent=2) if args.json else billing_verify.render_text(report))
    return 0 if report["ok"] else 1


def _error_message(exc: Exception) -> str:
    """The one-line reason a command could not run or report."""
    if isinstance(exc, billing_verify.VerifyError):
        return str(exc)
    if isinstance(exc, (SfApiError, SfCliError, requests.RequestException)):
        # RequestException: the --api-version latest lookup.
        return f"Salesforce request failed: {exc}"
    if isinstance(exc, FileNotFoundError) and exc.filename == "sf":
        return "the sf CLI was not found on PATH"
    if isinstance(exc, OSError):
        return f"could not run a command or read a file: {exc}"
    return f"unexpected {type(exc).__name__}: {exc}"


QUOTE_TO_CASH_CONFIG = (
    Path(__file__).resolve().parent / "scenarios" / "sales_txn_quote" / "20-quote-to-cash.yaml"
)
QUOTE_TO_CASH_STAGE = "payment_applied"


def _cmd_quote_to_cash(args: argparse.Namespace) -> int:
    """Run a quote through to an applied payment, then verify the balances.

    Exit 0 when every scenario reached ``payment_applied`` and the verifier
    checked at least one balance and failed none; 1 when a scenario fell short,
    a check failed or nothing was checked; 4 for a config that cannot be read
    or has a scenario not targeting ``payment_applied`` (refused before any
    write); 2 when the run or the verify raised an error (no ``sf``, a refused
    request); otherwise the generator's own code (2 auth, 3 discovery, 4
    config) when the run never started. It writes records: Posted invoices
    are not deletable.
    """
    argv = [
        "--org", args.org, "--config", str(args.config), "--concurrency", "1",
        "--api-version", args.api_version, "--transport", args.transport,
        "--poll-timeout", str(args.poll_timeout),
    ]
    if args.verbose:
        argv.append("-" + "v" * args.verbose)
    try:
        specs = load_scenarios(generate.parse_args(argv))
    except (ConfigError, OSError, ValueError) as exc:
        print(f"ERROR: bad config:\n  {exc}", file=sys.stderr)
        return 4
    off_target = sorted({s.target_stage for s in specs} - {QUOTE_TO_CASH_STAGE})
    if off_target:
        print(f"ERROR: quote-to-cash: every scenario in {args.config} must target "
              f"{QUOTE_TO_CASH_STAGE}, not {', '.join(off_target)}; nothing was written",
              file=sys.stderr)
        return 4
    batch: list = []
    try:
        code = generate.main(argv, on_batch=lambda result, manifests: batch.extend(manifests))
    except Exception as exc:  # noqa: BLE001 - exit 1 means short or failed, never an error
        print(f"ERROR: quote-to-cash run: {_error_message(exc)}", file=sys.stderr)
        return 2
    if not batch:
        print(f"ERROR: quote-to-cash: the run did not start (exit {code})", file=sys.stderr)
        return code or 2
    short = [m for m in batch if m.error or m.reached_stage != QUOTE_TO_CASH_STAGE]
    for m in short:
        reason = f": {m.error}" if m.error else ""
        print(f"FAIL: {m.run_id} reached {m.reached_stage or '(none)'}, "
              f"not {QUOTE_TO_CASH_STAGE}{reason}")
    if short or code:
        print(f"QUOTE-TO-CASH: fail ({len(short)} of {len(batch)} scenario(s) short)")
        return 1
    invoice_ids: list[str] = []
    payment_ids: list[str] = []
    try:
        for m in batch:
            inv, pay = billing_verify.ids_from_manifest(manifest_path(m.run_id))
            invoice_ids += [i for i in inv if i not in invoice_ids]
            payment_ids += [p for p in pay if p not in payment_ids]
        client = SfRestClient.from_alias(
            args.org, api_version=args.api_version, transport=args.transport
        )
        records = billing_verify.fetch_records(client, invoice_ids, payment_ids)
        report = billing_verify.run_checks(records)
    except Exception as exc:  # noqa: BLE001 - verify could not report: exit 2
        print(f"ERROR: quote-to-cash verify: {_error_message(exc)}", file=sys.stderr)
        return 2
    print(billing_verify.render_text(report))
    if not report["ok"]:
        print("QUOTE-TO-CASH: fail (a balance check failed)")
        return 1
    if not report["checked"]:
        print("QUOTE-TO-CASH: fail (no balance was checked)")
        return 1
    runs = ", ".join(m.run_id for m in batch)
    print(f"QUOTE-TO-CASH: pass ({len(batch)} scenario(s) at {QUOTE_TO_CASH_STAGE}: {runs})")
    return 0


def _emit(text: str) -> None:
    """Print to stdout; a reader that closed the pipe (``| head -1``) is not an error.

    The exit code stays the one already computed. stdout is pointed at /dev/null so
    the interpreter's final flush does not raise again.
    """
    try:
        print(text)
        sys.stdout.flush()
    except BrokenPipeError:
        try:
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
        except (OSError, ValueError):  # no real file descriptor (captured stdout)
            pass


def _cmd_prune(args: argparse.Namespace) -> int:
    """Delete manifest files older than a retention window (dry-run by default)."""
    retention = parse_retention(args.older_than)
    removed = prune_old_runs(retention, dry_run=not args.yes)
    verb = "Removed" if args.yes else "Would remove"
    print(f"{verb} {len(removed)} manifest(s) older than {args.older_than} "
          f"from {MANIFEST_DIR}:")
    for path in removed:
        print(f"  {path.name}")
    if not args.yes and removed:
        print("\n(dry run — pass --yes to delete)")
    return 0


def _json_usage_errors(parsers: list[argparse.ArgumentParser], as_json: bool) -> None:
    """For ``verify --json``, also print an argparse usage error as the JSON error object.

    Installed on the top-level parser (unrecognized or extra arguments) and the
    ``verify`` subparser (missing ``--org``, a bad choice), so every usage error of
    a ``verify`` command line that contains the exact token ``--json`` prints one
    ``{"ok": false, "error": "usage: ..."}`` object on stdout. argparse still prints
    usage and the error on stderr and exits 2; the first error exits, so there is
    never a second object. ``verify`` refuses abbreviated options, so ``--json`` is
    the only spelling that sets JSON output.
    """
    for parser in parsers:
        original = parser.error

        def error(message: str, _original=original):
            if as_json:
                _emit(json.dumps({"ok": False, "error": f"usage: {message}"}, indent=2))
            _original(message)

        parser.error = error  # type: ignore[method-assign]


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    tokens = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(
        prog="python -m scripts.txn_data_harness.cli",
        description="Composable commands for Transaction Data Harness workflows.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan", help="Resolve config/discovery and print the plan.")
    add_generate_args(plan)
    plan.set_defaults(func=_cmd_plan)

    run = sub.add_parser("run", help="Run the existing end-to-end generator.")
    add_generate_args(run)
    run.set_defaults(func=_cmd_run)

    inspect = sub.add_parser("inspect", help="Inspect a manifest by id/path.")
    group = inspect.add_mutually_exclusive_group(required=True)
    group.add_argument("--manifest", help="Run id or manifest path.")
    group.add_argument("--latest", action="store_true", help="Inspect the newest manifest.")
    inspect.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    inspect.set_defaults(func=_cmd_inspect)

    rate = sub.add_parser(
        "rate",
        help="Kick off org-wide usage rating/billing orchestration (~15 min, one-shot).",
    )
    rate.add_argument("--org", required=True,
                      help="Target org: sf CLI alias or username.")
    rate.add_argument("--flow-name", default="RLM_OrchestrateUsageManagement",
                      help="Autolaunched flow API name (default: RLM_OrchestrateUsageManagement).")
    rate.set_defaults(func=_cmd_rate)

    step = sub.add_parser("step", help="Run steps from a manifest to a target stage.")
    add_connection_args(step)
    add_resume_args(step)
    step.add_argument("--manifest", required=True, help="Run id or manifest path.")
    step.add_argument("--to-stage", required=True, choices=STAGES_QUOTE,
                      help="Run remaining steps through this stage.")
    step.add_argument("--application-level", choices=["line", "header"],
                      help="--to-stage payment_applied only: set the "
                           "application level when it could not be read or was read "
                           "wrong. A value equal to the recorded level is ignored; a "
                           "different one is refused once the payment is planned, and "
                           "the flag is refused when the manifest already reached "
                           "--to-stage.")
    step.set_defaults(func=_cmd_step)

    report = sub.add_parser("report", help="Rebuild a batch report from on-disk manifests.")
    report.add_argument("base_run_id", help="Batch base run id (e.g. DEMO-...).")
    report.add_argument("--markdown", action="store_true",
                        help="Print markdown instead of JSON.")
    report.set_defaults(func=_cmd_report)

    verify = sub.add_parser(
        "verify",
        allow_abbrev=False,
        help="Read-only billing checks on invoices and payments "
             "(exit 1 on a failed check, 2 on bad input).",
    )
    add_connection_args(verify)
    verify.add_argument("--manifest", action="append",
                        help="Run id or manifest path (repeatable); reads its "
                             "invoice_id(s) and payment_id(s) (the settlement "
                             "stage payment_applied writes payment_ids).")
    verify.add_argument("--latest", action="store_true",
                        help="Add the ids of the newest manifest only.")
    verify.add_argument("--invoice-ids", action="append",
                        help="Invoice ids, comma- or space-separated (repeatable).")
    verify.add_argument("--payment-ids", action="append",
                        help="Extra payment ids to check, such as one with no "
                             "applications (repeatable).")
    verify.add_argument("--expect-level", choices=["auto", "line", "header"],
                        default="auto",
                        help="Application level to expect (default: detect from the "
                             "records).")
    verify.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    verify.set_defaults(func=_cmd_verify)
    # The top-level parser has no options but -h, so its first token is the command.
    _json_usage_errors([parser, verify], tokens[:1] == ["verify"] and "--json" in tokens)

    q2c = sub.add_parser(
        "quote-to-cash",
        help="Run a quote to an applied payment on one account, then verify the "
             "balances (writes records; exit 1 on a short stage or failed check).",
    )
    add_connection_args(q2c)
    q2c.add_argument("--config", type=Path, default=QUOTE_TO_CASH_CONFIG,
                     help="Scenario config whose scenarios target payment_applied "
                          "(default: scenarios/sales_txn_quote/20-quote-to-cash.yaml).")
    q2c.add_argument("--poll-timeout", type=int, default=180,
                     help="Async poll timeout in seconds (default: 180).")
    q2c.add_argument("-v", "--verbose", action="count", default=0,
                     help="-v for INFO, -vv for DEBUG.")
    q2c.set_defaults(func=_cmd_quote_to_cash)

    prune = sub.add_parser("prune", help="Delete old manifests by retention age.")
    prune.add_argument("--older-than", required=True,
                       help="Retention window, e.g. 7d / 24h / 30m.")
    prune.add_argument("--yes", action="store_true",
                       help="Actually delete (default is a dry run).")
    prune.set_defaults(func=_cmd_prune)
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    try:
        return args.func(args)
    except (ConfigError, DiscoveryError, LifecycleError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
