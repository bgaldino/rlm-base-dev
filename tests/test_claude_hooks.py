"""Offline fixtures for the Claude Code hooks in .claude/hooks/ and scripts/ai/gate_python.py.

Each hook runs as a subprocess with a JSON event on stdin, the way Claude Code calls it, against
throwaway git repositories. Stdlib only; no org, network or agent client required.
Run with: python tests/test_claude_hooks.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GUARD = REPO / ".claude" / "hooks" / "pre_tool_guard.py"
STOP = REPO / ".claude" / "hooks" / "stop_gate.py"


def sh(cwd, *args):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


def run_hook(script, event, env=None):
    full_env = {k: v for k, v in os.environ.items()
                if k not in ("LOOP_ROLE", "LOOP_RUN_DIR", "LOOP_BASE", "RLM_GATE_PYTHON")}
    full_env.update(env or {})
    return subprocess.run([sys.executable, str(script)], input=json.dumps(event),
                          capture_output=True, text=True, env=full_env, timeout=120)


def make_repo(root):
    """A clone of a bare remote with main, a preview and a release line, a dev and a feature
    branch, all tracking origin. Branch names are placeholders: the guard matches `preview/*`
    and `release/*` by prefix, so no release number belongs here."""
    remote, work = root / "remote.git", root / "work"
    sh(root, "git", "init", "-q", "--bare", str(remote))
    sh(root, "git", "init", "-q", "-b", "main", str(work))
    for key, value in (("user.email", "t@example.com"), ("user.name", "t"),
                       ("commit.gpgsign", "false")):
        sh(work, "git", "config", key, value)
    sh(work, "git", "commit", "-q", "--allow-empty", "-m", "base")
    sh(work, "git", "remote", "add", "origin", str(remote))
    for branch in ("main", "preview/next", "release/next", "dev/next", "feature"):
        if branch != "main":  # main is checked out, and git won't force the current branch
            sh(work, "git", "branch", branch)
        sh(work, "git", "push", "-q", "-u", "origin", branch)
    sh(work, "git", "checkout", "-q", "feature")
    return work


class PushGuard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.work = make_repo(Path(cls.tmp.name))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def decision(self, command, branch="feature"):
        sh(self.work, "git", "checkout", "-q", branch)
        proc = run_hook(GUARD, {"tool_name": "Bash", "tool_input": {"command": command},
                                "cwd": str(self.work)})
        if proc.returncode == 2:
            return "deny"
        self.assertEqual(proc.returncode, 0, proc.stderr)
        if proc.stdout.strip():
            return json.loads(proc.stdout)["hookSpecificOutput"]["permissionDecision"]
        return "allow"

    def test_protected_targets_are_denied_however_spelled(self):
        for command in ("git push origin main", "git push origin HEAD:main",
                        "git push origin feature:refs/heads/release/next",
                        "git push origin release/next", "git push origin HEAD:preview/next",
                        "git -C . push origin main", "FOO=1 git push origin main",
                        "cd . && git push origin main", "git status; git push origin release/next",
                        "git push -o ci.skip origin main", "git push --delete origin main",
                        "git push --mirror", "git push --all origin", "git push origin :"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "deny")

    def test_bare_push_follows_the_current_branch_and_upstream(self):
        self.assertEqual(self.decision("git push", branch="main"), "deny")
        self.assertEqual(self.decision("git push", branch="release/next"), "deny")
        self.assertEqual(self.decision("git push", branch="preview/next"), "deny")
        self.assertEqual(self.decision("git push origin HEAD", branch="release/next"), "deny")
        self.assertEqual(self.decision("git push", branch="feature"), "allow")
        # A dev/ branch is ordinary work; only main, preview/* and release/* are protected.
        self.assertEqual(self.decision("git push", branch="dev/next"), "allow")

    def test_a_branch_tracking_main_cannot_bare_push(self):
        # `git switch -c work origin/main` tracks main. Plain git refuses a bare push from it,
        # but `-c push.default=upstream` would send it to main, so the guard refuses both.
        sh(self.work, "git", "branch", "-f", "--track", "tracks-main", "origin/main")
        for command in ("git push", "git -c push.default=upstream push"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command, branch="tracks-main"), "deny")
        self.assertEqual(self.decision("git push -u origin tracks-main:tracks-main",
                                       branch="tracks-main"), "allow")

    def test_force_push_to_a_feature_branch_asks(self):
        for command in ("git push --force origin feature", "git push -f",
                        "git push --force-with-lease origin feature", "git push origin +feature"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "ask")

    def test_ordinary_commands_are_allowed(self):
        for command in ("git push origin feature", "git push -u origin feature",
                        "echo git push origin main", "git log main", "git pushx origin main"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "allow")


class SfdmuGuard(unittest.TestCase):
    def decision(self, tool, tool_input):
        proc = run_hook(GUARD, {"tool_name": tool, "tool_input": tool_input, "cwd": str(REPO)})
        self.assertEqual(proc.returncode, 0, proc.stderr)
        if proc.stdout.strip():
            return json.loads(proc.stdout)["hookSpecificOutput"]["permissionDecision"]
        return "allow"

    def edit(self, old, new, path="datasets/sfdmu/qb/en-US/qb-pricing/export.json"):
        return self.decision("Edit", {"file_path": str(REPO / path), "old_string": old,
                                      "new_string": new})

    def test_adding_delete_old_data_asks(self):
        self.assertEqual(self.edit('"operation": "Upsert"',
                                   '"operation": "Upsert", "deleteOldData": true'), "ask")

    def test_flipping_upsert_to_insert_asks(self):
        self.assertEqual(self.edit('"operation": "Upsert"', '"operation": "Insert"'), "ask")

    def test_a_new_insert_object_or_a_non_dataset_file_is_allowed(self):
        self.assertEqual(self.edit('"objects": [', '"objects": [{"operation": "Insert"},'),
                         "allow")
        self.assertEqual(self.edit('"operation": "Upsert"', '"operation": "Insert"',
                                   path="docs/example.json"), "allow")

    def test_write_compares_against_the_file_on_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "datasets" / "plan" / "export.json"
            path.parent.mkdir(parents=True)
            path.write_text('{"operation": "Upsert", "deleteOldData": true}')
            same = {"file_path": str(path), "content": path.read_text()}
            self.assertEqual(self.decision("Write", same), "allow")
            path.write_text('{"operation": "Upsert"}')
            self.assertEqual(self.decision("Write", same), "ask")

    def test_multi_edit_is_checked(self):
        edits = [{"old_string": "a", "new_string": "b"},
                 {"old_string": '"x": 1', "new_string": '"deleteOldData": true'}]
        self.assertEqual(self.decision("MultiEdit", {
            "file_path": str(REPO / "datasets/plan/export.json"), "edits": edits}), "ask")


class KillSwitch(unittest.TestCase):
    def test_stop_file_refuses_loop_agents_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = make_repo(Path(tmp))
            (work / ".loop").mkdir()
            (work / ".loop" / "STOP").touch()
            event = {"tool_name": "Read", "tool_input": {"file_path": "x"}, "cwd": str(work)}
            self.assertEqual(run_hook(GUARD, event, {"LOOP_ROLE": "builder"}).returncode, 2)
            self.assertEqual(run_hook(GUARD, event).returncode, 0)


FAKE_GATE = textwrap.dedent("""\
    import os, sys
    DEPS = {}
    CHECKS = []
    def have_module(name):
        return True
    if __name__ == "__main__":
        code = int(open(os.path.join(os.path.dirname(__file__), "exit_code")).read())
        print("[FAIL] fake_check" if code == 1 else "[PASS] fake_check")
        print("3 checks: 3 executed, 0 skipped, 0 blocked on a missing dependency.")
        sys.exit(code)
