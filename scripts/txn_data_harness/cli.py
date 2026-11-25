"""Subcommand CLI for composable Transaction Data Harness operations."""

from __future__ import annotations

import argparse
import json
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
from .config import ConfigError, load_scenarios
from .discovery import DiscoveryError, discover, resolve_account, resolve_product
from .lifecycle import LifecycleError
from .manifests import (
    MANIFEST_DIR,
    list_manifests,
    load_manifest,
    parse_retention,
    prune_old_runs,
    resolve_manifest_path,
    summarize_manifest,
    write_manifest,
)
from .handlers import SCENARIO_HANDLERS
from .models import STAGES_QUOTE, LineItem
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
    account_name = args.account or manifest.account_name
    if not account_name:
        raise DiscoveryError(
            "step requires --account when the manifest has no account_name"
        )
    account = resolve_account(client, account_name)
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
    if not steps:
        print(json.dumps(summarize_manifest(manifest), indent=2))
        return 0

    step_ctx = _build_step_context(
        args, handler, client, ctx, account, manifest
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
            write_manifest(manifest)
    except LifecycleError as exc:
        manifest.error = str(exc)
        write_manifest(manifest)
        raise
    print(json.dumps(summarize_manifest(manifest), indent=2))
    return 0


def _build_step_context(
    args: argparse.Namespace,
    handler,
    client: SfRestClient,
    ctx,
    account,
    manifest,
) -> StepContext:
    """Build the per-kind StepContext for a ``cli step`` invocation.

    PST resumes need the LineItem set: either rebuilt from the manifest (if
    a prior stage already serialized lines) or freshly drawn from a config
    file passed via ``--config``. Ingestion resumes don't need lines from
    config -- the InvoiceLine records persist on the Invoice itself, so
    ``ingest_invoice`` is already done by the time we hit ``promote_to_posted``
    and the remaining step (post the existing Draft) only needs the invoice id.
    """
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
    if not lines and args.to_stage not in {"invoice_draft", "invoice_posted"}:
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
    )


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
        records = billing_verify.fetch_billing_records(client, invoice_ids, payment_ids)
        report = billing_verify.run_checks(records, args.expect_level)
    except Exception as exc:  # noqa: BLE001 - read-only command: any error is exit 2
        # Exit 1 means a check failed, so no error may reach main() (which maps
        # ValueError to 1) or escape as a traceback.
        if isinstance(exc, billing_verify.VerifyError):
            message = str(exc)
        elif isinstance(exc, (SfApiError, SfCliError, requests.RequestException)):
            # RequestException: the --api-version latest lookup.
            message = f"Salesforce request failed: {exc}"
        elif isinstance(exc, FileNotFoundError) and exc.filename == "sf":
            message = "the sf CLI was not found on PATH"
        elif isinstance(exc, OSError):
            message = f"could not run a command or read a file: {exc}"
        else:
            message = f"unexpected {type(exc).__name__}: {exc}"
        print(f"ERROR: {message}", file=sys.stderr)
        if args.json:
            print(json.dumps({"ok": False, "error": message}, indent=2))
        return 2
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(billing_verify.render_text(report))
    return 0 if report["ok"] else 1


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
                print(json.dumps({"ok": False, "error": f"usage: {message}"}, indent=2))
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
                             "invoice_id(s), and payment_id(s) if it has them "
                             "(harness stages write none).")
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
