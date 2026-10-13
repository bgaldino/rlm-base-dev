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

# Run as if outside any git hook. A hook exports GIT_DIR and friends, which would aim every fixture
# and every script under test at this repository instead of a throwaway one; one fixture once wrote
# its identity into the developer's .git/config that way (todo 237).
# GIT_CONFIG* would inject config into every fixture, past GIT_CONFIG_GLOBAL/SYSTEM; the ceiling
# and discovery variables only narrow where git looks, so they stay.
for _var in [v for v in os.environ
             if v in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                      "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_PREFIX",
                      "GIT_NAMESPACE", "GIT_CONFIG", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_COUNT")
             or v.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))]:
    os.environ.pop(_var)

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
                        "git push --mirror", "git push --all origin", "git push origin :",
                        "git push origin HEAD:heads/main", "git push origin HEAD:refs/heads/main",
                        "git push origin feature:heads/release/next", "git push origin :heads/main",
                        "env -i git push origin HEAD:main", "env -u HOME git push origin main",
                        "command git push origin main", "sudo -E git push origin main",
                        "time git push origin main", "nohup git push origin main &",
                        "nice -n 10 git push origin main", "git push \\\n  origin main",
                        "sudo -n git push origin main", "exec -a x git push origin main",
                        "timeout 60 git push origin main", "ionice -c3 git push origin main",
                        "true \\\\\ngit push origin main", "# note \\\ngit push origin main",
                        "git push \\\r\n  origin main", "sudo -u git git push origin main",
                        "! git push origin HEAD:main", "if git push origin main; then :; fi",
                        "while ! git push origin main; do sleep 1; done", "{ git push origin main; }",
                        "env -C /srv/git git push origin main", "env GIT_DIR=x git push origin feature",
                        "git push -fo ci.skip origin main",
                        "cat > x.md <<'EOF'\nnotes\nEOF\ngit push origin main"):
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

    def test_a_tag_only_push_from_a_protected_branch_is_allowed(self):
        # `--tags` with no other refspec pushes only tags, whatever branch is checked out.
        for command in ("git push --tags origin", "git push origin --tags", "git push --tags",
                        "git push --ta origin", "git -c push.default=matching push --tags"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command, branch="main"), "allow")
        sh(self.work, "git", "config", "remote.origin.push", "HEAD:refs/heads/main")
        try:
            self.assertEqual(self.decision("git push --tags origin"), "allow")
        finally:
            sh(self.work, "git", "config", "--unset", "remote.origin.push")
        # A branch named alongside --tags is still checked.
        self.assertEqual(self.decision("git push --tags origin main"), "deny")
        self.assertEqual(self.decision("git push --tags origin HEAD", branch="main"), "deny")
        self.assertEqual(self.decision("git push --follow-tags", branch="main"), "deny")
        # The last of --tags / --no-tags wins, as in git.
        self.assertEqual(self.decision("git push --tags --no-tags origin", branch="main"), "deny")
        self.assertEqual(self.decision("git push --tags --no-ta origin", branch="main"), "deny")
        self.assertEqual(self.decision("git push --no-tags --tags origin", branch="main"), "allow")
        # After `--`, every word is the repository or a refspec, as in git.
        self.assertEqual(self.decision("git push -- --tags main"), "deny")
        self.assertEqual(self.decision("git push -- --mirror main"), "deny")
        self.assertEqual(self.decision("git push -- origin main"), "deny")
        self.assertEqual(self.decision("git push -- origin feature"), "allow")

    def main_clone(self):
        """A second clone of this fixture's remote, checked out on main."""
        on_main = Path(self.tmp.name) / "on-main"
        if not on_main.exists():
            sh(Path(self.tmp.name), "git", "clone", "-q", "-b", "main",
               str(Path(self.tmp.name) / "remote.git"), str(on_main))
        return on_main

    def artifacts_clone(self):
        """A clone, on main, of a remote whose URL names the private artifacts repo."""
        root = Path(self.tmp.name)
        remote = root / "gh" / "bgaldino" / "rlm-base-artifacts.git"
        clone = root / "artifacts"
        if not clone.exists():
            remote.parent.mkdir(parents=True)
            sh(root, "git", "init", "-q", "--bare", str(remote))
            sh(root, "git", "init", "-q", "-b", "main", str(clone))
            for key, value in (("user.email", "t@example.com"), ("user.name", "t"),
                               ("commit.gpgsign", "false")):
                sh(clone, "git", "config", key, value)
            sh(clone, "git", "commit", "-q", "--allow-empty", "-m", "base")
            sh(clone, "git", "remote", "add", "origin", str(remote))
            sh(clone, "git", "push", "-q", "-u", "origin", "main")
            # What the guard matches is the push URL: GitHub host and repository path. The
            # guard only reads it; nothing in these tests pushes.
            sh(clone, "git", "config", "remote.origin.pushurl",
               "git@github.com:bgaldino/rlm-base-artifacts.git")
        return clone

    def test_the_artifacts_repo_takes_direct_pushes_to_main(self):
        art = self.artifacts_clone()
        for command in (f"git -C {art} push", f"git -C {art} push origin main",
                        f"cd {art} && git push", f"cd {art} && git add -A && git push -q 2>&1",
                        f"env -C {art} git push"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "allow")
        # A force push there still asks; this repository's main is still refused.
        self.assertEqual(self.decision(f"git -C {art} push -f origin main"), "ask")
        # GitHub names are case-insensitive, so a differently cased URL is still the repo.
        self.assertEqual(self.decision(f"git -C {art} -c remote.origin.pushurl=https://github.com/"
                                       "BGaldino/RLM-Base-Artifacts.git push origin main"), "allow")
        # The same repository path on another host, or as a local path, is not the repo.
        for url in ("https://example.com/bgaldino/rlm-base-artifacts.git",
                    "git@example.com:bgaldino/rlm-base-artifacts.git",
                    str(Path(self.tmp.name) / "gh" / "bgaldino" / "rlm-base-artifacts.git"),
                    "https://github.com.evil.example/bgaldino/rlm-base-artifacts.git"):
            with self.subTest(url=url):
                self.assertEqual(self.decision(f"git -C {art} -c remote.origin.pushurl={url} "
                                               "push origin main"), "deny")
        # So does deleting a protected-looking branch there.
        for command in (f"git -C {art} push origin :release/foo",
                        f"git -C {art} push --delete origin release/foo",
                        f"git -C {art} push -d origin main", f"git -C {art} push --del origin main",
                        f"git -C {art} push --delete origin heads/main",
                        f"git -C {art} push origin :refs/heads/release/x"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "ask")
        self.assertEqual(self.decision(f"git -C {art} push origin :scratch"), "allow")
        self.assertEqual(self.decision(f"git -C {art} push --delete --no-delete origin main"),
                         "allow")
        self.assertEqual(self.decision(f"cd {art} && git push && cd {self.work} && git push "
                                       "origin main"), "deny")
        # A second change of directory makes where a push runs unresolvable, so it's refused,
        # even from a feature checkout and even if the second target looks harmless.
        on_main = self.main_clone()
        for command in (f"cd {art} && cd {on_main} && git push", f"cd {art} && pushd {on_main} "
                        "&& git push", f"cd {art} && cd . && git push",
                        f"cd -- {on_main} && git push", f"cd -P {on_main} && git push",
                        f"cd {on_main}; git push", f"true && cd {on_main} && git push",
                        f"pushd {on_main} && git push"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "deny")
        self.assertEqual(self.decision(f"cd {art} && cd . && git status"), "allow")
        # A heredoc body that mentions cd is data, not a change of directory.
        self.assertEqual(self.decision("git commit -q -F - <<'EOF'\nfix: cd a && cd b\nEOF\n"
                                       "git push -q origin feature"), "allow")
        for command in (f"cd -- {art} && git push", f"cd -P {art} && git push",
                        f"cd -L -- {art} && git push"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command, branch="main"), "allow")
        self.assertEqual(self.decision("git push origin main"), "deny")

    def test_the_exemption_needs_every_push_url_to_be_the_artifacts_repo(self):
        art = self.artifacts_clone()
        remote = Path(self.tmp.name) / "gh" / "bgaldino" / "rlm-base-artifacts.git"
        here = Path(self.tmp.name) / "remote.git"
        # A second push URL that is another repository: git pushes to both, so no exemption.
        self.assertEqual(self.decision(f"git -C {art} -c remote.origin.pushurl={remote} "
                                       f"-c remote.origin.pushurl={here} push origin main"),
                         "deny")
        # A raw URL or path is never exempt, whatever insteadOf would rewrite it to.
        self.assertEqual(self.decision(f"git -C {art} push {remote} main"), "deny")
        self.assertEqual(self.decision(f"git -c url.{here}.insteadOf={remote} push {remote} "
                                       "main:main"), "deny")

    def test_a_leading_cd_is_followed_only_when_the_rest_depends_on_it(self):
        art = self.artifacts_clone()
        # If the cd fails, `;` and `||` still run the push here, on main.
        for command in (f"cd {art}; git push", f"cd {art} || git push", f"cd {art} && x; git push",
                        f"cd {art} && x\ngit push"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command, branch="main"), "deny")
        # A target the guard can't resolve as the shell would also checks the starting
        # directory; so does a separator hidden behind an escaped quote.
        for command in ("cd - && git push", 'cd "$PWD" && git push', "cd `pwd` && git push",
                        "cd /nonexistent && git push",
                        f"cd {art} && echo \\' ; git push \\'"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command, branch="main"), "deny")
        self.assertEqual(self.decision(f"cd {art} && git push", branch="main"), "allow")
        self.assertEqual(self.decision(f"(cd {art} && git push)", branch="main"), "allow")
        # After the subshell's `)`, commands run back in the starting directory.
        for command in (f"(cd {art} && true) && git push", f"(cd {art} && (true)) && git push",
                        f"(cd {art} && echo '(') && git push",
                        f"(cd {art} && git push) && git push"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command, branch="main"), "deny")
        # Only a push after the `)` runs back here; a redirection or a pipe to tail doesn't.
        for command in (f"(cd {art} && git push) 2>&1", f"(cd {art} && git push) 2>&1 | tail -1"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command, branch="main"), "allow")
        on_main = self.main_clone()
        # A target the shell resolves and the guard can't (a variable) is refused outright: it
        # could be any directory, not just the starting one.
        self.assertEqual(self.decision(f"ON_MAIN={on_main} && cd \"$ON_MAIN\" && git push"), "deny")
        self.assertEqual(self.decision("cd \"$MAIN_CHECKOUT\" && git push"), "deny")
        # A tilde target is refused: quoted it's a literal directory, unquoted it's $HOME.
        tilde = self.work / "~"
        if not tilde.exists():
            sh(self.work, "git", "clone", "-q", "-b", "main",
               str(Path(self.tmp.name) / "remote.git"), str(tilde))
        # A continuation inside a word is deleted by bash, so `c\⏎d` is a cd.
        art = self.artifacts_clone()
        self.assertEqual(self.decision(f"cd {art} && c\\\nd {on_main} && git push"), "deny")
        # Only a plain literal path is followed; anything the shell might expand is refused.
        for name in ("x!", "a b", "a=b"):
            (self.work / name).mkdir(exist_ok=True)
        for command in ("cd x! && git push", "cd 'a b' && git push", "cd a=b && git push",
                        f"cd \\{on_main.name} && git push"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "deny")
        # A glob or brace target is refused: quoted it's literal, unquoted the shell expands it.
        (self.work / "[x]").mkdir(exist_ok=True)
        for command in ("cd [x] && git push", "cd '[x]' && git push", "cd *x* && git push",
                        "cd {a,b} && git push", "cd ?x? && git push"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "deny")
        for command in ("cd '~' && git push", "cd \\~ && git push", "cd ~ && git push"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "deny")
        # `link/..` is where you started under bash's default `cd -L`, not the link's parent.
        art = self.artifacts_clone()
        (art / "sub").mkdir(exist_ok=True)
        link = self.work / "link-into-artifacts"
        if not link.exists():
            link.symlink_to(art / "sub")
        for command in (f"cd {link.name}/.. && git push", f"cd -L {link.name}/.. && git push",
                        f"cd -P {link.name}/.. && git push", f"cd -LP {link.name}/.. && git push"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command, branch="main"), "deny")
        self.assertEqual(self.decision(f"cd -PL {link.name}/.. && git status", branch="main"),
                         "allow")
        # Without an explicit -L, `..` is refused: the shell may be in physical mode.
        art_link = art / "link-into-main"
        if not art_link.exists():
            art_link.symlink_to(self.main_clone())
        self.assertEqual(self.decision(f"git -C {art} status && cd {art_link.name}/.. && git push"),
                         "deny")
        self.assertEqual(self.decision(f"cd -L {art}/{art_link.name}/.. && git push"), "allow")
        self.assertEqual(self.decision(f"cd {art}/{art_link.name}/.. && git push"), "deny")
        # A redirection's operand named cd is not a change of directory.
        for command in ("cat < cd && git push origin feature", "echo x > cd && git push origin feature",
                        "cat <<< cd && git push origin feature",
                        "git add cd-notes.md && git push origin feature"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "allow")
        # Any other standalone cd word counts, wherever it sits, so a prefix can't hide it; a cd
        # that is only data is refused too, which errs toward refusing.
        for command in (f"time cd {on_main} && git push", f"command -p cd {on_main} && git push",
                        f"{{fd}}>/tmp/log cd {on_main} && git push", f"exec cd {on_main} && git push",
                        "echo cd && git push origin feature"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "deny")
        self.assertEqual(self.decision(f"builtin cd {on_main} ; git push"), "deny")
        # A descriptor-prefixed redirection before the cd doesn't hide it.
        for command in (f"2>/tmp/x cd {on_main} && git push", f"2> /tmp/x cd {on_main} && git push",
                        f"0</dev/null cd {on_main} && git push"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "deny")
        self.assertEqual(self.decision(f"cd {art} && git add cd-notes.md && git commit -m "
                                       f"'a\nb' && git push", branch="main"), "allow")
        self.assertEqual(self.decision(f"cd '{art}' && git push 2>&1 | tail -1", branch="main"),
                         "allow")

    def test_a_quote_spanning_lines_does_not_hide_a_push(self):
        # The usual agent commit: a multi-line message, then a push, in one command.
        for command in ('git commit -m "title\n\nbody" && git push origin main',
                        "git commit -m \"$(cat <<'EOF'\nmsg\nEOF\n)\" && git push origin HEAD:main",
                        'echo "a\nb" ; git push origin HEAD:main'):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "deny")
        art = self.artifacts_clone()
        for command in (f'cd {art} && git commit -m "t\n\nb" && git push --force',
                        f'cd {art} && git commit -m "t\n\nb" && git push origin --delete main'):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "ask")
        self.assertEqual(self.decision('git commit -m "a\nb" && git push origin feature'), "allow")
        self.assertEqual(self.decision("git commit -q -F - <<'EOF'\nfix: x\n\nbody\nEOF\n"
                                       "git push -q origin feature 2>&1 | tail -1"), "allow")

    def test_redirections_are_not_push_arguments(self):
        for command in ("git push 2>&1 | tail -1", "git push >/tmp/push.log",
                        "git push &>> log", "git push 1>&2 2> /dev/null", "git push < /dev/null",
                        "git push -q 2>&1"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command, branch="main"), "deny")
        self.assertEqual(self.decision(">/tmp/push.log git push origin HEAD:main"), "deny")
        self.assertEqual(self.decision('git commit -m "a > b" && git push origin main'), "deny")
        self.assertEqual(self.decision("git push origin feature 2>&1 | tail -1"), "allow")
        self.assertEqual(self.decision("git push 2>&1"), "allow")

    def test_config_location_overrides_are_refused(self):
        for command in ("HOME=/tmp/elsewhere git push origin",
                        "env HOME=/tmp/elsewhere git push origin feature",
                        "XDG_CONFIG_HOME=/tmp/x git push origin feature"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "deny")
        self.assertEqual(self.decision("HOME=/tmp/elsewhere git status"), "allow")

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
                        "git push --force-with-lease origin feature", "git push origin +feature",
                        "git push -uf origin feature", "git push -fu origin feature",
                        "git push --force-with-lease=feature origin feature",
                        "git push --forc origin feature", "git push --force-with origin feature",
                        "git push --force-w origin feature",
                        "git push -fo ci.skip origin feature"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "ask")

    def test_ordinary_commands_are_allowed(self):
        for command in ("git push origin feature", "git push -u origin feature",
                        "echo git push origin main", "git log main", "git pushx origin main",
                        "git -c user.name=x push origin feature", "sudo ls", "time make",
                        "env -u HOME git push origin feature", "git push --follow-tags origin feature",
                        "command -v git", "git push -oforce origin feature",
                        "timeout 60 git fetch origin", "git push -o ci.skip origin feature",
                        "git push --no-force origin feature", "git push --push-option=x origin feature",
                        "git push --dry origin feature",
                        "cat > x.md <<'EOF'\ngit push origin main\nEOF",
                        "cat <<-EOF > x.md\n\tgit push origin main\n\tEOF",
                        "grep -c x <<< 'git push origin main'"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "allow")

    def test_a_wrapper_that_changes_directory_is_resolved_there(self):
        # From the feature checkout, `env -C <a checkout on main> git push` pushes main.
        other = Path(self.tmp.name) / "on-main"
        if not other.exists():
            sh(Path(self.tmp.name), "git", "clone", "-q", "-b", "main",
               str(Path(self.tmp.name) / "remote.git"), str(other))
        for command in (f"env -C {other} git push", f"env --chdir={other} git push",
                        f"sudo -D {other} git push", f"env --chd={other} git push",
                        f"env --c {other} git push", f"sudo --chd {other} git push",
                        f"timeout 60 env -C {other} git push",
                        f"nice -n 5 sudo -D {other} git push", f"env -C{other} git push",
                        f"sudo -D{other} git push"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "deny")
        self.assertEqual(self.decision(f"env -C {other} git status"), "allow")

    def test_configured_push_refspecs_are_resolved(self):
        # `git -c remote.origin.push=HEAD:main push origin` really pushes to main; the guard
        # used to resolve it with separate git calls that never saw the `-c`.
        for command in ("git -c remote.origin.push=HEAD:main push origin",
                        "git -c remote.origin.push=HEAD:main push",
                        "git -c remote.origin.push=refs/heads/feature:refs/heads/release/next "
                        "push origin",
                        "git -c remote.origin.push=HEAD:main push --recurse-submodules check "
                        "origin",
                        "git -c remote.origin.push=HEAD:main push --receive git-receive-pack "
                        "origin",
                        "git -c remote.origin.push=HEAD:main push --recurse check origin",
                        "git -c remote.origin.push=HEAD:main push --push-opt x origin",
                        "git push --mir", "git push --bra origin",
                        "git -c push.default=matching push",
                        "git -c push.default=Matching push origin",
                        "/usr/lib/git-core/git-push origin HEAD:main", "git-push origin main",
                        "env -i git-push origin main"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "deny")
        sh(self.work, "git", "config", "remote.origin.push", "HEAD:refs/heads/main")
        try:
            self.assertEqual(self.decision("git push origin"), "deny")
            self.assertEqual(self.decision("git push"), "deny")
            self.assertEqual(self.decision("git push origin feature"), "allow")  # explicit wins
        finally:
            sh(self.work, "git", "config", "--unset", "remote.origin.push")

    def test_aliases_that_push_are_resolved(self):
        sh(self.work, "git", "config", "alias.p", "push")
        sh(self.work, "git", "config", "alias.ship", "!git push origin HEAD:main")
        sh(self.work, "git", "config", "alias.lg", "log --oneline")
        # An alias may start with global options, or name another alias.
        sh(self.work, "git", "config", "alias.cp", "-c remote.origin.push=HEAD:main push")
        sh(self.work, "git", "config", "alias.pf", "p -f")
        sh(self.work, "git", "config", "alias.loop", "loop")
        try:
            self.assertEqual(self.decision("git p origin HEAD:main"), "deny")
            self.assertEqual(self.decision("git ship"), "deny")
            self.assertEqual(self.decision("git cp origin"), "deny")
            self.assertEqual(self.decision("git pf origin HEAD:main"), "deny")
            self.assertEqual(self.decision("git pf origin feature"), "ask")
            self.assertEqual(self.decision("git loop"), "allow")
            self.assertEqual(self.decision("git p origin feature"), "allow")
            self.assertEqual(self.decision("git lg"), "allow")
        finally:
            for name in ("p", "ship", "lg", "cp", "pf", "loop"):
                sh(self.work, "git", "config", "--unset", f"alias.{name}")

    def test_pushes_that_cannot_be_resolved_are_refused(self):
        for command in ("GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=remote.origin.push "
                        "GIT_CONFIG_VALUE_0=HEAD:main git push origin",
                        "git --config-env=remote.origin.push=TARGET push origin",
                        "git push origin 'refs/heads/*:refs/heads/*'"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(command), "deny")


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

    @staticmethod
    def plan(*objects, sets=False):
        """An SFDMU plan; each object is (sObject, operation, deleteOldData)."""
        listed = [{"query": f"SELECT Id FROM {name}", "operation": op,
                   **({"deleteOldData": True} if delete else {})}
                  for name, op, delete in objects]
        body = {"objectSets": [{"objects": listed}]} if sets else {"objects": listed}
        return json.dumps(body, indent=2)

    def write(self, before, after):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "datasets" / "plan" / "export.json"
            path.parent.mkdir(parents=True)
            path.write_text(before)
            return self.decision("Write", {"file_path": str(path), "content": after})

    def test_moving_delete_old_data_to_another_object_asks(self):
        # Same count of `"deleteOldData": true` before and after: the old aggregate allowed it.
        self.assertEqual(self.write(self.plan(("Account", "Upsert", True), ("Product2", "Upsert", False)),
                                    self.plan(("Account", "Upsert", False), ("Product2", "Upsert", True))),
                         "ask")

    def test_swapping_upsert_and_insert_between_objects_asks(self):
        self.assertEqual(self.write(self.plan(("Account", "Upsert", False), ("Product2", "Insert", False)),
                                    self.plan(("Account", "Insert", False), ("Product2", "Upsert", False))),
                         "ask")

    def test_object_sets_are_compared_object_by_object(self):
        self.assertEqual(self.write(self.plan(("Account", "Upsert", False), sets=True),
                                    self.plan(("Account", "Upsert", True), sets=True)), "ask")

    def test_reordering_or_making_an_object_safer_is_allowed(self):
        before = self.plan(("Account", "Upsert", True), ("Product2", "Insert", False))
        self.assertEqual(self.write(before, self.plan(("Product2", "Insert", False),
                                                      ("Account", "Upsert", True))), "allow")
        self.assertEqual(self.write(before, self.plan(("Account", "Upsert", False),
                                                      ("Product2", "Upsert", False))), "allow")

    def test_edits_are_replayed_against_the_whole_plan(self):
        # One MultiEdit moves deleteOldData from Account to Product2.
        before = self.plan(("Account", "Upsert", True), ("Product2", "Upsert", False))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "datasets" / "plan" / "export.json"
            path.parent.mkdir(parents=True)
            path.write_text(before)
            edits = [{"old_string": '"operation": "Upsert",\n      "deleteOldData": true',
                      "new_string": '"operation": "Upsert"'},
                     {"old_string": 'FROM Product2",\n      "operation": "Upsert"',
                      "new_string": 'FROM Product2",\n      "operation": "Upsert",\n'
                                    '      "deleteOldData": true'}]
            for edit in edits:
                self.assertIn(edit["old_string"], before)
            self.assertEqual(self.decision("MultiEdit", {"file_path": str(path),
                                                         "edits": edits}), "ask")