""")


class StopGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.work = make_repo(Path(self.tmp.name))
        ai = self.work / "scripts" / "ai"
        ai.mkdir(parents=True)
        shutil.copy(REPO / "scripts" / "ai" / "gate_python.py", ai)
        (ai / "pr_gate.py").write_text(FAKE_GATE)
        (self.work / "REVIEW.md").write_text(
            "# Review\n\n## The defect classes this repo actually produces\n\n"
            "**A partial failure hiding behind an aggregate.**\n\n## Next\n")
        sh(self.work, "git", "add", "-A")
        sh(self.work, "git", "commit", "-q", "-m", "fixture")
        sh(self.work, "git", "push", "-q", "origin", "feature")
        self.run_dir = Path(self.tmp.name) / "run"
        self.env = {"LOOP_ROLE": "builder", "LOOP_RUN_DIR": str(self.run_dir),
                    "LOOP_BASE": "origin/feature", "RLM_GATE_PYTHON": sys.executable}

    def gate_exits(self, code):
        (self.work / "scripts" / "ai" / "exit_code").write_text(str(code))

    def stop(self, env=None):
        return run_hook(STOP, {"hook_event_name": "Stop", "cwd": str(self.work)},
                        dict(self.env, **(env or {})))

    def checks(self):
        return (self.run_dir / "checks.log").read_text().splitlines()

    def test_interactive_sessions_and_unchanged_checkouts_are_not_gated(self):
        self.gate_exits(1)  # the untracked exit_code file is itself a change
        self.assertEqual(self.stop({"LOOP_ROLE": ""}).returncode, 0)
        self.assertEqual(self.stop({"LOOP_ROLE": "spec-reviewer"}).returncode, 0)
        (self.work / "scripts" / "ai" / "exit_code").unlink()
        self.assertEqual(self.stop().returncode, 0)

    def test_a_failing_gate_blocks_with_its_output_and_the_defect_classes(self):
        self.gate_exits(1)
        proc = self.stop()
        self.assertEqual(proc.returncode, 2)
        self.assertIn("[FAIL] fake_check", proc.stderr)
        self.assertIn("A partial failure hiding behind an aggregate", proc.stderr)
        self.assertTrue(self.checks()[0].startswith("blocked (3 checks:"))

    def test_a_passing_gate_allows_the_stop(self):
        self.gate_exits(0)
        self.assertEqual(self.stop().returncode, 0)
        self.assertTrue(self.checks()[0].startswith("pass"))

    def test_the_budget_lets_the_builder_stop_after_five_blocks(self):
        self.gate_exits(1)
        codes = [self.stop().returncode for _ in range(6)]
        self.assertEqual(codes, [2, 2, 2, 2, 2, 0])

    def test_setup_problems_block_once_and_do_not_spend_the_budget(self):
        self.gate_exits(1)
        missing = {"RLM_GATE_PYTHON": str(Path(self.tmp.name) / "no-python")}
        first, second = self.stop(missing), self.stop(missing)
        self.assertEqual((first.returncode, second.returncode), (2, 0))
        self.assertIn("setup problem", first.stderr)
        self.assertEqual([line.split()[0] for line in self.checks()], ["setup"])

    def test_a_gate_tool_error_is_a_setup_problem_not_a_pass(self):
        self.gate_exits(2)
        proc = self.stop()
        self.assertEqual(proc.returncode, 2)
        self.assertIn("setup problem", proc.stderr)
        self.assertNotIn("pass", " ".join(self.checks()))

    def test_an_interpreter_below_the_matrix_minimum_is_a_setup_problem(self):
        self.gate_exits(0)
        gate = self.work / "scripts" / "ai" / "pr_gate.py"
        gate.write_text(FAKE_GATE.replace("CHECKS = []", "CHECKS = [{'min_python': (99, 0)}]"))
        proc = self.stop()
        self.assertEqual(proc.returncode, 2)
        self.assertIn("needs 99.0+", proc.stderr)

    def test_the_kill_switch_lets_the_builder_stop(self):
        self.gate_exits(1)
        (self.work / ".loop").mkdir()
        (self.work / ".loop" / "STOP").touch()
        self.assertEqual(self.stop().returncode, 0)


class GatePython(unittest.TestCase):
    def test_an_incomplete_interpreter_is_reported_not_trusted(self):
        sys.path.insert(0, str(REPO / "scripts" / "ai"))
        import gate_python
        os.environ["RLM_GATE_PYTHON"] = "/nonexistent/python"
        try:
            python, problems = gate_python.problems(REPO)
        finally:
            del os.environ["RLM_GATE_PYTHON"]
        self.assertEqual(str(python), "/nonexistent/python")
        self.assertIn("does not exist", problems[0])


if __name__ == "__main__":
    unittest.main()
