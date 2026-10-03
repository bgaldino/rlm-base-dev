"""Unit tests for scripts/doc_snapshot presets + CLI wiring (offline, no browser).

Covers preset loading/validation, option precedence (release < preset < CLI),
that every shipped preset builds a valid snapshotter, the bootstrap block
(round-trips through the loader), and argparse wiring for each subcommand.

Run:  python3 tests/test_doc_snapshot_presets.py   (needs PyYAML)
"""

import contextlib
import io
import logging
import os
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.doc_snapshot import cli, presets  # noqa: E402
from scripts.doc_snapshot._core import OptionsError, as_bool, read_manifest, yaml_escape  # noqa: E402
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
    for name, value in (("output_dir", " "), ("headless", ""), ("article_id_prefix", "")):
        check(f"empty {name} override rejected, not read as 'use the default'",
              raises(OptionsError, HelpSnapshot, presets.resolve(
                  releases, "264", "help", "release_notes", {name: value})))
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
        for group in ("help: []", "dev_guide: false", "help: ''"):
            check(f"a falsy non-mapping group ({group}) is rejected at load",
                  raises(OptionsError, presets.load_presets,
                         _write(tmp, f"releases:\n  '1':\n    release_name: x\n    {group}\n")))
        check("missing releases mapping rejected",
              raises(OptionsError, presets.load_presets, _write(tmp, "foo: 1\n")))
        check("a misspelled preset option is rejected at load",
              raises(OptionsError, presets.load_presets, _write(
                  tmp, "releases:\n  '1':\n    release_name: x\n    help:\n      rn:\n"
                       "        root_article_id: r\n        article_id_prefix: r\n"
                       "        subtree_ony: true\n")))
        check("a help-only option on a dev-guide preset is rejected",
              raises(OptionsError, presets.load_presets, _write(
                  tmp, "releases:\n  '1':\n    release_name: x\n    dev_guide:\n"
                       "      g:\n        root_article_id: r\n")))
        check("malformed YAML is an OptionsError, not a traceback",
              raises(OptionsError, presets.load_presets, _write(tmp, "releases: [\n")))
        check("a non-mapping file is an OptionsError",
              raises(OptionsError, presets.load_presets, _write(tmp, "- a\n")))
        check("a missing presets file is an OptionsError",
              raises(OptionsError, presets.load_presets, Path(tmp) / "nope.yaml"))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc = cli.main(["--presets", str(Path(tmp) / "nope.yaml"), "list"])
        check("--presets pointing at a missing file is a usage error", rc == cli.EXIT_USAGE)

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
    # An unset shell variable must not append a block the snapshotters reject.
    for target, name in (("", "x"), ("  ", "x"), ("999", ""), ("999", "   ")):
        check(f"bootstrap rejects blank --to {target!r} / --release-name {name!r}",
              raises(OptionsError, presets.bootstrap_block, releases, "264", target, name))
    check("bootstrap strips the release name",
          '  "999":\n    release_name: "Spaced"\n'
          in presets.bootstrap_block(releases, "264", " 999 ", " Spaced "))
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "presets.yaml"
        shutil.copy(presets.PRESETS_PATH, path)
        path.write_text(path.read_text(encoding="utf-8") + block, encoding="utf-8")
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

    # Null/empty options would silently read as "use the default", and a
    # preset-level release identity would let a copied preset point at the
    # source release's corpus: both are rejected at load.
    head = ("releases:\n  '1':\n    release_name: x\n    help:\n      a:\n"
            "        root_article_id: r\n        article_id_prefix: r\n")
    with tempfile.TemporaryDirectory() as tmp:
        for extra in ("        output_dir:\n", "        output_dir: ''\n",
                      "        headless: ~\n"):
            check(f"empty preset option rejected at load ({extra.strip()})",
                  raises(OptionsError, presets.load_presets, _write(tmp, head + extra)))
        guide = "releases:\n  '1':\n    release_name: x\n    dev_guide:\n      g:\n"
        for extra in ("        sections: []\n", "        sections: ['a', ' ']\n"):
            check(f"empty sections rejected at load ({extra.strip()}), not read as 'whole guide'",
                  raises(OptionsError, presets.load_presets, _write(tmp, guide + extra)))
        for name in ("release_version", "release_name"):
            check(f"preset-level {name} rejected at load",
                  raises(OptionsError, presets.load_presets,
                         _write(tmp, head + f"        {name}: '1'\n")))
        check("the minimal preset itself loads",
              presets.preset_keys(presets.load_presets(_write(tmp, head)), "1", "help") == ["a"])
    custom = {"1": {"release_name": "One", "help": {"a": {
        "root_article_id": "r.htm", "article_id_prefix": "r",
        "output_dir": "/tmp/doc-snapshots/1/help"}}}}
    check("bootstrap rejects an output_dir it cannot retarget",
          raises(OptionsError, presets.bootstrap_block, custom, "1", "2", "Two"))

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "presets.yaml"
        shutil.copy(presets.PRESETS_PATH, path)
        path.write_text(path.read_text(encoding="utf-8") + block, encoding="utf-8")

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
    sub_dests = {name: {a.dest for a in sp._actions}
                 for action in cli.build_parser()._subparsers._group_actions
                 for name, sp in action.choices.items()}
    # Selectors and argparse's own `help` are the only dests that override nothing.
    selectors = {"help", "release", "area", "guide", "only"}
    for command, flags in (("help", cli.HELP_FLAGS), ("dev-guide", cli.DEV_GUIDE_FLAGS),
                           ("run", cli.RUN_FLAGS)):
        missing = set(flags) - sub_dests[command]
        check(f"every {command} override is an argparse flag (missing: {sorted(missing)})",
              not missing)
        unpicked = sub_dests[command] - selectors - set(flags)
        check(f"every {command} flag reaches the snapshotter (dropped: {sorted(unpicked)})",
              not unpicked)
    with tempfile.TemporaryDirectory() as tmp:
        blocker = Path(tmp) / "file"
        blocker.write_text("x")

        class _Unwritable:
            def __init__(self, options, logger=None):
                pass

            def preflight(self):
                pass

            def run(self):
                (blocker / "articles").mkdir(parents=True)  # NotADirectoryError

        real_cls = cli._snapshot_class
        cli._snapshot_class = lambda kind: _Unwritable
        try:
            with contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()) as err:
                rc = cli.main(["help", "--release", "264", "--area", "pcm"])
        finally:
            cli._snapshot_class = real_cls
        check("a single-target OSError exits 1 with a message, not a traceback",
              rc == cli.EXIT_FAILED and err.getvalue().startswith("error:"))
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
    for sel in ([], [" ", ""], ["a", ""]):
        check(f"blank sections {sel!r} rejected, not read as 'whole guide'",
              raises(OptionsError, DevGuideSnapshot,
                     presets.resolve(releases, "264", "dev_guide", "rlm", {"sections": sel})))
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        rc = cli.main(["dev-guide", "--release", "264", "--guide", "rlm",
                       "--section", " ", "--mode", "refresh"])
    check("--section ' ' is a usage error", rc == cli.EXIT_USAGE)
    check("single-target flag rejected across several presets",
          raises(OptionsError, cli.run_targets, releases,
                 [("264", "help", "pcm"), ("264", "help", "dro")],
                 {"output_dir": "/tmp/x"}, None))
    try:
        cli.run_targets(releases, [("264", "dev_guide", "rlm"), ("264", "dev_guide", "industries")],
                        {"sections": ["timeline"]}, None)
        conflict = ""
    except OptionsError as exc:
        conflict = str(exc)
    check("the multi-target error names the flag as typed (--section)",
          conflict.startswith("--section applies"))
    for kind, key, name in (("help", "pcm", "concurrency"), ("help", "pcm", "wait_ms"),
                            ("dev_guide", "rlm", "concurrency"), ("dev_guide", "rlm", "max_pages")):
        cls = HelpSnapshot if kind == "help" else DevGuideSnapshot
        check(f"{kind} {name}=0 rejected, not silently clamped",
              raises(OptionsError, cls, presets.resolve(releases, "264", kind, key, {name: 0})))

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
    try:
        cli._snapshot_class = lambda kind: _Fake
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc = cli.main(["dev-guide", "--release", "264", "--guide", "industries",
                           "--section", "Data Processing Engine, Batch Management",
                           "--section", "timeline"])
    finally:
        cli._snapshot_class = real
    check("--section repeats, and a title keeps its commas",
          rc == 0 and captured.get("section_filters")
          == ["Data Processing Engine, Batch Management", "timeline"])

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
        (Path(tmp) / "manifest.json").write_text("[]")
        dg = DevGuideSnapshot(presets.resolve(releases, "264", "dev_guide", "rlm",
                                              {"output_dir": tmp}))
        fresh = read_manifest(Path(tmp) / "manifest.json", {"pages": []}, "pages")
        check("a non-object manifest passes preflight and is replaced by defaults",
              dg.preflight() is None and fresh == {"pages": []})
        for bad in ('{"pages": 5}', '{"pages": ["x"]}', '{"pages": [{"page_id": "a"}, null]}'):
            (Path(tmp) / "manifest.json").write_text(bad)
            fresh = read_manifest(Path(tmp) / "manifest.json", {"pages": []}, "pages")
            check(f"a misshapen manifest ({bad}) passes preflight and is replaced",
                  dg.preflight() is None and fresh == {"pages": []})
    rlm = presets.resolve(releases, "264", "dev_guide", "rlm")
    for name, value in (("output_dir", ["a"]), ("deliverable", {"a": 1}),
                        ("sections", [["a"]]), ("sections", {"a": 1})):
        check(f"{name}={value!r} is rejected, not crashed on",
              raises(OptionsError, DevGuideSnapshot, {**rlm, name: value}))
    for name, value in (("concurrency", True), ("max_pages", 2.5), ("wait_ms", -1)):
        check(f"{name}={value!r} is rejected", raises(OptionsError, DevGuideSnapshot,
                                                      {**rlm, name: value}))
    yaml_numbers = DevGuideSnapshot({**rlm, "output_dir": 266, "doc_version": 264.0,
                                     "sections": 5})
    check("YAML numbers become strings (output_dir, doc_version, a lone section)",
          yaml_numbers.options["output_dir"] == "266"
          and yaml_numbers.options["doc_version"] == "264.0"
          and yaml_numbers.options["section_filters"] == ["5"])
    pcm_opts = presets.resolve(releases, "264", "help", "pcm")
    check("a numeric root_article_id becomes a string",
          HelpSnapshot({**pcm_opts, "root_article_id": 123}).options["root_article_id"] == "123")
    check("a list-valued help option is rejected",
          raises(OptionsError, HelpSnapshot, {**pcm_opts, "article_id_prefix": ["a"]}))
    with tempfile.TemporaryDirectory() as tmp:
        check("preflight with no manifest yet passes",
              DevGuideSnapshot(presets.resolve(releases, "264", "dev_guide", "rlm",
                                               {"output_dir": tmp})).preflight() is None)

    for raw, want in (("true", True), ("Yes", True), ("1", True), ("off", False),
                      ("FALSE", False), (None, True), (False, False)):
        check(f"as_bool({raw!r})", as_bool(raw, True) is want)
    check("as_bool rejects a typo instead of reading it as false",
          raises(OptionsError, as_bool, "tru", True))
    for raw, want in (("# Heading", '"# Heading"'), ("a: b", '"a: b"'),
                      ("two\nlines", "two lines"), ("plain", "plain"), (None, "")):
        check(f"yaml_escape({raw!r})", yaml_escape(raw) == want)
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        rc = cli.main(["help", "--release", "264", "--area", "pcm",
                       "--subtree-only", "tru"])
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
