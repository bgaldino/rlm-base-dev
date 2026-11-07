"""Offline checks for scripts/ai/org_cleanup.py.

The tool removes local auth, so these tests pin what must never happen: acting without hub
evidence, touching a live org's login because it looks like a stale one, printing a token,
or running a command that deletes an org.
Stdlib only. Run with: python tests/test_org_cleanup.py
"""
import contextlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts" / "ai"))
import org_cleanup as oc  # noqa: E402

TODAY = "2026-11-06"
HUB = "admin@hub.invalid"
SECRET = "SECRET-TOKEN-VALUE-1234567890"
DEAD_ORG = "00DAA0000000001"
LIVE_ORG = "00DAA0000000002"
NO_ROW_ORG = "00DAA0000000003"


def row(org, status="Deleted", expires="2026-01-01", user="signup@x.invalid"):
    return {"ScratchOrg": org, "SignupUsername": user, "Status": status, "ExpirationDate": expires}


class FakeCli:
    """Answers sf, cci and git from fixtures, recording every command."""

    def __init__(self, home, hub_rows=(), aliases=None, cci=None, fail_hubs=(), fail_logout=()):
        self.home, self.calls = home, []
        self.hub_rows, self.aliases = list(hub_rows), dict(aliases or {})
        self.cci, self.fail_hubs, self.fail_logout = cci, set(fail_hubs), set(fail_logout)
        self.tracked, self.config = set(), None

    def __call__(self, cmd):
        self.calls.append(cmd)
        if cmd[0] == "git":
            return 0, cmd[-1] + "\n" if cmd[-1] in self.tracked else ""
        if cmd[0] == "cci":
            if self.cci is None:
                return 1, ""
            return 0, "noise\nORG_CLEANUP_CCI " + json.dumps(self.cci) + "\n"
        args = cmd[1:]
        if args[:2] == ["alias", "list"]:
            rows = [{"alias": a, "value": v} for a, v in self.aliases.items()]
            return self.ok(rows)
        if args[:2] == ["alias", "unset"]:
            self.aliases.pop(args[2], None)
            return self.ok([{"alias": args[2], "success": True}])
        if args[:2] == ["data", "query"]:
            return self.query(args)
        if args[:2] == ["org", "logout"]:
            user = args[3]
            if user in self.fail_logout:
                return 1, json.dumps({"status": 1, "name": "Failed"})
            (self.home / ".sfdx" / (user + ".json")).unlink()
            self.aliases = {a: v for a, v in self.aliases.items() if v != user}
            if self.config:  # the real logout clears config keys naming the user
                data = json.loads(self.config.read_text())
                self.config.write_text(json.dumps({k: v for k, v in data.items() if v != user}))
            return self.ok([user])
        if args[:2] == ["config", "unset"]:
            return self.ok({"successes": [{"name": "target-org"}]})
        raise AssertionError("unexpected command: {}".format(cmd))

    @staticmethod
    def ok(result):
        return 0, json.dumps({"status": 0, "result": result})

    def query(self, args):
        hub, soql = args[3], args[5]
        if hub in self.fail_hubs:
            return 10, json.dumps({"status": 10, "name": "TypeError"})
        field = re.search(r"WHERE (\w+) IN", soql).group(1)
        values = re.search(r"IN \('(.*)'\)", soql).group(1).split("','")
        return self.ok({"done": True, "records": [r for r in self.hub_rows if r[field] in values]})


