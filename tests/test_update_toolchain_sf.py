#!/usr/bin/env python3
"""update-toolchain.sh step 4 updates the `sf` that runs, and names every other copy on PATH.

The step used to take its npm branch whenever an npm copy existed, so with a standalone install
first on PATH it updated the npm copy (which never ran), skipped the standalone, and logged the
standalone's unchanged version as "now" (todo 243). This runs the script's own step-4 block, cut
from the file, under bash with `set -euo pipefail`, against stub `npm` and `sf` installs on a
controlled PATH. No real sf, npm or network. Stdlib only.

Run with: python tests/test_update_toolchain_sf.py
"""
import os
import re
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "bash" / "update-toolchain.sh"
BASH = shutil.which("bash", path="/bin:/usr/bin") or "bash"


def step4():
    """The script's step-4 block, from its header up to step 5's."""
    text = SCRIPT.read_text(encoding="utf-8")
    m = re.search(r"^# ── 4\. sf CLI.*?(?=^# ── 5\.)", text, re.M | re.S)
    if not m:
        raise AssertionError("step 4 (`# ── 4. sf CLI`) not found before step 5 in update-toolchain.sh")
    return m.group(0)


def executable(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\n" + body)
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


class UpdateToolchainSf(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.calls = self.tmp / "calls.log"
        self.calls.touch()

    def npm_prefix(self, name, sf=True):
        """An nvm-style Node prefix whose bin/sf is a symlink into lib/node_modules, like npm makes."""
        prefix = self.tmp / name
        (prefix / "bin").mkdir(parents=True)
        if sf:
            run = executable(prefix / "lib/node_modules/@salesforce/cli/bin/run.js",
                             f'[ "$1" = --version ] && echo "@salesforce/cli/2.150.0 {name}" && exit 0\n'
                             f'echo "sf $* ({name})" >> "{self.calls}"\n')
            (prefix / "bin" / "sf").symlink_to(run)
        return prefix

    def npm_tool(self, prefix):
        """A stub `npm` whose global prefix is `prefix`; it records installs instead of running them."""
        return executable(self.tmp / "tools" / "npm",
                          f'[ "$1" = prefix ] && echo "{prefix}" && exit 0\n'
                          f'[ "$1" = root ] && echo "{prefix}/lib/node_modules" && exit 0\n'
                          f'echo "npm $*" >> "{self.calls}"\n').parent

    def standalone(self, name):
        return executable(self.tmp / name / "bin" / "sf",
                          f'[ "$1" = --version ] && echo "@salesforce/cli/2.140.0 {name}" && exit 0\n'
                          f'echo "sf $* ({name})" >> "{self.calls}"\n').parent

    def run_step(self, *path_dirs):
        prelude = ('set -euo pipefail\nNEW_NODE=v24.0.0\nSTEP_FAILED=()\n'
                   'log() { printf "LOG %s\\n" "$*"; }\nwarn() { printf "WARN %s\\n" "$*"; }\n'
                   'fail_later() { warn "$*"; STEP_FAILED+=("$*"); }\n')
        env = {"PATH": os.pathsep.join([str(d) for d in path_dirs] + ["/usr/bin", "/bin"]),
               "HOME": str(self.tmp)}
        proc = subprocess.run([BASH, "-c", prelude + step4()], env=env, capture_output=True,
                              text=True, timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return proc.stdout, self.calls.read_text().splitlines()

    def test_npm_sf_first_is_updated_through_npm(self):
        prefix = self.npm_prefix("node24")
        # Reach the npm bin through a symlinked alias: `-ef` must still see the same file.
        alias = self.tmp / "alias-bin"
        alias.symlink_to(prefix / "bin")
        out, calls = self.run_step(self.npm_tool(prefix), alias)
        self.assertEqual(calls, ["npm install -g @salesforce/cli@latest"])
        self.assertNotIn("WARN", out)

    def test_standalone_first_is_updated_with_sf_update_and_the_npm_copy_is_named(self):
        prefix = self.npm_prefix("node24")
        standalone = self.standalone("aisuite")
        out, calls = self.run_step(self.npm_tool(prefix), standalone, prefix / "bin")
        self.assertEqual(calls, ["sf update (aisuite)"], "the npm copy must not be updated instead")
        self.assertIn(f"installer-based install at {standalone / 'sf'}", out)
        self.assertRegex(out, r"WARN sf CLI: other copies on PATH were not updated: "
                              + re.escape(str(prefix / "bin" / "sf")) + r" —")

    def test_no_sf_installs_through_npm(self):
        prefix = self.npm_prefix("node24", sf=False)
        out, calls = self.run_step(self.npm_tool(prefix), prefix / "bin")
        self.assertEqual(calls, ["npm install -g @salesforce/cli@latest"])
        self.assertIn("WARN sf not found on PATH for v24.0.0", out)

    def test_a_stale_copy_later_on_path_is_named_once(self):
        current, stale = self.npm_prefix("node24"), self.npm_prefix("node24-old")
        out, calls = self.run_step(self.npm_tool(current), current / "bin", stale / "bin",
                                   stale / "bin")
        self.assertEqual(calls, ["npm install -g @salesforce/cli@latest"])
        warns = [ln for ln in out.splitlines() if ln.startswith("WARN sf CLI: other copies")]
        self.assertEqual(len(warns), 1, out)
        self.assertEqual(warns[0].count(str(stale / "bin" / "sf")), 1, warns[0])
        self.assertNotIn(str(current / "bin" / "sf") + " ", warns[0].split("updated:")[1])

    def test_a_failed_npm_update_is_reported_not_fatal(self):
        prefix = self.npm_prefix("node24")
        npm = executable(self.tmp / "tools" / "npm",
                         f'[ "$1" = prefix ] && echo "{prefix}" && exit 0\n'
                         f'[ "$1" = root ] && echo "{prefix}/lib/node_modules" && exit 0\nexit 1\n').parent
        out, _ = self.run_step(npm, prefix / "bin")
        self.assertIn("WARN sf CLI update failed", out)


if __name__ == "__main__":
    unittest.main()
