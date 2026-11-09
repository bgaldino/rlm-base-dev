"""Offline checks for scripts/ai/org_cleanup.py.

The tool removes local auth, so these tests pin what must never happen: acting without hub
evidence, touching a live org's login because it looks like a stale one, printing a token,
or running a command that deletes an org.
Stdlib only. Run with: python tests/test_org_cleanup.py
"""
import contextlib
import errno
import io
import json
import os
import re
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
CANARY = "CANARY-VALUE-1234567890"
DEAD_ORG = "00DAA0000000001"
LIVE_ORG = "00DAA0000000002"
NO_ROW_ORG = "00DAA0000000003"


def row(org, status="Deleted", expires="2026-01-01", user="signup@x.invalid"):
    return {"ScratchOrg": org, "SignupUsername": user, "Status": status, "ExpirationDate": expires}


class FakeCli:
    """Answers sf, cci and git from fixtures, recording every command."""

    def __init__(self, home, hub_rows=(), aliases=None, cci=None, fail_hubs=(), fail_logout=(),
                 clears_before_failing=False):
        self.home, self.calls = home, []
        self.hub_rows, self.aliases = list(hub_rows), dict(aliases or {})
        self.cci, self.fail_hubs, self.fail_logout = cci, set(fail_hubs), set(fail_logout)
        self.tracked, self.config = set(), None
        self.clears_before_failing = clears_before_failing  # what real sf did when unlink failed
        self.override = None  # cmd -> (code, stdout) to answer it, or None for the normal answer

    def __call__(self, cmd):
        self.calls.append(cmd)
        answer = self.override(cmd) if self.override else None
        if answer is not None:
            return answer
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
                if self.clears_before_failing:
                    self.aliases = {a: v for a, v in self.aliases.items() if v != user}
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
        data = dict(username=user, orgId=org + "MAA", refreshToken=CANARY, accessToken=CANARY)
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
            # No past date on either row, so only the mixed statuses can make this a conflict.
            ([row("x", "Deleted", "2026-12-01"), row("x", "Active", "2026-12-01")], "conflict"),
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

    def test_aliases_that_lead_nowhere_are_reported_and_never_listed(self):
        aliases = {"lost": "missing", "cycle-a": "cycle-b", "cycle-b": "cycle-a", "fine": HUB,
                   "no-auth": "gone@x.invalid"}
        plan = self.plan(FakeCli(self.home, aliases=aliases))
        self.assertEqual(plan["report"]["dangling_aliases"], ["cycle-a", "cycle-b", "lost"])
        self.assertEqual(plan["remove"]["aliases"], [])

    def test_a_default_that_leads_nowhere_is_reported_and_never_listed(self):
        (self.project / ".sf" / "config.json").write_text(json.dumps({"target-org": "lost"}))
        (self.home / ".sf" / "config.json").write_text(json.dumps({"target-org": "fine"}))
        plan = self.plan(FakeCli(self.home, aliases={"fine": HUB}))
        self.assertEqual(plan["report"]["dangling_defaults"], ["local"])
        self.assertEqual(plan["remove"]["defaults"], [])

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

    def test_an_unsafe_deploy_cache_key_is_reported_not_planned(self):
        cache = {"../../foo": {"target-org": "gone@x.invalid"}, "job1": {"target-org": "gone@x.invalid"}}
        (self.home / ".sf" / "deploy-cache.json").write_text(json.dumps(cache))
        plan = self.plan(FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")]))
        self.assertEqual(plan["remove"]["deploy_jobs"], ["job1"])
        self.assertEqual(plan["report"]["unsafe_deploy_cache_keys"], ["../../foo"])

    def test_a_stale_default_is_flagged_and_a_valid_one_is_not(self):
        (self.project / ".sf" / "config.json").write_text(json.dumps({"target-org": "stale"}))
        (self.home / ".sf" / "config.json").write_text(json.dumps({"target-org": HUB}))
        rows = [row("00DBB0000000001", user="gone@x.invalid")]
        plan = self.plan(FakeCli(self.home, rows, {"stale": "gone@x.invalid"}))
        self.assertEqual(plan["remove"]["defaults"], ["local"])


    def test_a_scope_holding_a_stale_and_a_valid_default_is_reported_not_unset(self):
        # `sf config unset target-org` clears the scope's key whatever it names.
        (self.project / ".sf" / "config.json").write_text(json.dumps({"target-org": HUB}))
        (self.project / ".sfdx" / "sfdx-config.json").write_text(json.dumps({"defaultusername": "stale"}))
        rows = [row("00DBB0000000001", user="gone@x.invalid")]
        plan = self.plan(FakeCli(self.home, rows, {"stale": "gone@x.invalid"}))
        self.assertEqual(plan["remove"]["defaults"], [])
        self.assertEqual(plan["report"]["mixed_defaults"], ["local"])

    def test_a_default_naming_only_a_username_is_judged_by_the_hub(self):
        (self.project / ".sf" / "config.json").write_text(json.dumps({"target-org": "gone@x.invalid"}))
        rows = [row("00DBB0000000001", user="gone@x.invalid")]
        plan = self.plan(FakeCli(self.home, rows))
        self.assertEqual(plan["remove"]["defaults"], ["local"])

    def test_a_default_username_is_not_judged_while_a_hub_has_not_answered(self):
        self.add_auth("hub2@x.invalid", "00DHUB000000002", isDevHub=True)
        (self.project / ".sf" / "config.json").write_text(json.dumps({"target-org": "gone@x.invalid"}))
        rows = [row("00DBB0000000001", user="gone@x.invalid")]
        plan = self.plan(FakeCli(self.home, rows, fail_hubs=["hub2@x.invalid"]))
        self.assertEqual(plan["hub_failures"], ["hub2@x.invalid"])
        self.assertEqual(plan["remove"]["defaults"], [])

    def test_a_username_is_not_judged_while_a_hub_has_not_answered(self):
        # A signup username can be reused by a newer org on the hub that failed.
        self.add_auth("hub2@x.invalid", "00DHUB000000002", isDevHub=True)
        rows = [row("00DBB0000000001", user="gone@x.invalid")]
        cli = FakeCli(self.home, rows, {"stale": "gone@x.invalid"}, fail_hubs=["hub2@x.invalid"])
        plan = self.plan(cli)
        self.assertEqual(plan["hub_failures"], ["hub2@x.invalid"])
        self.assertEqual(plan["remove"]["aliases"], [])


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

    def test_flags_a_hub_row_that_is_active_past_its_date(self):
        # Active with a past date classifies as conflict: the org may still be live.
        self.add_auth("live@x.invalid", LIVE_ORG)
        cli = FakeCli(self.home, [row(LIVE_ORG, "Active", "2026-01-01")],
                      {"p__old": "live@x.invalid"}, self.ORGS)
        predicted = self.plan(cli)["prune_prediction"]
        self.assertEqual(predicted["would_remove_but_active_on_hub"], ["old"])

    def test_flags_a_hub_with_disagreeing_rows(self):
        self.add_auth("live@x.invalid", LIVE_ORG)
        cli = FakeCli(self.home, [row(LIVE_ORG, "Deleted", "2026-12-01"), row(LIVE_ORG, "Active", "2026-12-01")],
                      {"p__old": "live@x.invalid"}, self.ORGS)
        predicted = self.plan(cli)["prune_prediction"]
        self.assertEqual(predicted["would_remove_but_active_on_hub"], ["old"])

    def test_unavailable_cci_is_not_a_prediction(self):
        self.assertEqual(self.plan(FakeCli(self.home))["prune_prediction"], {"available": False})

    def test_a_malformed_cci_line_is_not_a_prediction(self):
        # Invalid JSON, and valid JSON of the wrong shape, must both degrade to "unavailable".
        for line in ("{not json", "{}", '["a"]', '[{"name": "x"}]'):
            cli = FakeCli(self.home)
            cli.override = lambda cmd, line=line: ((0, "ORG_CLEANUP_CCI " + line + "\n")
                                                   if cmd[0] == "cci" else None)
            self.assertEqual(self.plan(cli)["prune_prediction"], {"available": False}, line)

    def test_an_empty_cci_list_is_an_available_prediction(self):
        predicted = self.plan(FakeCli(self.home, cci=[]))["prune_prediction"]
        self.assertTrue(predicted["available"])
        self.assertEqual(predicted["would_remove_expired"], [])


class Secrets(Base):
    def test_auth_inventory_holds_no_token_values(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        self.assertNotIn(CANARY, json.dumps(oc.read_auth(self.home)))

    def test_no_token_reaches_the_plan_or_the_output(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        (self.project / ".sfdx" / "saved-auth").write_text(CANARY)
        out = Path(self.project / "plan.json")
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = oc.main(["audit", "--out", str(out)], FakeCli(self.home, [row(DEAD_ORG)]),
                           self.home, self.project, TODAY)
        self.assertEqual(code, 0)
        self.assertNotIn(CANARY, stdout.getvalue())
        self.assertNotIn(CANARY, out.read_text())
        self.assertEqual(oct(out.stat().st_mode & 0o777), "0o600")

    def test_a_symlinked_or_renamed_credential_file_is_reported(self):
        elsewhere = self.home / "elsewhere.json"
        elsewhere.write_text(CANARY)
        (self.home / ".sfdx" / "linked@x.invalid.json").symlink_to(elsewhere)
        (self.home / ".sfdx" / "backup@x.invalid.json.bak").write_text(CANARY)
        (self.home / ".sfdx" / "saved@x.invalid.sfdxurl").write_text(CANARY)
        (self.home / ".sfdx" / (DEAD_ORG + "MAA.json")).symlink_to(elsewhere)
        # Only the home roots are read as auth and indexes, so the same names in the project are
        # nobody's: a credential copied into the repo tree must be reported.
        (self.project / ".sfdx" / "copied@x.invalid.json").write_text(CANARY)
        (self.project / ".sf" / (LIVE_ORG + "MAA.json")).write_text(CANARY)
        self.add_auth("plain@x.invalid", LIVE_ORG)  # a regular home auth file is not "unclassified"
        files = self.plan(FakeCli(self.home))["report"]["unclassified_files"]
        names = sorted(Path(f["path"]).name for f in files)
        self.assertEqual(names, sorted(["linked@x.invalid.json", "backup@x.invalid.json.bak",
                                        "saved@x.invalid.sfdxurl", DEAD_ORG + "MAA.json",
                                        "copied@x.invalid.json", LIVE_ORG + "MAA.json"]))
        self.assertNotIn(CANARY, json.dumps(files))

    def test_the_plan_is_created_with_mode_0600(self):
        real_open = os.open
        modes = []

        def spy(path, flags, mode=0o777, **kwargs):
            modes.append(mode)
            return real_open(path, flags, mode, **kwargs)

        with mock.patch.object(oc.os, "open", spy), contextlib.redirect_stdout(io.StringIO()):
            code = oc.main(["audit", "--out", str(self.project / "plan.json")],
                           FakeCli(self.home), self.home, self.project, TODAY)
        self.assertEqual(code, 0)
        self.assertEqual(modes, [0o600])  # never created under the umask and tightened later

    def test_the_plan_is_never_written_through_a_symlink(self):
        victim = self.project / "victim.txt"
        victim.write_text("keep")
        link = self.project / "plan.json"
        link.symlink_to(victim)
        stderr = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
            code = oc.main(["audit", "--out", str(link)], FakeCli(self.home),
                           self.home, self.project, TODAY)
        self.assertEqual(code, 1)
        self.assertEqual(victim.read_text(), "keep")
        self.assertIn("Could not write the plan", stderr.getvalue())

    def test_an_existing_loose_plan_file_is_tightened(self):
        out = self.project / "plan.json"
        out.write_text("old")
        out.chmod(0o644)
        with contextlib.redirect_stdout(io.StringIO()):
            code = oc.main(["audit", "--out", str(out)], FakeCli(self.home),
                           self.home, self.project, TODAY)
        self.assertEqual(code, 0)
        self.assertEqual(oct(out.stat().st_mode & 0o777), "0o600")

    def test_an_unknown_file_is_reported_without_being_opened(self):
        unknown = self.project / ".sfdx" / "saved-auth"
        unknown.write_text(CANARY)
        unknown.chmod(0)  # any attempt to read it would raise
        self.addCleanup(unknown.chmod, 0o600)
        files = self.plan(FakeCli(self.home))["report"]["unclassified_files"]
        self.assertEqual([Path(f["path"]).name for f in files], ["saved-auth"])
        self.assertNotIn(CANARY, json.dumps(files))


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

    def test_a_stale_legacy_tracking_folder_is_moved(self):
        legacy = self.project / ".sfdx" / "orgs" / "gone@x.invalid"
        legacy.mkdir()
        (legacy / "state").write_text("x")
        cli = FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")])
        self.assertEqual(self.audit_then_apply(cli), 0)
        self.assertFalse(legacy.exists())
        self.assertTrue((self.quarantine / "orgs" / legacy.name / "state").exists())

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

    def test_a_plan_reviewed_for_another_project_is_not_applied(self):
        rows = self.setup_stale_org()
        cli = FakeCli(self.home, rows, {"stale": "gone@x.invalid"})
        plan_file = self.project / "plan.json"
        with contextlib.redirect_stdout(io.StringIO()):
            oc.main(["audit", "--out", str(plan_file)], cli, self.home, self.project, TODAY)
        plan = json.loads(plan_file.read_text())
        plan["project"] = str(self.project.parent / "other-project")
        plan_file.write_text(json.dumps(plan))
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = oc.main(["apply", "--plan", str(plan_file), "--quarantine", str(self.quarantine)],
                           cli, self.home, self.project, TODAY)
        self.assertEqual(code, 3)
        self.assertEqual(self.logouts(cli), [])

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

    def test_a_failed_logout_that_cleared_the_direct_alias_does_not_strand_the_chain(self):
        rows = self.setup_stale_org()
        (self.project / ".sf" / "config.json").write_text(json.dumps({"target-org": "chained"}))
        aliases = {"base": "rep@x.invalid", "chained": "base"}
        cli = FakeCli(self.home, rows, aliases, fail_logout=["rep@x.invalid"],
                      clears_before_failing=True)
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertEqual(cli.aliases, {})
        unsets = [c for c in cli.calls if c[1:3] == ["config", "unset"]]
        self.assertEqual(len(unsets), 1)
        self.assertTrue((self.home / ".sfdx" / "rep@x.invalid.json").exists())
        self.assertTrue(self.index.exists())
        again = self.plan(cli)
        self.assertEqual(again["remove"]["logout"], ["rep@x.invalid"])
        self.assertEqual(again["report"]["dangling_aliases"], [])

    def test_a_failed_logout_keeps_the_chain_if_aliases_cannot_be_reread(self):
        rows = self.setup_stale_org()
        aliases = {"base": "rep@x.invalid", "chained": "base"}

        class AliasListBreaks(FakeCli):
            def __call__(self, cmd):
                if cmd[1:3] == ["alias", "list"] and any(c[1:3] == ["org", "logout"] for c in self.calls):
                    self.calls.append(cmd)
                    return 1, json.dumps({"status": 1, "name": "Failed"})
                return super().__call__(cmd)

        cli = AliasListBreaks(self.home, rows, aliases, fail_logout=["rep@x.invalid"],
                              clears_before_failing=True)
        plan_cli = FakeCli(self.home, rows, aliases)
        self.assertEqual(self.audit_then_apply(cli, plan_cli), 1)
        self.assertIn("chained", cli.aliases)

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
        with mock.patch.object(oc.os, "rename", side_effect=PermissionError(1, "Not permitted")):
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
        with mock.patch.object(oc.os, "rename", side_effect=PermissionError(1, "Not permitted")):
            self.assertEqual(self.audit_then_apply(cli), 0)
        self.assertEqual(len(self.logouts(cli)), 1)
        self.assertNotIn("Residual files moved", self.stdout.getvalue())

    def test_a_move_that_fails_later_is_reported_and_the_run_continues(self):
        rows = self.setup_stale_org()
        real_move, refused = os.rename, str(self.index)

        def move(src, dst):
            if src == refused:
                raise PermissionError(1, "Not permitted")
            return real_move(src, dst)

        with mock.patch.object(oc.os, "rename", side_effect=move):
            self.assertEqual(self.audit_then_apply(FakeCli(self.home, rows)), 1)
        self.assertTrue(self.index.exists())
        self.assertIn("could not move: Not permitted", self.stdout.getvalue())
        self.assertIn("Residual files moved", self.stdout.getvalue())
        self.assertTrue((self.quarantine / "orgs" / self.tracking.name / "state").exists())
        self.assertEqual(self.read_cache(), {"job2": {"target-org": HUB, "keep": 1}})

    def test_a_refused_rename_leaves_no_copy_and_a_retry_succeeds(self):
        rows = self.setup_stale_org()
        real_rename, refused = os.rename, str(self.index)

        def rename(src, dst):
            if src == refused:
                raise PermissionError(1, "Not permitted")
            return real_rename(src, dst)

        with mock.patch.object(oc.os, "rename", side_effect=rename):
            self.assertEqual(self.audit_then_apply(FakeCli(self.home, rows)), 1)
        self.assertTrue(self.index.exists())
        self.assertEqual(list(self.quarantine.rglob(self.index.name)), [])
        self.assertEqual(self.audit_then_apply(FakeCli(self.home, rows)), 0)
        self.assertFalse(self.index.exists())

    def test_a_move_across_volumes_still_works(self):
        source, dest = self.home / "file", self.home / "moved"
        source.write_text("x")
        with mock.patch.object(oc.os, "rename", side_effect=OSError(errno.EXDEV, "Cross-device")):
            with mock.patch.object(oc.shutil, "move") as copy_move:
                oc.move_path(str(source), str(dest))
        copy_move.assert_called_once_with(str(source), str(dest))

    def refuse_rename_of(self, path):
        real_rename, refused = os.rename, str(path)

        def rename(src, dst):
            if src == refused:
                raise PermissionError(1, "Not permitted")
            return real_rename(src, dst)

        return mock.patch.object(oc.os, "rename", side_effect=rename)

    def across_volumes(self):
        return mock.patch.object(oc.os, "rename", side_effect=OSError(errno.EXDEV, "Cross-device"))

    def writable_again(self, *paths):
        def restore():
            for path in paths:
                if path.exists():
                    path.chmod(0o755)
        self.addCleanup(restore)

    def files_under(self, path):
        return sorted(str(p.relative_to(path)) for p in path.rglob("*") if p.is_file())

    def test_a_failed_delete_across_volumes_loses_nothing_and_a_retry_finishes(self):
        if os.geteuid() == 0:
            self.skipTest("root ignores the read-only folder")
        root = self.project / ".sf" / "orgs"
        item = root / "00DAA0000000009MAA"
        (item / "sub").mkdir(parents=True)
        for name in ("a", "b", "sub/held"):
            (item / name).write_text("x")
        copy = self.quarantine / "orgs" / item.name
        (item / "sub").chmod(0o555)
        self.writable_again(item / "sub", copy / "sub")
        with self.across_volumes():
            why = oc.move_to_quarantine(FakeCli(self.home), item, [root], self.quarantine, self.project)
            self.assertIn("could not move", why)
            self.assertEqual(self.files_under(copy), ["a", "b", "sub/held"])  # the only complete one
            left = self.files_under(item)  # how far the delete got varies by Python and directory order
            self.assertIn("sub/held", left)
            (item / "sub").chmod(0o755)
            self.assertIsNone(oc.move_to_quarantine(FakeCli(self.home), item, [root], self.quarantine,
                                                    self.project))
        self.assertFalse(item.exists())
        self.assertEqual(self.files_under(copy), ["a", "b", "sub/held"])
        self.assertEqual(self.files_under(copy.with_name(item.name + ".1")), left)

    def test_a_failed_copy_across_volumes_leaves_the_source_and_a_retry_finishes(self):
        if os.geteuid() == 0:
            self.skipTest("root ignores the unreadable file")
        root = self.project / ".sf" / "orgs"
        item = root / "00DAA0000000009MAA"
        item.mkdir(parents=True)
        secret = "secret" + "x" * 150  # long, so the uncapped text exceeds the cap whatever the temp path
        (item / "a").write_text("x")
        (item / secret).write_text("x")
        (item / secret).chmod(0)
        self.addCleanup(lambda: (item / secret).exists() and (item / secret).chmod(0o644))
        with self.across_volumes():
            why = oc.move_to_quarantine(FakeCli(self.home), item, [root], self.quarantine, self.project)
            self.assertIn("could not move", why)
            self.assertLess(len(why), 330)  # shutil.Error's text lists every path it could not copy
            self.assertEqual(self.files_under(item), ["a", secret])
            (item / secret).chmod(0o644)
            self.assertIsNone(oc.move_to_quarantine(FakeCli(self.home), item, [root], self.quarantine,
                                                    self.project))
        self.assertFalse(item.exists())
        retried = self.quarantine / "orgs" / (item.name + ".1")
        self.assertEqual(self.files_under(retried), ["a", secret])

    def test_the_same_name_in_both_tracking_layouts_moves_without_a_collision(self):
        name = "00DAA0000000009MAA"
        results = []
        for layout in (".sf", ".sfdx"):
            root = self.project / layout / "orgs"
            (root / name).mkdir(parents=True)
            (root / name / layout).write_text("x")
            results.append(oc.move_to_quarantine(FakeCli(self.home), root / name, [root], self.quarantine,
                                                 self.project))
        self.assertEqual(results, [None, None])
        orgs = self.quarantine / "orgs"
        self.assertEqual(self.files_under(orgs / name), [".sf"])
        self.assertEqual(self.files_under(orgs / (name + ".1")), [".sfdx"])

    def test_an_item_already_in_the_quarantine_is_kept_and_the_new_one_numbered(self):
        rows = self.setup_stale_org()
        taken = self.quarantine / "manifestCache" / "job1.xml"
        taken.parent.mkdir(parents=True)
        taken.write_text("<earlier/>")
        taken.with_name("job1.xml.1").write_text("<retry/>")
        self.assertEqual(self.audit_then_apply(FakeCli(self.home, rows)), 0)
        self.assertEqual(taken.read_text(), "<earlier/>")
        self.assertEqual(taken.with_name("job1.xml.1").read_text(), "<retry/>")
        self.assertTrue(taken.with_name("job1.xml.2").exists())
        self.assertFalse(self.manifest.exists())
        self.assertNotIn("job1", self.read_cache())

    def test_a_dangling_link_in_the_quarantine_is_kept_and_the_new_item_numbered(self):
        root = self.project / ".sf" / "orgs"
        item = root / "00DAA0000000009MAA"
        item.mkdir(parents=True)
        (item / "state").write_text("x")
        link = self.quarantine / "orgs" / item.name
        link.parent.mkdir(parents=True)
        link.symlink_to(self.project / "nothing-here")
        self.assertIsNone(oc.move_to_quarantine(FakeCli(self.home), item, [root], self.quarantine, self.project))
        self.assertTrue(link.is_symlink())
        self.assertFalse(link.exists())
        self.assertFalse(item.exists())
        self.assertEqual(self.files_under(link.with_name(item.name + ".1")), ["state"])

    def test_a_refused_manifest_keeps_its_cache_entry(self):
        rows = self.setup_stale_org()
        with self.refuse_rename_of(self.manifest):
            self.assertEqual(self.audit_then_apply(FakeCli(self.home, rows)), 1)
        self.assertIn("job1", self.read_cache())
        self.assertTrue(self.manifest.exists())

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
        with self.refuse_rename_of(self.index):
            self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertNotIn("Residual files moved", self.stdout.getvalue())

    def test_a_git_failure_refuses_the_move(self):
        rows = self.setup_stale_org()
        cli = FakeCli(self.home, rows)
        cli.override = lambda cmd: (1, "") if cmd[0] == "git" else None
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertTrue(self.tracking.exists())
        self.assertIn("git could not say", self.stdout.getvalue())

    def test_a_logout_that_does_not_name_the_user_counts_as_failed(self):
        rows = self.setup_stale_org()
        cli = FakeCli(self.home, rows)
        cli.override = lambda cmd: FakeCli.ok([]) if cmd[1:3] == ["org", "logout"] else None
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertIn("rep@x.invalid (logout failed)", self.stdout.getvalue())
        self.assertTrue(self.index.exists())

    def test_an_alias_unset_reporting_no_success_counts_as_failed(self):
        rows = self.setup_stale_org()
        cli = FakeCli(self.home, rows, {"base": "rep@x.invalid", "chained": "base"})
        cli.override = lambda cmd: (FakeCli.ok([{"alias": cmd[3], "success": False}])
                                    if cmd[1:3] == ["alias", "unset"] else None)
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertIn("chained (alias unset failed)", self.stdout.getvalue())

    def test_a_failed_config_unset_is_reported(self):
        rows = self.setup_stale_org()
        (self.project / ".sf" / "config.json").write_text(json.dumps({"target-org": "chained"}))
        cli = FakeCli(self.home, rows, {"base": "rep@x.invalid", "chained": "base"})
        cli.override = lambda cmd: ((1, json.dumps({"status": 1, "name": "Failed"}))
                                    if cmd[1:3] == ["config", "unset"] else None)
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertIn("local default (config unset failed)", self.stdout.getvalue())

    def test_the_rewritten_cache_keeps_its_mode(self):
        rows = self.setup_stale_org()
        cache = self.home / ".sf" / "deploy-cache.json"
        os.chmod(str(cache), 0o644)  # mkstemp would make it 600 if the mode were not carried over
        self.assertEqual(self.audit_then_apply(FakeCli(self.home, rows)), 0)
        self.assertEqual(cache.stat().st_mode & 0o777, 0o644)

    def test_a_cache_key_that_is_not_a_plain_job_id_is_refused(self):
        outside = self.home / "foo.xml"
        outside.write_text("<x/>")
        (self.home / ".sf" / "deploy-cache.json").write_text(json.dumps({"../../foo": {"target-org": "x"}}))
        failures = []
        result = oc.remove_deploy_jobs(FakeCli(self.home), ["../../foo"], self.home, self.quarantine,
                                       self.project, failures)
        self.assertEqual(result, (0, 0))
        self.assertEqual([f[0] for f in failures], ["../../foo"])
        self.assertTrue(outside.exists())
        self.assertIn("../../foo", self.read_cache())

    def test_an_unreadable_cache_is_reported(self):
        (self.home / ".sf" / "deploy-cache.json").write_text("not json")
        failures = []
        result = oc.remove_deploy_jobs(FakeCli(self.home), ["job1"], self.home, self.quarantine,
                                       self.project, failures)
        self.assertEqual(result, (0, 0))
        self.assertEqual(failures, [("deploy-cache", "unreadable")])

    def test_tracked_state_is_refused(self):  # symlinks are refused in the tests that link a real entry
        rows = self.setup_stale_org()
        cli = FakeCli(self.home, rows)
        cli.tracked.add(str(self.tracking))
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertTrue(self.tracking.exists())

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
                     "expired_shape_instances_it_skips", "unrecognized_file_responses",
                     "mixed_defaults", "unsafe_deploy_cache_keys"]
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


class EvidenceEdges(Base):
    """Each pins a guard that a broad mutation pass showed nothing else would catch."""

    def audit_output(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = oc.main(["audit"], FakeCli(self.home, [row(DEAD_ORG)]),
                           self.home, self.project, TODAY)
        self.assertEqual(code, 0)
        return out.getvalue()

    def test_no_connected_dev_hub_is_said_out_loud(self):
        (self.home / ".sfdx" / (HUB + ".json")).unlink()
        self.add_auth("rep@x.invalid", DEAD_ORG)
        self.assertIn("NO CONNECTED DEV HUB", self.audit_output())

    def test_a_connected_dev_hub_gets_no_such_warning(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        self.assertNotIn("NO CONNECTED DEV HUB", self.audit_output())

    def test_a_partial_hub_answer_is_a_failure_not_evidence(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        cli = FakeCli(self.home, [row(DEAD_ORG)])
        cli.override = lambda cmd: (FakeCli.ok({"done": False, "records": [row(DEAD_ORG)]})
                                    if cmd[1:3] == ["data", "query"] else None)
        plan = self.plan(cli)
        self.assertEqual(plan["hub_failures"], [HUB])
        self.assertEqual(plan["remove"]["logout"], [])

    def test_a_value_that_could_break_out_of_soql_never_reaches_a_query(self):
        aliases = {"quote": "o'brien@x.invalid", "slash": "back\\slash@x.invalid"}
        cli = FakeCli(self.home, aliases=aliases)
        self.plan(cli)
        queries = [" ".join(c) for c in cli.calls if c[1:3] == ["data", "query"]]
        self.assertFalse([q for q in queries if "brien" in q or "slash" in q])

    def test_an_index_for_a_live_or_unknown_org_stays(self):
        for org in (LIVE_ORG, NO_ROW_ORG):
            (self.home / ".sfdx" / (org + "MAA.json")).write_text("{}")
        plan = self.plan(FakeCli(self.home, [row(LIVE_ORG, "Active", "2026-12-01")]))
        self.assertEqual(plan["remove"]["indexes"], [])
        self.assertEqual(plan["preserved"]["indexes"], 2)

    def test_a_symlinked_auth_file_is_not_read(self):
        target = self.home / "elsewhere.json"
        target.write_text(json.dumps({"username": "link@x.invalid", "orgId": DEAD_ORG + "MAA"}))
        (self.home / ".sfdx" / "link@x.invalid.json").symlink_to(target)
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(plan["remove"]["logout"], [])
        self.assertEqual(plan["preserved"]["logins"], 1)  # the hub only

    def test_a_symlinked_index_is_not_listed(self):
        target = self.home / "elsewhere.json"
        target.write_text("{}")
        (self.home / ".sfdx" / (DEAD_ORG + "MAA.json")).symlink_to(target)
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(plan["remove"]["indexes"], [])

    def test_a_symlinked_tracking_dir_is_reported_and_not_listed(self):
        target = self.home / "elsewhere"
        target.mkdir()
        link = self.project / ".sf" / "orgs" / (DEAD_ORG + "MAA")
        link.symlink_to(target)
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(plan["remove"]["tracking"], [])
        self.assertEqual(plan["report"]["symlinks_left_alone"], [str(link)])

    def test_an_unreadable_auth_file_is_reported(self):
        (self.home / ".sfdx" / "bad@x.invalid.json").write_text("not json")
        plan = self.plan(FakeCli(self.home))
        self.assertEqual(plan["report"]["unreadable_auth_files"], ["bad@x.invalid.json"])

    def test_a_nonzero_exit_fails_even_when_the_payload_says_status_0(self):
        run = lambda cmd: (1, json.dumps({"status": 0, "result": []}))  # noqa: E731
        self.assertIsNone(oc.sf_json(run, "anything"))

    def test_the_legacy_default_key_counts(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        (self.project / ".sfdx" / "sfdx-config.json").write_text(
            json.dumps({"defaultusername": "rep@x.invalid"}))
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(plan["remove"]["defaults"], ["local"])

    def test_check_logins_names_the_login_that_did_not_answer(self):
        self.add_auth("rep@x.invalid", LIVE_ORG)
        cli = FakeCli(self.home)

        def answer(cmd):
            if "rep@x.invalid" in cmd:
                return 1, json.dumps({"status": 1, "name": "Failed"})
            return FakeCli.ok({"done": True, "records": []})

        cli.override = answer
        self.assertEqual(oc.check_logins(cli, self.home), ["rep@x.invalid"])


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

    def test_without_a_trash_the_quarantine_stays_with_the_real_cli_state(self):
        """A container's home goes with it, and only the volume its state links to is kept."""
        state = self.home.parent / "volume"
        (state / "sf").mkdir(parents=True)
        (self.home / ".sf").rename(self.home.parent / "unused-sf")
        (self.home / ".sf").symlink_to(state / "sf")
        expected = Path(os.path.realpath(str(state))) / ".rlm-org-cleanup-quarantine" / TODAY
        self.assertEqual(oc.default_quarantine(self.home, TODAY), expected)

    def test_without_a_trash_or_links_the_quarantine_is_in_the_home_folder(self):
        expected = Path(os.path.realpath(str(self.home))) / ".rlm-org-cleanup-quarantine" / TODAY
        self.assertEqual(oc.default_quarantine(self.home, TODAY), expected)


class FileResponses(Base):
    """`<project>/.sf[dx]/fileResponses/<orgId>`: response logs keyed by org, with no login."""

    audit_then_apply = Apply.audit_then_apply

    def responses(self, state=".sfdx", org=DEAD_ORG + "MAA"):
        path = self.project / state / "fileResponses" / org
        path.mkdir(parents=True)
        (path / "deploy-2026-04-16T03-02-23-000Z.json").write_text("{}")
        return path

    def test_a_deleted_orgs_responses_are_planned_and_a_live_orgs_are_not(self):
        dead, live = self.responses(), self.responses(org=LIVE_ORG + "MAA")
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG), row(LIVE_ORG, "Active", "2026-12-01")]))
        self.assertEqual(plan["remove"]["file_responses"], [str(dead)])
        self.assertEqual(plan["preserved"]["file_responses"], 1)
        self.assertTrue(live.exists())

    def test_no_hub_row_preserves_them(self):
        self.responses(org=NO_ROW_ORG + "MAA")
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(plan["remove"]["file_responses"], [])
        self.assertEqual(plan["preserved"]["file_responses"], 1)  # read, and left alone

    def test_a_name_that_is_not_an_org_id_is_reported_and_never_planned(self):
        odd = self.project / ".sfdx" / "fileResponses" / "not-an-org"
        odd.mkdir(parents=True)
        stray = self.project / ".sfdx" / "fileResponses" / (DEAD_ORG + "MAA.json")
        stray.write_text("{}")  # an org-ID name, but a file rather than a directory
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(plan["remove"]["file_responses"], [])
        self.assertEqual(sorted(plan["report"]["unrecognized_file_responses"]),
                         sorted([str(odd), str(stray)]))

    def test_a_symlinked_entry_or_folder_is_left_alone(self):
        target = self.home / "elsewhere"
        target.mkdir()
        entry = self.project / ".sfdx" / "fileResponses"
        entry.mkdir(parents=True)
        (entry / (DEAD_ORG + "MAA")).symlink_to(target)
        (self.project / ".sf" / "fileResponses").symlink_to(target)
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(plan["remove"]["file_responses"], [])
        self.assertEqual(sorted(plan["report"]["symlinks_left_alone"]),
                         sorted([str(entry / (DEAD_ORG + "MAA")),
                                 str(self.project / ".sf" / "fileResponses")]))

    def test_a_symlinked_state_folder_or_parent_is_never_followed(self):
        # `.sfdx` itself linked, then `.sf/orgs` and `.sf/fileResponses` linked.
        outside = self.home / "outside"
        (outside / "orgs" / (DEAD_ORG + "MAA")).mkdir(parents=True)
        (outside / "fileResponses" / (DEAD_ORG + "MAA")).mkdir(parents=True)
        (self.project / ".sfdx" / "orgs").rmdir()
        (self.project / ".sfdx").rmdir()
        (self.project / ".sfdx").symlink_to(outside)
        other = self.home / "other"
        (other / (DEAD_ORG + "MAA")).mkdir(parents=True)
        (self.project / ".sf" / "orgs").rmdir()
        (self.project / ".sf" / "orgs").symlink_to(other)
        (self.project / ".sf" / "fileResponses").symlink_to(other)
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(plan["remove"]["tracking"], [])
        self.assertEqual(plan["remove"]["file_responses"], [])
        self.assertEqual(sorted(plan["report"]["symlinks_left_alone"]),
                         sorted([str(self.project / ".sfdx"),
                                 str(self.project / ".sf" / "orgs"),
                                 str(self.project / ".sf" / "fileResponses")]))

    def test_a_folder_swapped_for_a_link_after_the_audit_is_refused_at_the_move(self):
        outside = self.home / "outside"
        (outside / (DEAD_ORG + "MAA")).mkdir(parents=True)
        why = oc.move_to_quarantine(
            FakeCli(self.home), self.project / ".sf" / "linked" / (DEAD_ORG + "MAA"),
            [self.project / ".sf" / "linked"], self.quarantine, self.project)
        self.assertEqual(why, "missing")  # nothing at the path: no move is attempted
        (self.project / ".sf" / "linked").symlink_to(outside)
        why = oc.move_to_quarantine(
            FakeCli(self.home), self.project / ".sf" / "linked" / (DEAD_ORG + "MAA"),
            [self.project / ".sf" / "linked"], self.quarantine, self.project)
        self.assertEqual(why, "symlink")
        self.assertTrue((outside / (DEAD_ORG + "MAA")).exists())

    def test_a_state_folder_swapped_for_a_link_after_the_audit_is_refused_at_the_move(self):
        outside = self.home / "outside"
        (outside / "orgs" / (DEAD_ORG + "MAA")).mkdir(parents=True)
        (self.project / ".sf" / "orgs").rmdir()
        (self.project / ".sf").rmdir()
        (self.project / ".sf").symlink_to(outside)
        why = oc.move_to_quarantine(
            FakeCli(self.home), self.project / ".sf" / "orgs" / (DEAD_ORG + "MAA"),
            [self.project / ".sf" / "orgs"], self.quarantine, self.project)
        self.assertEqual(why, "symlink")
        self.assertTrue((outside / "orgs" / (DEAD_ORG + "MAA")).exists())

    def test_a_quarantine_that_refuses_files_stops_before_any_logout_for_responses_alone(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        dead = self.responses()
        cli = FakeCli(self.home, [row(DEAD_ORG)])
        with mock.patch.object(oc.os, "rename", side_effect=PermissionError(1, "Not permitted")):
            self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertEqual([c for c in cli.calls if c[1:3] == ["org", "logout"]], [])
        self.assertTrue(dead.exists())
        self.assertIn("before any logout", self.stderr.getvalue())

    def test_the_directory_is_not_reported_as_unclassified(self):
        self.responses()
        files = self.plan(FakeCli(self.home))["report"]["unclassified_files"]
        self.assertEqual(files, [])

    def test_apply_moves_them_to_the_quarantine_and_a_re_audit_is_empty(self):
        dead = self.responses()
        cli = FakeCli(self.home, [row(DEAD_ORG)])
        self.assertEqual(self.audit_then_apply(cli), 0)
        self.assertFalse(dead.exists())
        moved = self.quarantine / "fileResponses" / dead.name
        self.assertTrue((moved / "deploy-2026-04-16T03-02-23-000Z.json").exists())
        self.assertIn("Residual files moved", self.stdout.getvalue())
        self.assertEqual(self.plan(cli)["remove"]["file_responses"], [])

    def test_apply_moves_a_project_sf_responses_folder(self):
        dead = self.responses(state=".sf")
        self.assertEqual(self.audit_then_apply(FakeCli(self.home, [row(DEAD_ORG)])), 0)
        self.assertFalse(dead.exists())
        self.assertTrue((self.quarantine / "fileResponses" / dead.name / "deploy-2026-04-16T03-02-23-000Z.json").exists())

    def test_a_tracked_responses_folder_is_refused(self):
        dead = self.responses()
        cli = FakeCli(self.home, [row(DEAD_ORG)])
        cli.tracked.add(str(dead))
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertTrue(dead.exists())
        self.assertIn("tracked by git", self.stdout.getvalue())

    def test_a_failed_logout_keeps_that_orgs_responses(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        dead = self.responses()
        cli = FakeCli(self.home, [row(DEAD_ORG)], fail_logout={"rep@x.invalid"})
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertTrue(dead.exists())


if __name__ == "__main__":
    unittest.main()
