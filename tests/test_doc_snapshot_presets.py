"""Unit tests for scripts/doc_snapshot presets + CLI wiring (offline, no browser).

Covers preset loading/validation, option precedence (release < preset < CLI),
that every shipped preset builds a valid snapshotter, the bootstrap block
(round-trips through the loader), and argparse wiring for each subcommand.

Run:  python3 tests/test_doc_snapshot_presets.py   (needs PyYAML)
"""

import contextlib
import io
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.doc_snapshot import cli, presets  # noqa: E402
from scripts.doc_snapshot._core import OptionsError  # noqa: E402
from scripts.doc_snapshot.dev_guide import DevGuideSnapshot  # noqa: E402
from scripts.doc_snapshot.help_portal import HelpSnapshot  # noqa: E402

_passed = _total = 0


def check(label, cond):
    global _passed, _total
    _total += 1
    if cond:
        _passed += 1
        print(f"  [PASS] {label}")
    else:
        print(f"  [FAIL] {label}")


def raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    return False


def _write(tmp, text):
    path = Path(tmp) / "presets.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def main():
    releases = presets.load_presets()

    # --- shipped presets -----------------------------------------------------
    check("shipped presets include 260, 262, 264", {"260", "262", "264"} <= set(releases))
    built = 0
    failures = []
    for rel, kind, key, _ in presets.iter_presets(releases):
        try:
            opts = presets.resolve(releases, rel, kind, key)
            (HelpSnapshot if kind == "help" else DevGuideSnapshot)(opts)
            built += 1
        except Exception as exc:  # noqa: BLE001 — report every bad preset
            failures.append(f"{rel} {kind}.{key}: {exc}")
    for f in failures:
        print(f"    {f}")
    check(f"every shipped preset builds a snapshotter ({built})", not failures and built > 25)

    rn = presets.resolve(releases, "264", "help", "release_notes")
    check("explicit area wins over the preset key", rn["area"] == "revenue")
    check("subtree_only carried through", rn["subtree_only"] is True)
    pcm = presets.resolve(releases, "264", "help", "pcm")
    check("area defaults to the preset key", pcm["area"] == "pcm")
    check("release_name comes from the release block", pcm["release_name"] == "Winter '27")
    check("release_version is the string key", pcm["release_version"] == "264")
    ind262 = presets.resolve(releases, "262", "dev_guide", "industries")
    ind264 = presets.resolve(releases, "264", "dev_guide", "industries")
    check("264 industries sections match 262 (shared anchor)",
          ind264["sections"] == ind262["sections"] and len(ind262["sections"]) == 9)
    dg = DevGuideSnapshot(ind264)
    check("sections list becomes section_filters; follow_links defaults off",
          dg.options["section_filters"] == ind262["sections"] and dg.options["follow_links"] is False)

    # --- precedence and validation ------------------------------------------
    over = presets.resolve(releases, "264", "help", "pcm",
                           {"expect_min_articles": 1, "mode": None, "concurrency": 2})
    check("CLI override beats the preset", over["expect_min_articles"] == 1)
    check("unset (None) override never masks a preset value", "mode" not in over)
    check("override adds a new option", over["concurrency"] == 2)
    check("unknown preset without root/prefix raises",
          raises(OptionsError, presets.resolve, releases, "264", "help", "nope"))
    adhoc = presets.resolve(releases, "266", "help", "foo",
                            {"root_article_id": "ind.foo.htm", "article_id_prefix": "ind.foo",
                             "release_name": "Spring '27"})
    check("ad hoc help run needs no preset", adhoc["area"] == "foo"
          and HelpSnapshot(adhoc).options["output_dir"] == "docs/salesforce/266/help")
    check("unknown dev-guide key without --deliverable raises (no silent RLM fallback)",
          raises(OptionsError, presets.resolve, releases, "264", "dev_guide", "industrie"))
    check("ad hoc dev-guide run with --deliverable needs no preset",
          presets.resolve(releases, "264", "dev_guide", "foo",
                          {"deliverable": "foo_guide"})["deliverable"] == "foo_guide")
    check("ad hoc run without release_name fails in the snapshotter",
          raises(OptionsError, HelpSnapshot,
                 presets.resolve(releases, "266", "help", "foo",
                                 {"root_article_id": "x", "article_id_prefix": "x"})))

    with tempfile.TemporaryDirectory() as tmp:
        check("missing release_name rejected at load",
              raises(OptionsError, presets.load_presets,
                     _write(tmp, "releases:\n  '1':\n    help: {}\n")))
        check("non-mapping preset rejected at load",
              raises(OptionsError, presets.load_presets,
                     _write(tmp, "releases:\n  '1':\n    release_name: x\n    help:\n      a: 3\n")))
        check("missing releases mapping rejected",
              raises(OptionsError, presets.load_presets, _write(tmp, "foo: 1\n")))

    # --- bootstrap ------------------------------------------------------------
    block = presets.bootstrap_block(releases, "264", "999", "Test '99")
    keys = {ln.split(":")[0].strip() for ln in block.splitlines()
            if ln.strip() and not ln.strip().startswith("#")}
    check("bootstrap drops expect_min_articles", "expect_min_articles" not in keys)
    check("bootstrap drops doc_version", "doc_version" not in keys)
    check("bootstrap retargets output_dir",
          "docs/salesforce/999/release-notes" in block and "salesforce/264" not in block)
    check("bootstrap to an existing release raises",
          raises(OptionsError, presets.bootstrap_block, releases, "262", "264", "x"))
    check("bootstrap from an unknown release raises",
          raises(OptionsError, presets.bootstrap_block, releases, "123", "999", "x"))
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "presets.yaml"
        shutil.copy(presets.PRESETS_PATH, path)
        presets.append_block(block, path)
        reloaded = presets.load_presets(path)
        new = presets.resolve(reloaded, "999", "help", "release_notes")
        check("appended block loads and resolves",
              new["release_name"] == "Test '99" and new["subtree_only"] is True
              and new["root_article_id"] == "release-notes.rn_revenue.htm")
        check("appended block keeps every preset",
              presets.preset_keys(reloaded, "999", "help") == presets.preset_keys(releases, "264", "help")
              and presets.preset_keys(reloaded, "999", "dev_guide")
              == presets.preset_keys(releases, "264", "dev_guide"))
        check("existing releases untouched by the append",
              presets.resolve(reloaded, "264", "help", "pcm") == pcm)
        check("bootstrapped sections expand the anchor",
              presets.resolve(reloaded, "999", "dev_guide", "industries")["sections"]
              == ind262["sections"])

        # CLI bootstrap writes to --presets, dry-run writes nothing.
        before = path.read_text()
        with contextlib.redirect_stdout(io.StringIO()):
            rc = cli.main(["--presets", str(path), "bootstrap", "--from", "264",
                           "--to", "1000", "--release-name", "X", "--dry-run"])
        check("bootstrap --dry-run exits 0 and writes nothing",
              rc == 0 and path.read_text() == before)
        with contextlib.redirect_stdout(io.StringIO()):
            rc = cli.main(["--presets", str(path), "bootstrap", "--from", "264",
                           "--to", "1000", "--release-name", "X"])
        check("bootstrap appends to --presets",
              rc == 0 and "1000" in presets.load_presets(path))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc = cli.main(["--presets", str(path), "bootstrap", "--from", "264",
                           "--to", "1000", "--release-name", "X"])
        check("bootstrapping an existing release is a usage error", rc == cli.EXIT_USAGE)

    # --- CLI wiring -----------------------------------------------------------
    parser = cli.build_parser()
    a = parser.parse_args(["help", "--release", "264", "--area", "pcm", "--mode", "discover",
                           "--prefix", "ind.x", "--expect-min-articles", "5",
                           "--subtree-only", "true", "--headless", "false"])
    check("help flags map to snapshotter options",
          cli._pick(a, cli.HELP_FLAGS) == {
              **{k: None for k in cli.HELP_FLAGS},
              "mode": "discover", "article_id_prefix": "ind.x", "expect_min_articles": 5,
              "subtree_only": "true", "headless": "false"})
    a = parser.parse_args(["dev-guide", "--release", "264", "--guide", "rlm",
                           "--doc-version", "264.0", "--max-pages", "9", "--follow-links", "true"])
    picked = cli._pick(a, cli.DEV_GUIDE_FLAGS)
    check("dev-guide flags map to snapshotter options",
          picked["doc_version"] == "264.0" and picked["max_pages"] == 9
          and picked["follow_links"] == "true")
    for argv in (["list"], ["run", "--release", "264", "--only", "pcm"],
                 ["check", "--release", "264"]):
        check(f"parser accepts {' '.join(argv)}", parser.parse_args(argv).command == argv[0])
    check("invalid mode rejected by argparse",
          raises(SystemExit, lambda: _quiet(parser.parse_args,
                                            ["help", "--release", "264", "--area", "x",
                                             "--mode", "bogus"])))
    check("help --area all expands to every help preset",
          cli._expand(releases, "264", "help", "all") == presets.preset_keys(releases, "264", "help"))
    check("comma list expands", cli._expand(releases, "264", "help", "pcm, dro") == ["pcm", "dro"])
    for sel in ("", " , ,"):
        check(f"empty --area {sel!r} rejected",
              raises(OptionsError, cli._expand, releases, "264", "help", sel))
        run_args = parser.parse_args(["run", "--release", "264", "--only", sel])
        check(f"empty --only {sel!r} rejected, not read as 'run everything'",
              raises(OptionsError, cli.cmd_run, run_args, releases, None))
    check("single-target flag rejected across several presets",
          raises(OptionsError, cli.run_targets, releases,
                 [("264", "help", "pcm"), ("264", "help", "dro")],
                 {"output_dir": "/tmp/x"}, None))

    # --section on a preset that lists `sections` narrows to that one section.
    captured = {}

    class _Fake:
        def __init__(self, options, logger=None):
            captured.update(DevGuideSnapshot(options).options)

        def run(self):
            return {}

    real = cli._snapshot_class
    cli._snapshot_class = lambda kind: _Fake
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc = cli.main(["dev-guide", "--release", "264", "--guide", "industries",
                           "--section", "timeline"])
    finally:
        cli._snapshot_class = real
    check("--section supersedes the preset's sections",
          rc == 0 and captured.get("section_filters") == ["timeline"])

    with contextlib.redirect_stdout(io.StringIO()) as out:
        rc = cli.main(["list", "--release", "264"])
    check("list prints the release's presets", rc == 0 and "release_notes" in out.getvalue())

    print(f"\n{_passed}/{_total} checks passed.")
    return 0 if _passed == _total else 1


def _quiet(fn, *args):
    with contextlib.redirect_stderr(io.StringIO()):
        return fn(*args)


if __name__ == "__main__":
    sys.exit(main())