class Base(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.home, self.project = root / "home", root / "project"
        for path in (self.home / ".sfdx", self.home / ".sf" / "manifestCache",
                     self.project / ".sf" / "orgs", self.project / ".sfdx" / "orgs"):
            path.mkdir(parents=True)
        (self.project / "cumulusci.yml").write_text("project: {}\n")
        (self.project / "sfdx-project.json").write_text("{}\n")
        self.add_auth(HUB, "00DHUB000000001", isDevHub=True)
        self.quarantine = root / "quarantine"

    def add_auth(self, user, org, **fields):
        data = dict(username=user, orgId=org + "MAA", refreshToken=SECRET, accessToken=SECRET)
        data.update(fields)
        (self.home / ".sfdx" / (user + ".json")).write_text(json.dumps(data))

    def plan(self, cli):
        return oc.build_plan(cli, self.home, self.project, TODAY)


class Classification(unittest.TestCase):
    def test_lifecycle_classes(self):
        cases = [
            ([], "unknown"),
            ([row("x")], "deleted"),
            ([row("x", "Active", "2026-12-01")], "active"),
            ([row("x", "Active", "2026-11-06")], "active"),  # expiring today is not past
            ([row("x", "Active", "2026-11-05")], "conflict"),
            ([row("x", "Error", "2026-11-05")], "expired"),
            ([row("x", "Error", "2026-11-06")], "unknown"),
            ([row("x", "New", "2026-12-01")], "unknown"),
            ([row("x"), row("x", "Active", "2026-12-01")], "conflict"),
        ]
        for rows, expected in cases:
            self.assertEqual(oc.classify(rows, TODAY), expected, rows)


class Evidence(Base):
    def test_only_a_login_on_a_deleted_org_is_removed(self):
        self.add_auth("rep@x.invalid." + DEAD_ORG.lower(), DEAD_ORG, isScratch=False)
        self.add_auth("rep@x.invalid." + LIVE_ORG.lower(), LIVE_ORG, isScratch=False)
        self.add_auth("persistent@x.invalid", NO_ROW_ORG)
        cli = FakeCli(self.home, [row(DEAD_ORG), row(LIVE_ORG, "Active", "2026-12-01")])
        remove = self.plan(cli)["remove"]
        self.assertEqual(remove["logout"], ["rep@x.invalid." + DEAD_ORG.lower()])

    def test_a_failed_hub_query_removes_nothing_and_says_so(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)], fail_hubs=[HUB]))
        self.assertEqual(plan["remove"]["logout"], [])
        self.assertEqual(plan["hub_failures"], [HUB])

    def test_a_row_on_a_second_hub_counts_and_an_absent_row_elsewhere_does_not_block(self):
        self.add_auth("hub2@x.invalid", "00DHUB000000002", isDevHub=True)
        self.add_auth("rep@x.invalid", DEAD_ORG)
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)], fail_hubs=["hub2@x.invalid"]))
        self.assertEqual(plan["remove"]["logout"], ["rep@x.invalid"])

    def test_a_dev_hub_is_never_logged_out(self):
        plan = self.plan(FakeCli(self.home, [row("00DHUB000000001")]))
        self.assertEqual(plan["remove"]["logout"], [])

    def test_a_sandbox_is_never_logged_out(self):
        self.add_auth("sbx@x.invalid", DEAD_ORG, isSandbox=True)
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(plan["remove"]["logout"], [])

    def test_conflicting_evidence_is_preserved_and_reported(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG, "Active", "2026-01-01")]))
        self.assertEqual(plan["remove"]["logout"], [])
        self.assertEqual(plan["report"]["conflicting_evidence"], ["rep@x.invalid"])

    def test_a_token_only_login_is_reported_not_removed(self):
        self.add_auth("tok@x.invalid", LIVE_ORG, refreshToken="")
        plan = self.plan(FakeCli(self.home, [row(LIVE_ORG, "Active", "2026-12-01")]))
        self.assertEqual(plan["remove"]["logout"], [])
        self.assertEqual(plan["report"]["logins_with_no_refresh_token"], ["tok@x.invalid"])

    def test_18_character_state_matches_on_15(self):
        (self.home / ".sfdx" / (DEAD_ORG + "MAA.json")).write_text("{}")
        (self.project / ".sf" / "orgs" / (DEAD_ORG + "MAA")).mkdir()
        remove = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))["remove"]
        self.assertEqual(len(remove["indexes"]), 1)
        self.assertEqual(len(remove["tracking"]), 1)


