"""The local Docker build context leaves out git-ignored local state (stdlib only, no Docker).

The published image is built from a CI checkout, so it only ever holds tracked files. A local
build (`docker/rlm setup`, the devcontainer) uses the working tree as its context instead, so a
git-ignored folder that .dockerignore does not also exclude is copied into the image by
`COPY . /opt/rlm-base-dev`. A git-ignored local folder went into local images that way.

This suite emulates Docker's own matcher (moby/patternmatcher: patterns are anchored at the
context root, `*` stays within one path segment, `**` spans any number, a match on a parent
directory excludes everything under it, and the last matching pattern wins, so `!` re-includes)
and checks:

- a sample path from every class of private or org-derived local state is excluded;
- every tracked file is still in the context, apart from the few left out on purpose;
- every .gitignore pattern is mirrored in .dockerignore with the same scope: a pattern with no
  slash but a trailing one matches at any depth in git, so its mirror must be `**/<pattern>`,
  since a bare Docker pattern only matches at the root. NOT_MIRRORED holds only the entries a
  broader .dockerignore line already covers. A new .gitignore entry fails here until mirrored;
- a `!` re-include sits above every rule it could override, and does not bring back a secret
  nested under it: the last matching pattern wins, so a re-include placed after the recursive
  secret rules overrides them inside its subtree.
"""
import os
import re
import subprocess
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(name):
    with open(os.path.join(REPO, name), encoding="utf-8") as fh:
        return fh.read()


def _to_regex(pattern):
    """moby/patternmatcher's Pattern.compile, for the subset of syntax the repo uses."""
    out, i = "^", 0
    while i < len(pattern):
        ch = pattern[i]
        if ch == "*":
            if pattern[i + 1:i + 2] == "*":
                i += 1
                if pattern[i + 1:i + 2] == "/":
                    i += 1
                out += ".*" if i + 1 == len(pattern) else "(.*/)?"
            else:
                out += "[^/]*"
        elif ch == "?":
            out += "[^/]"
        elif ch == "[":
            end = pattern.find("]", i)
            if end < 0:
                raise ValueError(f"unterminated '[' in .dockerignore pattern {pattern!r}")
            out += pattern[i:end + 1]
            i = end
        else:
            out += re.escape(ch)
        i += 1
    return re.compile(out + "$")


def load_dockerignore(text):
    """[(exclusion, regex)] the way the dockerignore reader builds them."""
    patterns = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        exclusion = line.startswith("!")
        if exclusion:
            line = line[1:].strip()
        line = os.path.normpath(line).replace(os.sep, "/").lstrip("/")
        patterns.append((exclusion, _to_regex(line)))
    return patterns


def excluded(patterns, path):
    """PatternMatcher.MatchesOrParentMatches: True when `path` is left out of the context."""
    parents = path.split("/")[:-1]
    matched = False
    for exclusion, regex in patterns:
        if exclusion != matched:
            continue
        hit = bool(regex.match(path)) or any(
            regex.match("/".join(parents[:n])) for n in range(1, len(parents) + 1))
        if hit:
            matched = not exclusion
    return matched


PATTERNS = load_dockerignore(read(".dockerignore"))

