"""Offline fixtures for scripts/ai/check_skill_staleness.py (temp-dir snapshots).

Stdlib only. Run with: python tests/test_check_skill_staleness.py
"""
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts" / "ai"))
import check_skill_staleness as css  # noqa: E402


def touch(path: Path, text: str = "x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class Staleness(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()
        touch(self.root / ".claude/skill-manifest.yml", 'salesforce_release_active: "264"\n')
        touch(self.root / css.SNAPSHOTS / "264/dev-guide/a.md")
        touch(self.root / css.SNAPSHOTS / "262/dev-guide/a.md")
        touch(self.root / css.SNAPSHOTS / "262/dev-guide/old.md")
        for rel, name in (("264", "ind.both"), ("262", "ind.both"), ("262", "ind.only_old")):
            touch(self.root / css.SNAPSHOTS / rel / "help/articles" / f"{name}.htm.md")

    def run_text(self, text):
        active = css.active_release(self.root)
        return [(rule, msg) for _, rule, msg in
                css.findings(text, self.root, active, css.help_index(self.root))]

    def rules(self, text):
        return [r for r, _ in self.run_text(text)]

    def test_snapshot_links(self):
        self.assertEqual(self.rules("[a](../docs/salesforce/262/dev-guide/a.md)"),
                         ["snapshot-link"])
        self.assertEqual(self.rules("see `docs/salesforce/262/dev-guide/a.md`."), ["snapshot-link"])
        self.assertEqual(self.rules("`docs/salesforce/262/dev-guide/old.md`"), [])
        self.assertEqual(self.rules("`docs/salesforce/264/dev-guide/a.md`"), [])
        self.assertEqual(self.rules("`docs/salesforce/262/dev-guide/*.md`"), [])

    def test_pins(self):
        self.assertEqual(self.rules("Verified on Release 262, API v67.0."), ["stale-pin"])
        self.assertEqual(self.rules("verified on 260"), ["stale-pin"])
        self.assertEqual(self.rules("Verified on Release 262. Not yet re-verified on 264."), [])
        self.assertEqual(self.rules("Verified on Release 264."), [])

    def test_help_ids(self):
        self.assertEqual(self.rules("[Help: `ind.both`]"), [])
        self.assertEqual(self.rules("[Help: `ind.both.htm`]"), [])
        self.assertEqual(self.rules("[Help: `ind.nope`]"), ["help-id"])
        self.assertEqual(self.rules("[Help: `ind.both`, `ind.nope.htm`]"), ["help-id"])
        self.assertEqual(self.rules("[Help: `ind.only_old`]"), ["help-id"])
        self.assertEqual(self.rules("262 only [Help: `ind.only_old`]"), [])
        self.assertEqual(self.rules("[Help: `ind.both`; Repo: `scripts/x.py run`]"), [])

    def test_newer_release_is_not_repointed(self):
        touch(self.root / css.SNAPSHOTS / "266/dev-guide/a.md")
        touch(self.root / css.SNAPSHOTS / "266/help/articles/ind.preview.htm.md")
        self.assertEqual(self.rules("`docs/salesforce/266/dev-guide/a.md`"), [])
        self.assertEqual(self.rules("[Help: `ind.preview`]"), [])

    def test_line_suffix_is_not_part_of_the_path(self):
        self.assertEqual(self.rules("`docs/salesforce/262/dev-guide/a.md:40`"), ["snapshot-link"])
        self.assertEqual(self.rules("`docs/salesforce/262/dev-guide/old.md:40`"), [])

    def test_pin_and_reverification_on_one_line(self):
        self.assertEqual(self.rules("Verified on Release 262; re-verified on 264."), [])
        self.assertEqual(self.rules("Verified on 260 and verified on 262."),
                         ["stale-pin", "stale-pin"])

    def test_allow_needs_the_full_marker(self):
        self.assertEqual(self.rules("Verified on 262 and the rule name staleness: allow"),
                         ["stale-pin"])

    def test_file_arguments(self):
        f = self.root / "x.md"
        touch(f, "Verified on Release 262\n")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(css.main([str(f)], self.root), 1)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(css.main([str(self.root / "missing.md")], self.root), 2)

    def test_missing_active_help_corpus_skips_help_ids(self):
        import shutil
        shutil.rmtree(self.root / css.SNAPSHOTS / "264/help")
        self.assertEqual(self.rules("[Help: `ind.only_old`]"), [])
        self.assertEqual(self.rules("[Help: `ind.nope`]"), ["help-id"])

    def test_allow_marker(self):
        self.assertEqual(self.rules("Verified on 262 <!-- staleness: allow -->"), [])
        self.assertEqual(self.rules("[Help: `ind.nope`] <!-- staleness: allow -->"), [])

    def test_main_output_and_exit(self):
        bad = self.root / ".cursor/skills/s/SKILL.md"
        touch(bad, "ok\nVerified on Release 262\n")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = css.main([], self.root)
        self.assertEqual(code, 1)
        self.assertIn(".cursor/skills/s/SKILL.md:2: stale-pin:", out.getvalue())
        touch(bad, "fine\n")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(css.main([], self.root), 0)

    def test_missing_manifest_is_tool_error(self):
        (self.root / ".claude/skill-manifest.yml").unlink()
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(css.main([], self.root), 2)


if __name__ == "__main__":
    unittest.main()
