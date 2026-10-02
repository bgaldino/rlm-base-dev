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
from scripts.doc_snapshot._core import OptionsError, as_bool  # noqa: E402
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
    for name in ("output_dir", "doc_version", "sections"):
        check(f"empty {name} override rejected, not read as 'use the default'",
              raises(OptionsError, presets.resolve, releases, "264", "help",
                     "release_notes", {name: " "}))
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        rc = cli.main(["help", "--release", "264", "--area", "release_notes",
                       "--output-dir", ""])
    check("empty --output-dir is a usage error", rc == cli.EXIT_USAGE)
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

    # A preset left with no options once release-specific ones are dropped
    # must still load as a mapping, not as null.
    sparse = {"1": {"release_name": "One", "dev_guide": {
        "empty": {}, "pinned": {"doc_version": "1.0"}}}}
    sparse_block = presets.bootstrap_block(sparse, "1", "2", "Two")
    with tempfile.TemporaryDirectory() as tmp:
        path = _write(tmp, "releases:\n" + sparse_block)
        check("bootstrap emits {} for presets with no options left",
              presets.preset_keys(presets.load_presets(path), "2", "dev_guide")
              == ["empty", "pinned"])

    # Null/empty options keep their default instead of becoming "None" or "".
    nulls = {"1": {"release_name": "One", "help": {"a": {
        "root_article_id": "r.htm", "article_id_prefix": "r", "headless": None,
        "wait_ms": None, "output_dir": None}, "b": {
        "root_article_id": "r.htm", "article_id_prefix": "r", "output_dir": ""}}}}
    with tempfile.TemporaryDirectory() as tmp:
        path = _write(tmp, "releases:\n" + presets.bootstrap_block(nulls, "1", "2", "Two"))
        reloaded = presets.load_presets(path)
        for key in ("a", "b"):
            opts = presets.resolve(reloaded, "2", "help", key)
            check(f"bootstrap skips null/empty options ({key})",
                  not {"headless", "wait_ms", "output_dir"} & set(opts)
                  and HelpSnapshot(opts).options["output_dir"] == "docs/salesforce/2/help")
    custom = {"1": {"release_name": "One", "help": {"a": {
        "root_article_id": "r.htm", "article_id_prefix": "r",
        "output_dir": "/tmp/doc-snapshots/1/help"}}}}
    check("bootstrap rejects an output_dir it cannot retarget",
          raises(OptionsError, presets.bootstrap_block, custom, "1", "2", "Two"))

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "presets.yaml"
        shutil.copy(presets.PRESETS_PATH, path)
        presets.append_block(block, path)

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

        def preflight(self):
            pass

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

    # Every target is validated before any runs: a typo after a valid key is a
    # usage error (exit 2), and the valid preset must not have run first.
    ran = []

    class _Recording:
        def __init__(self, options, logger=None):
            self.options = options

        def preflight(self):
            pass

        def run(self):
            ran.append(self.options.get("area"))
            return {}

    cli._snapshot_class = lambda kind: _Recording
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc = cli.main(["help", "--release", "264", "--area", "pcm,prcing"])
            rc2 = cli.main(["help", "--release", "264", "--area", "typo,another_typo"])
    finally:
        cli._snapshot_class = real
    check("a typo after a valid key exits 2 before anything runs",
          rc == 2 and ran == [])
    check("several unknown keys still exit 2, not a per-target failure", rc2 == 2)

    # An OptionsError raised mid-run (e.g. a doc_version conflict) is a
    # per-target failure in a batch: later targets still run, exit is 1.
    class _MidRunOptionsError(_Recording):
        def run(self):
            if self.options.get("area") == "pcm":
                raise OptionsError("doc_version conflict")
            return super().run()

    ran.clear()
    cli._snapshot_class = lambda kind: _MidRunOptionsError
    try:
        with contextlib.redirect_stdout(io.StringIO()) as out, \
                contextlib.redirect_stderr(io.StringIO()):
            rc = cli.main(["help", "--release", "264", "--area", "pcm,dro"])
            rc_one = cli.main(["help", "--release", "264", "--area", "pcm"])
    finally:
        cli._snapshot_class = real
    check("a mid-run OptionsError is fail-soft in a batch (exit 1, rest still run)",
          rc == cli.EXIT_FAILED and ran == ["dro"] and "Summary" in out.getvalue())
    check("a mid-run OptionsError on a single target stays a usage error",
          rc_one == cli.EXIT_USAGE)

    # preflight: a pinned doc_version that conflicts with an already-captured
    # manifest is a usage error before any target runs (the real snapshotters).
    import json
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "manifest.json").write_text(json.dumps(
            {"doc_version": "262.0", "pages": [{"page_id": "a", "status": "captured"}]}))
        dg_opts = presets.resolve(releases, "264", "dev_guide", "rlm",
                                  {"output_dir": tmp, "mode": "all"})
        check("preflight rejects a pinned doc_version over a captured manifest",
              raises(OptionsError, DevGuideSnapshot(dg_opts).preflight))
        check("preflight allows the same conflict under --mode refresh",
              DevGuideSnapshot(dict(dg_opts, mode="refresh")).preflight() is None)
        check("preflight allows a discover preview",
              DevGuideSnapshot(dict(dg_opts, mode="discover")).preflight() is None)
        class _GuideInTmp(DevGuideSnapshot):
            def __init__(self, options, logger=None):
                super().__init__(dict(options, output_dir=tmp), logger=logger)

        ran.clear()
        cli._snapshot_class = lambda kind: (_GuideInTmp if kind == "dev_guide"
                                            else _Recording)
        try:
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()):
                rc = cli.main(["run", "--release", "264", "--only", "pcm,rlm"])
        finally:
            cli._snapshot_class = real
        check("run: a later dev guide's version conflict exits 2 before Help runs",
              rc == cli.EXIT_USAGE and ran == [])
    with tempfile.TemporaryDirectory() as tmp:
        check("preflight with no manifest yet passes",
              DevGuideSnapshot(presets.resolve(releases, "264", "dev_guide", "rlm",
                                               {"output_dir": tmp})).preflight() is None)

    for raw, want in (("true", True), ("Yes", True), ("1", True), ("off", False),
                      ("FALSE", False), ("", True), (None, True), (False, False)):
        check(f"as_bool({raw!r})", as_bool(raw, True) is want)
    check("as_bool rejects a typo instead of reading it as false",
          raises(OptionsError, as_bool, "tru", True))
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        rc = cli.main(["help", "--release", "264", "--area", "pcm",
                       "--include-release-param", "tru"])
    check("a malformed boolean flag is a usage error", rc == 2)

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
