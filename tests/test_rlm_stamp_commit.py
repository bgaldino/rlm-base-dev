#!/usr/bin/env python3
"""
Offline tests for tasks/rlm_stamp_commit.StampGitCommit.

    python tests/test_rlm_stamp_commit.py
    python -m unittest tests.test_rlm_stamp_commit

Needs PyYAML (the task module imports it at module level), so pr_gate runs this suite
in yaml_offline_suites rather than the stdlib list. CumulusCI is optional: the task is
built without its __init__, and the module's no-CumulusCI fallback is loaded on purpose
in one case. Every git and `sf` call goes through a fake `subprocess.run`, so there is
no repository read, no org and no deploy.

What is asserted
----------------
The stamp is a CMDT record deployed from a temp directory, so the checks read what a
deploy would have shipped: the sfdx-project.json and the RLM_Build_Info record XML the
fake `sf` finds in its cwd, and the exact `sf project deploy start` argv. Around that,
the branches that decide what is stamped (detached HEAD, dirty tree with build-output
exclusions, org definition, feature flags with secret redaction and truncation) and the
deploy-result parsing that decides between "stamped" and the non-fatal warning.
"""
import importlib.util
import json
import logging
import os
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import yaml  # noqa: E402

from tasks import rlm_stamp_commit as mod  # noqa: E402
from tasks.rlm_stamp_commit import StampGitCommit  # noqa: E402

MD_NS = "{http://soap.sforce.com/2006/04/metadata}"
XSI_TYPE = "{http://www.w3.org/2001/XMLSchema-instance}type"
CMDT_RELPATH = os.path.join(
    "force-app", "main", "default", "customMetadata", "RLM_Build_Info.Latest.md-meta.xml"
)

SHORT = "abc1234"
FULL = "abc1234def5678abc1234def5678abc1234def56"


def completed(cmd, stdout="", returncode=0, stderr=""):
    return subprocess.CompletedProcess(cmd, returncode, stdout=stdout, stderr=stderr)


class FakeRunner:
    """Stands in for subprocess.run: answers git from a table, records the sf deploy.

    The deploy fake reads the generated files out of its cwd at call time, because the
    task deletes the temp directory as soon as the deploy returns.
    """

    def __init__(self, git=None, deploy_stdout=None, deploy_returncode=0, deploy_exc=None,
                 git_exc=None):
        self.git = {
            ("rev-parse", "--short", "HEAD"): SHORT,
            ("rev-parse", "HEAD"): FULL,
            ("rev-parse", "--abbrev-ref", "HEAD"): "main",
            ("status", "--porcelain"): "",
        }
        self.git.update(git or {})
        self.git_exc = git_exc or {}
        self.deploy_stdout = (
            json.dumps({"status": 0, "result": {"success": True}})
            if deploy_stdout is None else deploy_stdout
        )
        self.deploy_returncode = deploy_returncode
        self.deploy_exc = deploy_exc
        self.calls = []
        self.deploy_cwd = None
        self.deployed_files = {}

    def __call__(self, command, **kwargs):
        self.calls.append((list(command), kwargs))
        if command[0] == "git":
            key = tuple(command[1:])
            if key in self.git_exc:
                raise self.git_exc[key]
            if key not in self.git:
                raise AssertionError(f"unexpected git call: {command}")
            value = self.git[key]
            if isinstance(value, BaseException):
                raise value
            return completed(command, stdout=value + "\n")
        if command[0] == "sf":
            self.deploy_cwd = kwargs.get("cwd")
            if self.deploy_cwd:
                for rel in ("sfdx-project.json", CMDT_RELPATH):
                    p = os.path.join(self.deploy_cwd, rel)
                    if os.path.exists(p):
                        with open(p, encoding="utf-8") as f:
                            self.deployed_files[rel] = f.read()
            if self.deploy_exc:
                raise self.deploy_exc
            return completed(command, stdout=self.deploy_stdout, returncode=self.deploy_returncode)
        raise AssertionError(f"unexpected command: {command}")

    def sf_calls(self):
        return [(c, k) for c, k in self.calls if c[0] == "sf"]


