"""Offline tests for _core.backfill_attribution (footer for retained atlas articles).

Run:  python3 tests/test_snapshot_attribution.py   (stdlib only)
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.doc_snapshot import check as check_mod, cli, guard  # noqa: E402
from scripts.doc_snapshot import site_guide as sg  # noqa: E402
from scripts.doc_snapshot._core import (  # noqa: E402
    attribution_note, attribution_state, backfill_attribution, has_footer, is_failure)

_passed = _total = 0


def check(label, cond, detail=""):
    global _passed, _total
    _total += 1
    _passed += bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}" + ("" if cond or not detail else f"\n         {detail!r}"))


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
for bad_name, content, want in (("nosrc.md", "---\ntitle: T\n---\n\nbody\n", 0), ("bin.md", b"\xff\xfe\x00bad", 1),
                                ("bom.md", "\ufeff" + FM + BODY, 1), ("unterm.md", "---\ntitle: T\nbody\n", 1)):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        arts = root / "docs" / "salesforce" / "999" / "g" / "articles"
        arts.mkdir(parents=True)
        f = arts / bad_name
        f.write_bytes(content if isinstance(content, bytes) else content.encode())
        ns = type("A", (), {"release": "999"})()
        rc, out = run_scan(root, lambda: cli.cmd_backfill_attribution(ns, {}, None))
        check(f"backfill-attribution exit {want} and prints the skipped {bad_name}", rc == want and bad_name in out)

# footer detection looks at the tail, not any mention
note = attribution_note(URL, "Salesforce developer documentation")
check("a fresh capture's bytes count as having the footer", has_footer("x\n\n" + note + "\n"))
check("the marker quoted mid-body is not a footer",
      not has_footer("see > **Source attribution and limited-use note.** here\n\nmore text\n")
      and attribution_state(FM + "Quote: " + note.splitlines()[-1] + "\n\nBody continues.\n")[0] == "missing")
check("a footer followed by more text is not the tail", not has_footer(note + "\n\nTrailing paragraph.\n"))
check("a BOM before the frontmatter is its own reason, and a failure",
      attribution_state("\ufeff" + FM + BODY)[0] == "bom-frontmatter" and is_failure("bom-frontmatter")
      and not is_failure("no-frontmatter") and is_failure("not writable: PermissionError"))

# an unwritable file is skipped with a reason and the command exits 1
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    arts = root / "docs" / "salesforce" / "999" / "g" / "articles"
    arts.mkdir(parents=True)
    ro = arts / "ro.md"
    ro.write_text(FM + BODY, encoding="utf-8")
    ro.chmod(0o444)
    try:
        ch, sk = backfill_attribution(arts)
        writable = os.access(ro, os.W_OK)  # root ignores the mode: then there is nothing to test
        if not writable:
            check("an unwritable file is skipped as 'not writable', unchanged", ch == [] and sk == [("ro.md", "not writable: PermissionError")]
                  and ro.read_text(encoding="utf-8") == FM + BODY)
            ns = type("A", (), {"release": "999"})()
            rc, out = run_scan(root, lambda: cli.cmd_backfill_attribution(ns, {}, None))
            check("backfill-attribution exits 1 on it and names it", rc == 1 and "ro.md" in out and "not writable" in out)
    finally:
        ro.chmod(0o644)

# check: unreadable and BOM files exit 1; an unscoped check skips the footer gate and returns 0
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    arts = root / "docs" / "salesforce" / "999" / "g" / "articles"
    arts.mkdir(parents=True)
    (arts / "bad.md").write_text(FM + BODY, encoding="utf-8")
    rc, out = run_scan(root, lambda: check_mod.scan(None))
    check("an unscoped check skips the footer gate and returns 0 even with a footer missing",
          rc == 0 and "Footer check skipped" in out and "bad.md" not in out)
    (arts / "bad.md").write_text(FM + BODY + "\n" + note + "\n", encoding="utf-8")
    (arts / "bin.md").write_bytes(b"\xff\xfe\x00bad")
    (arts / "nofm.md").write_text("# plain\n", encoding="utf-8")
    rc, out = run_scan(root, lambda: check_mod.scan("999"))
    check("check never tracebacks on an unreadable file, lists it and exits 1",
          rc == 1 and "bin.md: unreadable" in out)
    check("check lists a file with no frontmatter like the backfill does",
          "nofm.md: no-frontmatter" in out)
    (arts / "bin.md").unlink()
    rc, out = run_scan(root, lambda: check_mod.scan("999"))
    check("no-frontmatter alone does not fail the check", rc == 0 and "nofm.md" in out)
    (arts / "bom.md").write_text("\ufeff" + FM + BODY, encoding="utf-8")
    rc, out = run_scan(root, lambda: check_mod.scan("999"))
    check("a BOM file fails the check", rc == 1 and "bom.md: bom-frontmatter" in out)

# --active: the release comes from the manifest; a missing manifest or key fails
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / ".claude").mkdir()
    (root / ".claude" / "skill-manifest.yml").write_text('x: 1\nsalesforce_release_active: "999"\n', encoding="utf-8")
    check("active_release reads salesforce_release_active", check_mod.active_release(root) == "999")
    (root / ".claude" / "skill-manifest.yml").write_text("x: 1\n", encoding="utf-8")
    try:
        check_mod.active_release(root)
        check("a manifest without the key raises", False)
    except OSError:
        check("a manifest without the key raises", True)
    try:
        check_mod.active_release(root / "nowhere")
        check("a missing manifest raises", False)
    except OSError:
        check("a missing manifest raises", True)
err = io.StringIO()
with contextlib.redirect_stderr(err):
    rc, out = run_scan(Path(tempfile.gettempdir()) / "no-such-root-401", lambda: check_mod.main(["--active"]))
check("check --active exits 1 (no traceback) and names the missing manifest on stderr",
      rc == 1 and "error:" in err.getvalue() and "skill-manifest.yml" in err.getvalue(), err.getvalue())
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    (root / ".claude").mkdir()
    (root / ".claude" / "skill-manifest.yml").write_text("x: 1\n", encoding="utf-8")
    err = io.StringIO()
    with contextlib.redirect_stderr(err):
        rc, _ = run_scan(root, lambda: check_mod.main(["--active"]))
    check("check --active exits 1 and names the missing key when the manifest lacks it",
          rc == 1 and "salesforce_release_active not found" in err.getvalue(), err.getvalue())
    (root / ".claude" / "skill-manifest.yml").write_text('salesforce_release_active: "999"\n', encoding="utf-8")
    arts = root / "docs" / "salesforce" / "999" / "g" / "articles"
    arts.mkdir(parents=True)
    (arts / "bad.md").write_text(FM + BODY, encoding="utf-8")
    rc, out = run_scan(root, lambda: check_mod.main(["--active"]))
    check("check --active gates the manifest's release: a missing footer exits 1", rc == 1 and "bad.md" in out, out)
    backfill_attribution(arts)
    rc, _ = run_scan(root, lambda: check_mod.main(["--active"]))
    check("check --active passes once the footer is there", rc == 0)
for txt, want_key in (("salesforce_release_active: 264a\n", False), ("salesforce_release_active:\n 264\n", False),
                      ("salesforce_release_active: '264'  # now\n", True), ("salesforce_release_active: 264\n", True)):
    m = check_mod.ACTIVE_KEY.search(txt)
    check(f"the release key parser {'accepts' if want_key else 'rejects'} {txt.strip()!r}",
          bool(m) == want_key and (m.group(1) == "264" if m else True))

# the quoted note as the body's last line is not the footer; unterminated and BOM-only files
quoted = FM + "Quote:\n\n" + note.splitlines()[-1] + "\n"
check("a body whose last line quotes the note (no rule line) is missing, not ok",
      not has_footer(quoted) and attribution_state(quoted) == ("missing", URL))
check("the real footer, rule line included, still counts", has_footer(FM + BODY + "\n" + note + "\n"))
check("frontmatter that never closes is a distinct failing reason",
      attribution_state("---\ntitle: T\nbody\n")[0] == "unterminated-frontmatter"
      and is_failure("unterminated-frontmatter"))
check("a BOM before a file with no frontmatter is no-frontmatter, not a BOM failure",
      attribution_state("\ufeff# plain\n")[0] == "no-frontmatter")
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    arts = root / "docs" / "salesforce" / "999" / "g" / "articles"
    arts.mkdir(parents=True)
    (arts / "bom.md").write_text("\ufeff" + FM + BODY, encoding="utf-8")
    rc, out = run_scan(root, lambda: check_mod.scan("999"))
    check("check prints the strip-the-BOM hint and a real release in its fix line",
          rc == 1 and "strip the UTF-8 BOM" in out)
    (arts / "bad.md").write_text(FM + BODY, encoding="utf-8")
    rc, out = run_scan(root, lambda: check_mod.scan("999"))
    check("the fix line names the release, not a literal R", "backfill-attribution --release 999" in out)

# the site guide's relink step runs the backfill and logs added and skipped files
class _Log:
    def __init__(self):
        self.lines = []
    info = warning = lambda self, m: self.lines.append(m)


class _Fake:
    logger = _Log()


with tempfile.TemporaryDirectory() as tmp:
    out_dir = Path(tmp)
    (out_dir / "articles").mkdir()
    (out_dir / "articles" / "r.htm.md").write_text(FM + BODY, encoding="utf-8")
    (out_dir / "articles" / "nofm.md").write_text("# plain\n", encoding="utf-8")
    fake = _Fake()
    sg.SiteGuideSnapshot._relink_retained(fake, out_dir, {})
    check("_relink_retained appends the footer to a retained article",
          has_footer((out_dir / "articles" / "r.htm.md").read_text(encoding="utf-8")))
    check("_relink_retained logs the added count and the skipped file",
          any("added the attribution footer to 1 retained" in m for m in fake.logger.lines)
          and any("nofm.md (no-frontmatter)" in m for m in fake.logger.lines))

print(f"\n{_passed}/{_total} passed")
sys.exit(0 if _passed == _total else 1)
