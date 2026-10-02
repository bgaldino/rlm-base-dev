#!/usr/bin/env python3
"""
UX assembly and drift tooling, runnable without CumulusCI.

Assembles feature-conditional UX metadata from ``templates/`` into
``unpackaged/post_ux/``, deploys it, and captures/applies drift between a live
org and the templates. Orgs are addressed by their **sf CLI** alias or
username (``--target-org``), never by a CCI alias.

Commands:
    flags          print the resolved UX feature flags
    assemble       templates/ → unpackaged/post_ux/ (optionally --deploy)
    deploy         sf project deploy start the assembled output
    retrieve       org flexipages → unpackaged/post_ux/flexipages/
    diff           org state in unpackaged/post_ux/ vs. templates → drift_report.json
    writeback      reverse-apply patches: org state → templates/ (dry run unless --apply)
    capture-drift  retrieve, then diff
    apply-drift    writeback --apply, diff the org state against the new templates,
                   then reassemble the output (no deploy)

Feature flags default to ``project.custom`` in cumulusci.yml. Layer on top:
    --flags-from-manifest [PATH]   flags recorded by the last assembly
                                   (default unpackaged/post_ux/assembly_manifest.json)
    --flag NAME=true|false         runtime override (repeatable; wins over both)

Relative paths are resolved against the repository root.

Examples:
    python scripts/ux/ux_tool.py assemble
    python scripts/ux/ux_tool.py assemble --deploy --target-org my-scratch
    python scripts/ux/ux_tool.py capture-drift --target-org my-scratch
    python scripts/ux/ux_tool.py writeback                 # dry run
    python scripts/ux/ux_tool.py apply-drift
    python scripts/ux/ux_tool.py diff --flag billing_ui=false --fail-on-drift
"""
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.ux._assemble import UxAssembler, VALID_TYPES  # noqa: E402
from scripts.ux._context import UxContext, UxError  # noqa: E402
from scripts.ux._deploy import deploy  # noqa: E402
from scripts.ux._diff import UxDiff, drift_count  # noqa: E402
from scripts.ux._flags import parse_flag_overrides, resolve_features  # noqa: E402
from scripts.ux._retrieve import UxRetriever  # noqa: E402
from scripts.ux._writeback import WRITEBACK_TYPES, UxWriteback  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = "unpackaged/post_ux"
MANIFEST_NAME = "assembly_manifest.json"

#: Exit code when --fail-on-drift is set and drift is found.
EXIT_DRIFT = 1
#: Exit code for a failed step or invalid option.
EXIT_ERROR = 2


def _build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--repo-root", type=Path, default=REPO_ROOT,
        help="Repository root (default: the checkout containing this script).",
    )
    common.add_argument(
        "--flag", action="append", default=[], metavar="NAME=VALUE",
        help="Override a UX feature flag, e.g. --flag billing_ui=false (repeatable).",
    )
    common.add_argument(
        "--flags-from-manifest", nargs="?", const="", default=None, metavar="PATH",
        help=(
            "Use the flags recorded in an assembly manifest "
            f"(default <output-path>/{MANIFEST_NAME}); --flag still wins."
        ),
    )
    common.add_argument("-v", "--verbose", action="store_true", help="Debug logging.")

    parser = argparse.ArgumentParser(
        prog="ux_tool.py",
        description=__doc__.split("\n\n")[0].strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Run '<command> --help' for command options.",
    )
    sub = parser.add_subparsers(dest="command", required=True, metavar="<command>")

    def add(name: str, help_text: str) -> argparse.ArgumentParser:
        return sub.add_parser(name, parents=[common], help=help_text, description=help_text)

    def output_arg(p: argparse.ArgumentParser, help_text: str) -> None:
        p.add_argument("--output-path", default=DEFAULT_OUTPUT, help=f"{help_text} (default {DEFAULT_OUTPUT}).")

    def org_arg(p: argparse.ArgumentParser, required: bool) -> None:
        p.add_argument(
            "--target-org", "-o", required=required,
            help="sf CLI alias or username of the org (not a CCI alias).",
        )

    def name_arg(p: argparse.ArgumentParser, help_text: str) -> None:
        p.add_argument("--name", dest="metadata_name", help=help_text)

    def diff_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--report-file", help="Drift report path (default <output-path>/drift_report.json).")
        p.add_argument("--fail-on-drift", action="store_true", help=f"Exit {EXIT_DRIFT} when drift is found.")

    add("flags", "Print the resolved UX feature flags as JSON.")

    p = add("assemble", "Assemble UX metadata from templates/.")
    p.add_argument("--type", dest="metadata_type", default="all", choices=sorted(VALID_TYPES))
    name_arg(p, "One item by full source filename, e.g. RLM_Quote_Record_Page.flexipage-meta.xml.")
    output_arg(p, "Output directory")
    p.add_argument("--deploy", action="store_true", help="Deploy the output afterwards (needs --target-org).")
    org_arg(p, required=False)

    p = add("deploy", "Deploy already-assembled output with sf project deploy start.")
    output_arg(p, "Directory to deploy")
    org_arg(p, required=True)

    p = add("retrieve", "Retrieve live flexipages from an org into the output directory.")
    name_arg(p, "One flexipage, e.g. RLM_Order_Record_Page.flexipage-meta.xml.")
    output_arg(p, "Destination directory")
    org_arg(p, required=True)

    p = add("diff", "Diff org state in the output directory against current templates.")
    name_arg(p, "One flexipage to diff.")
    output_arg(p, "Directory holding the org state")
    diff_args(p)

    p = add("writeback", "Reverse-apply patches to write org state back into templates/ (dry run by default).")
    name_arg(p, "One flexipage to write back.")
    p.add_argument(
        "--type", dest="metadata_type", default="flexipages", choices=list(WRITEBACK_TYPES),
        help="Default flexipages: retrieve fetches only flexipages, so layout writeback "
        "needs org layouts placed in <output-path>/layouts by hand.",
    )
    output_arg(p, "Directory holding the org state")
    p.add_argument("--apply", action="store_true", help="Write templates/ (default is a dry run).")
    p.add_argument("--no-backup", action="store_true", help="Do not keep *.bak copies of overwritten templates.")

    p = add("capture-drift", "Retrieve flexipages from an org, then diff them against templates/.")
    output_arg(p, "Directory for the org state")
    org_arg(p, required=True)
    diff_args(p)

    p = add(
        "apply-drift",
        "Write org state back into templates/, report any drift that remains, "
        "then reassemble the output (no deploy).",
    )
    output_arg(p, "Directory holding the org state")
    p.add_argument("--no-backup", action="store_true", help="Do not keep *.bak copies of overwritten templates.")
    diff_args(p)

    return parser


