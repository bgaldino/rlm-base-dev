#!/usr/bin/env python3
"""Snapshot public Salesforce documentation into markdown for AI grounding.

Subcommands:

    list        show the presets in presets.yaml
    help        snapshot help.salesforce.com areas (and release notes)
    dev-guide   snapshot developer.salesforce.com atlas developer guides
    run         snapshot every preset of a release
    check       lint the captured Help corpus for glued-link artifacts
    backfill-attribution
                offline: add the source-attribution footer to captured articles lacking it
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

# Override flags per subcommand: each argparse dest is the snapshotter option
# of the same name, so these derive from the preset schema. `--area` selects
# presets rather than overriding one; `--release-name` overrides the release
# block's name. A flag left unset is None and never overrides the preset.
HELP_FLAGS = sorted(
    presets_mod.PRESET_OPTIONS["help"] - {"area"} | {"release_name"} | presets_mod.CLI_ONLY_OPTIONS
)
DEV_GUIDE_FLAGS = sorted(
    presets_mod.PRESET_OPTIONS["dev_guide"] | {"release_name"} | presets_mod.CLI_ONLY_OPTIONS
    | presets_mod.DEV_GUIDE_CLI_ONLY
)
RUN_FLAGS = sorted(
    presets_mod.SHARED_OPTIONS - {"output_dir"} | presets_mod.CLI_ONLY_OPTIONS
    | presets_mod.DEV_GUIDE_CLI_ONLY
)
# Flags that describe one specific target, meaningless across several presets:
# argparse dest -> the flag as the user types it.
SINGLE_TARGET_FLAGS = {
    "root_article_id": "--root-article-id",
    "article_id_prefix": "--prefix",
    "output_dir": "--output-dir",
    "deliverable": "--deliverable",
    "site_url": "--site-url",
    "api_version": "--api-version",
    "probe_page": "--probe-page",
    "sections": "--section",
}


def _snapshot_class(kind: str):
    if kind == "help":
        from scripts.doc_snapshot.help_portal import HelpSnapshot
        return HelpSnapshot
    from scripts.doc_snapshot.dev_guide import DevGuideSnapshot
    return DevGuideSnapshot


def _class_for(kind: str, options: Dict[str, Any]):
    """The snapshotter for a resolved preset: a ``source: site`` dev guide is read
    over HTTP by ``site_guide``; every other preset keeps its ``_snapshot_class``."""
    if kind == "dev_guide" and presets_mod.dev_guide_source(options) == "site":
        from scripts.doc_snapshot.site_guide import SiteGuideSnapshot
        return SiteGuideSnapshot
    return _snapshot_class(kind)


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def _id_list(value: str) -> List[str]:
    """Parse ``ID[,ID...]``; an empty list must not read as "accept nothing"."""
    ids = [part.strip() for part in value.split(",") if part.strip()]
    if not ids:
        raise argparse.ArgumentTypeError("needs at least one page or article id")
    return ids


def _add_common_run_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--mode", choices=VALID_MODES,
                   help="discover | capture | all | refresh (default all)")
    p.add_argument("--headless", metavar="BOOL",
                   help="true|false: run Chromium without a window (default true)")
    p.add_argument("--concurrency", type=int, help="parallel fetches")
    p.add_argument("--wait-ms", dest="wait_ms", type=int,
                   help="ms to wait after each navigation")
    p.add_argument("--accept-shrinkage", dest="accept_shrinkage", type=_id_list,
                   metavar="ID[,ID...]",
                   help="write these pages even when the capture kept under 50%% of "
                        "the prior text's characters and under 60%% of its words (a "
                        "real upstream cut you have checked); named pages only, and "
                        "a not-found page is never written")


def _add_site_switch_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--accept-uncovered", dest="accept_uncovered", type=_id_list,
                   metavar="ID[,ID...]",
                   help="atlas page ids (with .htm) a sectioned atlas-to-site switch may leave on "
                        "atlas because the site's section has no page replacing them; any other "
                        "captured atlas page without a replacement refuses the switch")


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
    p.add_argument("--source", choices=presets_mod.SOURCES,
                   help="atlas (default) or site: a server-rendered guide read over HTTP")
    p.add_argument("--site-url", dest="site_url",
                   help="source=site: any page of the guide, e.g. "
                        "https://developer.salesforce.com/docs/revenue/revenue-management/guide/rlm-get-started.html")
    p.add_argument("--api-version", dest="api_version",
                   help="source=site: the API version the release serves, e.g. 68.0; "
                        "a capture refuses when the site shows another")
    p.add_argument("--probe-page", dest="probe_page",
                   help="source=site: slug of a page that shows /services/data/vNN.0, "
                        "fetched only when the captured pages show no API version")
    p.add_argument("--section", dest="sections", action="append", metavar="SECTION",
                   help="TOC section title or page_id; repeat for several "
                        "(replaces the preset's sections)")
    p.add_argument("--output-dir", dest="output_dir",
                   help="relative paths resolve from the repo root")
    _add_common_run_flags(p)
    p.add_argument("--batch-delay-ms", dest="batch_delay_ms", type=int)
    p.add_argument("--follow-links", dest="follow_links", metavar="BOOL")
    p.add_argument("--max-pages", dest="max_pages", type=int)
    _add_site_switch_flags(p)

    p = sub.add_parser("run", help="snapshot every preset of a release")
    p.add_argument("--release", required=True)
    p.add_argument("--only", help="comma-separated preset keys to include "
                                  "(matched across help and dev_guide presets)")
    _add_common_run_flags(p)
    _add_site_switch_flags(p)

    p = sub.add_parser("check", help="lint the Help corpus for glued-link artifacts")
    p.add_argument("--release", help="only this release's corpus")

    p = sub.add_parser("backfill-attribution",
                       help="offline: add the attribution footer to captured articles lacking it")
    p.add_argument("--release", required=True, help="release version, e.g. 264")

    p = sub.add_parser("bootstrap", help="add a release to presets.yaml")
    p.add_argument("--from", dest="source", required=True, help="release to copy")
    p.add_argument("--to", dest="target", required=True, help="new release version")
    p.add_argument("--release-name", dest="release_name", required=True)
    p.add_argument("--dry-run", action="store_true", help="print the block; write nothing")
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
    multi = len(targets) > 1
    if multi:
        conflicting = [flag for dest, flag in SINGLE_TARGET_FLAGS.items()
                       if overrides.get(dest) is not None]
        if conflicting:
            flags = ", ".join(conflicting)
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
        snapshot = _class_for(kind, options)(options, logger=logger)
        snapshot.preflight()
        planned.append((f"{release} {kind}.{key}", snapshot))

    # (label, error or None, stats)
    results: List[Tuple[str, Optional[str], Dict[str, Any]]] = []
    try:
        for label, snapshot in planned:
            logger.info(f"=== {label} ===")
            try:
                results.append((label, None, snapshot.run() or {}))
            except (SnapshotError, OSError) as exc:
                # Includes an OptionsError raised mid-run (a doc_version conflict, a
                # renamed section): earlier targets already ran, so record it and
                # carry on. Selector errors were raised while planning, above.
                if not multi:
                    raise
                logger.error(f"{label} failed: {exc}")
                results.append((label, str(exc), {}))
    finally:
        _warn_unused_accepts(overrides.get("accept_shrinkage"),
                             (s for _, s in planned), logger)

    failed = sum(1 for _, error, _ in results if error is not None)
    if multi:
        _print_summary(results, failed)
    return EXIT_FAILED if failed else 0


def _warn_unused_accepts(requested, snapshots, logger) -> None:
    """Warn about ``--accept-shrinkage`` ids no capture used (a typo, a moved id,
    or a page that did not shrink). The exit code is unchanged."""
    if not requested:
        return
    used = {i for s in snapshots for i in getattr(s, "accepted", ())}
    unused = sorted(set(requested) - used)
    if unused:
        logger.warning(
            "--accept-shrinkage: no capture shrank past the guard's threshold for "
            f"{', '.join(unused)} in this run, so nothing was accepted for "
            "them (check the id, or the run may have stopped before reaching the page)"
        )


def _print_summary(results, failed: int) -> None:
    print("\nSummary")
    width = max(len(label) for label, _, _ in results)
    for label, error, stats in results:
        if error is None:
            status = "ok"
            detail = (f"discovered {stats.get('discovered', '?')}, "
                      f"captured {stats.get('captured', '?')}, "
                      f"errored {stats.get('errored', '?')}")
        else:
            status, detail = "FAILED", error
        print(f"  {label.ljust(width)}  {status:<6}  {detail}")
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
            if preset.get("source") == "site":
                target = preset.get("site_url", "")
                note = f"site, API {preset.get('api_version', '?')}"
            else:
                target = preset.get("deliverable", "(default)")
                note = f"doc {preset['doc_version']}" if preset.get("doc_version") else ""
        rows.append((release, kind, key, target, note))
    if not rows:
        print(f"No presets{' for release ' + args.release if args.release else ''}.")
        return 0
    widths = [max(len(str(r[i])) for r in rows) for i in range(4)] + [0]
    for r in rows:
        print("  ".join(str(c).ljust(w) for c, w in zip(r, widths)).rstrip())
    return 0


def cmd_help(args, releases, logger) -> int:
    overrides = _pick(args, HELP_FLAGS)
    keys = _expand(releases, args.release, "help", args.area)
    return run_targets(releases, [(args.release, "help", k) for k in keys], overrides, logger)


def cmd_dev_guide(args, releases, logger) -> int:
    overrides = _pick(args, DEV_GUIDE_FLAGS)
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


def cmd_backfill_attribution(args, releases, logger) -> int:
    from scripts.doc_snapshot._core import backfill_attribution
    from scripts.doc_snapshot.check import REPO_ROOT
    base = REPO_ROOT / "docs" / "salesforce" / args.release
    total, failed = 0, 0
    for articles in sorted(base.glob("*/articles")):
        changed, skipped = backfill_attribution(articles)
        total += len(changed)
        if changed:
            print(f"{articles.relative_to(REPO_ROOT)}: added the footer to {len(changed)} file(s)")
        for name, reason in skipped:
            print(f"  skipped {articles.relative_to(REPO_ROOT)}/{name}: {reason}")
            # no frontmatter or source_url: nothing to build a footer from, not a failure
            failed += not reason.startswith("no-")
    print(f"Release {args.release}: {total} article(s) updated.")
    return EXIT_FAILED if failed else 0


def cmd_bootstrap(args, releases, logger) -> int:
    path = args.presets or presets_mod.PRESETS_PATH
    block = presets_mod.bootstrap_block(
        releases, args.source, args.target, args.release_name
    )
    if args.dry_run:
        print(block)
        return 0
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(block)
    print(f"Added release {args.target} to {path}")
    print("Before capturing dev guides, set `doc_version` on the new release's dev_guide presets: "
          "without it the unversioned endpoint serves the previous release.")
    print(f"Next: `help --release {args.target} --area all --mode discover`, "
          "then set expect_min_articles floors from the counts.")
    return 0


COMMANDS = {
    "list": cmd_list,
    "help": cmd_help,
    "dev-guide": cmd_dev_guide,
    "run": cmd_run,
    "check": cmd_check,
    "backfill-attribution": cmd_backfill_attribution,
    "bootstrap": cmd_bootstrap,
}


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = get_logger()
    try:
        # `check` reads the corpus, not the presets, so it needs no PyYAML.
        releases = {} if args.command in ("check", "backfill-attribution") else presets_mod.load_presets(args.presets)
        return COMMANDS[args.command](args, releases, logger)
    except OptionsError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE
    except (SnapshotError, OSError) as exc:
        # OSError: an unwritable --output-dir, a full disk, a failed bootstrap
        # append. A runtime failure (exit 1), as in a multi-target run.
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_FAILED


if __name__ == "__main__":
    sys.exit(main())