# One path per class of local state that must never be baked into an image.
MUST_EXCLUDE = [
    ".agents/artifacts/todos/open/001-example.md",
    ".agents/artifacts/attachments/a.png",
    ".agents/artifacts.old/notes.md",
    "docs/.agents/Artifacts/notes.md",
    "docs/analysis/example-core-code-questions.md",
    ".cursor/plans/plan.md",
    "core.code-workspace",
    ".claude/worktrees/wt/README.md",
    ".claude/settings.local.json",
    ".claude/launch.json",
    ".loop/run/state.json",
    ".rescan_tmp/x",
    "scripts/build_harness/tui/settings.local.json",
    ".mcp.json",
    "scripts/mcp/.mcp.json",
    ".mcp-state/token",
    ".env",
    ".env.local",
    ".sf/config.json",
    ".sfdx/sfdx-config.json",
    ".cci/keychain",
    ".cumulusci/keychain",
    "force-app/main/default/connectedApps/App.connectedApp-meta.xml",
    "extracted/org/Product2.csv",
    "datasets/sfdmu/qb/en-US/qb-tax/source/TaxPolicy.csv",
    "datasets/sfdmu/qb/en-US/qb-tax/target/TaxPolicy.csv",
    "datasets/sfdmu/qb/en-US/qb-tax/CSVIssuesReport.csv",
    "datasets/sfdmu/qb/en-US/qb-tax/MissingParentRecordsReport.csv",
    "datasets/sfdmu/test/x.csv",
    "datasets/sfdmu/reconcile/x.csv",
    "datasets/sfdmu/extractions/x.csv",
    "datasets/bre/exports/x.json",
    "scripts/permsets.txt",
    "scripts/psl.csv",
    "scripts/txn_data_harness/out/run.json",
    "robot/rlm-base/results/output.xml",
    "unpackaged/post_ux/drift_report.json",
    "unpackaged/post_ux/retrieve_scope.json",
    "templates/flexipages/patches/x.yml.bak",
    "docs/erds/erd-data.json.bak2",
    "docs/erds/orphan-candidates.md",
    "docs/salesforce/262/revenue-cloud-summer-26.pdf",
    "docs/salesforce/262/solution-overview-summer-26-rca.pdf",
    "logs/build.log",
    # Slashless .gitignore entries match at any depth, so their mirrors have to as well.
    "docker/.env",
    "scripts/mcp/.env.local",
    "tasks/.sf/config.json",
    "robot/rlm-base/.cci/keychain",
    "certs/server.key",
    "scripts/x/logs/run.txt",
    "datasets/sfdmu/qb/en-US/qb-tax/sfdmu.log",
    "unpackaged/post_x/core.code-workspace",
    "scripts/x/.harness/run.json",
    # Robot output from a direct `robot` run lands outside robot/rlm-base/results and records
    # queried org data.
    "log.html",
    "report.html",
    "output.xml",
    "robot/rlm-base/tests/e2e/log.html",
    "selenium-screenshot-1.png",
    "robot/rlm-base/selenium-screenshot-2.png",
    "document_builder_toggle_verification_failed.png",
    # Browser profiles left by third-party tooling, retrieved org metadata.
    "browser/Default/Cookies",
    "mdapi/package.xml",
    "deploy/objects/Account.object",
    "postman/archive/env.json",
    # Secrets nested under a `!` re-included .claude path (the re-include must not win).
    ".claude/hooks/.env",
    ".claude/commands/credentials.pem",
    ".claude/skills/tool/.sf/orgs/local.json",
]

# Local secrets and org-derived files that could sit anywhere, including inside a subtree a `!`
# line re-includes. Each is checked under every re-included path in .dockerignore.
NESTED_SECRETS = [
    ".env", ".env.local", "server.key", "cert.pem", ".sf/orgs/x.json", ".sfdx/x.json",
    ".cci/keychain", ".cumulusci/keychain", ".mcp.json", ".mcp-state/x", "run.log", "logs/x",
    "x.bak", "log.html", "output.xml", "selenium-screenshot-1.png", ".harness/x",
]


def reincluded_paths(text):
    """The paths .dockerignore re-includes with `!`, as written."""
    return [line.strip()[1:].strip() for line in text.splitlines() if line.strip().startswith("!")]


def _diverges(pattern, path):
    """True when a literal segment of `pattern` differs from `path` at the same depth, so the
    pattern cannot match `path` or anything under it. A wildcard segment, or a pattern that
    continues below `path`, might."""
    for pat_seg, path_seg in zip(pattern.split("/"), path.split("/")):
        if any(c in pat_seg for c in "*?["):
            return False
        if pat_seg != path_seg:
            return True
    return False


def misplaced_reincludes(text):
    """(re-include, earlier exclusion) pairs where the `!` line comes after a rule it can override.

    Docker applies the last matching pattern, so a `!R` line wins over every earlier exclusion
    inside R's subtree. The only exclusions allowed before it are the one it carves R out of
    (which matches R itself, like `.claude/*` for `!.claude/hooks`) and ones whose literal path
    leaves R's before reaching it (`.git`, `.claude/launch.json`), which cannot match under R.
    """
    rules, bad = [], []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("!"):
            target = line[1:].strip().lstrip("/")
            for earlier in rules:
                if excluded(load_dockerignore(earlier), target):
                    continue  # the rule this line carves the path out of
                if _diverges(earlier.lstrip("/"), target):
                    continue  # a literal segment leaves the re-included path
                bad.append((line, earlier))
        else:
            rules.append(line)
    return bad

