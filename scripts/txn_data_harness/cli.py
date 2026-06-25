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

from . import generate
from .auth import DEFAULT_API_VERSION, SfRestClient
from .config import ConfigError, load_scenarios
from .discovery import DiscoveryError, discover, resolve_account, resolve_product
from .lifecycle import LifecycleError
from .manifests import (
    MANIFEST_DIR,
    list_manifests,
    load_manifest,
    parse_retention,
    prune_old_runs,
    summarize_manifest,
    write_manifest,
)
from .handlers import SCENARIO_HANDLERS
from .models import STAGES, LineItem
from .report import build_batch_report, render_markdown
from .runner import DEFAULT_MAX_RETRIES, draw_lines
from .steps import StepContext, execute_step


def _add_run_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--org", required=True,
                   help="Target org: sf CLI alias or username (NOT a CCI alias).")
    p.add_argument("--config", help="YAML/JSON config file (all fields optional).")
    p.add_argument("--count", type=int, help="Number of transactions to generate.")
    p.add_argument("--target-stage", choices=STAGES,
                   help="How far through the lifecycle to run.")
    p.add_argument("--account", help="Pin the account by Name.")
    p.add_argument("--product", help="Pin the product by SKU.")
    p.add_argument("--with-opportunity", action="store_true",
                   help="Prepend an Opportunity the quote links to.")
    p.add_argument("--opportunity-stage", help="Pin the Opportunity StageName.")
    p.add_argument("--concurrency", type=int, default=4,
                   help="Parallel scenario workers (default: 4).")
    p.add_argument("--poll-timeout", type=int, default=180,
                   help="Async poll timeout in seconds (default: 180).")
    p.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES,
                   help=f"Retries for transient scenario failures "
                        f"(default: {DEFAULT_MAX_RETRIES}; 0 disables).")
    p.add_argument("--api-version", default=DEFAULT_API_VERSION,
                   help=f"API version (default: {DEFAULT_API_VERSION}; 'latest' to query).")
    p.add_argument("--transport", choices=["requests", "cli"], default="requests",
                   help="REST transport (default: requests; cli = sf api proxy).")
    p.add_argument("--no-probe", action="store_true",
                   help="Reserved for future PST probes; currently no-op.")
    p.add_argument("--keep-probes", action="store_true",
                   help="Reserved for future PST probes; currently no-op.")
    p.add_argument("-v", "--verbose", action="count", default=0,
                   help="-v for INFO, -vv for DEBUG.")


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
    # --json is the explicit machine-readable flag, but since summarize_manifest
    # already returns a plain dict the default print is already JSON. Keep the
    # flag for forward compatibility (a future human-readable default).
    print(json.dumps(summarize_manifest(manifest), indent=2))
    return 0


def _lines_from_manifest(client: SfRestClient, manifest) -> list[LineItem]:
    """Rebuild ``LineItem``s from a manifest, including any resolved usage spec.

    ``LineItem.to_manifest_record`` writes the resolved usage targets (with
    UsageResource + UoM ids) so we don't need a second discovery pass for the
    common case of resuming an ``activate`` run to ``usage``.
    """
    lines: list[LineItem] = []
    for rec in manifest.lines:
        sku = rec.get("sku")
        if not sku:
            continue
        lines.append(
            LineItem.from_manifest_record(rec, resolve_product(client, sku))
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
            manifest = execute_step(step, step_ctx, manifest)
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

    # PST path
    try:
        specs = load_scenarios(args)
        resolved = [handler.resolve(client, ctx, s) for s in specs]
        default_lines = draw_lines(resolved[0].options) if resolved else []
    except ConfigError:
        default_lines = []
    lines = _lines_from_manifest(client, manifest) or default_lines
    if not lines and args.to_stage not in {"invoice", "post"}:
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


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="python -m scripts.txn_data_harness.cli",
        description="Composable commands for Transaction Data Harness workflows.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    plan = sub.add_parser("plan", help="Resolve config/discovery and print the plan.")
    _add_run_args(plan)
    plan.set_defaults(func=_cmd_plan)

    run = sub.add_parser("run", help="Run the existing end-to-end generator.")
    _add_run_args(run)
    run.set_defaults(func=_cmd_run)

    inspect = sub.add_parser("inspect", help="Inspect a manifest by id/path.")
    group = inspect.add_mutually_exclusive_group(required=True)
    group.add_argument("--manifest", help="Run id or manifest path.")
    group.add_argument("--latest", action="store_true", help="Inspect the newest manifest.")
    inspect.add_argument("--json", action="store_true",
                         help="Print JSON (current default; reserved for forward use).")
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
    _add_run_args(step)
    step.add_argument("--manifest", required=True, help="Run id or manifest path.")
    step.add_argument("--to-stage", required=True, choices=STAGES,
                      help="Run remaining steps through this stage.")
    step.set_defaults(func=_cmd_step)

    report = sub.add_parser("report", help="Rebuild a batch report from on-disk manifests.")
    report.add_argument("base_run_id", help="Batch base run id (e.g. DEMO-...).")
    report.add_argument("--markdown", action="store_true",
                        help="Print markdown instead of JSON.")
    report.set_defaults(func=_cmd_report)

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
