"""Unit tests for scripts/doc_snapshot/help_portal.py — discovery guard + stabilization loop.

Exercises `_validate_discovery` (pack 146: fail loud on a thin/empty walk) and
`_discover_articles`'s polling loop (pack 146 companion: the sidebar hydrates
at variable speed, so a single fixed wait races — live probing showed 3 of 4
single-read trials at a fixed 3s wait succeeding and one catching the tree
mid-hydration) against a fake `page` stub. No browser or Playwright install is
needed: `_validate_discovery` uses only `self.options`, and `_discover_articles`
only calls `page.goto` / `page.wait_for_timeout` / `page.evaluate`, all of
which the stub fakes.

Run:  python3 tests/test_snapshot_help.py   (stdlib only)
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.doc_snapshot.help_portal import (  # noqa: E402
    HelpSnapshot,
    OptionsError,
    SnapshotError,
)


_passed = _total = 0


def check(label, cond):
    global _passed, _total
    _total += 1
    if cond:
        _passed += 1
        print(f"  [PASS] {label}")
    else:
        print(f"  [FAIL] {label}")


class _NullLogger:
    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


def _task(**options):
    # Neither _validate_discovery nor _discover_articles needs the option
    # normalization __init__ runs — only self.options/self.logger — so bypass
    # __init__ and set exactly the options each check exercises.
    t = HelpSnapshot.__new__(HelpSnapshot)
    t.options = {
        "article_id_prefix": "ind.example",
        "root_article_id": "ind.example_introduction.htm",
        "expect_min_articles": None,
        "wait_ms": 1,
        "discover_timeout_ms": 5,
        "include_release_param": False,
        "release_version": "264",
        **options,
    }
    t.logger = _NullLogger()
    return t


class _FakePage:
    """Stubs the three Playwright Page methods `_discover_articles` calls.

    `evaluate_sequence` is returned one element per call, in order; the last
    element repeats once exhausted (simulates the tree staying stable once
    hydrated).
    """

    def __init__(self, evaluate_sequence):
        self._sequence = evaluate_sequence
        self._i = 0
        self.evaluate_calls = 0
        self.sleeps = []

    async def goto(self, url, wait_until=None):
        pass

    async def wait_for_timeout(self, ms):
        self.sleeps.append(ms)

    async def evaluate(self, js):
        self.evaluate_calls += 1
        idx = min(self._i, len(self._sequence) - 1)
        self._i += 1
        return self._sequence[idx]


def _articles(ids):
    return [{"id": i, "title": i, "parent_id": None} for i in ids]


def main():
    # --- _validate_discovery ---------------------------------------------
    t = _task()
    try:
        t._validate_discovery(0, 3, True)
        check("zero kept raises", False)
    except SnapshotError:
        check("zero kept raises", True)

    check("nonzero kept with no expect_min_articles passes",
          t._validate_discovery(1, 3, True) is None)
    try:
        t._validate_discovery(1, 3, True, only_root=True)
        check("root-only walk raises (wrong root id)", False)
    except SnapshotError:
        check("root-only walk raises (wrong root id)", True)

    t2 = _task(expect_min_articles=50)
    try:
        t2._validate_discovery(10, 12, True)
        check("below expect_min_articles raises", False)
    except SnapshotError:
        check("below expect_min_articles raises", True)
    check("at-or-above expect_min_articles passes",
          t2._validate_discovery(50, 60, True) is None)

    try:
        t2._validate_discovery(60, 60, False)
        check("unstabilized-at-timeout raises even above expect_min_articles", False)
    except SnapshotError:
        check("unstabilized-at-timeout raises even above expect_min_articles", True)

    # --- _validate_timing_options -------------------------------------------
    t7 = _task(wait_ms=0)
    try:
        t7._validate_timing_options()
        check("wait_ms=0 raises", False)
    except OptionsError:
        check("wait_ms=0 raises", True)

    t8 = _task(wait_ms=-100)
    try:
        t8._validate_timing_options()
        check("negative wait_ms raises", False)
    except OptionsError:
        check("negative wait_ms raises", True)

    t9 = _task(discover_timeout_ms=0)
    try:
        t9._validate_timing_options()
        check("discover_timeout_ms=0 raises", False)
    except OptionsError:
        check("discover_timeout_ms=0 raises", True)

    t10 = _task()
    check("positive wait_ms/discover_timeout_ms passes",
          t10._validate_timing_options() is None)

    # --- _discover_articles polling loop -----------------------------------
    async def run_discover(t, page):
        return await t._discover_articles(page)

    # Mid-hydration read (1 article) followed by the stabilized read (83
    # articles) twice in a row — the exact shape seen live against the 264
    # Help portal. Must recover to the stabilized count, not the first read.
    t3 = _task()
    page3 = _FakePage([
        _articles(["ind.example_introduction.htm"]),
        _articles([f"ind.example_{n}.htm" for n in range(83)]),
        _articles([f"ind.example_{n}.htm" for n in range(83)]),
    ])
    result, stabilized3 = asyncio.run(run_discover(t3, page3))
    check("recovers from a mid-hydration partial read to the stabilized count",
          len(result) == 83)
    check("recovered walk reports stabilized", stabilized3 is True)

    # Already-stable on the first read: two consecutive equal non-zero reads
    # required, so it takes exactly 2 polls even when the count never moves.
    t4 = _task()
    page4 = _FakePage([_articles([f"ind.example_{n}.htm" for n in range(5)])])
    result4, stabilized4 = asyncio.run(run_discover(t4, page4))
    check("stable-from-the-start still returns the full set",
          len(result4) == 5)
    check("stable-from-the-start needs only 2 reads to confirm stability",
          page4.evaluate_calls == 2)
    check("stable-from-the-start reports stabilized", stabilized4 is True)

    # Never stabilizes (count keeps climbing) and never returns a bare-zero
    # count either — must bail out at discover_timeout_ms rather than loop
    # forever, returning whatever the last read saw, flagged as unstabilized.
    t5 = _task(wait_ms=1, discover_timeout_ms=3)
    page5 = _FakePage([
        _articles([f"ind.example_{n}.htm" for n in range(n)]) for n in (1, 2, 3, 4, 5)
    ])
    result5, stabilized5 = asyncio.run(run_discover(t5, page5))
    check("bails out at discover_timeout_ms instead of looping forever",
          page5.evaluate_calls <= 4)  # ceil(discover_timeout_ms / wait_ms) + 1
    check("never-stabilizing walk reports unstabilized", stabilized5 is False)

    # Non-divisible, never-stabilizing walk: wait_ms=7 into discover_timeout_ms=10
    # must clamp the second sleep to 3ms (not the full 7ms), so total elapsed time
    # never exceeds the documented budget — PR #408 review round 2.
    t5b = _task(wait_ms=7, discover_timeout_ms=10)
    page5b = _FakePage([
        _articles([f"ind.example_{n}.htm" for n in range(n)]) for n in (1, 2, 3, 4, 5)
    ])
    asyncio.run(run_discover(t5b, page5b))
    check("clamps each sleep to the remaining budget instead of overshooting it",
          page5b.sleeps == [7, 3])

    # A walk that never finds anything (all reads empty) must still terminate
    # at discover_timeout_ms — this is the raw walker path pack 146's guard
    # then rejects via _validate_discovery, not an infinite loop here.
    t6 = _task(wait_ms=1, discover_timeout_ms=3)
    page6 = _FakePage([[]])
    result6, _ = asyncio.run(run_discover(t6, page6))
    check("an always-empty walk terminates rather than looping forever",
          result6 == [])

    # A stable-but-below-floor plateau must keep polling rather than stop early:
    # 1 article holds for 2 reads (would satisfy the bare stability check), then
    # climbs to the full 50 on read 3 and holds there — with expect_min_articles=50,
    # the loop must not exit at the read-2 plateau.
    t7b = _task(expect_min_articles=50, wait_ms=1, discover_timeout_ms=10)
    page7b = _FakePage([
        _articles(["ind.example_0.htm"]),
        _articles(["ind.example_0.htm"]),
        _articles([f"ind.example_{n}.htm" for n in range(50)]),
        _articles([f"ind.example_{n}.htm" for n in range(50)]),
    ])
    result7b, stabilized7b = asyncio.run(run_discover(t7b, page7b))
    check("does not stop at a stable plateau below expect_min_articles",
          len(result7b) == 50)
    check("recovered-above-floor walk reports stabilized", stabilized7b is True)

    # PR #408 review round 3: a walk whose count grows on every single read
    # (never two consecutive equal reads) but is already above
    # expect_min_articles when discover_timeout_ms is hit must still be
    # rejected — _validate_discovery must not accept an unstabilized count
    # just because it clears the floor.
    t7c = _task(expect_min_articles=3, wait_ms=1, discover_timeout_ms=3)
    page7c = _FakePage([
        _articles([f"ind.example_{n}.htm" for n in range(n)]) for n in (1, 2, 3, 4, 5)
    ])
    result7c, stabilized7c = asyncio.run(run_discover(t7c, page7c))
    check("ever-growing walk above the floor still reports unstabilized",
          stabilized7c is False)
    try:
        t7c._validate_discovery(len(result7c), len(result7c), stabilized7c)
        check("validate_discovery rejects an unstabilized above-floor result", False)
    except SnapshotError:
        check("validate_discovery rejects an unstabilized above-floor result", True)

    # PR #485 review: subtree_only prunes from the whole walk, so stability on
    # the kept count alone is not enough. Here the root subtree is complete from
    # the first read while an outside branch is still hydrating; the walk must
    # not stabilize until the full (id, parent) set repeats.
    root = {"id": "rn.rev.htm", "title": "", "parent_id": None}
    outside = [{"id": f"rn.out_{n}.htm", "title": "", "parent_id": None} for n in range(3)]
    t7d = _task(article_id_prefix="rn.", root_article_id="rn.rev.htm",
                subtree_only=True, wait_ms=1, discover_timeout_ms=10)
    page7d = _FakePage([[root] + outside[:1], [root] + outside[:2],
                        [root] + outside, [root] + outside])
    result7d, stabilized7d = asyncio.run(run_discover(t7d, page7d))
    check("subtree_only waits for the out-of-subtree walk to stop changing",
          page7d.evaluate_calls == 4 and len(result7d) == 4)
    check("subtree_only walk reports stabilized once the full set repeats",
          stabilized7d is True)

    # PR #487 review: _classify_subtree also reads top_level, so an
    # aria-level="1" flag that changes between reads whose IDs and parents
    # already repeat must keep the walk polling (2 reads under the old key).
    flat = {"id": "rn.out_top.htm", "title": "", "parent_id": None}
    t7e = _task(article_id_prefix="rn.", root_article_id="rn.rev.htm",
                subtree_only=True, wait_ms=1, discover_timeout_ms=10)
    page7e = _FakePage([[root, flat], [root, dict(flat, top_level=True)]])
    result7e, stabilized7e = asyncio.run(run_discover(t7e, page7e))
    check("subtree_only waits for a late top_level flag to stop changing",
          page7e.evaluate_calls == 3 and stabilized7e is True
          and result7e[1].get("top_level") is True)

    # --- _filter_discovered subtree_only ------------------------------------
    # Release notes share one `release-notes.rn_` prefix across every product,
    # so the prefix alone kept all 1,596 sidebar IDs when only the Revenue
    # subtree was wanted. subtree_only keeps the root and its descendants.
    tree = [
        {"id": "rn.root.htm", "title": "", "parent_id": None},
        {"id": "rn.rev.htm", "title": "", "parent_id": "rn.root.htm"},
        {"id": "rn.rev_billing.htm", "title": "", "parent_id": "rn.rev.htm"},
        {"id": "rn.rev_billing_forecast.htm", "title": "", "parent_id": "rn.rev_billing.htm"},
        {"id": "rn.sales.htm", "title": "", "parent_id": "rn.root.htm"},
        {"id": "rn.sales_x.htm", "title": "", "parent_id": "rn.sales.htm"},
        {"id": "rn.loop_a.htm", "title": "", "parent_id": "rn.loop_b.htm"},
        {"id": "rn.loop_b.htm", "title": "", "parent_id": "rn.loop_a.htm"},
    ]
    t14 = _task(article_id_prefix="rn.", root_article_id="rn.rev.htm")
    check("without subtree_only the prefix alone keeps every ID",
          len(t14._filter_discovered(tree)) == len(tree))
    t15 = _task(article_id_prefix="rn.", root_article_id="rn.rev.htm", subtree_only=True)
    check("subtree_only keeps the root and all its descendants only",
          [d["id"] for d in t15._filter_discovered(tree)]
          == ["rn.rev.htm", "rn.rev_billing.htm", "rn.rev_billing_forecast.htm"])
    t16 = _task(article_id_prefix="rn.rev_", root_article_id="rn.rev.htm", subtree_only=True)
    check("subtree_only still applies the prefix filter",
          [d["id"] for d in t16._filter_discovered(tree)]
          == ["rn.rev_billing.htm", "rn.rev_billing_forecast.htm"])

    # --- _prune_moved_out subtree_only prune (PR #481/#483/#485 review) ----
    # A pre-GA note that moves out of the root subtree must leave this area's
    # manifest and article files, or mode=refresh recaptures it. Only IDs the
    # walk positively saw outside the subtree are pruned: a record merely
    # absent from the walk stays, because a partial walk can stabilize above
    # expect_min_articles. Another area's record in the shared manifest is kept.
    # The prune only edits the manifest and returns the IDs: _async_run deletes
    # the files after saving the manifest, so a crash between the two leaves an
    # orphan file, never a captured record whose file is gone (PR #485 review).
    manifest = {"articles": [
        {"article_id": "rn.rev_billing.htm", "status": "captured", "area": "revenue"},
        {"article_id": "rn.rev_moved.htm", "status": "captured", "area": "revenue"},
        {"article_id": "rn.legacy_moved.htm", "status": "captured"},
        {"article_id": "rn.rev_unseen.htm", "status": "captured", "area": "revenue"},
        {"article_id": "rn.other.htm", "status": "captured", "area": "sales"},
    ]}
    walk = [{"id": "rn.rev.htm", "title": "", "parent_id": None},
            {"id": "rn.rev_billing.htm", "title": "", "parent_id": "rn.rev.htm"}]
    moved = {"rn.rev_moved.htm", "rn.legacy_moved.htm", "rn.other.htm"}
    t17 = _task(area="revenue", subtree_only=True)
    pruned17 = t17._prune_moved_out(manifest, moved)
    check("subtree_only returns the pruned current-area and untagged IDs",
          sorted(pruned17) == ["rn.legacy_moved.htm", "rn.rev_moved.htm"])
    ids = [a["article_id"] for a in t17._merge_discovered(manifest, walk)["articles"]]
    check("subtree_only prunes current-area and untagged records seen outside the subtree",
          ids == ["rn.other.htm", "rn.rev.htm", "rn.rev_billing.htm", "rn.rev_unseen.htm"])
    check("subtree_only keeps a record merely absent from a partial walk",
          "rn.rev_unseen.htm" in ids)
    t18 = _task(area="revenue")
    keep = {"articles": [{"article_id": "rn.rev_moved.htm", "status": "captured", "area": "revenue"}]}
    check("without subtree_only nothing is pruned",
          t18._prune_moved_out(keep, moved) == [])
    check("without subtree_only the merge stays add-only",
          [a["article_id"] for a in t18._merge_discovered(keep, walk)["articles"]]
          == ["rn.rev.htm", "rn.rev_billing.htm", "rn.rev_moved.htm"])

    # PR #487 review: the manifest save must happen before the file delete.
    # A save that fails leaves the pruned file in place; a save that succeeds
    # is followed by the delete.
    import pathlib
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        adir = pathlib.Path(tmp)
        stale = adir / "rn.rev_moved.htm.md"
        stale.write_text("x")
        t18b = _task(area="revenue", subtree_only=True)
        events = []

        def failing_save(path, m):
            events.append(("save", stale.exists()))
            raise OSError("disk full")
        t18b._save_manifest = failing_save
        try:
            t18b._save_then_delete(adir / "manifest.json", {}, adir, {"rn.rev_moved.htm"})
        except OSError:
            pass
        check("a failed manifest save leaves the pruned file in place",
              stale.exists() and events == [("save", True)])
        t18b._save_manifest = lambda path, m: events.append(("save", stale.exists()))
        t18b._save_then_delete(adir / "manifest.json", {}, adir, {"rn.rev_moved.htm"})
        check("the manifest is saved before the pruned file is deleted",
              events[-1] == ("save", True) and not stale.exists())

        # PR #487 review: a file orphaned after an earlier run's save has no
        # manifest record left, so the prune cannot return it again. The next
        # validated walk still deletes it, while a moved-out ID that another
        # area records keeps its file.
        orphan = adir / "rn.rev_orphan.htm.md"
        shared = adir / "rn.other.htm.md"
        orphan.write_text("x")
        shared.write_text("x")
        t18b._save_manifest = lambda path, m: None
        t18b._save_then_delete(
            adir / "manifest.json",
            {"articles": [{"article_id": "rn.other.htm", "area": "sales"}]},
            adir, {"rn.rev_orphan.htm", "rn.other.htm"})
        check("a later walk deletes a moved-out file left orphaned by an earlier run",
              not orphan.exists())
        check("a moved-out file another area still records is kept",
              shared.exists())

    # PR #483 review round 3: parent extraction is best-effort, so only a
    # complete chain to an ancestor of the root proves an article moved out.
    # rn.gap's parent is missing from the walk and rn.flat has no parent at
    # all; both are "unknown" and must never be pruned.
    t19 = _task(article_id_prefix="rn.", root_article_id="rn.rev.htm", subtree_only=True)
    gappy = tree + [
        {"id": "rn.gap.htm", "title": "", "parent_id": "rn.unwalked.htm"},
        {"id": "rn.flat.htm", "title": "", "parent_id": None},
    ]
    where = t19._classify_subtree(gappy)
    check("classify: a descendant of the root is in",
          where["rn.rev_billing_forecast.htm"] == "in")
    check("classify: a sibling-branch article with a complete chain is out",
          where["rn.sales_x.htm"] == "out")
    check("classify: a broken or missing parent chain is unknown, not out",
          where["rn.gap.htm"] == where["rn.flat.htm"] == where["rn.loop_a.htm"] == "unknown")
    t20 = _task(article_id_prefix="rn.", root_article_id="rn.orphan_root.htm", subtree_only=True)
    check("classify: without a top-level signal, a parentless end is unknown",
          "out" not in t20._classify_subtree(
              tree + [{"id": "rn.orphan_root.htm", "title": "", "parent_id": None}]).values())
    # The live 264 shape: the Revenue root has no parent, and other sections
    # chain to a separate aria-level 1 tree root. A complete chain to that
    # top-level node is out; a chain broken before it stays unknown.
    live = [
        {"id": "rn.revenue.htm", "title": "", "parent_id": None},
        {"id": "rn.revenue_billing.htm", "title": "", "parent_id": "rn.revenue.htm"},
        {"id": "rn.all.htm", "title": "", "parent_id": None, "top_level": True},
        {"id": "rn.sales.htm", "title": "", "parent_id": "rn.all.htm"},
        {"id": "rn.sales_moved.htm", "title": "", "parent_id": "rn.sales.htm"},
        {"id": "rn.broken.htm", "title": "", "parent_id": "rn.unwalked.htm"},
    ]
    t21 = _task(article_id_prefix="rn.", root_article_id="rn.revenue.htm", subtree_only=True)
    where21 = t21._classify_subtree(live)
    check("classify: a complete chain to another top-level tree root is out",
          where21["rn.sales_moved.htm"] == where21["rn.all.htm"] == "out")
    check("classify: the root's own descendants stay in beside a top-level peer",
          where21["rn.revenue_billing.htm"] == "in")
    check("classify: a chain broken before the top-level node stays unknown",
          where21["rn.broken.htm"] == "unknown")

    # --- _capture_one not-found-shell detection (PR #409 review) -----------
    # The Help portal renders a real H1 for a broken/retired article id
    # instead of a 404 status, so the generic "no H1 found" guard alone
    # doesn't catch it — live-captured on
    # ind.dro_create_custom_context_definition_and_map_attribute_to_field.htm.
    class _FakeCapturePage:
        def __init__(self, eval_result):
            self._eval_result = eval_result

        async def goto(self, url, wait_until=None, timeout=None):
            pass

        async def wait_for_timeout(self, ms):
            pass

        async def evaluate(self, js):
            return self._eval_result

    async def run_capture(t, page):
        return await t._capture_one(page, "ind.example_broken.htm")

    t11 = _task()
    page11 = _FakeCapturePage({
        "title": "We looked high and low\nbut couldn't find that page.",
        "body": "We looked high and low\nbut couldn't find that page.\nGo Home",
        "breadcrumb": None,
    })
    result11 = asyncio.run(run_capture(t11, page11))
    check("rejects the rendered not-found shell as an error",
          "error" in result11 and "not-found" in result11["error"])

    t12 = _task()
    page12 = _FakeCapturePage({
        "title": "A Real Article Title",
        "body": "Substantive real content.",
        "breadcrumb": None,
    })
    result12 = asyncio.run(run_capture(t12, page12))
    check("a genuine article title/body is not flagged as not-found",
          "error" not in result12)

    # --- _capture_articles stale-artifact cleanup on refresh (PR #409 review
    # round 2) -----------------------------------------------------------
    # A `mode: refresh` run on an article that was previously captured
    # successfully but has since become an error (not-found shell, empty
    # body, etc.) must not leave the prior capture's file/body_length behind
    # — a directory scan of articles/*.md that doesn't filter on manifest
    # `status` would otherwise still surface the stale, now-invalid content.
    import tempfile
    from pathlib import Path

    async def run_capture_articles(t, browser, articles, articles_dir, manifest, manifest_path):
        return await t._capture_articles(browser, articles, articles_dir, manifest, manifest_path)

    class _FakeErrorPage:
        async def goto(self, url, wait_until=None, timeout=None):
            pass

        async def wait_for_timeout(self, ms):
            pass

        async def evaluate(self, js):
            return {
                "title": "We looked high and low\nbut couldn't find that page.",
                "body": "We looked high and low\nbut couldn't find that page.\nGo Home",
                "breadcrumb": None,
            }

    class _FakeErrorContext:
        async def new_page(self):
            return _FakeErrorPage()

        async def close(self):
            pass

    class _FakeErrorBrowser:
        async def new_context(self):
            return _FakeErrorContext()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        articles_dir = tmp_path / "articles"
        articles_dir.mkdir()
        article_id = "ind.example_retired.htm"
        stale_path = articles_dir / f"{article_id}.md"
        stale_path.write_text("stale captured content", encoding="utf-8")

        t13 = _task(area="dro", concurrency=1)
        manifest = {
            "articles": [
                {
                    "article_id": article_id,
                    "title": "A Previously Real Title",
                    "status": "captured",
                    "area": "dro",
                    "file": f"articles/{article_id}.md",
                    "body_length": 23,
                }
            ]
        }
        manifest_path = tmp_path / "manifest.json"
        t13._save_manifest = lambda path, m: None  # avoid touching disk mid-run
        t13._article_url = lambda aid: f"https://example.test/{aid}"

        failed13 = asyncio.run(run_capture_articles(
            t13,
            _FakeErrorBrowser(),
            manifest["articles"],
            articles_dir,
            manifest,
            manifest_path,
        ))

        refreshed = manifest["articles"][0]
        check("refresh-to-error clears the stale file field",
              "file" not in refreshed)
        check("refresh-to-error clears the stale body_length field",
              "body_length" not in refreshed)
        check("refresh-to-error deletes the stale markdown file from disk",
              not stale_path.exists())
        check("refresh-to-error preserves the discovery/prior title",
              refreshed["title"] == "A Previously Real Title")
        check("refresh-to-error marks status error",
              refreshed["status"] == "error")
        check("_capture_articles returns this run's failed ids",
              failed13 == [article_id])

    # --- run-level failure reporting ------------------------------------------
    # A run whose own captures errored must exit non-zero (after saving), and a
    # Playwright error must surface as SnapshotError so a batch run continues.
    from scripts.doc_snapshot import _core

    check("no failed captures does not raise",
          _core.raise_on_capture_errors([], 5, "articles") is None)
    try:
        _core.raise_on_capture_errors(["b", "a"], 5, "articles")
        msg = ""
    except SnapshotError as exc:
        msg = str(exc)
    check("failed captures raise SnapshotError naming the ids",
          msg.startswith("2 of 5 articles failed to capture: a, b"))

    import types
    fake_pkg = types.ModuleType("playwright")
    fake_api = types.ModuleType("playwright.async_api")

    class _FakePlaywrightError(Exception):
        pass

    fake_api.Error = _FakePlaywrightError
    saved = {k: sys.modules.get(k) for k in ("playwright", "playwright.async_api")}
    sys.modules.update({"playwright": fake_pkg, "playwright.async_api": fake_api})
    try:
        async def _boom():
            raise _FakePlaywrightError("Timeout 30000ms exceeded")

        async def _fine():
            return {"ok": 1}

        try:
            _core.run_browser(_boom())
            translated = False
        except SnapshotError:
            translated = True
        check("Playwright error becomes SnapshotError", translated)
        check("run_browser returns the coroutine's result",
              _core.run_browser(_fine()) == {"ok": 1})
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v

    print(f"\n{_passed}/{_total} checks passed.")
    return 0 if _passed == _total else 1


if __name__ == "__main__":
    sys.exit(main())