class UsernameKeyedState(Base):
    def test_orphan_alias_needs_a_deleted_signup_row(self):
        rows = [row("00DBB0000000001", user="gone@x.invalid")]
        aliases = {"stale": "gone@x.invalid", "no-row": "unknown@x.invalid"}
        remove = self.plan(FakeCli(self.home, rows, aliases))["remove"]
        self.assertEqual(remove["aliases"], ["stale"])

    def test_alias_of_a_valid_alias_is_kept(self):
        self.add_auth("real@x.invalid", NO_ROW_ORG)
        aliases = {"base": "real@x.invalid", "chained": "base"}
        self.assertEqual(self.plan(FakeCli(self.home, [], aliases))["remove"]["aliases"], [])

    def test_alias_of_a_stale_alias_is_removed(self):
        rows = [row("00DBB0000000001", user="gone@x.invalid")]
        aliases = {"base": "gone@x.invalid", "chained": "base"}
        remove = self.plan(FakeCli(self.home, rows, aliases))["remove"]
        self.assertEqual(remove["aliases"], ["base", "chained"])

    def test_alias_of_a_direct_alias_of_a_logged_out_user_is_listed(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        aliases = {"base": "rep@x.invalid", "chained": "base", "deeper": "chained"}
        remove = self.plan(FakeCli(self.home, [row(DEAD_ORG)], aliases))["remove"]
        self.assertEqual(remove["logout"], ["rep@x.invalid"])
        # Logout clears "base" itself, and only that, so the two that reach it remain on the plan.
        self.assertEqual(remove["aliases"], ["chained", "deeper"])

    def test_preserved_aliases_excludes_those_logout_clears(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        aliases = {"base": "rep@x.invalid", "chained": "base", "keep": HUB, "keep2": "keep"}
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)], aliases))
        self.assertEqual(plan["remove"]["aliases"], ["chained"])
        self.assertEqual(plan["preserved"]["aliases"], 2)

    def test_legacy_username_tracking_needs_a_deleted_signup_row(self):
        for name in ("gone@x.invalid", "unknown@x.invalid"):
            (self.project / ".sfdx" / "orgs" / name).mkdir()
        rows = [row("00DBB0000000001", user="gone@x.invalid")]
        tracking = self.plan(FakeCli(self.home, rows))["remove"]["tracking"]
        self.assertEqual([Path(p).name for p in tracking], ["gone@x.invalid"])

    def test_deploy_job_follows_its_target(self):
        cache = {"job1": {"target-org": "gone@x.invalid"}, "job2": {"target-org": "unknown@x.invalid"}}
        (self.home / ".sf" / "deploy-cache.json").write_text(json.dumps(cache))
        rows = [row("00DBB0000000001", user="gone@x.invalid")]
        self.assertEqual(self.plan(FakeCli(self.home, rows))["remove"]["deploy_jobs"], ["job1"])

    def test_a_stale_default_is_flagged_and_a_valid_one_is_not(self):
        (self.project / ".sf" / "config.json").write_text(json.dumps({"target-org": "stale"}))
        (self.home / ".sf" / "config.json").write_text(json.dumps({"target-org": HUB}))
        rows = [row("00DBB0000000001", user="gone@x.invalid")]
        plan = self.plan(FakeCli(self.home, rows, {"stale": "gone@x.invalid"}))
        self.assertEqual(plan["remove"]["defaults"], ["local"])


class PrunePrediction(Base):
    ORGS = [
        dict(name="shape-old", shape=True, active=False, scratch=True, expired=True,
             instantiated=True, default=False, alias="p__shape-old"),
        dict(name="old", shape=False, active=False, scratch=True, expired=True,
             instantiated=True, default=False, alias="p__old"),
        dict(name="other-branch", shape=False, active=False, scratch=True, expired=False,
             instantiated=False, default=False, alias="p__other-branch"),
        dict(name="current", shape=False, active=True, scratch=True, expired=False,
             instantiated=True, default=True, alias="p__current"),
        dict(name="connected", shape=False, active=False, scratch=False, expired=False,
             instantiated=False, default=False, alias=""),
    ]

    def test_matches_what_prune_does(self):
        predicted = self.plan(FakeCli(self.home, cci=self.ORGS))["prune_prediction"]
        self.assertEqual(predicted["would_remove_expired"], ["old"])
        self.assertEqual(predicted["would_remove_never_instantiated"], ["other-branch"])
        self.assertEqual(predicted["expired_shape_instances_it_skips"], ["shape-old"])
        self.assertEqual(predicted["would_remove_but_active_on_hub"], [])
        self.assertEqual(predicted["default"], "current")

    def test_flags_a_local_expiry_the_hub_disagrees_with(self):
        self.add_auth("live@x.invalid", LIVE_ORG)
        cli = FakeCli(self.home, [row(LIVE_ORG, "Active", "2026-12-01")],
                      {"p__old": "live@x.invalid"}, self.ORGS)
        predicted = self.plan(cli)["prune_prediction"]
        self.assertEqual(predicted["would_remove_but_active_on_hub"], ["old"])

    def test_unavailable_cci_is_not_a_prediction(self):
        self.assertEqual(self.plan(FakeCli(self.home))["prune_prediction"], {"available": False})