def make_org(**overrides):
    attrs = dict(
        username="stamp@example.com",
        config_name="beta",
        scratch=True,
        is_sandbox=False,
        config_file="orgs/beta.json",
    )
    attrs.update(overrides)
    return SimpleNamespace(**attrs)


def make_project(custom=None, api_version="66.0"):
    return SimpleNamespace(project__custom=custom, project__package__api_version=api_version)


def make_task(options=None, org_config="default", project_config=None):
    """A StampGitCommit with the attributes BaseTask.__init__ would set, and nothing else."""
    task = StampGitCommit.__new__(StampGitCommit)
    task.options = dict(options or {})
    task.logger = logging.getLogger("test_rlm_stamp_commit")
    task.org_config = make_org() if org_config == "default" else org_config
    task.project_config = project_config or make_project(custom={"billing": True})
    return task


def cmdt_values(xml_text):
    """{field: (xsi:type, text)} from the generated CMDT record (also proves it parses)."""
    root = ET.fromstring(xml_text)
    out = {}
    for values in root.findall(f"{MD_NS}values"):
        field = values.find(f"{MD_NS}field").text
        value = values.find(f"{MD_NS}value")
        out[field] = (value.get(XSI_TYPE), value.text)
    return root, out


class ClassContract(unittest.TestCase):
    def test_task_accepts_org_and_declares_optional_flow_name(self):
        # Without salesforce_task cci rejects --org (todo 244).
        self.assertIs(StampGitCommit.salesforce_task, True)
        self.assertEqual(set(StampGitCommit.task_options), {"flow_name"})
        self.assertFalse(StampGitCommit.task_options["flow_name"]["required"])

    def test_sf_wait_leaves_headroom_under_the_subprocess_timeout(self):
        self.assertEqual(mod.DEPLOY_TIMEOUT_SECONDS, 300)
        self.assertEqual(mod.DEPLOY_WAIT_MINUTES, 4)
        self.assertLess(mod.DEPLOY_WAIT_MINUTES * 60, mod.DEPLOY_TIMEOUT_SECONDS)

    def test_module_imports_without_cumulusci(self):
        # The try/except ImportError fallback: block every cumulusci module and load a
        # fresh copy under another name, so the real import above is untouched.
        blocked = {k: None for k in list(sys.modules) if k == "cumulusci" or k.startswith("cumulusci.")}
        blocked["cumulusci"] = None
        spec = importlib.util.spec_from_file_location(
            "_stamp_commit_no_cci", REPO_ROOT / "tasks" / "rlm_stamp_commit.py"
        )
        fallback = importlib.util.module_from_spec(spec)
        with mock.patch.dict(sys.modules, blocked):
            spec.loader.exec_module(fallback)
        self.assertIs(fallback.SFDXBaseTask, object)
        self.assertIs(fallback.TaskOptionsError, Exception)
        self.assertIs(fallback.CommandException, Exception)
        self.assertIs(fallback.StampGitCommit.keychain_class, object)


