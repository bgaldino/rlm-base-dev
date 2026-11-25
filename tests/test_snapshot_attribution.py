"""Offline tests for _core.backfill_attribution (footer for retained atlas articles).

Run:  python3 tests/test_snapshot_attribution.py   (stdlib only)
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.doc_snapshot import guard  # noqa: E402
from scripts.doc_snapshot._core import attribution_note, backfill_attribution  # noqa: E402

_passed = _total = 0


def check(label, cond):
    global _passed, _total
    _total += 1
    _passed += bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


URL = "https://developer.salesforce.com/docs/atlas.en-us.x.meta/x/a.htm"
FM = f"---\npage_id: a.htm\ntitle: A\nsource_url: {URL}\nfetched_at: 2026-08-24\n---\n\n"
BODY = "# A\n\nBody.\n\n```\ncode\n```\n"

with tempfile.TemporaryDirectory() as tmp:
    out = Path(tmp) / "guide"
    arts = out / "articles"
    arts.mkdir(parents=True)
    (arts / "a.htm.md").write_text(FM + BODY, encoding="utf-8")
    help_url = "https://help.salesforce.com/s/articleView?id=x.htm&type=5"
    (arts / "h.md").write_text(FM.replace(URL, help_url) + BODY, encoding="utf-8")
    done = attribution_note(URL, "Salesforce developer documentation")
    (arts / "done.md").write_text(FM + BODY + "\n" + done + "\n", encoding="utf-8")
    (arts / "nofm.md").write_text("# no frontmatter\n", encoding="utf-8")
    (out / "index.md").write_text("# Index\n", encoding="utf-8")

    before = (arts / "a.htm.md").read_text(encoding="utf-8")
    changed = backfill_attribution(arts)
    got = (arts / "a.htm.md").read_text(encoding="utf-8")
    check("footer appended to a retained article", sorted(changed) == ["a.htm.md", "h.md"])
    check("footer is exactly attribution_note, last, after the body",
          got == before.rstrip() + "\n\n" + done + "\n")
    check("help source uses the Help label",
          (arts / "h.md").read_text(encoding="utf-8").endswith(
              attribution_note(help_url, "Salesforce Help content") + "\n"))
    check("guard comparison ignores the footer",
          guard.body_of(got) == guard.body_of(before))
    check("an article with a footer is untouched",
          (arts / "done.md").read_text(encoding="utf-8") == FM + BODY + "\n" + done + "\n")
    check("a file without frontmatter is untouched",
          (arts / "nofm.md").read_text(encoding="utf-8") == "# no frontmatter\n")
    check("index.md is untouched", (out / "index.md").read_text(encoding="utf-8") == "# Index\n")
    check("rerun adds nothing and never duplicates",
          backfill_attribution(arts) == []
          and (arts / "a.htm.md").read_text(encoding="utf-8").count("Source attribution") == 1)
    check("a missing directory is a no-op", backfill_attribution(out / "nope") == [])

print(f"\n{_passed}/{_total} passed")
sys.exit(0 if _passed == _total else 1)