class KillSwitch(unittest.TestCase):
    def test_stop_file_refuses_loop_agents_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = make_repo(Path(tmp))
            (work / ".loop").mkdir()
            (work / ".loop" / "STOP").touch()
            event = {"tool_name": "Read", "tool_input": {"file_path": "x"}, "cwd": str(work)}
            self.assertEqual(run_hook(GUARD, event, {"LOOP_ROLE": "builder"}).returncode, 2)
            self.assertEqual(run_hook(GUARD, event).returncode, 0)

    def test_a_run_stop_file_refuses_only_that_run(self):
        # A remote cancel aimed at one run must not stop another run on the same workstation.
        with tempfile.TemporaryDirectory() as tmp:
            work = make_repo(Path(tmp))
            cancelled, other = work / ".loop" / "7", work / ".loop" / "8"
            cancelled.mkdir(parents=True)
            other.mkdir()
            (cancelled / "STOP").touch()
            event = {"tool_name": "Read", "tool_input": {"file_path": "x"}, "cwd": str(work)}
            hit = run_hook(GUARD, event, {"LOOP_ROLE": "builder", "LOOP_RUN_DIR": str(cancelled)})
            self.assertEqual(hit.returncode, 2)
            self.assertIn("this run's stop file", hit.stderr)
            self.assertEqual(run_hook(GUARD, event, {"LOOP_ROLE": "builder",
                                                     "LOOP_RUN_DIR": str(other)}).returncode, 0)
            self.assertEqual(run_hook(GUARD, event, {"LOOP_RUN_DIR": str(cancelled)}).returncode, 0)


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

    def stop(self, env=None, session=None):
        event = {"hook_event_name": "Stop", "cwd": str(self.work)}
        if session:
            event["session_id"] = session
        return run_hook(STOP, event, dict(self.env, **(env or {})))

    def checks(self):
        return (self.run_dir / "checks.log").read_text().splitlines()

    def test_interactive_sessions_and_unchanged_checkouts_are_not_gated(self):
        self.gate_exits(1)  # the untracked exit_code file is itself a change
        self.assertEqual(self.stop({"LOOP_ROLE": ""}).returncode, 0)
        self.assertEqual(self.stop({"LOOP_ROLE": "spec-reviewer"}).returncode, 0)
        (self.work / "scripts" / "ai" / "exit_code").unlink()
        self.assertEqual(self.stop().returncode, 0)

    def test_a_branch_the_base_has_moved_past_is_not_gated(self):
        # The gate would fail if it ran; the branch has nothing of its own, so it mustn't.
        self.gate_exits(1)
        sh(self.work, "git", "add", "-A")
        sh(self.work, "git", "commit", "-q", "-m", "gate fails")
        sh(self.work, "git", "push", "-q", "origin", "feature")
        sh(self.work, "git", "checkout", "-q", "-b", "ahead")
        (self.work / "later.txt").write_text("base moved on\n")
        sh(self.work, "git", "add", "-A")
        sh(self.work, "git", "commit", "-q", "-m", "base moves")
        sh(self.work, "git", "push", "-q", "origin", "ahead:feature")
        sh(self.work, "git", "checkout", "-q", "feature")
        self.assertEqual(self.stop().returncode, 0)
        self.assertFalse((self.run_dir / "checks.log").exists())

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

    def test_a_run_stop_file_lets_that_builder_stop(self):
        self.gate_exits(1)
        self.run_dir.mkdir(parents=True)
        (self.run_dir / "STOP").touch()
        self.assertEqual(self.stop().returncode, 0)

    def test_sessions_without_a_run_dir_do_not_share_a_budget(self):
        # With no LOOP_RUN_DIR, the run folder used to be one shared .loop/: after one
        # session spent its five blocks, no later session was ever gated again.
        self.gate_exits(1)
        unset = {"LOOP_RUN_DIR": ""}
        first = [self.stop(unset, session="s1").returncode for _ in range(6)]
        self.assertEqual(first, [2, 2, 2, 2, 2, 0])
        self.assertEqual(self.stop(unset, session="s2").returncode, 2)
        self.assertTrue((self.work / ".loop" / "session-s1" / "checks.log").exists())


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

    def test_the_matrix_probed_is_the_worktrees_not_the_main_checkouts(self):
        # The interpreter is shared, but a worktree's branch may need more of it.
        sys.path.insert(0, str(REPO / "scripts" / "ai"))
        import gate_python
        with tempfile.TemporaryDirectory() as tmp:
            work = make_repo(Path(tmp))
            ai = work / "scripts" / "ai"
            ai.mkdir(parents=True)
            (ai / "pr_gate.py").write_text(FAKE_GATE)
            sh(work, "git", "add", "-A")
            sh(work, "git", "commit", "-q", "-m", "fixture")
            tree = Path(tmp) / "tree"
            sh(work, "git", "worktree", "add", "-q", str(tree), "-b", "wt")
            (tree / "scripts" / "ai" / "pr_gate.py").write_text(
                FAKE_GATE.replace("CHECKS = []", "CHECKS = [{'min_python': (99, 0)}]"))
            os.environ["RLM_GATE_PYTHON"] = sys.executable
            try:
                self.assertEqual(gate_python.problems(work)[1], [])
                self.assertTrue(any("needs 99.0+" in p for p in gate_python.problems(tree)[1]))
            finally:
                del os.environ["RLM_GATE_PYTHON"]


if __name__ == "__main__":
    unittest.main()
