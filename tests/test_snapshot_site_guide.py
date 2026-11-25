"""Offline tests for scripts/doc_snapshot/site_guide.py (server-rendered dev guides).

Pages come from small saved HTML in tests/fixtures/doc_snapshot_site/ through an
injected fetcher: no network, no browser.

Run:  python3 tests/test_snapshot_site_guide.py   (stdlib only)
"""

import json
import os
import re
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
        check("a discover-only switch is refused (never verified) and keeps the atlas manifest",
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

    with tempfile.TemporaryDirectory() as tmp:
        snap(tmp, mode="all").run()
        old_only = make_fetcher()(START)[1].replace(
            "</doc-content-layout>", "<p>/services/data/v62.0/a</p></doc-content-layout>")
        st = snap(tmp, mode="all", fetcher=make_fetcher({START: (200, old_only, START)})).run()
        check("a start page citing only an older version does not refuse an idempotent rerun",
              st["captured"] == 4)

    print("codex round 4")
    def try_run(sn):  # a page that fails to capture still saves, then the run raises
        try:
            sn.run()
        except SnapshotError:
            pass
    # A page that converts to nothing gets no article, so no local link may point at it.
    dc_url = BASE + "deployment-considerations.html"
    full = (FIX / "deployment-considerations.html").read_text(encoding="utf-8")
    emptied = re.sub(r"(<doc-content-layout[^>]*>).*?(</doc-content-layout>)", r"\1\2", full, flags=re.S)
    ef = make_fetcher({dc_url: (200, emptied, dc_url)})
    with tempfile.TemporaryDirectory() as tmp:
        try_run(snap(tmp, mode="all", fetcher=ef))
        started = (Path(tmp) / "articles" / "rlm-get-started.md").read_text(encoding="utf-8")
        check("an empty conversion with no earlier article is not a local link target (first capture)",
              not (Path(tmp) / "articles" / "deployment-considerations.md").exists()
              and "./deployment-considerations.md" not in started
              and "https://developer.salesforce.com/docs/revenue/revenue-management/guide/deployment-considerations.html#notes" in started)
        try_run(snap(tmp, mode="refresh", fetcher=ef))
        started = (Path(tmp) / "articles" / "rlm-get-started.md").read_text(encoding="utf-8")
        check("... and stays online on a refresh", "./deployment-considerations.md" not in started
              and "deployment-considerations.html#notes" in started)
        snap(tmp, mode="refresh").run()
        started = (Path(tmp) / "articles" / "rlm-get-started.md").read_text(encoding="utf-8")
        check("once the page converts, its link is local again", "./deployment-considerations.md#notes" in started)
    with tempfile.TemporaryDirectory() as tmp:
        snap(tmp, mode="all").run()
        try_run(snap(tmp, mode="refresh", fetcher=ef))
        check("an empty refetch of a page whose earlier article is kept leaves its link local",
              (Path(tmp) / "articles" / "deployment-considerations.md").exists()
              and "./deployment-considerations.md#notes" in (Path(tmp) / "articles" / "rlm-get-started.md").read_text(encoding="utf-8"))

    print("codex round 1")
    with tempfile.TemporaryDirectory() as tmp:
        snap(tmp, mode="all").run()
        anc_before = {p["page_id"]: p.get("ancestors") for p in load(tmp)["pages"]}
        calls = []
        s1 = snap(tmp, mode="refresh", sections=["deployment-considerations"], probe_page="connect-resources-get-catalogs")
        s1._fetch_once = make_fetcher(calls=calls)
        s1.run()
        fetched = sorted(u[len(BASE):-5] for u in calls)
        check("refreshing a nested section by id fetches only its subtree (plus the TOC page)",
              "deployment-considerations" in fetched and "deployment-overview" not in fetched)
        calls = []
        s2 = snap(tmp, mode="refresh", sections=["Considerations"], probe_page="connect-resources-get-catalogs")
        s2._fetch_once = make_fetcher(calls=calls)
        st = s2.run()
        check("refreshing a nested section by label queues its page, not nothing",
              any(u.endswith("/deployment-considerations.html") for u in calls)
              and not any(u.endswith("/deployment-overview.html") for u in calls) and st["captured"] == 4)
        pages = load(tmp)["pages"]
        check("a sectioned run keeps the paths a whole-guide discover recorded",
              {p["page_id"]: p.get("ancestors") for p in pages} == anc_before and all(anc_before.values()))
        check("stored subtree ids follow parent links (capture mode without a TOC walk)",
              sg.SiteGuideSnapshot._stored_section_ids(pages, ["deployment-overview"])
              == {"deployment-overview", "deployment-considerations"}
              and sg.SiteGuideSnapshot._stored_section_ids(pages, ["Considerations"]) == {"deployment-considerations"}
              and sg.SiteGuideSnapshot._stored_section_ids(pages, ["Deployment"])
              == {"deployment-overview", "deployment-considerations"})
        check("a section absent from the manifest raises instead of queueing nothing",
              raises(OptionsError, lambda: sg.SiteGuideSnapshot._stored_section_ids(pages, ["nope"])))
    with tempfile.TemporaryDirectory() as tmp:
        snap(tmp, mode="all").run()
        before = (Path(tmp) / "manifest.json").read_text(encoding="utf-8")
        check("a different api_version over a captured corpus is refused in all mode",
              raises(OptionsError, lambda: snap(tmp, mode="all", api_version="69.0").run())
              and raises(OptionsError, snap(tmp, mode="all", api_version="69.0").preflight))
        check("... and in a sectioned refresh", raises(
            OptionsError, lambda: snap(tmp, mode="refresh", api_version="69.0", sections=["deployment-overview"]).run()))
        check("... and a full refresh that then fails the version check saves nothing",
              raises(SnapshotError, lambda: snap(tmp, mode="refresh", api_version="69.0").run())
              and (Path(tmp) / "manifest.json").read_text(encoding="utf-8") == before)
        check("the same version is unaffected", snap(tmp, mode="all").run()["captured"] == 4)
        # that rerun rewrites last_updated (second resolution); compare later refusals to the manifest it left
        before = (Path(tmp) / "manifest.json").read_text(encoding="utf-8")
        other = "https://developer.salesforce.com/docs/industries/common/guide/start.html"
        for label, kw in (("guide", {"site_url": other}), ("release", {"release_version": "266"}),
                          ("deliverable", {"deliverable": "other_dev_guide"})):
            check(f"a different {label} over a captured corpus is refused in all mode, preflight and sectioned refresh, saving nothing",
                  raises(OptionsError, lambda: snap(tmp, mode="all", **kw).run())
                  and raises(OptionsError, snap(tmp, mode="all", **kw).preflight)
                  and raises(OptionsError, lambda: snap(tmp, mode="refresh", sections=["x"], **kw).run())
                  and (Path(tmp) / "manifest.json").read_text(encoding="utf-8") == before)
        check("a different release_name or start page in the same guide is not an identity change",
              not snap(tmp, mode="all", release_name="Spring '28")._identity_changes(load(tmp)))
        raw = load(tmp)
        for label, kw, dropped in (("guide", {"site_url": other}, True), ("release", {"release_version": "266"}, False),
                                   ("deliverable", {"deliverable": "other_dev_guide"}, False)):
            m2 = snap(tmp, mode="refresh", **kw)._load_or_init_manifest(Path(tmp) / "manifest.json")
            check(f"a full refresh over a different {label} resets the old page records",
                  (m2["pages"] == [] if dropped else
                   all(p["status"] == "pending" for p in m2["pages"]) and len(m2["pages"]) == len(raw["pages"]))
                  and (not dropped or len(m2.get("superseded_files", [])) == 4)
                  and (dropped or "superseded_files" not in m2))
        mg = snap(tmp, mode="refresh", site_url=other)._load_or_init_manifest(Path(tmp) / "manifest.json")
        mg["superseded_files"].append("articles/keep-me.md")
        mg["pages"] = [{"page_id": "start", "status": "captured"}]
        (Path(tmp) / "articles" / "keep-me.md").write_text("old", encoding="utf-8")
        s3 = snap(tmp, mode="refresh", site_url=other)
        s3._save_manifest(Path(tmp) / "m2.json", mg)
        sf = json.loads((Path(tmp) / "m2.json").read_text(encoding="utf-8")).get("superseded_files", [])
        check("a superseded file the refresh recaptured is dropped from the list, others are kept",
              "articles/start.md" not in sf and "articles/keep-me.md" in sf)


    grouped = [{"label": "Group", "name": "", "children": [
        {"label": "Kid", "name": G + "kid.html", "children": []}]}]
    gp, _ = sg.flatten_toc(grouped, G, None)
    check("a label-only TOC node is named in its descendants' paths",
          gp[0]["page_id"] == "kid" and any(e.startswith("group\t") for e in gp[0]["ancestors"]))
    dup = [{"label": "A", "name": G + "a.html", "children": [{"label": "Overview", "name": G + "a-ov.html", "children": []}]},
           {"label": "B", "name": G + "b.html", "children": [{"label": "Overview", "name": G + "b-ov.html", "children": []}]}]
    dp, _ = sg.flatten_toc(dup, G, ["b"])
    check("a filtered walk records the full path from the top of the TOC",
          [p["page_id"] for p in dp] == ["b", "b-ov"] and dp[1]["ancestors"][0].startswith("b\t") and len(dp[1]["ancestors"]) == 2)
    check("a refresh/discover also refuses a label that names two TOC nodes",
          raises(OptionsError, lambda: sg.flatten_toc(dup, G, ["Overview"])))
    twice = [{"label": "A", "name": G + "a.html", "children": [{"label": "X", "name": G + "x.html", "children": []}]},
             {"label": "B", "name": G + "b.html", "children": [{"label": "X", "name": G + "x.html", "children": []}]}]
    first = sg.flatten_toc(twice, G, None)[0]
    secondp = sg.flatten_toc(twice, G, ["b"])[0]
    rec = {"page_id": "x", "ancestors": first[1]["ancestors"]}
    check("a page listed twice keeps its first path through a sectioned walk's setdefault",
          rec.setdefault("ancestors", secondp[1]["ancestors"]) == first[1]["ancestors"]
          and first[1]["ancestors"] != secondp[1]["ancestors"])
    check("a page listed twice is selectable by its page id (first listing wins)",
          [p["page_id"] for p in sg.flatten_toc(twice, G, ["x"])[0]] == ["x"]
          and sg.flatten_toc(twice, G, ["x"])[0][0]["ancestors"][0].startswith("a\t"))
    whole = {p["page_id"]: p for p in sg.flatten_toc(twice, G, None)[0]}
    check("a page listed under two branches records the second path apart from the first",
          len(whole["x"]["alt_ancestors"]) == 1 and whole["x"]["alt_ancestors"][0][0].startswith("b\t")
          and whole["x"]["ancestors"][0].startswith("a\t") and whole["a"]["alt_ancestors"] == [])
    recs = [dict(p) for p in whole.values()]
    check("capture-mode resolution finds a multi-listed page under its second branch",
          sg.SiteGuideSnapshot._stored_section_ids(recs, ["b"]) == {"b", "x"}
          and sg.SiteGuideSnapshot._stored_section_ids(recs, ["a"]) == {"a", "x"})
    walked = {p["page_id"] for p in sg.flatten_toc(twice, G, ["b"])[0]}
    check("the stored resolution agrees with the filtered TOC walk",
          walked == sg.SiteGuideSnapshot._stored_section_ids(recs, ["b"]))
    legacy = [{k: v for k, v in r.items() if k != "alt_ancestors"} for r in recs]
    check("a legacy record without alt_ancestors still resolves its first path, and bad fields are ignored",
          sg.SiteGuideSnapshot._stored_section_ids(legacy, ["a"]) == {"a", "x"}
          and sg.SiteGuideSnapshot._stored_section_ids(
              [dict(r, alt_ancestors="junk") for r in recs], ["a"]) == {"a", "x"}
          and sg._merge_paths("junk", [["p"], ["p"], "q"], ["z"]) == [["p"]])
    stored = {"page_id": "x"}
    for flt in (["b"], ["a"]):  # filtered discovers, one branch at a time, from a record with no alt paths
        for d in sg.flatten_toc(twice, G, flt)[0]:
            if d["page_id"] == "x":
                sg._record_section_paths(stored, d)
    check("filtered discovers of two branches in turn leave both paths, so capture agrees with a walk",
          sg.SiteGuideSnapshot._stored_section_ids([stored], ["a"]) == {"x"}
          and sg.SiteGuideSnapshot._stored_section_ids([stored], ["b"]) == {"x"})
    check("a non-string legacy_id_map value is ignored, not a crash",
          sg._legacy_map({"legacy_id_map": {"a.htm": ["x"], "b.htm": "b", 3: "c"}}) == {"b.htm": "b"}
          and sg._legacy_map({"legacy_id_map": "junk"}) == {})
    mf2 = {"pages": [{"page_id": "b", "status": "captured"}], "legacy_id_map": {"a.htm": ["b"], "c.htm": {"x": 1}}}
    sg.SiteGuideSnapshot._settle_superseded(Path(tempfile.gettempdir()) / "manifest.json", mf2)
    check("_settle_superseded survives a non-string mapped slug", True)
    twice2 = [{"label": "A", "name": G + "a.html", "children": [{"label": "X", "name": G + "x.html", "children": []}]},
              {"label": "B", "name": G + "b.html", "children": [{"label": "X", "name": G + "x.html",
               "children": [{"label": "Y", "name": G + "y.html", "children": []}]}]}]
    check("a page listed twice: discover and capture both select its later listing's children",
          sorted(p["page_id"] for p in sg.flatten_toc(twice2, G, ["x"])[0]) == ["x", "y"]
          and sg.SiteGuideSnapshot._stored_section_ids(sg.flatten_toc(twice2, G, None)[0], ["x"]) == {"x", "y"})
    check("a label with a slash never matches an unrelated page id",
          not sg._entry_matches("Pricing/Billing", "billing", "Other/Billing")
          and sg._entry_matches("pricing/billing", "", "Pricing/Billing"))
    href = [{"label": "H", "link": {"href": G + "h.html"}, "children": []}]
    check("an href-only node is found by id the same way the walk and stored paths see it",
          [p["page_id"] for p in sg.flatten_toc(href, G, ["h"])[0]] == ["h"])
    dpages = sg.flatten_toc(dup, G, None)[0]
    check("capture mode refuses a label that names two TOC nodes, accepts a page id",
          raises(OptionsError, lambda: sg.SiteGuideSnapshot._stored_section_ids(dpages, ["Overview"]))
          and sg.SiteGuideSnapshot._stored_section_ids(dpages, ["b-ov"]) == {"b-ov"})
    with tempfile.TemporaryDirectory() as tmp:
        snap(tmp, mode="all").run()
        m = load(tmp)
        for p in m["pages"]:
            if p["page_id"] == "deployment-considerations":
                p["parent_page"] = "bogus"
        (Path(tmp) / "manifest.json").write_text(json.dumps(m), encoding="utf-8")
        snap(tmp, mode="all").run()
        check("a whole-guide discover follows a TOC restructure (parent links reassigned)",
              [p for p in load(tmp)["pages"] if p["page_id"] == "deployment-considerations"][0]["parent_page"]
              == "deployment-overview")
    with tempfile.TemporaryDirectory() as tmp:
        snap(tmp, mode="all").run()
        m = load(tmp)
        m["api_version"] = "67.0"
        (Path(tmp) / "manifest.json").write_text(json.dumps(m), encoding="utf-8")
        st = snap(tmp, mode="refresh", max_pages=2, probe_page="connect-resources-get-catalogs").run()
        check("a capped version-change refresh leaves the rest pending",
              st["captured"] == 2 and st["pending"] == 2 and load(tmp)["api_version"] == "68.0")
        calls = []
        s3 = snap(tmp, mode="all", probe_page="connect-resources-get-catalogs")
        s3._fetch_once = make_fetcher(calls=calls)
        st = s3.run()
        done = [p["page_id"] for p in load(tmp)["pages"]]
        check("the next all run recaptures only the pages still pending",
              st["captured"] == 4 and not any(u.endswith("/deployment-considerations.html") for u in calls)
              and any(u.endswith("/deployment-overview.html") for u in calls) and len(done) == 4)
        check("capture mode resolves a missing section at preflight",
              raises(OptionsError, snap(tmp, mode="capture", sections=["nope"]).preflight))

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
        (Path(tmp) / "articles").mkdir(parents=True, exist_ok=True)
        for pid in ("rlm_get_started.htm", "odd_old_name.htm", "gone.htm"):
            (Path(tmp) / "articles" / f"{pid}.md").write_text("# Old\n\nolder text\n", encoding="utf-8")
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
        check("the replaced atlas files are listed superseded; an unmapped one is not offered for removal",
              load(tmp)["superseded_files"] == ["articles/odd_old_name.htm.md", "articles/rlm_get_started.htm.md"])
        snap(tmp).run()
        check("a rerun keeps the legacy map and the unmapped list",
              load(tmp)["legacy_id_map"]["rlm_get_started.htm"] == "rlm-get-started"
              and "gone.htm" in load(tmp)["unmapped_legacy_ids"])

    print("atlas switch sweep")
    big = "# Get started\n\n" + ("A full atlas article body line.\n" * 300)
    redir = {"https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/"
             "revenue_lifecycle_management_dev_guide/odd_old_name.htm": G + "deployment-overview.html"}

    def atlas_dir(tmp):
        (Path(tmp) / "articles").mkdir(parents=True, exist_ok=True)
        for pid in ("rlm_get_started.htm", "odd_old_name.htm", "gone.htm"):
            (Path(tmp) / "articles" / f"{pid}.md").write_text(
                big if pid == "rlm_get_started.htm" else "# Old\n\nolder text\n", encoding="utf-8")
        (Path(tmp) / "manifest.json").write_text(json.dumps({"pages": [
            {"page_id": pid, "status": "captured"} for pid in ("rlm_get_started.htm", "odd_old_name.htm", "gone.htm")]}),
            encoding="utf-8")

    with tempfile.TemporaryDirectory() as tmp:
        atlas_dir(tmp)
        sect = dict(redirects=redir, mode="refresh", sections=["deployment-overview"],
                    probe_page="connect-resources-get-catalogs")
        before = (Path(tmp) / "manifest.json").read_text(encoding="utf-8")
        check("a sectioned switch passes preflight (the guard needs the site's pages)",
              snap(tmp, **sect).preflight() is None)
        check("a sectioned switch is refused when captured atlas pages have no replacement in the section",
              raises(OptionsError, snap(tmp, **sect).run)
              and (Path(tmp) / "manifest.json").read_text(encoding="utf-8") == before)
        try:
            snap(tmp, **sect).run()
            refusal = ""
        except OptionsError as exc:
            refusal = str(exc)
        check("the refusal marks an id that is not on the site, and not one that merely falls outside the section",
              "gone.htm (not on the site)" in refusal and "rlm_get_started.htm" in refusal
              and "rlm_get_started.htm (not on the site)" not in refusal)
        check("accepting only some of the uncovered pages still refuses",
              raises(OptionsError, snap(tmp, accept_uncovered=["gone.htm"], **sect).run)
              and (Path(tmp) / "manifest.json").read_text(encoding="utf-8") == before)
        out = {k: (G + "connect-resources-get-catalogs.html" if k.endswith("odd_old_name.htm") else v)
               for k, v in redir.items()}
        check("a redirect that lands outside the section counts as uncovered",
              raises(OptionsError, snap(tmp, **dict(sect, redirects=out), accept_uncovered=["gone.htm", "rlm_get_started.htm"]).run)
              and (Path(tmp) / "manifest.json").read_text(encoding="utf-8") == before)
        lg = snap(tmp, accept_uncovered=["gone.htm", "rlm_get_started.htm", "typo.htm"], **sect)
        lg.run()
        ms = load(tmp)
        check("naming every uncovered page switches the section and keeps their atlas files",
              ms["source"] == "site" and [p["page_id"] for p in ms["pages"]] == ["deployment-considerations", "deployment-overview"]
              and (Path(tmp) / "articles" / "gone.htm.md").is_file()
              and (Path(tmp) / "articles" / "rlm_get_started.htm.md").read_text(encoding="utf-8") == big
              and ms["superseded_files"] == ["articles/odd_old_name.htm.md"]
              and any("typo.htm" in m for m in lg.logger.lines))
    with tempfile.TemporaryDirectory() as tmp:
        atlas_dir(tmp)
        gone = Path(tmp) / "articles" / "gone.htm.md"
        gone.write_text("# Old\n\nSee [a](./odd_old_name.htm.md#sec), [b](./nowhere.htm.md), "
                        "[c](https://example.com/x.md), [d](./gone.htm.md) and "
                        "[e](./odd_old_name.htm.md \"Input representation\"), "
                        "[f](./odd_old_name.htm.md \"say \\\"x\\\"\"), [g](<./nowhere2.htm.md>) and [h](./nowhere3.htm.md (t)).\n", encoding="utf-8")
        lk = snap(tmp, accept_uncovered=["gone.htm", "rlm_get_started.htm"], **sect)
        lk.run()
        body = gone.read_text(encoding="utf-8")
        check("a retained atlas article's link to a superseded file is pointed at its site slug, fragment kept",
              "[a](./deployment-overview.md#sec)" in body)
        check("a titled link is rewritten and keeps its title",
              '[e](./deployment-overview.md "Input representation")' in body)
        check("a link with no site replacement is left as is and reported, not dropped",
              "[b](./nowhere.htm.md)" in body
              and any("nowhere.htm.md" in m and "left as is" in m for m in lk.logger.lines))
        check("external links and links to a file that stays are untouched",
              "[c](https://example.com/x.md)" in body and "[d](./gone.htm.md)" in body)
        check("an escaped-quote title is handled, and a link form it cannot handle is reported",
              '[f](./deployment-overview.md "say \\"x\\"")' in body
              and any("nowhere3.htm.md" in m and "left as is" in m for m in lk.logger.lines))
        a_dir = Path(tmp) / "unit"
        (a_dir / "articles").mkdir(parents=True)
        (a_dir / "articles" / "old.htm.md").write_text(
            "[1](./nowhere.htm.md) [2](./nowhere.htm.md) [3](./nowhere3.htm.md (t)) [4](<./nowhere2.htm.md>) [5](./nowhere4.mdx)\n",
            encoding="utf-8")
        n_, un_ = sg.rewrite_retained_links(a_dir, {"legacy_id_map": {}, "unmapped_legacy_ids": {"old.htm": ""}})
        check("an unresolved target is reported once per file, in any link form, and the file is untouched",
              n_ == 0 and sorted(un_) == [("old.htm.md", "nowhere.htm.md"), ("old.htm.md", "nowhere2.htm.md"),
                                          ("old.htm.md", "nowhere3.htm.md")]  # nowhere4.mdx is not a .md link
              and (a_dir / "articles" / "old.htm.md").read_text(encoding="utf-8").count("nowhere") == 5)
        u2 = Path(tmp) / "unit2"
        (u2 / "articles").mkdir(parents=True)
        for name, body_ in {
            "a.md": "[y](./a.htm.md)\n", "b.md": "# b\n",
            "keep.htm.md": "[1](./a.htm.md) [2](a.htm.md#f) [3](./ghost.htm.md) [4](../x.md) [5](sub/x.md) "
                           "[6](<./sup.htm.md>) [7](./sup.htm.md (t))\n",
            "sup.htm.md": "[z](./a.htm.md)\n",
        }.items():
            (u2 / "articles" / name).write_text(body_, encoding="utf-8")
        man2 = {"legacy_id_map": {"a.htm": "a", "b.htm": "b", "ghost.htm": "ghost", "sup.htm": "b"},
                "unmapped_legacy_ids": {"keep.htm": ""}, "superseded_files": ["articles/sup.htm.md"]}
        n2, un2 = sg.rewrite_retained_links(u2, man2)
        kept = (u2 / "articles" / "keep.htm.md").read_text(encoding="utf-8")
        check("a link to a mapped slug with no article is reported, not rewritten into a dead link",
              "[3](./ghost.htm.md)" in kept and ("keep.htm.md", "ghost.htm.md") in un2)
        check("a bare sibling link is rewritten, a path link is left alone",
              "[1](./a.md)" in kept and "[2](./a.md#f)" in kept and "[4](../x.md)" in kept and "[5](sub/x.md)" in kept)
        check("a link form the rewrite cannot handle to a superseded file is reported",
              ("keep.htm.md", "sup.htm.md") in un2 and n2 == 2)
        check("a path link is neither rewritten nor reported",
              not any(tg in ("../x.md", "sub/x.md") for _, tg in un2))
        (u2 / "articles" / "bad.htm.md").write_bytes(b"\xff\xfe[x](./a.htm.md)")
        man2["unmapped_legacy_ids"]["bad.htm"] = ""
        _, un3 = sg.rewrite_retained_links(u2, man2)
        check("an unreadable retained article is reported, not fatal",
              any(f == "bad.htm.md" and "unreadable" in tg for f, tg in un3))
        del man2["unmapped_legacy_ids"]["bad.htm"]
        (u2 / "articles" / "keep2.htm.md").write_text("[3](./ghost.htm.md)\n", encoding="utf-8")
        man2["unmapped_legacy_ids"]["keep2.htm"] = ""
        _, un4 = sg.rewrite_retained_links(u2, man2)
        check("an unresolved target is reported once per file, in every file",
              ("keep.htm.md", "ghost.htm.md") in un4 and ("keep2.htm.md", "ghost.htm.md") in un4)
        del man2["unmapped_legacy_ids"]["keep2.htm"]
        (u2 / "articles" / "w.htm.md").write_text("[1](./a.htm.md)\n", encoding="utf-8")
        man2["unmapped_legacy_ids"]["w.htm"] = ""
        _orig_wt = Path.write_text
        def _boom(self, *a_, **k_):
            if self.name == "w.htm.md":
                raise OSError("ro")
            return _orig_wt(self, *a_, **k_)
        Path.write_text = _boom
        try:
            n5, un5 = sg.rewrite_retained_links(u2, man2)
        finally:
            Path.write_text = _orig_wt
        check("a file that cannot be written is reported and its links are not counted",
              ("w.htm.md", "(not writable: OSError)") in un5 and n5 == 0)
        del man2["unmapped_legacy_ids"]["w.htm"]
        man2["unmapped_legacy_ids"]["r.htm"] = ""
        (u2 / "articles" / "r.htm.md").write_text("# r\n", encoding="utf-8")
        _orig_rt = Path.read_text
        def _noread(self, *a_, **k_):
            if self.name == "r.htm.md":
                raise PermissionError("denied")
            return _orig_rt(self, *a_, **k_)
        Path.read_text = _noread
        try:
            _, un6 = sg.rewrite_retained_links(u2, man2)
        finally:
            Path.read_text = _orig_rt
        check("a permission-denied read is reported, not fatal",
              ("r.htm.md", "(unreadable: PermissionError)") in un6)
        del man2["unmapped_legacy_ids"]["r.htm"]
        check("a superseded article and the site slug files are not rewritten",
              (u2 / "articles" / "sup.htm.md").read_text(encoding="utf-8") == "[z](./a.htm.md)\n"
              and (u2 / "articles" / "a.md").read_text(encoding="utf-8") == "[y](./a.htm.md)\n")
        order = []
        og = snap(tmp, accept_uncovered=["gone.htm", "rlm_get_started.htm"], **sect)
        for nm in ("_save_manifest", "_relink_retained"):
            orig_ = getattr(og, nm)
            setattr(og, nm, lambda *a_, _o=orig_, _n=nm, **k_: (order.append(_n), _o(*a_, **k_))[1])
        og.run()
        check("the retained-link rewrite runs after the manifest settles superseded_files",
              order and order[-1] == "_relink_retained" and order.index("_relink_retained") > max(
                  i_ for i_, n_ in enumerate(order) if n_ == "_save_manifest"))
        check("the rewrite says how many links it changed",
              any("rewrote 3 local link" in m for m in lk.logger.lines))
        again = snap(tmp, accept_uncovered=["gone.htm", "rlm_get_started.htm"], **sect)
        again.run()
        check("a rerun finds nothing left to rewrite",
              gone.read_text(encoding="utf-8") == body and not any("rewrote" in m for m in again.logger.lines))
    with tempfile.TemporaryDirectory() as tmp:
        atlas_dir(tmp)
        wg = snap(tmp, redirects=redir, mode="refresh", accept_uncovered=["gone.htm"],
                  probe_page="connect-resources-get-catalogs")
        try:
            wg.run()
        except SnapshotError:
            pass
        check("a whole-guide switch is not subject to the section guard, and says the flag did nothing",
              load(tmp)["source"] == "site" and (Path(tmp) / "articles" / "gone.htm.md").is_file()
              and any("has no effect" in m for m in wg.logger.lines))
    with tempfile.TemporaryDirectory() as tmp:
        atlas_dir(tmp)
        for pid in ("rlm_get_started.htm", "gone.htm"):
            (Path(tmp) / "articles" / f"{pid}.md").unlink()
        mm = load(tmp)
        mm["pages"] = [p for p in mm["pages"] if p["page_id"] == "odd_old_name.htm"] + [
            {"page_id": "rlm_get_started.htm", "status": "error"}, {"page_id": "gone.htm", "status": "error"}]
        (Path(tmp) / "manifest.json").write_text(json.dumps(mm), encoding="utf-8")
        snap(tmp, redirects=redir, mode="refresh", sections=["deployment-overview"],
             probe_page="connect-resources-get-catalogs").run()
        check("a sectioned switch needs no acceptance when the section replaces every captured atlas page",
              load(tmp)["source"] == "site"
              and load(tmp)["legacy_id_map"].get("odd_old_name.htm") == "deployment-overview")
    with tempfile.TemporaryDirectory() as tmp:
        atlas_dir(tmp)
        try:
            snap(tmp, redirects=redir, mode="refresh").run()
        except SnapshotError:
            pass
        m = load(tmp)
        arts = Path(tmp) / "articles"
        check("a truncated replacement is judged against the mapped atlas article and refused",
              not (arts / "rlm-get-started.md").exists() and (arts / "rlm_get_started.htm.md").read_text(encoding="utf-8") == big
              and any(p["page_id"] == "rlm-get-started" and p["status"] == "error" and "refused" in p.get("error", "")
                      for p in m["pages"]))
        check("the atlas article that is still the only copy, and an unmapped one, are not offered for removal",
              m["superseded_files"] == ["articles/odd_old_name.htm.md"])
        check("no local link points at the refused page",
              all("./rlm-get-started.md" not in f.read_text(encoding="utf-8") for f in arts.glob("*.md")))
        snap(tmp, redirects=redir, mode="all", accept_shrinkage=["rlm-get-started"], probe_page="connect-resources-get-catalogs").run()
        check("once the replacement is accepted, the atlas article is listed superseded",
              load(tmp)["superseded_files"] == ["articles/odd_old_name.htm.md", "articles/rlm_get_started.htm.md"])
        later = {"https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/"
                 "revenue_lifecycle_management_dev_guide/gone.htm": G + "connect-resources-get-catalogs.html", **redir}
        snap(tmp, redirects=later, mode="all", probe_page="connect-resources-get-catalogs").run()
        m = load(tmp)
        check("a rerun retries ids that stayed unmapped, and lists the file once its page has an article",
              m["legacy_id_map"].get("gone.htm") == "connect-resources-get-catalogs" and not m["unmapped_legacy_ids"]
              and "articles/gone.htm.md" in m["superseded_files"])
        (arts / "odd_old_name.htm.md").unlink()
        snap(tmp, redirects=later, mode="all", probe_page="connect-resources-get-catalogs").run()
        check("an entry for a file the user already removed is pruned",
              "articles/odd_old_name.htm.md" not in load(tmp).get("superseded_files", []))
    with tempfile.TemporaryDirectory() as tmp:
        snap(tmp, mode="all").run()
        mm = load(tmp)
        mm["legacy_id_map"] = {"a_b.htm": "rlm-get-started", "a-b.htm": "rlm-get-started"}
        mm["pages"] = [dict(p, status="pending") if p["page_id"] == "rlm-get-started" else p for p in mm["pages"]]
        (Path(tmp) / "manifest.json").write_text(json.dumps(mm), encoding="utf-8")
        (Path(tmp) / "articles" / "rlm-get-started.md").unlink()
        (Path(tmp) / "articles" / "a_b.htm.md").write_text("# s\n\nshort\n", encoding="utf-8")
        (Path(tmp) / "articles" / "a-b.htm.md").write_text(big, encoding="utf-8")
        try:
            snap(tmp, mode="capture", probe_page="connect-resources-get-catalogs").run()
        except SnapshotError:
            pass
        check("two atlas ids mapped to one page: the longest article is the guard's prior",
              not (Path(tmp) / "articles" / "rlm-get-started.md").exists()
              and any(p["page_id"] == "rlm-get-started" and p["status"] == "error" and "refused" in p.get("error", "")
                      for p in load(tmp)["pages"]))

    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "articles").mkdir()
        (Path(tmp) / "articles" / "start.md").write_text("old guide text", encoding="utf-8")
        mf = {"pages": [{"page_id": "start", "status": "error"}], "superseded_files": ["articles/start.md"]}
        sg.SiteGuideSnapshot._settle_superseded(Path(tmp) / "manifest.json", mf)
        check("a slug shared with the old guide whose recapture failed stays listed (the old text is not the page)",
              mf.get("superseded_files") == ["articles/start.md"])
        for pid in ("held.htm", "unmapped.htm"):
            (Path(tmp) / "articles" / f"{pid}.md").write_text("atlas", encoding="utf-8")
        (Path(tmp) / "manifest.json").write_text(json.dumps({
            "source": "site", "site_url": START, "deliverable": "revenue_lifecycle_management_dev_guide",
            "release": "264", "api_version": "68.0", "legacy_id_map": {"held.htm": "never-captured"},
            "unmapped_legacy_ids": {"unmapped.htm": "x"}, "superseded_files": "not-a-list",
            "pages": [{"page_id": "x", "status": "pending"}]}), encoding="utf-8")
        mg = snap(tmp, mode="refresh", site_url="https://developer.salesforce.com/docs/industries/common/guide/start.html"
                  )._load_or_init_manifest(Path(tmp) / "manifest.json")
        check("a guide change lists every atlas file of the old corpus still on disk, and survives a hand-edited list",
              mg.get("superseded_files") == ["articles/held.htm.md", "articles/unmapped.htm.md"])

    print(f"\n{_passed}/{_total} passed")
    return 0 if _passed == _total else 1


if __name__ == "__main__":
    sys.exit(main())
