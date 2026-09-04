"""Unit tests for tasks/rlm_snapshot_help.py — discovery guard + stabilization loop.

Exercises `_validate_discovery` (pack 146: fail loud on a thin/empty walk) and
`_discover_articles`'s polling loop (pack 146 companion: the sidebar hydrates
at variable speed, so a single fixed wait races — live probing showed 3 of 4
single-read trials at a fixed 3s wait succeeding and one catching the tree
mid-hydration) against a fake `page` stub. No browser or CumulusCI runtime is
needed: `_validate_discovery` uses only `self.options`, and `_discover_articles`
only calls `page.goto` / `page.wait_for_timeout` / `page.evaluate`, all of
which the stub fakes.

Run:  <cci-venv-python> tests/test_snapshot_help.py
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tasks.rlm_snapshot_help import (  # noqa: E402
    SnapshotSalesforceHelp,
    CommandException,
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

    def error(self, msg):
        pass


def _task(**options):
    # Neither _validate_discovery nor _discover_articles touch CumulusCI init
    # state (org_config, project_config, etc.) — only self.options/self.logger —
    # so bypass BaseTask.__init__ entirely.
    t = SnapshotSalesforceHelp.__new__(SnapshotSalesforceHelp)
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

    async def goto(self, url, wait_until=None):
        pass

    async def wait_for_timeout(self, ms):
        pass

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
        t._validate_discovery(0, 3)
        check("zero kept raises", False)
    except CommandException:
        check("zero kept raises", True)

    check("nonzero kept with no expect_min_articles passes",
          t._validate_discovery(1, 3) is None)

    t2 = _task(expect_min_articles=50)
    try:
        t2._validate_discovery(10, 12)
        check("below expect_min_articles raises", False)
    except CommandException:
        check("below expect_min_articles raises", True)
    check("at-or-above expect_min_articles passes",
          t2._validate_discovery(50, 60) is None)

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
    result = asyncio.run(run_discover(t3, page3))
    check("recovers from a mid-hydration partial read to the stabilized count",
          len(result) == 83)

    # Already-stable on the first read: two consecutive equal non-zero reads
    # required, so it takes exactly 2 polls even when the count never moves.
    t4 = _task()
    page4 = _FakePage([_articles([f"ind.example_{n}.htm" for n in range(5)])])
    result4 = asyncio.run(run_discover(t4, page4))
    check("stable-from-the-start still returns the full set",
          len(result4) == 5)
    check("stable-from-the-start needs only 2 reads to confirm stability",
          page4.evaluate_calls == 2)

    # Never stabilizes (count keeps climbing) and never returns a bare-zero
    # count either — must bail out at discover_timeout_ms rather than loop
    # forever, returning whatever the last read saw.
    t5 = _task(wait_ms=1, discover_timeout_ms=3)
    page5 = _FakePage([
        _articles([f"ind.example_{n}.htm" for n in range(n)]) for n in (1, 2, 3, 4, 5)
    ])
    result5 = asyncio.run(run_discover(t5, page5))
    check("bails out at discover_timeout_ms instead of looping forever",
          page5.evaluate_calls <= 4)  # ceil(discover_timeout_ms / wait_ms) + 1

    # A walk that never finds anything (all reads empty) must still terminate
    # at discover_timeout_ms — this is the raw walker path pack 146's guard
    # then rejects via _validate_discovery, not an infinite loop here.
    t6 = _task(wait_ms=1, discover_timeout_ms=3)
    page6 = _FakePage([[]])
    result6 = asyncio.run(run_discover(t6, page6))
    check("an always-empty walk terminates rather than looping forever",
          result6 == [])

    print(f"\n{_passed}/{_total} checks passed.")
    return 0 if _passed == _total else 1


if __name__ == "__main__":
    sys.exit(main())