# Tracked paths .dockerignore leaves out on purpose; everything else tracked must be copied.
# Exact names and directory prefixes, so `.gitignore` itself is not excused by a `.git` prefix.
TRACKED_EXCLUDED_FILES = {".gitattributes"}
TRACKED_EXCLUDED_DIRS = (".github/",)

# .gitignore patterns not mirrored line for line because a broader .dockerignore line already
# excludes everything they match (the comment names it). Anything else is mirrored. Each maps to
# sample paths that git ignores under that pattern and Docker must exclude, so the "covered"
# claim is checked rather than taken on trust.
NOT_MIRRORED = {
    ".env.local": [".env.local", "docker/.env.local"],                          # **/.env.*
    "datasets/bre/exports/**": ["datasets/bre/exports/a.json"],                 # datasets/bre
    "datasets/sfdmu/**/*.csv.bak": ["datasets/sfdmu/qb/en-US/x/Product2.csv.bak"],  # **/*.bak
    "docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf":               # revenue-cloud-*.pdf
        ["docs/salesforce/260/revenue-cloud-spring-26-2026-01-15.pdf"],
    "docs/salesforce/262/salesforce-release-notes-summer-26-2026-05-07.pdf":    # ...-notes-*.pdf
        ["docs/salesforce/262/salesforce-release-notes-summer-26-2026-05-07.pdf"],
}


def tracked_files():
    """Every tracked path. No skip when git is unavailable: a skipped suite exits 0, and the gate
    would book a pass for a check that verified nothing."""
    out = subprocess.run(["git", "ls-files", "-z"], cwd=REPO, check=True,
                         capture_output=True, text=True).stdout
    files = [f for f in out.split("\0") if f]
    if not files:
        raise AssertionError("git ls-files listed no tracked files")
    return files


def _gitignore_patterns():
    for line in read(".gitignore").splitlines():
        line = line.strip()
        if line and not line.startswith(("#", "!")):
            yield line


def _forms(pattern):
    """The .dockerignore spellings that mirror a .gitignore pattern with the same scope.

    Git anchors a pattern only when a slash appears at its start or middle; any other pattern
    matches at every depth. Docker anchors every pattern at the context root, so an unanchored
    git pattern is mirrored only by `**/<pattern>`. An anchored one is mirrored by itself (or
    the `**/` form, which is broader). A trailing `/` or `/**` is dropped: Docker excludes the
    subtree of a bare path, and `dir/**` would leave the empty directory behind.
    """
    body = pattern.rstrip("/")
    anchored = "/" in body
    core = body.lstrip("/")
    if core.endswith("/**"):
        core = core[:-3]
    if core.startswith("**/"):
        return {core}
    return {core, "**/" + core} if anchored else {"**/" + core}


