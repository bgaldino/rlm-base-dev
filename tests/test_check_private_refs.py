#!/usr/bin/env python3
"""Tests for scripts/ai/check_private_refs.py (the `private_refs` pr_gate check, todo 358).

Each case copies the script into a throwaway git repository, so the leak guard, the shape check
and MOVED.tsv resolution are exercised against a tree this test controls. Stdlib only.
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# The shared scrub (tests/test_claude_hooks.py): drop what would aim git at another repository or
# inject config, and keep the ceiling and discovery variables, which only narrow where git looks.
for _var in [v for v in os.environ
             if v in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                      "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_PREFIX",
                      "GIT_NAMESPACE", "GIT_CONFIG", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT")
             or v.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))]:
    os.environ.pop(_var)

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "ai" / "check_private_refs.py"

spec = importlib.util.spec_from_file_location("check_private_refs", SCRIPT)
refs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refs)


def sh(cwd, *args):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True)


class Fixture(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        sh(self.root, "git", "init", "-q")
        (self.root / "scripts" / "ai").mkdir(parents=True)
        shutil.copy(SCRIPT, self.root / "scripts" / "ai" / "check_private_refs.py")

    def tearDown(self):
        shutil.rmtree(self.root)

    def write(self, rel, text):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def run_check(self):
        sh(self.root, "git", "add", "-A", "-f")
        return subprocess.run([sys.executable, "scripts/ai/check_private_refs.py"], cwd=self.root,
                              capture_output=True, text=True)


class LeakGuard(Fixture):
    def test_a_tracked_file_in_the_private_tree_fails(self):
        self.write(".agents/artifacts/notes.md", "private\n")
        proc = self.run_check()
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn(".agents/artifacts/notes.md: private content is tracked", proc.stdout)

    def test_a_sibling_backup_and_core_code_names_fail(self):
        self.write(".agents/artifacts.old/notes.md", "private\n")
        self.write("docs/analysis/x-core-code-y.md", "private\n")
        proc = self.run_check()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("artifacts.old/notes.md", proc.stdout)
        self.assertIn("x-core-code-y.md", proc.stdout)

    def test_public_agents_files_pass(self):
        self.write(".agents/README.md", "public\n")
        self.assertEqual(self.run_check().returncode, 0)

    def test_a_git_failure_is_a_tool_error_not_a_verdict(self):
        shutil.rmtree(self.root / ".git")  # not a repository: `git ls-files` fails
        proc = subprocess.run([sys.executable, "scripts/ai/check_private_refs.py"], cwd=self.root,
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)

    def test_forced_grep_colour_does_not_hide_citations(self):
        sh(self.root, "git", "config", "color.ui", "always")
        sh(self.root, "git", "config", "color.grep", "always")
        self.write("docs/a.md", ".agents/artifacts/feature-gaps.md\n")
        self.assertIn("1 citation(s)", self.run_check().stdout)


class Shape(Fixture):
    def test_top_level_citations_warn_while_shape_is_not_gating(self):
        self.write("docs/a.md", "see `.agents/artifacts/feature-gaps.md` and .agents/artifacts/old-dir/x.md.\n")
        proc = self.run_check()
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("docs/a.md:1: .agents/artifacts/feature-gaps.md cites the private tree's top level",
                      proc.stdout)
        self.assertIn(".agents/artifacts/old-dir/x.md cites", proc.stdout)
        self.assertIn("2 citation(s) shape-checked, not resolved (private tree absent)", proc.stdout)

    def test_tier_bare_and_template_citations_pass_quietly(self):
        self.write("docs/a.md", "`.agents/artifacts/` and .agents/artifacts and "
                   ".agents/artifacts/topics/x/README.md and .agents/artifacts/todos/<id>/ and "
                   ".agents/artifacts/{tier}/x.md and .agents/artifacts/**\n")
        proc = self.run_check()
        self.assertEqual(proc.returncode, 0)
        self.assertNotIn("[WARN", proc.stdout)
        self.assertIn("2 citation(s)", proc.stdout)  # topics/x/README.md and todos/ (cut at <id>)

    def test_anchors_and_queries_end_a_citation(self):
        self.write("docs/a.md", "[s](.agents/artifacts/topics/x/README.md#status) "
                   ".agents/artifacts/inbox/a.md?raw=1\n")
        proc = self.run_check()
        self.assertNotIn("#status", proc.stdout)
        self.assertNotIn("?raw", proc.stdout)
        self.assertIn("2 citation(s)", proc.stdout)

    def test_markdown_emphasis_does_not_hide_or_mangle_a_citation(self):
        self.write("docs/a.md", "See **.agents/artifacts/stray.md** and _.agents/artifacts/other.md_\n")
        proc = self.run_check()
        self.assertIn(".agents/artifacts/stray.md cites the private tree's top level", proc.stdout)
        self.assertIn(".agents/artifacts/other.md cites the private tree's top level", proc.stdout)
        self.assertNotIn("other.md_", proc.stdout)

    def test_a_nested_tree_folder_fails_the_leak_guard(self):
        self.write("docs/.agents/artifacts/notes.md", "private\n")
        proc = self.run_check()
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("docs/.agents/artifacts/notes.md: private content is tracked", proc.stdout)

    def test_case_variants_of_the_tree_fail_the_leak_guard(self):
        self.write(".Agents/artifacts/notes.md", "private\n")
        proc = self.run_check()
        self.assertEqual(proc.returncode, 1, proc.stdout)
        self.assertIn("private content is tracked", proc.stdout)

    def test_lookalike_siblings_are_not_citations(self):
        self.write("docs/a.md", "a decoy at .agents/artifacts-notes/x.md and .agents/artifacts.old/\n")
        self.assertIn("0 citation(s)", self.run_check().stdout)

    def test_tests_and_exempt_files_are_not_scanned(self):
        self.write("tests/fixture.py", "'.agents/artifacts/misplaced.md'\n")
        self.write(".cursor/rules/analysis-artifacts.mdc", ".agents/artifacts/example.md\n")
        self.assertIn("0 citation(s)", self.run_check().stdout)

    def test_gating_turns_shape_warnings_into_errors(self):
        script = self.root / "scripts" / "ai" / "check_private_refs.py"
        script.write_text(script.read_text().replace("SHAPE_GATING = False", "SHAPE_GATING = True"))
        self.write("docs/a.md", ".agents/artifacts/feature-gaps.md\n")
        self.assertEqual(self.run_check().returncode, 1)

    def test_a_citing_file_with_a_stray_byte_is_still_scanned(self):
        (self.root / "docs").mkdir()
        (self.root / "docs" / "latin1.md").write_bytes(
            b"caf\xe9 notes\n.agents/artifacts/feature-gaps.md\n")
        proc = self.run_check()
        self.assertIn("docs/latin1.md:2: .agents/artifacts/feature-gaps.md", proc.stdout)

    def test_a_lone_carriage_return_does_not_shift_line_numbers(self):
        self.write("docs/a.md", "a\rb\n.agents/artifacts/stray.md\n")
        self.assertIn("docs/a.md:2: .agents/artifacts/stray.md", self.run_check().stdout)

    def test_gitignore_ignores_exactly_what_the_leak_guard_flags(self):
        # `.gitignore`, the guard hook and check (a) each define a private copy; keep them one set.
        shutil.copy(REPO / ".gitignore", self.root / ".gitignore")
        samples = {".agents/artifacts/x.md": True, ".agents/artifacts.old/x.md": True,
                   ".agents/Artifacts/x.md": True, "docs/.agents/artifacts/x.md": True,
                   ".Agents/artifacts-bak/x.md": True, ".agents/artifact/x.md": False,
                   ".agents/README.md": False, "docs/artifacts/x.md": False}
        for path, private in samples.items():
            ignored = subprocess.run(["git", "check-ignore", "-q", "--no-index", path],
                                     cwd=self.root).returncode == 0
            flagged = refs.is_private_path(path)
            self.assertEqual((ignored, flagged), (private, private), path)

    def test_locations_and_typographic_punctuation_end_a_citation(self):
        self.write("docs/a.md", "a\fb\n.agents/artifacts/stray.md:12:3 and "
                   ".agents/artifacts/other.md\u2014then\n")
        proc = self.run_check()
        # Line 2 as git counts it: a form feed is not a line break.
        self.assertIn("docs/a.md:2: .agents/artifacts/stray.md cites", proc.stdout)
        self.assertIn("docs/a.md:2: .agents/artifacts/other.md cites", proc.stdout)
        self.assertNotIn(":12", proc.stdout)

    def test_classify(self):
        self.assertEqual(refs.classify(".agents/artifacts"), "bare")
        self.assertEqual(refs.classify(".agents/artifacts/"), "bare")
        self.assertEqual(refs.classify(".agents/artifacts/inbox/2026-11-09-x.md"), "tier")
        self.assertEqual(refs.classify(".agents/artifacts/todos/attachments/358/"), "tier")
        self.assertEqual(refs.classify(".agents/artifacts/{tier}/x.md"), "template")
        self.assertEqual(refs.classify(".agents/artifacts/$DIR/x.md"), "template")
        # A concrete top-level name with a placeholder inside is still top-level.
        self.assertEqual(refs.classify(".agents/artifacts/x-{release}.md"), "top-level")
        self.assertEqual(refs.classify(".agents/artifacts/collections/x.md"), "top-level")
        # The private repository's own root files are not misplaced documents.
        self.assertEqual(refs.classify(".agents/artifacts/README.md"), "tier")
        self.assertEqual(refs.classify(".agents/artifacts/MOVED.tsv"), "tier")

    def test_the_tier_list_matches_the_guard_hook(self):
        # Two public copies of the private layout; they must not drift apart.
        hook_spec = importlib.util.spec_from_file_location(
            "pre_tool_guard_for_refs", REPO / ".claude" / "hooks" / "pre_tool_guard.py")
        hook = importlib.util.module_from_spec(hook_spec)
        hook_spec.loader.exec_module(hook)
        self.assertEqual(set(refs.PRIVATE_TIERS), set(hook.ARTIFACTS_ROOT))


class Resolution(Fixture):
    """With the private clone present (an untracked nested tree here), citations are resolved."""

    def setUp(self):
        super().setUp()
        self.tree = self.root / ".agents" / "artifacts"
        (self.tree / ".git").mkdir(parents=True)  # the clone is a repository of its own
        (self.tree / "topics" / "collections").mkdir(parents=True)
        (self.tree / "topics" / "collections" / "gaps.md").write_text("x")
        (self.tree / "MOVED.tsv").write_text(
            "old_prefix\tnew_prefix\tref\tdate\ncollections/\ttopics/collections/\tW3\t2026-11-09\n")

    def run_check(self):
        sh(self.root, "git", "add", "docs", "scripts")  # the nested tree stays untracked
        return subprocess.run([sys.executable, "scripts/ai/check_private_refs.py"], cwd=self.root,
                              capture_output=True, text=True)

    def test_moved_and_missing_paths_warn(self):
        self.write("docs/a.md", ".agents/artifacts/collections/gaps.md\n"
                   ".agents/artifacts/topics/collections/gaps.md\n"
                   ".agents/artifacts/topics/nope.md\n")
        proc = self.run_check()
        self.assertEqual(proc.returncode, 0, proc.stdout)
        self.assertIn("moved; rewrite to .agents/artifacts/topics/collections/gaps.md", proc.stdout)
        self.assertIn("topics/nope.md is not at that path and MOVED.tsv has no row", proc.stdout)
        self.assertNotIn("a.md:2", proc.stdout)
        self.assertIn("resolved against the private tree", proc.stdout)

    def test_an_overlong_or_unreadable_citation_does_not_crash(self):
        self.write("docs/a.md", ".agents/artifacts/topics/" + "n" * 300 + ".md\n")
        (self.tree / "MOVED.tsv").write_bytes(
            b"old_prefix\tnew_prefix\tref\tdate\n\xff\xfe/\tx/\tW3\t2026-11-09\n"
            b"collections/\ttopics/collections/\tW3\t2026-11-09\n")
        proc = self.run_check()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("MOVED.tsv has no row for it", proc.stdout)
        self.assertEqual(refs.resolve_moved(self.tree, "collections/gaps.md"),
                         "topics/collections/gaps.md")
        self.assertFalse(refs.exists_in(self.tree, "a\x00b"))

    def test_an_unreadable_moved_tsv_warns_instead_of_failing_the_run(self):
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            self.skipTest("root ignores file permissions")
        self.write("docs/a.md", ".agents/artifacts/topics/nope.md\n")
        (self.tree / "MOVED.tsv").chmod(0)
        try:
            proc = self.run_check()
            self.assertEqual(refs.moved_rows(self.tree), [])
        finally:
            (self.tree / "MOVED.tsv").chmod(0o644)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("MOVED.tsv has no row for it", proc.stdout)

    def test_a_plain_folder_is_not_the_private_tree(self):
        # A stand-in left by an old `mkdir -p`: nothing is resolved against it.
        shutil.rmtree(self.tree / ".git")
        self.write("docs/a.md", ".agents/artifacts/topics/nope.md\n")
        proc = self.run_check()
        self.assertIn("not resolved (private tree absent)", proc.stdout)
        self.assertNotIn("MOVED.tsv has no row", proc.stdout)

    def test_a_glob_citation_is_not_resolved_as_a_path(self):
        self.write("docs/a.md", "see .agents/artifacts/topics/collections/2026-*-notes.md and "
                   "**.agents/artifacts/topics/nope.md**\n")
        proc = self.run_check()
        self.assertNotIn("2026-", proc.stdout)  # the glob draws no warning
        self.assertIn("topics/nope.md is not at that path", proc.stdout)  # bold is not a glob

    def test_resolve_moved_chains_rows(self):
        (self.tree / "MOVED.tsv").write_text(
            "old_prefix\tnew_prefix\tref\tdate\nold/\tcollections/\tW2\t2026-11-09\n"
            "collections/\ttopics/collections/\tW3\t2026-11-09\n")
        self.assertEqual(refs.resolve_moved(self.tree, "old/gaps.md"), "topics/collections/gaps.md")
        self.assertIsNone(refs.resolve_moved(self.tree, "elsewhere/gaps.md"))


if __name__ == "__main__":
    unittest.main()
