"""Offline tests for _core.backfill_attribution (footer for retained atlas articles).

Run:  python3 tests/test_snapshot_attribution.py   (stdlib only)
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.doc_snapshot import check as check_mod, cli, guard  # noqa: E402
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
    changed, skipped = backfill_attribution(arts)
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
          backfill_attribution(arts)[0] == []
          and (arts / "a.htm.md").read_text(encoding="utf-8").count("Source attribution") == 1)
    check("a missing directory is a no-op", backfill_attribution(out / "nope") == ([], []))

    check("a file without frontmatter is reported skipped, with a reason",
          skipped == [("nofm.md", "no-frontmatter")])

# check: flags a missing footer, passes a footer, ignores index.md (scan runs against a fake repo root)
import contextlib, io  # noqa: E402


def run_scan(root, fn):
    old = check_mod.REPO_ROOT
    check_mod.REPO_ROOT = root
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = fn()
    finally:
        check_mod.REPO_ROOT = old
    return rc, buf.getvalue()


with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    arts = root / "docs" / "salesforce" / "999" / "g" / "articles"
    arts.mkdir(parents=True)
    (arts / "good.md").write_text(FM + BODY + "\n" + attribution_note(URL, "x") + "\n", encoding="utf-8")
    (arts.parent / "index.md").write_text(FM + BODY, encoding="utf-8")
    rc, out = run_scan(root, lambda: check_mod.scan("999"))
    check("check passes (0) when every article has a footer and index.md has none", rc == 0 and "index.md" not in out)
    (arts / "bad.md").write_text(FM + BODY, encoding="utf-8")
    rc, out = run_scan(root, lambda: check_mod.scan("999"))
    check("check flags an article with no footer and returns non-zero",
          rc == 1 and "bad.md" in out and "good.md" not in out and "index.md" not in out)
    changed, _ = backfill_attribution(arts)
    rc, _ = run_scan(root, lambda: check_mod.scan("999"))
    check("check agrees with the backfill: clean after it", changed == ["bad.md"] and rc == 0)

# skips are recorded; unwritable is a failure, no source_url is not
with tempfile.TemporaryDirectory() as tmp:
    arts = Path(tmp) / "articles"
    arts.mkdir()
    (arts / "nosrc.md").write_text("---\ntitle: T\n---\n\nbody\n", encoding="utf-8")
    (arts / "bin.md").write_bytes(b"\xff\xfe\x00bad")
    ch, sk = backfill_attribution(arts)
    check("no source_url and unreadable files are listed as skipped, not changed",
          ch == [] and dict(sk) == {"nosrc.md": "no-source_url", "bin.md": "unreadable: UnicodeDecodeError"})

# backfill-attribution exit code: unreadable fails, no source_url does not
for bad_name, content, want in (("nosrc.md", "---\ntitle: T\n---\n\nbody\n", 0), ("bin.md", b"\xff\xfe\x00bad", 1)):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        arts = root / "docs" / "salesforce" / "999" / "g" / "articles"
        arts.mkdir(parents=True)
        f = arts / bad_name
        f.write_bytes(content if isinstance(content, bytes) else content.encode())
        ns = type("A", (), {"release": "999"})()
        rc, out = run_scan(root, lambda: cli.cmd_backfill_attribution(ns, {}, None))
        check(f"backfill-attribution exit {want} and prints the skipped {bad_name}", rc == want and bad_name in out)

print(f"\n{_passed}/{_total} passed")
sys.exit(0 if _passed == _total else 1)