class Secrets(Base):
    def test_auth_inventory_holds_no_token_values(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        self.assertNotIn(SECRET, json.dumps(oc.read_auth(self.home)))

    def test_no_token_reaches_the_plan_or_the_output(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        (self.project / ".sfdx" / "saved-auth").write_text(SECRET)
        out = Path(self.project / "plan.json")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = oc.main(["audit", "--out", str(out)], FakeCli(self.home, [row(DEAD_ORG)]),
                           self.home, self.project, TODAY)
        self.assertEqual(code, 0)
        self.assertNotIn(SECRET, stdout.getvalue())
        self.assertNotIn(SECRET, out.read_text())
        self.assertEqual(oct(out.stat().st_mode & 0o777), "0o600")

    def test_an_unknown_file_is_reported_without_being_opened(self):
        unknown = self.project / ".sfdx" / "saved-auth"
        unknown.write_text(SECRET)
        unknown.chmod(0)  # any attempt to read it would raise
        self.addCleanup(unknown.chmod, 0o600)
        files = self.plan(FakeCli(self.home))["report"]["unclassified_files"]
        self.assertEqual([Path(f["path"]).name for f in files], ["saved-auth"])
        self.assertNotIn(SECRET, json.dumps(files))


class Apply(Base):
    def setup_stale_org(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        self.index = self.home / ".sfdx" / (DEAD_ORG + "MAA.json")
        self.index.write_text("{}")
        self.tracking = self.project / ".sf" / "orgs" / (DEAD_ORG + "MAA")
        self.tracking.mkdir()
        (self.tracking / "state").write_text("x")
        self.manifest = self.home / ".sf" / "manifestCache" / "job1.xml"
        self.manifest.write_text("<x/>")
        self.other_manifest = self.home / ".sf" / "manifestCache" / "unmatched.xml"
        self.other_manifest.write_text("<x/>")
        cache = {"job1": {"target-org": "rep@x.invalid"}, "job2": {"target-org": HUB, "keep": 1}}
        (self.home / ".sf" / "deploy-cache.json").write_text(json.dumps(cache))
        return [row(DEAD_ORG), row("00DBB0000000001", user="gone@x.invalid")]

    def audit_then_apply(self, cli, plan_cli=None):
        plan_file = self.project / "plan.json"
        with contextlib.redirect_stdout(io.StringIO()):
            oc.main(["audit", "--out", str(plan_file)], plan_cli or cli, self.home, self.project, TODAY)
        self.stdout, self.stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(self.stdout), contextlib.redirect_stderr(self.stderr):
            return oc.main(["apply", "--plan", str(plan_file), "--quarantine", str(self.quarantine)],
                           cli, self.home, self.project, TODAY)

    def logouts(self, cli):
        return [c for c in cli.calls if c[1:3] == ["org", "logout"]]

    def read_cache(self):
        return json.loads((self.home / ".sf" / "deploy-cache.json").read_text())

    def test_removes_the_allowlist_moves_rather_than_deletes_and_then_is_a_no_op(self):
        rows = self.setup_stale_org()
        cli = FakeCli(self.home, rows, {"stale-a": "gone@x.invalid", "stale-b": "gone@x.invalid"})
        self.assertEqual(self.audit_then_apply(cli), 0)
        self.assertFalse((self.home / ".sfdx" / "rep@x.invalid.json").exists())
        self.assertTrue((self.home / ".sfdx" / (HUB + ".json")).exists())
        self.assertFalse(self.index.exists())
        self.assertTrue((self.quarantine / ".sfdx" / self.index.name).exists())
        self.assertTrue((self.quarantine / "orgs" / self.tracking.name / "state").exists())
        self.assertTrue((self.quarantine / "manifestCache" / "job1.xml").exists())
        self.assertTrue(self.other_manifest.exists())
        cache = json.loads((self.home / ".sf" / "deploy-cache.json").read_text())
        self.assertEqual(cache, {"job2": {"target-org": HUB, "keep": 1}})
        remove = self.plan(cli)["remove"]
        self.assertEqual({k: v for k, v in remove.items() if v}, {})

    def test_aliases_go_one_per_command(self):
        rows = self.setup_stale_org()
        cli = FakeCli(self.home, rows, {"stale-a": "gone@x.invalid", "stale-b": "gone@x.invalid"})
        self.audit_then_apply(cli)
        unsets = [c for c in cli.calls if c[1:3] == ["alias", "unset"]]
        self.assertEqual(len(unsets), 2)
        self.assertTrue(all(len(c) == 5 for c in unsets), unsets)  # sf alias unset <one> --json

    def test_only_supported_and_non_deleting_commands_run(self):
        rows = self.setup_stale_org()
        cli = FakeCli(self.home, rows, {"stale": "gone@x.invalid"}, cci=PrunePrediction.ORGS)
        self.audit_then_apply(cli)
        joined = [" ".join(c) for c in cli.calls]
        for banned in ("org delete", "--clean", "--all", "org prune", "org remove", "org default",
                       "org info", "org display", "ActiveScratchOrg"):
            self.assertFalse([c for c in joined if banned in c], banned)

    def test_audit_does_not_mutate(self):
        rows = self.setup_stale_org()
        cli = FakeCli(self.home, rows, {"stale": "gone@x.invalid"})
        before = sorted(str(p) for p in self.home.rglob("*"))
        with contextlib.redirect_stdout(io.StringIO()):
            oc.main(["audit"], cli, self.home, self.project, TODAY)
        self.assertEqual(sorted(str(p) for p in self.home.rglob("*")), before)
        allowed = (["alias", "list"], ["data", "query"])
        self.assertTrue(all(c[0] in ("cci",) or c[1:3] in allowed for c in cli.calls), cli.calls)

    def test_drift_since_review_stops_before_anything_happens(self):
        rows = self.setup_stale_org()
        plan_cli = FakeCli(self.home, [])  # reviewed when nothing was stale
        cli = FakeCli(self.home, rows)
        self.assertEqual(self.audit_then_apply(cli, plan_cli), 3)
        self.assertTrue((self.home / ".sfdx" / "rep@x.invalid.json").exists())
        self.assertTrue(self.index.exists())

    def test_a_failed_logout_keeps_that_orgs_residual_state(self):
        rows = self.setup_stale_org()
        cli = FakeCli(self.home, rows, fail_logout=["rep@x.invalid"])
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertTrue(self.index.exists())
        self.assertTrue(self.tracking.exists())

    def test_a_failed_logout_keeps_that_users_deploy_entry_and_manifest(self):
        rows = self.setup_stale_org()
        cli = FakeCli(self.home, rows, fail_logout=["rep@x.invalid"])
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertIn("job1", self.read_cache())
        self.assertTrue(self.manifest.exists())
        self.assertIn("FAILED: job1 (skipped because its logout failed)", self.stdout.getvalue())

    def test_a_failed_logout_keeps_jobs_named_by_an_alias_another_logout_cleared(self):
        rows = self.setup_stale_org()
        self.add_auth("second@x.invalid", DEAD_ORG)
        cache = {"job1": {"target-org": "second-alias"}}
        (self.home / ".sf" / "deploy-cache.json").write_text(json.dumps(cache))
        cli = FakeCli(self.home, rows, {"second-alias": "second@x.invalid"},
                      fail_logout=["rep@x.invalid"])
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertNotIn("second-alias", cli.aliases)  # that logout worked and cleared it
        self.assertIn("job1", self.read_cache())  # but its org keeps its state
        self.assertTrue(self.manifest.exists())

    def test_a_failed_logout_keeps_a_chained_alias_and_a_default_naming_the_user(self):
        rows = self.setup_stale_org()
        config = self.project / ".sf" / "config.json"
        config.write_text(json.dumps({"target-org": "rep@x.invalid"}))
        aliases = {"base": "rep@x.invalid", "chained": "base"}
        cli = FakeCli(self.home, rows, aliases, fail_logout=["rep@x.invalid"])
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertEqual(cli.aliases, aliases)
        self.assertEqual([c for c in cli.calls if c[1:3] == ["config", "unset"]], [])

    def test_a_failed_logout_keeps_a_default_naming_its_chained_alias(self):
        rows = self.setup_stale_org()
        (self.project / ".sf" / "config.json").write_text(json.dumps({"target-org": "chained"}))
        aliases = {"base": "rep@x.invalid", "chained": "base"}
        cli = FakeCli(self.home, rows, aliases, fail_logout=["rep@x.invalid"])
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertEqual([c for c in cli.calls if c[1:3] == ["config", "unset"]], [])

    def test_residual_line_appears_when_only_a_tracking_dir_moved(self):
        (self.project / ".sf" / "orgs" / DEAD_ORG).mkdir()
        self.assertEqual(self.audit_then_apply(FakeCli(self.home, [row(DEAD_ORG)])), 0)
        self.assertIn("Residual files moved", self.stdout.getvalue())

    def test_residual_line_appears_when_only_an_index_moved(self):
        (self.home / ".sfdx" / (DEAD_ORG + ".json")).write_text("{}")
        self.assertEqual(self.audit_then_apply(FakeCli(self.home, [row(DEAD_ORG)])), 0)
        self.assertIn("Residual files moved", self.stdout.getvalue())

    def test_residual_line_appears_when_only_a_manifest_moved(self):
        cache = {"job1": {"target-org": "gone@x.invalid"}}
        (self.home / ".sf" / "deploy-cache.json").write_text(json.dumps(cache))
        (self.home / ".sf" / "manifestCache" / "job1.xml").write_text("<x/>")
        rows = [row("00DBB0000000001", user="gone@x.invalid")]
        self.assertEqual(self.audit_then_apply(FakeCli(self.home, rows)), 0)
        self.assertIn("Residual files moved", self.stdout.getvalue())

    def test_a_chained_alias_is_gone_after_apply_and_a_re_audit_is_empty(self):
        rows = self.setup_stale_org()
        config = self.project / ".sf" / "config.json"
        config.write_text(json.dumps({"target-org": "chained"}))
        aliases = {"base": "rep@x.invalid", "chained": "base", "keep": HUB, "keep2": "keep"}
        cli = FakeCli(self.home, rows, aliases)
        self.assertEqual(self.audit_then_apply(cli), 0)
        self.assertEqual(cli.aliases, {"keep": HUB, "keep2": "keep"})
        unsets = [c for c in cli.calls if c[1:3] == ["config", "unset"]]
        self.assertEqual(unsets, [["sf", "config", "unset", "target-org", "--json"]])

    def test_a_quarantine_that_refuses_files_stops_before_any_logout(self):
        rows = self.setup_stale_org()
        cli = FakeCli(self.home, rows)
        # The folder can be created, as ~/.Trash allows: only moving a file in shows the refusal.
        with mock.patch.object(oc.shutil, "move", side_effect=PermissionError(1, "Not permitted")):
            self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertEqual(self.logouts(cli), [])
        self.assertTrue((self.home / ".sfdx" / "rep@x.invalid.json").exists())
        self.assertTrue(self.index.exists())
        self.assertIn("before any logout", self.stderr.getvalue())
        self.assertNotIn("Residual files moved", self.stdout.getvalue())
        self.assertFalse(self.quarantine.exists())
        self.assertEqual(list(self.home.glob(".org-cleanup-probe-*")), [])

    def test_a_quarantine_path_that_cannot_be_examined_is_reported_not_raised(self):
        # Mocked so the result does not depend on the interpreter: Python 3.14 swallows this error.
        with mock.patch.object(oc.Path, "exists", side_effect=PermissionError(13, "Denied")):
            self.assertEqual(oc.check_quarantine(self.quarantine, self.home), "Denied")
        self.assertFalse(self.quarantine.exists())
        self.assertEqual(list(self.home.glob(".org-cleanup-probe-*")), [])

    def test_the_quarantine_check_is_skipped_when_nothing_needs_moving(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        cli = FakeCli(self.home, [row(DEAD_ORG)])
        with mock.patch.object(oc.shutil, "move", side_effect=PermissionError(1, "Not permitted")):
            self.assertEqual(self.audit_then_apply(cli), 0)
        self.assertEqual(len(self.logouts(cli)), 1)
        self.assertNotIn("Residual files moved", self.stdout.getvalue())

    def test_a_move_that_fails_later_is_reported_and_the_run_continues(self):
        rows = self.setup_stale_org()
        real_move, refused = shutil.move, str(self.index)

        def move(src, dst):
            if src == refused:
                raise PermissionError(1, "Not permitted")
            return real_move(src, dst)

        with mock.patch.object(oc.shutil, "move", side_effect=move):
            self.assertEqual(self.audit_then_apply(FakeCli(self.home, rows)), 1)
        self.assertTrue(self.index.exists())
        self.assertIn("could not move: Not permitted", self.stdout.getvalue())
        self.assertIn("Residual files moved", self.stdout.getvalue())
        self.assertTrue((self.quarantine / "orgs" / self.tracking.name / "state").exists())
        self.assertEqual(self.read_cache(), {"job2": {"target-org": HUB, "keep": 1}})

    def test_a_refused_manifest_keeps_its_cache_entry(self):
        rows = self.setup_stale_org()
        taken = self.quarantine / "manifestCache" / "job1.xml"
        taken.parent.mkdir(parents=True)
        taken.write_text("<earlier/>")
        self.assertEqual(self.audit_then_apply(FakeCli(self.home, rows)), 1)
        self.assertIn("job1", self.read_cache())
        self.assertTrue(self.manifest.exists())
        self.assertEqual(taken.read_text(), "<earlier/>")

    def test_a_failed_cache_write_is_reported_and_leaves_the_cache_intact(self):
        rows = self.setup_stale_org()
        before = self.read_cache()
        with mock.patch.object(oc.os, "replace", side_effect=PermissionError(1, "Not permitted")):
            self.assertEqual(self.audit_then_apply(FakeCli(self.home, rows)), 1)
        self.assertEqual(self.read_cache(), before)
        self.assertIn("could not write: Not permitted", self.stdout.getvalue())
        self.assertEqual(list((self.home / ".sf").glob(".deploy-cache.*")), [])

    def test_no_residual_line_when_every_move_was_refused(self):
        rows = self.setup_stale_org()
        (self.home / ".sf" / "deploy-cache.json").unlink()
        self.manifest.unlink()
        cli = FakeCli(self.home, rows)
        cli.tracked.add(str(self.tracking))
        taken = self.quarantine / ".sfdx" / self.index.name
        taken.parent.mkdir(parents=True)
        taken.write_text("{}")
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertNotIn("Residual files moved", self.stdout.getvalue())

    def test_tracked_and_symlinked_state_is_refused(self):
        rows = self.setup_stale_org()
        cli = FakeCli(self.home, rows)
        cli.tracked.add(str(self.tracking))
        target = self.project / "elsewhere"
        target.mkdir()
        link = self.project / ".sf" / "orgs" / "00DAA0000000009MAA"
        link.symlink_to(target)
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertTrue(self.tracking.exists())
        self.assertTrue(link.is_symlink())
        self.assertTrue(target.exists())

    def test_a_default_logout_already_cleared_is_not_unset_again(self):
        rows = self.setup_stale_org()
        config = self.project / ".sf" / "config.json"
        config.write_text(json.dumps({"target-org": "rep@x.invalid"}))
        cli = FakeCli(self.home, rows)
        cli.config = config
        self.assertEqual(self.audit_then_apply(cli), 0)
        self.assertEqual([c for c in cli.calls if c[1:3] == ["config", "unset"]], [])

    def test_a_default_on_an_orphan_alias_is_unset(self):
        rows = self.setup_stale_org()
        (self.project / ".sf" / "config.json").write_text(json.dumps({"target-org": "stale"}))
        cli = FakeCli(self.home, rows, {"stale": "gone@x.invalid"})
        self.assertEqual(self.audit_then_apply(cli), 0)
        unsets = [c for c in cli.calls if c[1:3] == ["config", "unset"]]
        self.assertEqual(unsets, [["sf", "config", "unset", "target-org", "--json"]])

    def test_a_symlink_that_appears_after_the_audit_is_refused(self):
        target = self.project / "elsewhere"
        target.mkdir()
        root = self.project / ".sf" / "orgs"
        link = root / "00DAA0000000009MAA"
        link.symlink_to(target)
        why = oc.move_to_quarantine(FakeCli(self.home), link, [root], self.quarantine, self.project)
        self.assertEqual(why, "symlink")
        self.assertTrue(link.is_symlink())

    def test_a_path_outside_the_state_roots_is_refused(self):
        stray = self.project / "keep.txt"
        stray.write_text("x")
        root = self.project / ".sf" / "orgs"
        why = oc.move_to_quarantine(FakeCli(self.home), stray, [root], self.quarantine, self.project)
        self.assertEqual(why, "outside the expected state roots")
        self.assertTrue(stray.exists())

    def test_a_valid_default_survives(self):
        rows = self.setup_stale_org()
        (self.project / ".sf" / "config.json").write_text(json.dumps({"target-org": HUB}))
        cli = FakeCli(self.home, rows)
        self.audit_then_apply(cli)
        self.assertEqual([c for c in cli.calls if c[1:3] == ["config", "unset"]], [])


class DocStaysInStep(unittest.TestCase):
    DOC = (REPO / ".cursor" / "skills" / "cci-orchestration" / "org-cleanup.md").read_text()

    def test_every_review_key_the_tool_reports_is_explained(self):
        plan_keys = ["hub_failures", "prune_prediction", "conflicting_evidence",
                     "logins_with_no_refresh_token", "unreadable_auth_files",
                     "symlinks_left_alone", "unclassified_files", "would_remove_expired",
                     "would_remove_never_instantiated", "would_remove_but_active_on_hub",
                     "expired_shape_instances_it_skips"]
        source = (REPO / "scripts" / "ai" / "org_cleanup.py").read_text()
        for key in plan_keys:
            self.assertIn(key, source)
            self.assertIn(key, self.DOC)

    def test_doc_names_the_commands_it_depends_on(self):
        for command in ("org_cleanup.py audit", "org_cleanup.py apply", "--check-logins"):
            self.assertIn(command, self.DOC)

    def test_the_tool_never_offers_a_remote_delete(self):
        source = (REPO / "scripts" / "ai" / "org_cleanup.py").read_text()
        code = source.split('"""', 2)[2]  # past the docstring, which names what it never runs
        for banned in ('"delete"', "org delete", "--clean", "ActiveScratchOrg"):
            self.assertNotIn(banned, code)


class Usage(Base):
    def test_refuses_to_run_outside_a_project_root(self):
        elsewhere = self.home
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = oc.main(["audit"], FakeCli(self.home), self.home, elsewhere, TODAY)
        self.assertEqual(code, 2)
        self.assertIn("project root", stderr.getvalue())

    def test_default_quarantine_prefers_the_trash(self):
        self.assertEqual(oc.default_quarantine(self.home, TODAY).name, TODAY)
        (self.home / ".Trash").mkdir()
        self.assertEqual(oc.default_quarantine(self.home, TODAY).parent, self.home / ".Trash")


if __name__ == "__main__":
    unittest.main()