class DockerignoreTest(unittest.TestCase):

    def test_private_and_org_state_is_excluded(self):
        leaked = [p for p in MUST_EXCLUDE if not excluded(PATTERNS, p)]
        self.assertEqual(leaked, [], "copied into a locally built image")

    def test_a_reinclude_does_not_bring_back_a_nested_secret(self):
        roots = reincluded_paths(read(".dockerignore"))
        self.assertTrue(roots, "no `!` lines found: update this test if that is intended")
        leaked = [f"{root}/{name}" for root in roots for name in NESTED_SECRETS
                  if not excluded(PATTERNS, f"{root}/{name}")]
        self.assertEqual(leaked, [], "a `!` line after the secret rules re-includes these; "
                                     "keep re-includes above every other rule")

    def test_the_excluded_folder_itself_is_gone_not_just_its_contents(self):
        # `dir/**` would exclude the children but still create an empty `dir` in the image.
        for path in (".agents/artifacts", ".claude/worktrees", "extracted", ".loop"):
            self.assertTrue(excluded(PATTERNS, path), path)

    def test_tracked_claude_files_stay_in_the_image(self):
        for path in (".claude/skill-manifest.yml", ".claude/settings.json",
                     ".claude/commands/rlm-todos.md", ".claude/hooks/stop_gate.py",
                     ".claude/skills/todo-tracker"):
            self.assertFalse(excluded(PATTERNS, path), path)

    def test_every_tracked_file_is_copied(self):
        dropped = [f for f in tracked_files() if f not in TRACKED_EXCLUDED_FILES
                   and not f.startswith(TRACKED_EXCLUDED_DIRS) and excluded(PATTERNS, f)]
        self.assertEqual(dropped, [], "tracked files left out of the build context")

    def test_every_gitignore_pattern_is_mirrored_or_explained(self):
        docker = {line.strip() for line in read(".dockerignore").splitlines()}
        unhandled = [p for p in _gitignore_patterns()
                     if p not in NOT_MIRRORED and not (_forms(p) & docker)]
        self.assertEqual(unhandled, [], "mirror each in .dockerignore with the same scope, or "
                                        "list it in NOT_MIRRORED with a covered sample path")

    def test_the_root_gitignore_is_the_only_one(self):
        # The mirror check reads only the root .gitignore. A nested one would ignore paths it
        # never compares with .dockerignore, so its arrival has to fail here until it is mirrored
        # (with its directory prefixed) and this test and _gitignore_patterns are extended.
        nested = [f for f in tracked_files() if f.endswith("/.gitignore")]
        self.assertEqual(nested, [], "nested .gitignore files are not mirrored by this suite")

    def test_not_mirrored_has_no_stale_entries(self):
        gitignore = set(_gitignore_patterns())
        self.assertEqual(sorted(set(NOT_MIRRORED) - gitignore), [], "no longer in .gitignore")

    def test_not_mirrored_entries_really_are_covered(self):
        samples = [p for paths in NOT_MIRRORED.values() for p in paths]
        self.assertTrue(all(NOT_MIRRORED.values()), "every NOT_MIRRORED entry needs a sample")
        # The samples must be paths the repo's .gitignore ignores, or they prove nothing about the
        # pattern. `-v` names the source, so a workstation's core.excludesFile or
        # .git/info/exclude cannot stand in for it.
        out = subprocess.run(["git", "check-ignore", "--no-index", "-v", "--stdin"], cwd=REPO,
                             input="\n".join(samples) + "\n", capture_output=True,
                             text=True).stdout
        ignored = {path for source, _, path in (ln.partition("\t") for ln in out.splitlines())
                   if source.split(":")[0] == ".gitignore"}
        self.assertEqual(sorted(set(samples) - ignored), [], "samples .gitignore does not ignore")
        leaked = [p for p in samples if not excluded(PATTERNS, p)]
        self.assertEqual(leaked, [], "listed as covered, but copied into the image")

    def test_reincludes_sit_above_every_rule_they_could_override(self):
        self.assertEqual(misplaced_reincludes(read(".dockerignore")), [],
                         "move each `!` line above the rules it follows")

    def test_reinclude_ordering_rule_can_fail(self):
        self.assertEqual(misplaced_reincludes(".git\nx/*\n!x/keep\n**/.env\n"), [])
        self.assertEqual(misplaced_reincludes("x/*\n**/.env\n!x/keep\n"),
                         [("!x/keep", "**/.env")])
        self.assertEqual(misplaced_reincludes("x/*\nx/keep/logs\n!x/keep\n"),
                         [("!x/keep", "x/keep/logs")])
        # A literal sibling under the same parent cannot reach the re-included subtree.
        self.assertEqual(misplaced_reincludes("x/*\nx/other.json\n!x/keep\n"), [])
        self.assertEqual(misplaced_reincludes("x/*\nx/*/logs\n!x/keep\n"),
                         [("!x/keep", "x/*/logs")])

    def test_an_unterminated_bracket_names_the_pattern(self):
        with self.assertRaisesRegex(ValueError, "unterminated.*'a\\[b'"):
            load_dockerignore("a[b\n")

    def test_matcher_emulation(self):
        pats = load_dockerignore("a/b\n**/*.pyc\nx/*\n!x/keep\n/root/\nd/**\n")
        cases = {
            "a/b": True, "a/b/c/d": True, "a/bc": False, "z/a/b": False,
            "m.pyc": True, "deep/er/m.pyc": True,
            "x/drop": True, "x/drop/inner": True, "x/keep": False, "x/keep/inner": False,
            "root": True, "root/f": True,
            "d": False, "d/f": True,
        }
        for path, want in cases.items():
            self.assertEqual(excluded(pats, path), want, path)


if __name__ == "__main__":
    unittest.main()
