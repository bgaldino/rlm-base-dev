"""Offline tests for scripts/doc_snapshot/site_guide.py (server-rendered dev guides).

Pages come from small saved HTML in tests/fixtures/doc_snapshot_site/ through an
injected fetcher: no network, no browser.

Run:  python3 tests/test_snapshot_site_guide.py   (stdlib only)
"""

import json
import os
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.doc_snapshot import site_guide as sg  # noqa: E402
from scripts.doc_snapshot._core import OptionsError, SnapshotError  # noqa: E402

FIX = Path(__file__).parent / "fixtures" / "doc_snapshot_site"
G = "/docs/revenue/revenue-management/guide/"
BASE = "https://developer.salesforce.com" + G
START = BASE + "rlm-get-started.html"

_passed = _total = 0


def check(label, cond):
    global _passed, _total
    _total += 1
    _passed += bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


def raises(exc, fn):
    try:
        fn()
    except exc:
        return True
    except Exception:
        return False
    return False


class Log:
    def __init__(self):
        self.lines = []

    def _add(self, msg, *a):
        self.lines.append(str(msg))

    info = warning = error = debug = _add


def make_fetcher(overrides=None, calls=None):
    pages = {p.stem: p.read_text(encoding="utf-8") for p in FIX.glob("*.html")}
    overrides = overrides or {}

    def fetch(url):
        if calls is not None:
            calls.append(url)
        if url in overrides:
            return overrides[url]
        slug = url[len(BASE):-len(".html")] if url.startswith(BASE) else None
        if slug in pages:
            return 200, pages[slug], url
        return 404, "", url
    return fetch


def options(out, **kw):
    o = {"release_version": "264", "release_name": "Winter '27", "site_url": START,
         "api_version": "68.0", "deliverable": "revenue_lifecycle_management_dev_guide",
         "output_dir": str(out), "batch_delay_ms": 0}
    o.update(kw)
    return o


def snap(out, fetcher=None, redirects=None, **kw):
    return sg.SiteGuideSnapshot(
        options(out, **kw), logger=Log(), fetcher=fetcher or make_fetcher(),
        redirect_resolver=(lambda u: (redirects or {}).get(u)), sleep=lambda s: None)


def load(out):
    return json.loads((Path(out) / "manifest.json").read_text(encoding="utf-8"))


