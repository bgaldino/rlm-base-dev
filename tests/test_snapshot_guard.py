"""Unit tests for scripts/doc_snapshot/guard.py and its use in both snapshotters.

Fixtures under tests/fixtures/doc_snapshot_guard/ are real captures from the
2026-11-23 264 refresh (public Salesforce Help / developer-guide text): the
portal's not-found page written over a Help article, a developer-guide page cut
to a stub (with the first 3.2 KB of its prior capture), and a page whose text
really changed (blank description cells, verified at source) which must pass.

Run:  python3 tests/test_snapshot_guard.py   (stdlib, plus PyYAML for presets)
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.doc_snapshot import guard  # noqa: E402
from scripts.doc_snapshot.dev_guide import DevGuideSnapshot  # noqa: E402
from scripts.doc_snapshot.help_portal import HelpSnapshot  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "doc_snapshot_guard"

_passed = _total = 0


def check(label, cond):
    global _passed, _total
    _total += 1
    if cond:
        _passed += 1
        print(f"  [PASS] {label}")
    else:
        print(f"  [FAIL] {label}")


def fx(name):
    return (FIX / name).read_text(encoding="utf-8")


class _Log:
    def __init__(self):
        self.lines = []

    def info(self, msg):
        pass

    def warning(self, msg):
        self.lines.append(msg)

    def error(self, msg):
        self.lines.append(msg)


def title_of(text):
    for line in text.splitlines():
        if line.startswith("title: "):
            return line[len("title: "):].strip()
    return None


def main():
    # --- placeholder ----------------------------------------------------------
    nf = fx("not_found_help.md")
    check("real not-found capture is refused by title",
          guard.placeholder_reason(title_of(nf), guard.body_of(nf)) is not None)
    check("not-found body alone (different title) is refused by its first line",
          "opens with" in guard.placeholder_reason(
              "Something else", "We couldn't find the page you're looking for.\n\nx"))
    check("curly apostrophe in the headline is folded",
          guard.placeholder_reason("We couldn’t find the page you’re looking for.", "") is not None)
    check("older 'looked high and low' shell is still refused",
          guard.placeholder_reason("We looked high and low\nbut couldn't find that page.", "") is not None)
    check("short body with both boilerplate markers is refused even if reworded",
          guard.placeholder_reason(
              "Page unavailable",
              "Nothing here.\n\nSearching for something? Agentforce can help.\n\nMay we also suggest\nX")
          is not None)
    long_real = "Intro. " + "Real content sentence. " * 100 + (
        "\nSearching for something? Agentforce can help. May we also suggest reading more.")
    check("a long real article that quotes both markers is not refused",
          guard.placeholder_reason("A real title", long_real) is None)
    check("one marker on a short body is not enough",
          guard.placeholder_reason("T", "Searching for something? Agentforce can help.") is None)
    check("a normal article is not a placeholder",
          guard.placeholder_reason("Create Price Books", "Define prices.\n\nSteps.") is None)
    prior_nf = fx("not_found_prior.md")
    check("a placeholder over a good prior is refused",
          guard.refusal_reason(title_of(nf), guard.body_of(nf), prior_nf) is not None)
    check("a placeholder is refused even when its page is named in accept_shrinkage",
          guard.refusal_reason(title_of(nf), guard.body_of(nf), prior_nf, "p", {"p"}) is not None)
    check("a converted body opens with the H1 marker; the headline still matches (M4)",
          "opens with" in guard.placeholder_reason(
              "Decision Table Definitions (POST)",
              "# We couldn't find the page you're looking for.\n\nSearch."))
    check("a placeholder is refused with no prior capture",
          guard.refusal_reason(title_of(nf), guard.body_of(nf), None) is not None)

    # --- body_of --------------------------------------------------------------
    prior = fx("stub_prior_excerpt.md")
    b = guard.body_of(prior)
    check("body_of drops frontmatter and the H1",
          b.startswith("Create a decision table definition") and "page_id:" not in b)
    full = fx("not_found_prior.md")
    check("body_of drops the preview banner",
          "Note: This release is in preview" not in guard.body_of(
              "---\nk: v\n---\nNote: This release is in preview. More.\n\n# T\n\nBody text."))
    check("body_of drops the attribution footer",
          "Source attribution" not in guard.body_of(nf) and "Source attribution" in nf)
    check("body_of leaves a prior with a footer comparable to a new body",
          guard.body_of(full) == guard.body_of(full + "\n"))

    # --- shrinkage ------------------------------------------------------------
    stub = fx("stub_new.md")
    reason = guard.refusal_reason(title_of(stub), guard.body_of(stub), prior)
    check("real truncated stub is refused against its prior capture",
          reason is not None and "shrank" in reason)
    accepted = []
    check("accept_shrinkage naming the page lets the stub through and reports why",
          guard.refusal_reason(title_of(stub), guard.body_of(stub), prior, "p", {"p"},
                               accepted.append) is None
          and len(accepted) == 1 and "shrank" in accepted[0])
    check("accept_shrinkage naming another page does not",
          guard.refusal_reason(title_of(stub), guard.body_of(stub), prior, "p", {"q"}) is not None)
    check("no page id means nothing is accepted",
          guard.refusal_reason(title_of(stub), guard.body_of(stub), prior, "", {""}) is not None)
    check("a new body is measured without its H1 (L1)",
          guard.refusal_reason(
              "T", "# " + "T" * 100 + "\n\n" + "word " * 90, "# P\n\n" + "word " * 200) is not None)
    check("strip_page_chrome drops banner and H1",
          guard.strip_page_chrome("Note: This release is in preview. x\n# T\n\nBody") == "Body")
    check("the first capture of a page (no prior) is not a shrink",
          guard.refusal_reason(title_of(stub), guard.body_of(stub), None) is None)
    old_e, new_e = fx("edit_prior.md"), fx("edit_new.md")
    check("a real upstream edit that drops a few cells passes",
          guard.refusal_reason(title_of(new_e), guard.body_of(new_e), old_e) is None)
    check("a prior under the size floor is never refused",
          guard.shrink_reason("x" * (guard.SHRINK_MIN_PRIOR_CHARS - 1), "y") is None)
    base = "word " * 200
    check("a same-words reformat that halves the characters passes (both ratios must fall)",
          guard.shrink_reason(base.replace(" ", " | "), base) is None)
    check("losing words while characters stay above the limit is not refused",
          guard.shrink_reason(base, "wordwordword " * 60) is None)
    dense = "a " * 130   # 26% of the characters, 65% of the words
    check("losing characters but not enough words is not refused (M5)",
          len(dense) / len(base) < guard.SHRINK_CHAR_RATIO
          and guard._words(dense) / guard._words(base) >= guard.SHRINK_WORD_RATIO
          and guard.shrink_reason(base, dense) is None)
    with tempfile.TemporaryDirectory() as tmp:
        bad = Path(tmp) / "bad.md"
        bad.write_bytes(b"\xff\xfe not utf-8")
        check("read_prior treats an undecodable file or a missing one as absent (L2)",
              guard.read_prior(bad) is None and guard.read_prior(Path(tmp) / "none.md") is None)
    check("losing most characters and words is refused",
          guard.shrink_reason(base, "word " * 20) is not None)
    check("an identical body is never refused",
          guard.shrink_reason(base, base) is None)
    check("a longer body is never refused",
          guard.shrink_reason(base, base * 3) is None)

    # --- Help snapshot end to end ---------------------------------------------
    class Page:
        def __init__(self, result):
            self.result = result

        async def goto(self, *a, **k):
            pass

        async def wait_for_timeout(self, ms):
            pass

        async def evaluate(self, js):
            return self.result

    class Ctx:
        def __init__(self, result):
            self.result = result

        async def new_page(self):
            return Page(self.result)

        async def close(self):
            pass

    class Browser:
        def __init__(self, result):
            self.result = result

        async def new_context(self):
            return Ctx(self.result)

    def help_run(result, prior_text, accept=(), walked=None):
        with tempfile.TemporaryDirectory() as tmp:
            adir = Path(tmp) / "articles"
            adir.mkdir()
            aid = "ind.example_page.htm"
            path = adir / f"{aid}.md"
            rec = {"article_id": aid, "title": "Prior Title", "area": "x"}
            if isinstance(prior_text, bytes):
                path.write_bytes(prior_text)
                rec.update(status="captured", file=f"articles/{aid}.md", body_length=7)
            elif prior_text is not None:
                path.write_text(prior_text, encoding="utf-8")
                rec.update(status="captured", file=f"articles/{aid}.md",
                           body_length=len(guard.body_of(prior_text)))
            manifest = {"articles": [rec]}
            t = HelpSnapshot.__new__(HelpSnapshot)
            t.options = {"area": "x", "concurrency": 1, "release_version": "264",
                         "release_name": "Winter '27", "accept_shrinkage": frozenset(accept), "wait_ms": 1}
            t.logger = _Log()
            t._save_manifest = lambda p, m: None
            t._article_url = lambda a: f"https://example.test/{a}"
            t._walked_ids = walked
            failed = asyncio.run(t._capture_articles(
                Browser(result), manifest["articles"], adir, manifest, Path(tmp) / "m.json"))
            return t, failed, rec, (path.read_bytes().decode("utf-8", "replace") if path.exists() else None)

    sbody = guard.body_of(stub)
    t1, f1, r1, text1 = help_run(
        {"title": "Decision Table Definitions (POST)", "body": sbody, "breadcrumb": None}, prior)
    check("help: a stub is refused, the prior file kept byte for byte", text1 == prior)
    check("help: the refused page is status error with a reason and kept sizes",
          r1["status"] == "error" and r1["error"].startswith("refused: ")
          and r1["file"] == "articles/ind.example_page.htm.md" and r1["body_length"] > 500)
    check("help: the refusal is counted and returned as failed",
          len(t1.refused) == 1 and f1 == ["ind.example_page.htm"])
    check("help: the end-of-run report names the page and the override",
          any("ind.example_page.htm" in m for m in t1.logger.lines)
          and any("--accept-shrinkage" in m for m in t1.logger.lines))
    t2, f2, r2, text2 = help_run(
        {"title": "Decision Table Definitions (POST)", "body": sbody, "breadcrumb": None},
        prior, accept={"ind.example_page.htm"})
    check("help: accept_shrinkage naming the article writes the shrunken capture",
          f2 == [] and r2["status"] == "captured" and text2 != prior and "Resource Example" in text2)
    check("help: one warning per accepted page names it",
          sum("[accepted] ind.example_page.htm" in m for m in t2.logger.lines) == 1)
    t2b, f2b, r2b, text2b = help_run(
        {"title": "Decision Table Definitions (POST)", "body": sbody, "breadcrumb": None},
        prior, accept={"ind.other.htm"})
    check("help: accept_shrinkage naming a different article does not accept this one",
          text2b == prior and r2b["status"] == "error" and f2b == ["ind.example_page.htm"])
    t3, f3, r3, text3 = help_run(
        {"title": title_of(nf), "body": guard.body_of(nf), "breadcrumb": None}, prior_nf,
        accept={"ind.example_page.htm"})
    check("help: a not-found page keeps the prior file even with accept_shrinkage",
          text3 == prior_nf and r3["status"] == "error" and f3 == ["ind.example_page.htm"])
    t4, f4, r4, text4 = help_run(
        {"title": title_of(nf), "body": guard.body_of(nf), "breadcrumb": None}, None)
    check("help: a not-found page with no prior writes no file",
          text4 is None and r4["status"] == "error")
    t5, f5, r5, text5 = help_run(
        {"title": "Create Price Books", "body": "Fresh body " * 80, "breadcrumb": None}, prior_nf)
    check("help: a normal refresh is written", f5 == [] and "Fresh body" in text5)
    t6, f6, r6, _ = help_run(
        {"title": title_of(nf), "body": guard.body_of(nf), "breadcrumb": None}, prior_nf,
        walked={"ind.other.htm"})
    check("help: a refused page is not reported as an orphan", t6.orphaned == [])
    t7, f7, r7, text7 = help_run({"error": "navigate failed: timeout"}, prior, walked=None)
    check("help: a failed fetch keeps the prior file and its file/body_length (M2)",
          text7 == prior and r7["status"] == "error" and r7["file"] == "articles/ind.example_page.htm.md"
          and r7["body_length"] > 0 and f7 == ["ind.example_page.htm"])
    check("help: no sidebar walk this run means no orphan claim", t7.orphaned == [])
    t8, f8, r8, text8 = help_run({"error": "no H1 found"}, prior, walked={"ind.other.htm"})
    check("help: an errored article the sidebar walk no longer lists is an orphan",
          t8.orphaned == ["ind.example_page.htm"] and text8 == prior)
    t9, f9, r9, text9 = help_run({"error": "no H1 found"}, prior, walked={"ind.example_page.htm"})
    check("help: an errored article still in the sidebar is not an orphan", t9.orphaned == [])
    t10, f10, r10, text10 = help_run(
        {"title": "New", "body": "Fresh body " * 80, "breadcrumb": None}, b"\xff\xfe bad")
    check("help: an undecodable prior file is replaced, not a crash (L2)",
          f10 == [] and "Fresh body" in text10)

    # --- dev-guide snapshot end to end ----------------------------------------
    class DGPage:
        def __init__(self, results):
            self.results = results

        async def evaluate(self, js, arg=None):
            return [self.results[i] for i in arg["ids"]]

        async def wait_for_timeout(self, ms):
            pass

    def dg_run(html, prior_text, accept=(), toc_ids=None, res=None, extra=None):
        pid = "dg_page.htm"
        with tempfile.TemporaryDirectory() as tmp:
            adir = Path(tmp) / "articles"
            adir.mkdir()
            rec = {"page_id": pid, "title": "Prior", "status": "captured",
                   "file": f"articles/{pid}.md", "body_length": 9999}
            if isinstance(prior_text, bytes):
                (adir / f"{pid}.md").write_bytes(prior_text)
            elif prior_text is not None:
                (adir / f"{pid}.md").write_text(prior_text, encoding="utf-8")
            recs = [rec] + [{"page_id": x} for x in (extra or {})]
            manifest = {"pages": recs}
            t = DevGuideSnapshot.__new__(DevGuideSnapshot)
            t.options = {"concurrency": 4, "deliverable": "d", "doc_version": "264.0",
                         "follow_links": False, "max_pages": 50, "batch_delay_ms": 0,
                         "release_version": "264", "release_name": "Winter '27",
                         "accept_shrinkage": frozenset(accept)}
            t.logger = _Log()
            t._save_manifest = lambda p, m: None
            t._page_source_url = lambda p: f"https://example.test/{p}"
            t._toc_ids = toc_ids
            result = res or {pid: {"id": pid, "ok": True, "title": "Prior", "content": html}}
            result = {**result, **(extra or {})}
            failed, attempted = asyncio.run(t._capture_pages(
                DGPage(result), recs, adir, manifest, Path(tmp) / "m.json"))
            text = (adir / f"{pid}.md").read_text(encoding="utf-8") if (adir / f"{pid}.md").exists() else None
            t.written = {x: (adir / f"{x}.md").read_text(encoding="utf-8")
                         for x in (extra or {}) if (adir / f"{x}.md").exists()}
            return t, failed, rec, text

    short = "<p>Short stub.</p>"
    d1, df1, dr1, dt1 = dg_run(short, prior)
    check("dev-guide: a stub is refused and the prior file kept", dt1 == prior)
    check("dev-guide: refused page is status error with reason, counted and failed",
          dr1["status"] == "error" and dr1["error"].startswith("refused: ")
          and len(d1.refused) == 1 and df1 == ["dg_page.htm"])
    check("dev-guide: refusal keeps file and body_length",
          dr1["file"] == "articles/dg_page.htm.md" and dr1["body_length"] == 9999)
    d2, df2, dr2, dt2 = dg_run(short, prior, accept={"dg_page.htm"})
    check("dev-guide: accept_shrinkage naming the page writes it, with one warning",
          df2 == [] and dr2["status"] == "captured" and "Short stub." in dt2
          and sum("[accepted] dg_page.htm" in m for m in d2.logger.lines) == 1)
    d2b, df2b, dr2b, dt2b = dg_run(short, prior, accept={"other.htm"})
    check("dev-guide: accept_shrinkage naming another page does not accept this one",
          dt2b == prior and df2b == ["dg_page.htm"])
    d2c, df2c, dr2c, dt2c = dg_run(short, b"\xff\xfe bad")
    check("dev-guide: an undecodable prior file is replaced, not a crash (L2)",
          df2c == [] and "Short stub." in dt2c)
    d3, df3, dr3, dt3 = dg_run(
        "<h1>We couldn't find the page you're looking for.</h1>", prior, accept={"dg_page.htm"},
        res={"dg_page.htm": {"id": "dg_page.htm", "ok": True,
                             "title": "We couldn't find the page you're looking for.",
                             "content": "<p>We couldn't find the page you're looking for.</p>"}})
    check("dev-guide: a not-found page is refused even with accept_shrinkage",
          dt3 == prior and dr3["status"] == "error" and df3 == ["dg_page.htm"])
    d3b, df3b, dr3b, dt3b = dg_run(
        "", prior,
        res={"dg_page.htm": {"id": "dg_page.htm", "ok": True, "title": "Decision Table Definitions (POST)",
                             "content": "<h1>We couldn't find the page you're looking for.</h1><p>Search.</p>"}})
    check("dev-guide: a not-found body under the real page title is refused (M4)",
          dt3b == prior and dr3b["status"] == "error" and "opens with" in dr3b["error"])
    link = '<p>See <a href="/docs/atlas.en-us.d.meta/d/gone.htm">gone</a> and ' \
           '<a href="/docs/atlas.en-us.d.meta/d/here.htm">here</a>.</p>' + "<p>filler text</p>" * 5
    nf_page = {"id": "gone.htm", "ok": True, "title": "We couldn't find the page you're looking for.",
               "content": "<p>We couldn't find the page you're looking for.</p>"}
    ok_page = {"id": "here.htm", "ok": True, "title": "Here", "content": "<p>" + "Real text. " * 30 + "</p>"}
    d3c, df3c, dr3c, dt3c = dg_run(
        link, None,
        res={"dg_page.htm": {"id": "dg_page.htm", "ok": True, "title": "Linker", "content": link}},
        extra={"gone.htm": nf_page, "here.htm": ok_page})
    check("dev-guide: no local link to a refused page that has no prior file (L4)",
          "gone.htm.md" not in dt3c and "./here.htm.md" in dt3c
          and "gone.htm" in dt3c and "gone.htm" not in d3c.written)
    d3d, df3d, dr3d, dt3d = dg_run(
        "", None,
        res={"dg_page.htm": {"id": "dg_page.htm", "ok": True, "title": "Linker", "content": link}},
        extra={"gone.htm": nf_page})
    check("dev-guide: the refused page is still counted as failed", "gone.htm" in df3d)
    d4, df4, dr4, dt4 = dg_run(
        "", prior, toc_ids={"other.htm"},
        res={"dg_page.htm": {"id": "dg_page.htm", "ok": False, "error": "HTTP 404"}})
    check("dev-guide: an errored page absent from the TOC is reported as an orphan",
          d4.orphaned == ["dg_page.htm"] and dt4 == prior)
    d5, df5, dr5, dt5 = dg_run(
        "", prior, toc_ids={"dg_page.htm"},
        res={"dg_page.htm": {"id": "dg_page.htm", "ok": False, "error": "HTTP 404"}})
    check("dev-guide: an errored page still in the TOC is not an orphan", d5.orphaned == [])
    d6, df6, dr6, dt6 = dg_run(
        "", prior, toc_ids=None,
        res={"dg_page.htm": {"id": "dg_page.htm", "ok": False, "error": "HTTP 404"}})
    check("dev-guide: with no whole-guide TOC walk nothing is called an orphan", d6.orphaned == [])

    # --- CLI flag and run summary ----------------------------------------------
    from scripts.doc_snapshot import cli
    from scripts.doc_snapshot._core import SnapshotError, as_id_set, raise_on_capture_errors
    p = cli.build_parser()
    check("--accept-shrinkage is off unless given",
          p.parse_args(["help", "--release", "264", "--area", "x"]).accept_shrinkage is None)
    check("--accept-shrinkage takes page ids on help, dev-guide and run (M3)",
          p.parse_args(["help", "--release", "264", "--area", "x",
                        "--accept-shrinkage", "a.htm,b.htm"]).accept_shrinkage == ["a.htm", "b.htm"]
          and p.parse_args(["dev-guide", "--release", "264", "--guide", "x",
                            "--accept-shrinkage", "a"]).accept_shrinkage == ["a"]
          and p.parse_args(["run", "--release", "264", "--accept-shrinkage", "a"]).accept_shrinkage == ["a"])
    import contextlib
    import io
    try:
        with contextlib.redirect_stderr(io.StringIO()):
            p.parse_args(["run", "--release", "264", "--accept-shrinkage"])
        bare = False
    except SystemExit:
        bare = True
    check("a bare --accept-shrinkage (no ids) is a usage error", bare)
    check("as_id_set accepts a list or a comma-separated string",
          as_id_set(["a, b", "c"]) == frozenset("abc") and as_id_set(None) == frozenset())
    check("the flag reaches the snapshotter options through every command's override list",
          all("accept_shrinkage" in flags
              for flags in (cli.HELP_FLAGS, cli.DEV_GUIDE_FLAGS, cli.RUN_FLAGS)))
    check("help text states both thresholds (L6)",
          all(x in p._subparsers._group_actions[0].choices["run"].format_help().replace("\n", " ")
              for x in ("50%", "60%")))

    # M1: a refusal fails the run, so its counts ride on the error to the FAILED row.
    try:
        raise_on_capture_errors(df1, 3, "pages", refused=d1.refused, orphaned=["gone.htm"])
        err = None
    except SnapshotError as exc:
        err = exc
    check("the error carries refused and orphaned counts and ids",
          err is not None and err.refused == d1.refused and err.orphaned == ["gone.htm"]
          and "1 refused by the capture guard" in str(err) and "1 no longer in the contents" in str(err))

    class FakeSnapshot:
        failing = True

        def __init__(self, options, logger=None):
            self.options = options

        def preflight(self):
            pass

        def run(self):
            if self.options["area"] == "bad":
                raise_on_capture_errors(df1, 3, "articles", refused=d1.refused)
            return {"discovered": 3, "captured": 3, "errored": 0}

    releases = {"264": {"release_name": "Winter '27", "help": {
        "bad": {"root_article_id": "r.htm", "article_id_prefix": "r"},
        "good": {"root_article_id": "g.htm", "article_id_prefix": "g"}}}}
    saved = cli._snapshot_class
    cli._snapshot_class = lambda kind: FakeSnapshot
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            code = cli.run_targets(
                releases, [("264", "help", "bad"), ("264", "help", "good")], {}, _Log())
    finally:
        cli._snapshot_class = saved
    rows = out.getvalue().splitlines()
    failed_row = next(r for r in rows if "help.bad" in r)
    ok_row = next(r for r in rows if "help.good" in r)
    check("run_targets: the FAILED row shows the guard's refusal count and the run exits 1",
          code == cli.EXIT_FAILED and "FAILED" in failed_row
          and "1 refused by the capture guard" in failed_row)
    check("run_targets: the ok row has no refused column",
          "ok" in ok_row and "refused" not in ok_row)

    print(f"\n{_passed}/{_total} checks passed.")
    return 0 if _passed == _total else 1


if __name__ == "__main__":
    sys.exit(main())