class RunTask(unittest.TestCase):
    def run_task(self, task, runner):
        with mock.patch.object(mod.subprocess, "run", runner):
            with self.assertLogs("test_rlm_stamp_commit", level="DEBUG") as logs:
                task._run_task()
        return logs.output

    def test_missing_org_config_is_an_options_error(self):
        for org in (None, False):
            with self.subTest(org=org):
                task = make_task(org_config=org)
                runner = FakeRunner()
                with mock.patch.object(mod.subprocess, "run", runner):
                    with self.assertRaisesRegex(mod.TaskOptionsError, "No org config available"):
                        task._run_task()
                self.assertEqual(runner.calls, [], "must fail before running git or sf")

    def test_org_without_username_is_an_options_error(self):
        for username in (None, ""):
            with self.subTest(username=username):
                task = make_task(org_config=make_org(username=username))
                runner = FakeRunner()
                with mock.patch.object(mod.subprocess, "run", runner):
                    with self.assertRaisesRegex(mod.TaskOptionsError, "Org config has no username"):
                        task._run_task()
                self.assertEqual(runner.calls, [])

    def test_happy_path_deploys_the_record_with_every_field(self):
        project = make_project(custom={"billing": True, "qb": False, "api_token": "s3cr3t-v4lue"})
        task = make_task(options={"flow_name": "prepare_rlm_org"}, project_config=project)
        runner = FakeRunner(git={("rev-parse", "--abbrev-ref", "HEAD"): "feature/x"})
        logs = self.run_task(task, runner)

        # The exact deploy command, run from the temp dir with a relative source dir.
        (cmd, kwargs), = runner.sf_calls()
        self.assertEqual(cmd, [
            "sf", "project", "deploy", "start",
            "--source-dir", "force-app",
            "--target-org", "stamp@example.com",
            "--ignore-conflicts",
            "--wait", "4",
            "--json",
        ])
        self.assertEqual(kwargs["timeout"], mod.DEPLOY_TIMEOUT_SECONDS)
        self.assertIs(kwargs["check"], False)
        self.assertTrue(os.path.basename(runner.deploy_cwd).startswith("rlm_stamp_"))
        self.assertFalse(os.path.exists(runner.deploy_cwd), "temp dir must be removed after deploy")

        project_json = json.loads(runner.deployed_files["sfdx-project.json"])
        self.assertEqual(project_json, {
            "packageDirectories": [{"path": "force-app", "default": True}],
            "sfdcLoginUrl": "https://login.salesforce.com",
            "sourceApiVersion": "66.0",
        })

        root, values = cmdt_values(runner.deployed_files[CMDT_RELPATH])
        self.assertEqual(root.find(f"{MD_NS}label").text, "Latest")
        self.assertEqual(root.find(f"{MD_NS}protected").text, "false")
        self.assertEqual(values["RLM_Commit_Hash__c"], ("xsd:string", SHORT))
        self.assertEqual(values["RLM_Full_Commit_Hash__c"], ("xsd:string", FULL))
        self.assertEqual(values["RLM_Branch__c"], ("xsd:string", "feature/x"))
        self.assertEqual(values["RLM_Dirty_Tree__c"], ("xsd:boolean", "false"))
        self.assertEqual(values["RLM_CCI_Flow__c"], ("xsd:string", "prepare_rlm_org"))
        self.assertEqual(values["RLM_Org_Definition__c"], ("xsd:string", "beta (scratch, orgs/beta.json)"))
        stamp_type, stamp = values["RLM_Build_Timestamp__c"]
        self.assertEqual(stamp_type, "xsd:dateTime")
        self.assertRegex(stamp, r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        self.assertEqual(
            yaml.safe_load(values["RLM_Feature_Flags__c"][1]),
            {"api_token": "[REDACTED]", "billing": True, "qb": False},
        )
        # The secret value is nowhere in what was shipped.
        self.assertNotIn("s3cr3t-v4lue", runner.deployed_files[CMDT_RELPATH])

        joined = "\n".join(logs)
        self.assertIn(f"Stamping org with commit {SHORT} (branch: feature/x, flow: prepare_rlm_org", joined)
        self.assertIn(f"Stamped org: commit={SHORT}, branch=feature/x", joined)
        self.assertNotIn("Failed to stamp org", joined)

    def test_flow_name_defaults_to_manual(self):
        for options in ({}, {"flow_name": ""}, {"flow_name": None}):
            with self.subTest(options=options):
                runner = FakeRunner()
                self.run_task(make_task(options=options), runner)
                _, values = cmdt_values(runner.deployed_files[CMDT_RELPATH])
                self.assertEqual(values["RLM_CCI_Flow__c"][1], "manual")

    def test_dirty_tree_is_stamped_and_labelled(self):
        runner = FakeRunner(git={("status", "--porcelain"): "?? new_file.py"})
        logs = self.run_task(make_task(), runner)
        _, values = cmdt_values(runner.deployed_files[CMDT_RELPATH])
        self.assertEqual(values["RLM_Dirty_Tree__c"], ("xsd:boolean", "true"))
        self.assertIn(f"Stamped org: commit={SHORT} (dirty),", "\n".join(logs))

    def test_deploy_failure_is_a_warning_not_an_error(self):
        failure = json.dumps({"status": 1, "message": "INVALID_SESSION_ID"})
        runner = FakeRunner(deploy_stdout=failure, deploy_returncode=1)
        logs = self.run_task(make_task(), runner)  # must not raise
        joined = "\n".join(logs)
        self.assertIn("WARNING", joined)
        self.assertIn("Failed to stamp org (non-fatal): Deploy failed: INVALID_SESSION_ID", joined)
        self.assertNotIn("Stamped org:", joined)
        self.assertFalse(os.path.exists(runner.deploy_cwd), "temp dir must be removed on failure too")

    def test_sf_missing_is_also_non_fatal(self):
        runner = FakeRunner(deploy_exc=FileNotFoundError("sf"))
        logs = self.run_task(make_task(), runner)
        self.assertIn("sf command not found", "\n".join(logs))

    def test_git_failure_before_deploy_is_fatal(self):
        # Only the deploy is wrapped as non-fatal; a git error propagates and no deploy runs.
        err = subprocess.CalledProcessError(128, ["git"], stderr="fatal: not a git repository")
        runner = FakeRunner(git_exc={("rev-parse", "--short", "HEAD"): err})
        with mock.patch.object(mod.subprocess, "run", runner):
            with self.assertRaisesRegex(
                mod.CommandException,
                r"git command failed: git rev-parse --short HEAD\nfatal: not a git repository",
            ):
                make_task()._run_task()
        self.assertEqual(runner.sf_calls(), [])


class GitHelpers(unittest.TestCase):
    def git_task(self, runner):
        task = make_task()
        patcher = mock.patch.object(mod.subprocess, "run", runner)
        patcher.start()
        self.addCleanup(patcher.stop)
        return task

    def test_git_strips_output_and_runs_with_check_and_timeout(self):
        runner = FakeRunner(git={("log", "-1"): "  hello  "})
        task = self.git_task(runner)
        self.assertEqual(task._git("log", "-1"), "hello")
        cmd, kwargs = runner.calls[-1]
        self.assertEqual(cmd, ["git", "log", "-1"])
        self.assertEqual(kwargs, {"capture_output": True, "text": True, "check": True, "timeout": 10})

    def test_git_not_installed(self):
        runner = FakeRunner(git_exc={("rev-parse", "HEAD"): FileNotFoundError("git")})
        task = self.git_task(runner)
        with self.assertRaisesRegex(mod.CommandException, "git not found"):
            task._git("rev-parse", "HEAD")

    def test_branch_on_a_named_branch(self):
        task = self.git_task(FakeRunner(git={("rev-parse", "--abbrev-ref", "HEAD"): "main"}))
        self.assertEqual(task._resolve_branch(SHORT), "main")

    def test_detached_head_on_a_tag_uses_the_tag(self):
        runner = FakeRunner(git={
            ("rev-parse", "--abbrev-ref", "HEAD"): "HEAD",
            ("describe", "--tags", "--exact-match", "HEAD"): "v264.1",
        })
        self.assertEqual(self.git_task(runner)._resolve_branch(SHORT), "v264.1")

    def test_detached_head_without_a_tag_falls_back_to_the_hash(self):
        runner = FakeRunner(
            git={("rev-parse", "--abbrev-ref", "HEAD"): "HEAD"},
            git_exc={("describe", "--tags", "--exact-match", "HEAD"):
                     subprocess.CalledProcessError(128, ["git"], stderr="no tag exactly matches")},
        )
        self.assertEqual(self.git_task(runner)._resolve_branch(SHORT), f"detached@{SHORT}")

    def dirty(self, porcelain):
        runner = FakeRunner(git={("status", "--porcelain"): porcelain})
        return self.git_task(runner)._is_dirty_tree()

    def test_clean_tree(self):
        self.assertIs(self.dirty(""), False)

    def test_any_change_outside_build_output_is_dirty(self):
        for porcelain in ("?? scratch.txt", "M  tasks/rlm_x.py", "A  docs/new.md\n?? unpackaged/post_ux/x"):
            with self.subTest(porcelain=porcelain):
                self.assertIs(self.dirty(porcelain), True)

    def test_only_build_output_changes_are_clean(self):
        porcelain = (
            "M  unpackaged/post_ux/assembly_manifest.json\n"
            " M unpackaged/post_ux/objects/Quote.object-meta.xml\n"
            "?? unpackaged/post_ux/layouts/"
        )
        self.assertIs(self.dirty(porcelain), False)

    def test_a_rename_across_the_build_output_boundary_is_dirty_either_way(self):
        self.assertIs(self.dirty("R  unpackaged/post_ux/a.xml -> force-app/a.xml"), True)
        self.assertIs(self.dirty("R  force-app/a.xml -> unpackaged/post_ux/a.xml"), True)
        self.assertIs(self.dirty("R  unpackaged/post_ux/a.xml -> unpackaged/post_ux/b.xml"), False)

    def test_pins_suspected_bug_first_unstaged_build_output_line_reads_dirty(self):
        # PINS A SUSPECTED BUG. `_git` strips stdout, which removes the leading space of the
        # first porcelain line when its index column is blank (" M path"). `line[3:]` then
        # drops the path's first character ("npackaged/post_ux/..."), so the exclusion
        # misses and an unstaged, regenerated post_ux file - the state every build leaves -
        # stamps the tree dirty. The same line in second position is excluded correctly.
        # If this assertion starts failing, the bug was fixed: flip it to False.
        self.assertIs(self.dirty(" M unpackaged/post_ux/assembly_manifest.json"), True)
        self.assertIs(
            self.dirty("M  unpackaged/post_ux/a.json\n M unpackaged/post_ux/assembly_manifest.json"),
            False,
        )


class OrgDefinition(unittest.TestCase):
    def definition(self, **org):
        task = make_task(org_config=SimpleNamespace(**org))
        return task._resolve_org_definition()

    def test_scratch_with_relative_config_file(self):
        self.assertEqual(
            self.definition(config_name="beta", scratch=True, config_file="orgs/beta.json"),
            "beta (scratch, orgs/beta.json)",
        )

    def test_sandbox_without_config_file(self):
        self.assertEqual(
            self.definition(config_name="dev-sb0", scratch=False, is_sandbox=True),
            "dev-sb0 (sandbox)",
        )

    def test_absolute_config_file_is_reduced_to_its_basename(self):
        # Keeps CI runner paths (/home/runner/...) out of the org.
        self.assertEqual(
            self.definition(config_name="beta", scratch=True,
                            config_file="/home/runner/work/repo/orgs/beta.json"),
            "beta (scratch, beta.json)",
        )

    def test_scratch_wins_over_sandbox(self):
        self.assertEqual(self.definition(config_name="x", scratch=True, is_sandbox=True), "x (scratch)")

    def test_nothing_known_is_production(self):
        # The org-type part is always present, so the "unknown" fallback is unreachable.
        self.assertEqual(self.definition(), "(production)")


class FeatureFlags(unittest.TestCase):
    def flags(self, custom, missing=False):
        project = SimpleNamespace(project__package__api_version="66.0")
        if not missing:
            project.project__custom = custom
        return make_task(project_config=project)._resolve_feature_flags()

    def test_scalars_only_sorted_yaml(self):
        out = self.flags({
            "zeta": "z", "billing": True, "count": 3,
            "permsets": ["A", "B"], "nested": {"a": 1},
        })
        self.assertEqual(out, "billing: true\ncount: 3\nzeta: z")

    def test_secret_looking_keys_are_redacted_not_stamped(self):
        custom = {
            "billing": True,
            "GitHub_Token": "ghp_realtoken",
            "db_password": "hunter2",
            "client_secret": "shh",
            "sf_auth_url": "force://x",
            "my_apikey": "k1",
            "service_credential": "c1",
        }
        out = self.flags(custom)
        parsed = yaml.safe_load(out)
        self.assertEqual(parsed["billing"], True)
        for key in custom:
            if key != "billing":
                self.assertEqual(parsed[key], "[REDACTED]", key)
        for secret in ("ghp_realtoken", "hunter2", "shh", "force://x", "k1", "c1"):
            self.assertNotIn(secret, out)

    def test_secret_key_detection(self):
        for key in ("token", "API_KEY", "apikey", "Secret", "passwd", "PASSWORD",
                    "private_key_path", "credentials", "oauth_client"):
            with self.subTest(key=key):
                self.assertTrue(StampGitCommit._is_potential_secret_key(key))
        for key in ("billing", "quantumbit", "pde", "trial", "docgen", "keyword"):
            with self.subTest(key=key):
                self.assertFalse(StampGitCommit._is_potential_secret_key(key))

    def test_no_scalar_config_is_none(self):
        self.assertEqual(self.flags({}), "none")
        self.assertEqual(self.flags(None), "none")
        self.assertEqual(self.flags({"only_list": [1], "only_dict": {}}), "none")
        self.assertEqual(self.flags(None, missing=True), "none")

    def test_oversized_config_is_truncated_to_the_field_limit(self):
        out = self.flags({"big": "x" * 40000})
        self.assertEqual(len(out), 32000)
        self.assertRegex(out, r"\n\n\[TRUNCATED: original length \d+ chars exceeds 32000\]$")
        self.assertTrue(out.startswith("big: "))

    def test_exactly_the_limit_is_not_truncated(self):
        value = "x" * (32000 - len("k: "))
        out = self.flags({"k": value})
        self.assertEqual(len(out), 32000)
        self.assertNotIn("TRUNCATED", out)


class RecordGeneration(unittest.TestCase):
    FIELDS = dict(
        commit_hash_short=SHORT, commit_hash_full=FULL,
        branch="feat/a&b<c>", dirty=True, build_timestamp="2026-11-19T00:00:00Z",
        flow_name="flow \"x\" & y", org_definition="o", feature_flags="k: <v>",
    )

    def test_values_are_xml_escaped_and_the_record_parses(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_task()._write_cmdt_record(tmp, **self.FIELDS)
            raw = Path(tmp, CMDT_RELPATH).read_text(encoding="utf-8")
        self.assertIn("feat/a&amp;b&lt;c&gt;", raw)
        _, values = cmdt_values(raw)  # would raise on an unescaped & or <
        self.assertEqual(values["RLM_Branch__c"][1], "feat/a&b<c>")
        self.assertEqual(values["RLM_CCI_Flow__c"][1], 'flow "x" & y')
        self.assertEqual(values["RLM_Feature_Flags__c"][1], "k: <v>")
        self.assertEqual(values["RLM_Dirty_Tree__c"], ("xsd:boolean", "true"))
        self.assertEqual(len(values), 8)

    def test_sfdx_project_api_version_is_a_string(self):
        task = make_task(project_config=make_project(api_version=66.0))
        with tempfile.TemporaryDirectory() as tmp:
            task._write_sfdx_project(tmp)
            data = json.loads(Path(tmp, "sfdx-project.json").read_text(encoding="utf-8"))
        self.assertEqual(data["sourceApiVersion"], "66.0")


class Deploy(unittest.TestCase):
    def deploy(self, stdout=None, returncode=0, exc=None):
        runner = FakeRunner(deploy_stdout=stdout, deploy_returncode=returncode, deploy_exc=exc)
        task = make_task()
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(mod.subprocess, "run", runner):
                task._deploy(tmp, "stamp@example.com")
        return runner

    def test_result_success_true_passes(self):
        runner = self.deploy(json.dumps({"status": 0, "result": {"success": True}}))
        self.assertEqual(len(runner.sf_calls()), 1)

    def test_result_success_false_fails_even_with_status_zero(self):
        out = {"status": 0, "result": {"success": False, "details": {"componentFailures": {
            "fullName": "RLM_Build_Info.Latest", "problem": "Field RLM_Branch__c does not exist"}}}}
        with self.assertRaisesRegex(
            mod.CommandException,
            r"Deploy failed: Component failures:\n  RLM_Build_Info\.Latest: Field RLM_Branch__c does not exist",
        ):
            self.deploy(json.dumps(out))

    def test_no_result_success_falls_back_to_status(self):
        with self.assertRaisesRegex(mod.CommandException, "Deploy failed: No authorization information"):
            self.deploy(json.dumps({"status": 1, "message": "No authorization information"}), returncode=1)
        # status 0 and no result.success is a pass
        self.deploy(json.dumps({"status": 0, "result": {}}))

    def test_no_status_falls_back_to_return_code(self):
        with self.assertRaisesRegex(mod.CommandException, "Deploy failed: boom"):
            self.deploy(json.dumps({"message": "boom"}), returncode=1)
        self.deploy(json.dumps({"result": None}), returncode=0)

    def test_invalid_json(self):
        with self.assertRaisesRegex(mod.CommandException, r"invalid JSON\.\nExit code: 2\nStdout: not json"):
            self.deploy("not json", returncode=2)

    def test_timeout(self):
        exc = subprocess.TimeoutExpired(["sf"], 300)
        with self.assertRaisesRegex(mod.CommandException, "Deploy timed out after 300 seconds"):
            self.deploy(exc=exc)

    def test_sf_not_installed(self):
        with self.assertRaisesRegex(mod.CommandException, "sf command not found"):
            self.deploy(exc=FileNotFoundError("sf"))


class ExtractDeployError(unittest.TestCase):
    extract = staticmethod(StampGitCommit._extract_deploy_error)

    def test_top_level_message_wins(self):
        out = {"message": "top", "result": {"errorMessage": "inner"}}
        self.assertEqual(self.extract(out), "top")

    def test_component_failures_are_capped_at_five_with_name_fallbacks(self):
        failures = [{"fullName": f"C{i}", "problem": f"p{i}"} for i in range(5)]
        failures += [{"fullName": "C5", "problem": "p5"}, {"fullName": "C6", "problem": "p6"}]
        failures[1] = {"fileName": "file1.xml", "problem": "p1"}
        failures[2] = {}
        msg = self.extract({"result": {"details": {"componentFailures": failures}}})
        lines = msg.splitlines()
        self.assertEqual(lines[0], "Component failures:")
        self.assertEqual(lines[1:], ["  C0: p0", "  file1.xml: p1", "  unknown: unknown", "  C3: p3", "  C4: p4"])
        self.assertNotIn("C5", msg)

    def test_result_error_message_then_message(self):
        self.assertEqual(self.extract({"result": {"errorMessage": "em", "message": "m"}}), "em")
        self.assertEqual(self.extract({"result": {"message": "m"}}), "m")

    def test_unknown_shape_dumps_the_response(self):
        msg = self.extract({"status": 1, "result": None})
        self.assertTrue(msg.startswith("Unknown error. Full response:\n"))
        self.assertIn('"status": 1', msg)


if __name__ == "__main__":
    unittest.main()