def _resolve(repo_root: Path, value) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def _make_context(args, logger: logging.Logger) -> UxContext:
    repo_root = Path(args.repo_root).resolve()
    manifest = None
    if args.flags_from_manifest is not None:
        manifest = (
            _resolve(repo_root, args.flags_from_manifest)
            if args.flags_from_manifest
            else _resolve(repo_root, getattr(args, "output_path", DEFAULT_OUTPUT)) / MANIFEST_NAME
        )
    features, api_version = resolve_features(
        repo_root, parse_flag_overrides(args.flag), manifest_path=manifest,
    )
    return UxContext(repo_root=repo_root, features=features, api_version=api_version, logger=logger)


def _run_diff(ctx: UxContext, args, output_path: Path, metadata_name: Optional[str] = None) -> int:
    report_file = _resolve(ctx.repo_root, args.report_file) if args.report_file else None
    report = UxDiff(ctx).run(output_path, metadata_name=metadata_name, report_file=report_file)
    if args.fail_on_drift and drift_count(report):
        return EXIT_DRIFT
    return 0


def _run(args, logger: logging.Logger) -> int:
    ctx = _make_context(args, logger)

    if args.command == "flags":
        print(json.dumps(ctx.features, indent=2))
        return 0

    output_path = _resolve(ctx.repo_root, args.output_path)

    if args.command == "assemble":
        if args.deploy and not args.target_org:
            raise UxError("--deploy needs --target-org <sf alias or username>.")
        manifest = UxAssembler(ctx).run(output_path, args.metadata_type, args.metadata_name)
        if args.deploy:
            if not manifest["assembled"]:
                logger.warning("No items assembled — skipping deploy")
                return 0
            deploy(output_path, args.target_org, logger, cwd=ctx.repo_root)
        return 0

    if args.command == "deploy":
        deploy(output_path, args.target_org, logger, cwd=ctx.repo_root)
        return 0

    if args.command == "retrieve":
        UxRetriever(ctx, args.target_org).run(output_path, args.metadata_name)
        return 0

    if args.command == "diff":
        return _run_diff(ctx, args, output_path, args.metadata_name)

    if args.command == "writeback":
        UxWriteback(ctx).run(
            output_path,
            metadata_name=args.metadata_name,
            metadata_type=args.metadata_type,
            dry_run=not args.apply,
            backup=not args.no_backup,
        )
        return 0

    if args.command == "capture-drift":
        UxRetriever(ctx, args.target_org).run(output_path)
        return _run_diff(ctx, args, output_path)

    if args.command == "apply-drift":
        # Flexipages only: retrieve never fetches layouts, so layouts in
        # output_path are assembled output, and writing them back would overwrite
        # the feature layout templates with the base versions.
        UxWriteback(ctx).run(output_path, dry_run=False, backup=not args.no_backup)
        # Diff before reassembling: assembly overwrites the org state in
        # output_path, after which a diff would only compare templates to themselves.
        rc = _run_diff(ctx, args, output_path)
        UxAssembler(ctx).run(output_path)
        return rc

    raise UxError(f"Unknown command: {args.command}")


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s",
    )
    logger = logging.getLogger("rlm_ux")
    try:
        return _run(args, logger)
    except UxError as exc:
        logger.error(f"ERROR: {exc}")
        return EXIT_ERROR


if __name__ == "__main__":
    sys.exit(main())
