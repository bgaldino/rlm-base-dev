#!/usr/bin/env python3
"""Snapshot public Salesforce documentation into markdown for AI grounding.

Subcommands:

    list        show the presets in presets.yaml
    help        snapshot help.salesforce.com areas (and release notes)
    dev-guide   snapshot developer.salesforce.com atlas developer guides
    run         snapshot every preset of a release
    check       lint the captured Help corpus for glued-link artifacts
    bootstrap   add a release to presets.yaml by copying another one

Examples:

    python -m scripts.doc_snapshot list --release 264
    python -m scripts.doc_snapshot help --release 264 --area pricing --mode discover
    python -m scripts.doc_snapshot help --release 264 --area all
    python -m scripts.doc_snapshot help --release 266 --release-name "Spring '27" \\
        --area foo --root-article-id ind.foo.htm --prefix ind.foo
    python -m scripts.doc_snapshot dev-guide --release 264 --guide industries
    python -m scripts.doc_snapshot run --release 264 --only pcm,rlm
    python -m scripts.doc_snapshot check --release 264
    python -m scripts.doc_snapshot bootstrap --from 264 --to 266 \\
        --release-name "Spring '27" --dry-run

No Salesforce org or CumulusCI is involved. See scripts/doc_snapshot/README.md.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if __package__ in (None, ""):
    # Direct `python scripts/doc_snapshot/cli.py` run: make the repo importable.
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.doc_snapshot import presets as presets_mod  # noqa: E402
from scripts.doc_snapshot._core import (  # noqa: E402
    VALID_MODES,
    OptionsError,
    SnapshotError,
    get_logger,
)

EXIT_FAILED = 1
EXIT_USAGE = 2

# CLI dest -> snapshotter option name, per kind. A flag left unset is None and
# never overrides the preset.
HELP_FLAGS = (
    "release_name", "root_article_id", "article_id_prefix", "output_dir", "mode",
    "headless", "concurrency", "wait_ms", "discover_timeout_ms",
    "expect_min_articles", "include_release_param", "subtree_only",
)
DEV_GUIDE_FLAGS = (
    "release_name", "deliverable", "doc_version", "section", "sections",
    "output_dir", "mode", "headless", "concurrency", "wait_ms", "batch_delay_ms",
    "follow_links", "max_pages",
)
# Flags that describe one specific target; meaningless across several presets.
SINGLE_TARGET_FLAGS = (
    "root_article_id", "article_id_prefix", "output_dir", "deliverable",
    "section", "sections",
)
RUN_FLAGS = ("mode", "headless", "concurrency", "wait_ms")


def _snapshot_class(kind: str):
    if kind == "help":
        from scripts.doc_snapshot.help_portal import HelpSnapshot
        return HelpSnapshot
    from scripts.doc_snapshot.dev_guide import DevGuideSnapshot
    return DevGuideSnapshot


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def _add_common_run_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--mode", choices=VALID_MODES,
                   help="discover | capture | all | refresh (default all)")
    p.add_argument("--headless", metavar="BOOL",
                   help="true|false: run Chromium without a window (default true)")
    p.add_argument("--concurrency", type=int, help="parallel fetches")
    p.add_argument("--wait-ms", dest="wait_ms", type=int,
                   help="ms to wait after each navigation")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m scripts.doc_snapshot",
        description=__doc__.split("\n\n")[0],
        epilog="Output goes to docs/salesforce/{release}/ by default; presets live in "
               "scripts/doc_snapshot/presets.yaml. Run `<subcommand> --help` for its "
               "flags, and see scripts/doc_snapshot/README.md.",
    )
    parser.add_argument("--presets", type=Path, help="alternate presets.yaml (testing)")
    sub = parser.add_subparsers(dest="command", required=True, metavar="SUBCOMMAND")

    p = sub.add_parser("list", help="show presets")
    p.add_argument("--release", help="only this release")

    p = sub.add_parser("help", help="snapshot Help portal areas")
    p.add_argument("--release", required=True, help="release version, e.g. 264")
    p.add_argument("--area", required=True,
                   help="preset key, comma-separated keys, or 'all'; any name for an "
                        "ad hoc run with --root-article-id and --prefix (plus "
                        "--release-name for a release not in presets.yaml)")
    p.add_argument("--release-name", dest="release_name",
                   help="e.g. \"Winter '27\" (default: from presets)")
    p.add_argument("--root-article-id", dest="root_article_id")
    p.add_argument("--prefix", "--article-id-prefix", dest="article_id_prefix")
    p.add_argument("--output-dir", dest="output_dir",
                   help="relative paths resolve from the repo root")
    _add_common_run_flags(p)
    p.add_argument("--discover-timeout-ms", dest="discover_timeout_ms", type=int)
    p.add_argument("--expect-min-articles", dest="expect_min_articles", type=int,
                   help="fail discovery when fewer articles are found")
    p.add_argument("--include-release-param", dest="include_release_param", metavar="BOOL")
    p.add_argument("--subtree-only", dest="subtree_only", metavar="BOOL")

    p = sub.add_parser("dev-guide", help="snapshot atlas developer guides")
    p.add_argument("--release", required=True, help="release version, e.g. 264")
    p.add_argument("--guide", required=True,
                   help="preset key, comma-separated keys, or 'all'; any name for an "
                        "ad hoc run with --deliverable")
    p.add_argument("--release-name", dest="release_name")
    p.add_argument("--deliverable", help="atlas deliverable slug")
    p.add_argument("--doc-version", dest="doc_version",
                   help="atlas doc version, e.g. 264.0; without it the unversioned "
                        "endpoint may still serve the previous release")
    p.add_argument("--section", help="one TOC section (title or page_id)")
    p.add_argument("--sections", help="comma-separated TOC sections (titles or page_ids)")
    p.add_argument("--output-dir", dest="output_dir",
                   help="relative paths resolve from the repo root")
    _add_common_run_flags(p)
    p.add_argument("--batch-delay-ms", dest="batch_delay_ms", type=int)
    p.add_argument("--follow-links", dest="follow_links", metavar="BOOL")
    p.add_argument("--max-pages", dest="max_pages", type=int)

    p = sub.add_parser("run", help="snapshot every preset of a release")
    p.add_argument("--release", required=True)
    p.add_argument("--only", help="comma-separated preset keys to include "
                                  "(matched across help and dev_guide presets)")
    _add_common_run_flags(p)

    p = sub.add_parser("check", help="lint the Help corpus for glued-link artifacts")
    p.add_argument("--release", help="only this release's corpus")

    p = sub.add_parser("bootstrap", help="add a release to presets.yaml")
    p.add_argument("--from", dest="source", required=True, help="release to copy")
    p.add_argument("--to", dest="target", required=True, help="new release version")
    p.add_argument("--release-name", dest="release_name", required=True)
    p.add_argument("--dry-run", action="store_true", help="print the block; write nothing")
    p.add_argument("--discover", action="store_true",
                   help="after writing, run discover mode for every new help preset")
    return parser


# ---------------------------------------------------------------------------
# Running presets
# ---------------------------------------------------------------------------


def _pick(args: argparse.Namespace, names) -> Dict[str, Any]:
    return {n: getattr(args, n, None) for n in names}


def _split_keys(selector: str, flag: str) -> List[str]:
    """Split a comma-separated selector; an explicitly empty one is an error.

    An empty value (an unset shell variable, or only commas) must not be read
    as "no filter": for ``--only`` that would run every preset.
    """
    keys = [k.strip() for k in selector.split(",") if k.strip()]
    if not keys:
        raise OptionsError(f"{flag} needs at least one preset key (see `list`)")
    return keys


def _expand(releases, release: str, kind: str, selector: str) -> List[str]:
    keys = presets_mod.preset_keys(releases, release, kind)
    if selector == "all":
        if not keys:
            raise OptionsError(f"release {release} has no {kind} presets")
        return keys
    return _split_keys(selector, "--area" if kind == "help" else "--guide")


def run_targets(
    releases, targets: List[Tuple[str, str, str]], overrides: Dict[str, Any], logger
) -> int:
    """Run ``(release, kind, key)`` targets; fail-soft when there are several."""
    if len(targets) > 1:
        conflicting = [f for f in SINGLE_TARGET_FLAGS if overrides.get(f) is not None]
        if conflicting:
            flags = ", ".join("--" + f.replace("_", "-") for f in conflicting)
            raise OptionsError(
                f"{flags} applies to a single preset only; {len(targets)} selected"
            )

    # Resolve and validate every target before running any, so a typo in a
    # later key is a usage error (exit 2) and can't follow a partial run.
    # Building a snapshotter only normalizes its options; preflight() then
    # reads (never writes) its manifest for conflicts detectable offline.
    planned = []
    for release, kind, key in targets:
        options = presets_mod.resolve(releases, release, kind, key, overrides)
        snapshot = _snapshot_class(kind)(options, logger=logger)
        snapshot.preflight()
        planned.append((f"{release} {kind}.{key}", snapshot))

    results = []
    for label, snapshot in planned:
        logger.info(f"=== {label} ===")
        try:
            stats = snapshot.run() or {}
            results.append((label, "ok", stats, ""))
        except (SnapshotError, OSError) as exc:
            # Includes an OptionsError raised mid-run (a doc_version conflict, a
            # renamed section): earlier targets already ran, so record it and
            # carry on. Selector errors were raised while planning, above.
            if len(targets) == 1:
                raise
            logger.error(f"{label} failed: {exc}")
            results.append((label, "FAILED", {}, str(exc)))

    if len(targets) > 1:
        _print_summary(results)
    return EXIT_FAILED if any(r[1] != "ok" for r in results) else 0


def _print_summary(results) -> None:
    print("\nSummary")
    width = max(len(r[0]) for r in results)
    for label, status, stats, error in results:
        if status == "ok":
            detail = (f"discovered {stats.get('discovered', '?')}, "
                      f"captured {stats.get('captured', '?')}, "
                      f"errored {stats.get('errored', '?')}")
        else:
            detail = error
        print(f"  {label.ljust(width)}  {status:<6}  {detail}")
    failed = sum(1 for r in results if r[1] != "ok")
    print(f"\n{len(results) - failed}/{len(results)} succeeded.")


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------


def cmd_list(args, releases, logger) -> int:
    rows = []
    for release, kind, key, preset in presets_mod.iter_presets(releases, args.release):
        if kind == "help":
            target = preset.get("root_article_id", "")
            floor = preset.get("expect_min_articles")
            note = f"min {floor}" if floor else ""
        else:
            target = preset.get("deliverable", "(default)")
            note = f"doc {preset['doc_version']}" if preset.get("doc_version") else ""
            if preset.get("sections"):
                note = (note + f" {len(preset['sections'])} sections").strip()
        rows.append((release, kind, key, target, note))
    if not rows:
        print(f"No presets{' for release ' + args.release if args.release else ''}.")
        return 0
    widths = [max(len(str(r[i])) for r in rows) for i in range(4)]
    for r in rows:
        print("  ".join(str(c).ljust(widths[i]) for i, c in enumerate(r[:4])) + "  " + r[4])
    return 0


def cmd_help(args, releases, logger) -> int:
    overrides = _pick(args, HELP_FLAGS)
    keys = _expand(releases, args.release, "help", args.area)
    return run_targets(releases, [(args.release, "help", k) for k in keys], overrides, logger)


def cmd_dev_guide(args, releases, logger) -> int:
    overrides = _pick(args, DEV_GUIDE_FLAGS)
    if args.section and args.sections is None:
        # A one-off --section narrows a preset that lists `sections`, which
        # the snapshotter would otherwise prefer.
        overrides["sections"] = []
    keys = _expand(releases, args.release, "dev_guide", args.guide)
    return run_targets(
        releases, [(args.release, "dev_guide", k) for k in keys], overrides, logger
    )


def cmd_run(args, releases, logger) -> int:
    only = set(_split_keys(args.only, "--only")) if args.only is not None else set()
    available = [
        (rel, kind, key)
        for rel, kind, key, _ in presets_mod.iter_presets(releases, args.release)
    ]
    if not available:
        raise OptionsError(f"release {args.release} has no presets")
    unknown = only - {t[2] for t in available}
    if unknown:
        raise OptionsError(
            f"unknown preset(s) for release {args.release}: {', '.join(sorted(unknown))}"
            " (see `list`)"
        )
    targets = [t for t in available if not only or t[2] in only]
    return run_targets(releases, targets, _pick(args, RUN_FLAGS), logger)


def cmd_check(args, releases, logger) -> int:
    from scripts.doc_snapshot import check
    return check.scan(args.release)


def cmd_bootstrap(args, releases, logger) -> int:
    path = args.presets or presets_mod.PRESETS_PATH
    block = presets_mod.bootstrap_block(
        releases, args.source, args.target, args.release_name
    )
    if args.dry_run:
        print(block)
        return 0
    presets_mod.append_block(block, path)
    print(f"Added release {args.target} to {path}")
    print("Before capturing dev guides, set `doc_version` on the new release's dev_guide presets: "
          "without it the unversioned endpoint serves the previous release.")
    if not args.discover:
        print(f"Next: `help --release {args.target} --area all --mode discover`, "
              "then set expect_min_articles floors from the counts.")
        return 0
    releases = presets_mod.load_presets(path)
    keys = presets_mod.preset_keys(releases, args.target, "help")
    return run_targets(
        releases, [(args.target, "help", k) for k in keys], {"mode": "discover"}, logger
    )


COMMANDS = {
    "list": cmd_list,
    "help": cmd_help,
    "dev-guide": cmd_dev_guide,
    "run": cmd_run,
    "check": cmd_check,
    "bootstrap": cmd_bootstrap,
}


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = get_logger()
    try:
        # `check` reads the corpus, not the presets, so it needs no PyYAML.
        releases = {} if args.command == "check" else presets_mod.load_presets(args.presets)
        return COMMANDS[args.command](args, releases, logger)
    except OptionsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE
    except SnapshotError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_FAILED


if __name__ == "__main__":
    sys.exit(main())