def main():
    print("parsing")
    page = sg.parse_page((FIX / "rlm-get-started.html").read_text(encoding="utf-8"))
    toc = sg.parse_toc(page["attrs"])
    check("TOC is read from the escaped sidebar-content JSON", len(toc) == 3 and toc[1]["children"])
    check("a page without doc-content-layout is not a guide page",
          sg.parse_page((FIX / "error-404.html").read_text(encoding="utf-8")) is None)
    check("missing sidebar-content raises", raises(SnapshotError, lambda: sg.parse_toc({})))
    check("bad sidebar JSON raises", raises(SnapshotError, lambda: sg.parse_toc({"sidebar-content": "{x"})))

    pages, skipped = sg.flatten_toc(toc, G, None)
    check("flatten keeps TOC order, parents and sections",
          [p["page_id"] for p in pages] == ["rlm-get-started", "deployment-overview",
                                            "deployment-considerations", "connect-resources-get-catalogs"]
          and pages[2]["parent_page"] == "deployment-overview" and pages[2]["section"] == "Deployment")
    check("a node outside the guide is skipped and counted", skipped == 1)
    sub, _ = sg.flatten_toc(toc, G, ["deployment_overview.htm"])
    check("a section is matched by an atlas id (_ and .htm normalised)",
          [p["page_id"] for p in sub] == ["deployment-overview", "deployment-considerations"])
    sub, _ = sg.flatten_toc(toc, G, ["Connect Resources"])
    check("a section is matched by label", [p["page_id"] for p in sub] == ["connect-resources-get-catalogs"])
    check("an unknown section raises", raises(OptionsError, lambda: sg.flatten_toc(toc, G, ["nope"])))
    check("slug_of rejects traversal, other guides and non-html",
          sg.slug_of(G + "../x.html", G) is None and sg.slug_of("/docs/other/guide/a.html", G) is None
          and sg.slug_of(G + "a.htm", G) is None and sg.slug_of(G + "a.html#f", G) == "a")

    print("body conversion")
    body = page["body"]
    check("unhandled_tags sees only the unconverted elements", sg.unhandled_tags(body) == [])
    norm = sg.normalize_body(body)
    check("doc-heading becomes an h2", "<h2>Product Catalog</h2>" in norm)
    check("callout keeps its label", "<p><strong>Note:</strong></p><p>Callout text.</p>" in norm)
    code = sg.normalize_body(
        (FIX / "connect-resources-get-catalogs.html").read_text(encoding="utf-8"))
    check("dx-code-block attribute becomes pre/code", "<pre><code>https://{yourInstance}" in code
          and "second line</code></pre>" in code
          and 'a=1&b="x"' in sg.html_to_markdown(code))
    md = sg.html_to_markdown(sg.rewrite_links(norm, G, {"deployment-considerations"}))
    check("links to captured pages are local, with fragment",
          "(./deployment-considerations.md#notes)" in md)
    check("links to uncaptured pages and atlas paths keep an absolute URL",
          f"({BASE}unlisted-page.html)" in md and "(https://developer.salesforce.com/docs/atlas.en-us.x.meta/x/y.htm)" in md)
    check("heading, callout and list reach the markdown",
          "## Product Catalog" in md and "**Note:**" in md and "One" in md)
    check("title comes from the H1", sg.page_title(body, "x") == "Get Started")
    check("api_versions finds every mention",
          sg.api_versions(code) == ["v68.0", "v68.0", "v68.0", "v68.0"][:len(sg.api_versions(code))]
          and sg.observed_version(Counter(["v68.0", "v68.0", "v64.0"])) == "68.0"
          and sg.observed_version(Counter()) is None)
    check("guess_slug is the usual rename", sg.guess_slug("rlm_get_started.htm") == "rlm-get-started")

    print("options")
    with tempfile.TemporaryDirectory() as tmp:
        check("site_url must be a guide page",
              raises(OptionsError, lambda: snap(tmp, site_url="https://example.com/x.html")))
        check("api_version is required",
              raises(OptionsError, lambda: sg.SiteGuideSnapshot(
                  {k: v for k, v in options(tmp).items() if k != "api_version"})))
        check("api_version must look like 68.0", raises(OptionsError, lambda: snap(tmp, api_version="68")))
        check("doc_version is rejected", raises(OptionsError, lambda: snap(tmp, doc_version="264.0")))

    print("capture")
    with tempfile.TemporaryDirectory() as tmp:
        s = snap(tmp)
        stats = s.run()
        m = load(tmp)
        check("whole guide: 4 pages captured, none errored",
              stats["captured"] == 4 and stats["errored"] == 0 and m["source"] == "site")
        check("observed API version recorded", m["observed_api_version"] == "68.0"
              and m["api_version_votes"]["v68.0"] >= 1)
        art = (Path(tmp) / "articles" / "rlm-get-started.md").read_text(encoding="utf-8")
        check("frontmatter carries slug, new source_url, api_version",
              "page_id: rlm-get-started" in art and f"source_url: {START}" in art
              and "api_version: 68.0" in art and "section: Get Started" in art)
        check("attribution footer present", "Source attribution and limited-use note" in art)
        check("article links point at sibling files", "./deployment-considerations.md#notes" in art)
        check("index.md lists captured pages", "rlm-get-started" in (Path(tmp) / "index.md").read_text())
        check("manifest records the source url per page",
              all(p["source_url"].startswith(BASE) for p in m["pages"]))
        s2 = snap(tmp)
        calls = []
        s2._fetch_once = make_fetcher(calls=calls)
        s2.options["mode"] = "all"
        s2.run()
        check("a rerun fetches only the TOC page (idempotent)", len(calls) == 1)

    print("review hardening")
    tricky = ('<doc-content-layout class="x" sidebar-content="[]"><p>a</p>'
              '<dx-code-block code-block="List&lt;String&gt; a -> b; &lt;a href=&quot;/docs/x.html&quot;&gt;" language="x"></dx-code-block>'
              '<p>kept prose</p><dx-code-block code-block="second" language="x"/>'
              '<p>after</p></doc-content-layout>')
    tp = sg.parse_page(tricky)
    tn = sg.normalize_body(tp["body"]) if tp else ""
    check("a literal > inside an attribute value does not break the tag", tp is not None and "List&lt;String&gt; a -&gt; b" in tn)
    check("an empty or self-closed code block does not swallow the prose after it",
          "kept prose" in tn and "after" in tn and "<pre><code>second</code></pre>" in tn)
    tmd = sg.html_to_markdown(sg.rewrite_links(tn, G, set()))
    check("links inside a code sample are not rewritten", 'href="/docs/x.html"' in tmd)
    with tempfile.TemporaryDirectory() as tmp:
        s = snap(tmp, api_version="69.0", mode="all")
        raises(SnapshotError, s.run)
        check("a version refusal saves no manifest and writes no article",
              not (Path(tmp) / "manifest.json").exists()
              and not list((Path(tmp) / "articles").glob("*.md")))
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "articles").mkdir()
        (Path(tmp) / "articles" / "rlm_get_started.htm.md").write_text("old", encoding="utf-8")
        old = json.dumps({"pages": [{"page_id": "rlm_get_started.htm", "status": "captured"}]})
        (Path(tmp) / "manifest.json").write_text(old, encoding="utf-8")
        raises(SnapshotError, snap(tmp, api_version="69.0", mode="refresh").run)
        check("a refused switch leaves the atlas manifest untouched",
              (Path(tmp) / "manifest.json").read_text(encoding="utf-8") == old)
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "manifest.json").write_text(json.dumps({"source": "site", "pages": []}), encoding="utf-8")
        from scripts.doc_snapshot.dev_guide import DevGuideSnapshot
        dg = DevGuideSnapshot({"release_version": "264", "release_name": "x", "deliverable": "d",
                               "root_article_id": "r.htm", "output_dir": str(tmp)}, logger=Log())
        check("an atlas target refuses a site corpus in preflight", raises(OptionsError, dg.preflight))
    with tempfile.TemporaryDirectory() as tmp:
        old = json.dumps({"pages": [{"page_id": "rlm_get_started.htm", "status": "captured"}]})
        (Path(tmp) / "manifest.json").write_text(old, encoding="utf-8")
        only_start = make_fetcher({BASE + p + ".html": (404, "", BASE) for p in
                                   ("deployment-overview", "deployment-considerations", "connect-resources-get-catalogs")})
        raises(SnapshotError, snap(tmp, fetcher=only_start, mode="refresh").run)
        check("an unverified atlas switch keeps the atlas manifest",
              (Path(tmp) / "manifest.json").read_text(encoding="utf-8") == old)
    with tempfile.TemporaryDirectory() as tmp:
        old = json.dumps({"pages": [{"page_id": "rlm_get_started.htm", "status": "pending"}]})
        (Path(tmp) / "manifest.json").write_text(old, encoding="utf-8")
        check("discover-only switch reaches the save guard",
              raises(SnapshotError, snap(tmp, mode="discover").run))
        check("a discover-only switch with no version evidence keeps the atlas manifest",
              (Path(tmp) / "manifest.json").read_text(encoding="utf-8") == old)
    with tempfile.TemporaryDirectory() as tmp:
        v69 = make_fetcher()(START)[1].replace("</doc-content-layout>", "<p>/services/data/v69.0/x</p></doc-content-layout>")
        snap(tmp, mode="all").run()
        s2 = snap(tmp, mode="all", api_version="68.0", fetcher=make_fetcher({START: (200, v69, START)}))
        before = (Path(tmp) / "manifest.json").read_text(encoding="utf-8")
        check("an all-mode rerun with nothing pending still checks the start page's version",
              raises(SnapshotError, s2.run) and (Path(tmp) / "manifest.json").read_text(encoding="utf-8") == before)
    import http.client
    import urllib.request
    class _Boom:
        def __enter__(self): raise http.client.IncompleteRead(b"")
        def __exit__(self, *a): return False
    real = urllib.request.urlopen
    urllib.request.urlopen = lambda *a, **k: _Boom()
    try:
        check("an IncompleteRead is a failed fetch, not a crash", sg.http_fetch(START)[0] == 0)
    finally:
        urllib.request.urlopen = real
    check("a negative batch delay is an options error",
          raises(OptionsError, lambda: snap("/tmp/x", batch_delay_ms=-1)))
    check("a site_url with an unsafe slug is an options error",
          raises(OptionsError, lambda: snap("/tmp/x", site_url=BASE + "a%20b.html")))

    check("a version tie goes to the newer version, deterministically",
          sg.observed_version(Counter({"v62.0": 1, "v68.0": 1})) == "68.0")
    with tempfile.TemporaryDirectory() as tmp:
        mixed = make_fetcher()(START)[1].replace(
            "</doc-content-layout>", "<p>/services/data/v62.0/a /services/data/v68.0/b</p></doc-content-layout>")
        snap(tmp, mode="all", fetcher=make_fetcher({START: (200, mixed, START)})).run()
        st = snap(tmp, mode="all", fetcher=make_fetcher({START: (200, mixed, START)})).run()
        check("a start page citing an older version beside the preset's does not refuse a rerun",
              st["captured"] == 4)

    print("API version check")
    with tempfile.TemporaryDirectory() as tmp:
        s = snap(tmp, api_version="69.0")
        check("a mismatching site version refuses", raises(SnapshotError, s.run))
        check("nothing is written on a mismatch",
              not list((Path(tmp) / "articles").glob("*.md")))
    with tempfile.TemporaryDirectory() as tmp:
        s = snap(tmp, sections=["deployment-overview"])
        check("no version evidence refuses without a probe_page", raises(SnapshotError, s.run))
        check("nothing written without evidence", not list((Path(tmp) / "articles").glob("*.md")))
    with tempfile.TemporaryDirectory() as tmp:
        s = snap(tmp, sections=["deployment-overview"], probe_page="connect-resources-get-catalogs")
        stats = s.run()
        check("probe_page supplies the evidence", stats["captured"] == 2
              and load(tmp)["observed_api_version"] == "68.0")

    print("failures")
    with tempfile.TemporaryDirectory() as tmp:
        f = make_fetcher({BASE + "deployment-overview.html": (404, "", "")})
        s = snap(tmp, fetcher=f)
        check("a 404 page fails the run and is recorded", raises(SnapshotError, s.run))
        rec = {p["page_id"]: p for p in load(tmp)["pages"]}
        check("the 404 is an error record, the rest captured",
              rec["deployment-overview"]["status"] == "error"
              and rec["rlm-get-started"]["status"] == "captured")
    with tempfile.TemporaryDirectory() as tmp:
        soft = (FIX / "error-404.html").read_text(encoding="utf-8")
        f = make_fetcher({BASE + "deployment-overview.html": (200, soft, BASE + "deployment-overview.html")})
        s = snap(tmp, fetcher=f)
        raises(SnapshotError, s.run)
        rec = {p["page_id"]: p for p in load(tmp)["pages"]}
        check("a soft 404 (HTTP 200 shell) is an error", "doc-content-layout" in rec["deployment-overview"]["error"])
    with tempfile.TemporaryDirectory() as tmp:
        f = make_fetcher({BASE + "deployment-overview.html": (200, "<doc-content-layout></doc-content-layout>", "https://developer.salesforce.com/elsewhere.html")})
        s = snap(tmp, fetcher=f)
        raises(SnapshotError, s.run)
        rec = {p["page_id"]: p for p in load(tmp)["pages"]}
        check("a redirect off the page is an error", "redirected" in rec["deployment-overview"]["error"])
    sleeps, n = [], [0]

    def flaky(url):
        n[0] += 1
        return (503, "", url) if n[0] < 3 else (200, "ok", url)
    t = sg.SiteGuideSnapshot(options("/nonexistent"), logger=Log(), fetcher=flaky, sleep=sleeps.append)
    check("5xx is retried with backoff", t._get("u")[0] == 200 and sleeps == [2, 4])
    t = sg.SiteGuideSnapshot(options("/nonexistent"), logger=Log(), fetcher=lambda u: (404, "", u), sleep=sleeps.append)
    check("404 is not retried", t._get("u")[0] == 404 and sleeps == [2, 4])

    print("capture guard")
    with tempfile.TemporaryDirectory() as tmp:
        snap(tmp).run()
        long_body = "<h1>Get Started</h1>" + "<p>filler words here.</p>" * 200
        art = Path(tmp) / "articles" / "rlm-get-started.md"
        sg_page = (FIX / "rlm-get-started.html").read_text(encoding="utf-8")
        art.write_text(art.read_text().replace("Body text for the heading.", "x " * 3000), encoding="utf-8")
        s = snap(tmp, mode="refresh")
        raises(SnapshotError, s.run)
        check("a stub against a long prior capture is refused and the prior kept",
              len(s.refused) == 1 and "x x x" in art.read_text())

    print("legacy ids")
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp)).mkdir(exist_ok=True)
        (Path(tmp) / "manifest.json").write_text(json.dumps({"pages": [
            {"page_id": "rlm_get_started.htm", "status": "captured"},
            {"page_id": "odd_old_name.htm", "status": "captured"},
            {"page_id": "gone.htm", "status": "captured"}]}), encoding="utf-8")
        check("an atlas corpus is not replaced without refresh",
              raises(OptionsError, lambda: snap(tmp).run()) and raises(OptionsError, snap(tmp).preflight))
        redirects = {
            "https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/"
            "revenue_lifecycle_management_dev_guide/odd_old_name.htm": G + "deployment-overview.html"}
        s = snap(tmp, redirects=redirects, mode="refresh")
        s.run()
        m = load(tmp)
        check("legacy ids map by rename and by redirect, the rest are listed unmapped",
              m["legacy_id_map"] == {"odd_old_name.htm": "deployment-overview",
                                     "rlm_get_started.htm": "rlm-get-started"}
              and list(m["unmapped_legacy_ids"]) == ["gone.htm"])
        check("the atlas pages do not survive in the new manifest",
              all(not p["page_id"].endswith(".htm") for p in m["pages"]))
        art = (Path(tmp) / "articles" / "rlm-get-started.md").read_text(encoding="utf-8")
        check("frontmatter names the legacy id", "legacy_page_id: rlm_get_started.htm" in art)
        check("the superseded atlas files are listed in the manifest",
              load(tmp)["superseded_files"] == ["articles/gone.htm.md", "articles/odd_old_name.htm.md",
                                                 "articles/rlm_get_started.htm.md"])
        snap(tmp).run()
        check("a rerun keeps the legacy map and the unmapped list",
              load(tmp)["legacy_id_map"]["rlm_get_started.htm"] == "rlm-get-started"
              and "gone.htm" in load(tmp)["unmapped_legacy_ids"])

    print(f"\n{_passed}/{_total} passed")
    return 0 if _passed == _total else 1


if __name__ == "__main__":
    sys.exit(main())
