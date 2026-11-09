"""Offline checks for scripts/ai/org_cleanup.py.

The tool removes local auth, so these tests pin what must never happen: acting without hub
evidence, touching a live org's login because it looks like a stale one, printing a token,
or running a command that deletes an org.

FakeCli answers the way sf 2.157.8 (@salesforce/core 9.4.1) does where the tool depends on it:
logins live only in ~/.sfdx, a name resolves through at most one alias, a logout clears the
config keys holding the user or one of its direct aliases in both scopes and both config
files, and queries match signup usernames regardless of case and can be cut short.
Stdlib only. Run with: python tests/test_org_cleanup.py
"""
import contextlib
import errno
import io
import json
import os
import re
import subprocess
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
OTHER_DEAD = "00DBB0000000002"
LEGACY = {new: old for old, new in oc.LEGACY_KEYS.items()}


def row(org, status="Deleted", expires="2026-01-01", user="signup@x.invalid"):
    return {"ScratchOrg": org, "SignupUsername": user, "Status": status, "ExpirationDate": expires}


def cci_org(name, **flags):
    org = dict(name=name, shape=False, active=False, scratch=True, expired=False, instantiated=True,
               org_id="", username="")
    org.update(flags)
    return org


class FakeCli:
    """Answers sf, cci and git from fixtures, recording every command."""

    def __init__(self, home, hub_rows=(), aliases=None, cci=None, fail_hubs=(), fail_logout=(), default=None):
        self.home, self.project, self.calls = home, home.parent / "project", []
        self.hub_rows, self.aliases = list(hub_rows), dict(aliases or {})
        self.cci, self.default = cci, default
        self.fail_hubs, self.fail_logout = set(fail_hubs), set(fail_logout)
        self.tracked = set()
        self.override = None  # cmd -> (code, stdout) to answer it, or None for the normal answer
        self.unset_works = True
        self.logout_clears_config = True  # False: sf's config write silently does not land (read-only file)
        self.max_query = None  # sf's org-max-query-limit

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
            payload = {"orgs": self.cci, "default": self.default}
            return 0, "noise\nORG_CLEANUP_CCI " + json.dumps(payload) + "\n"
        args = cmd[1:]
        if args[:2] == ["alias", "list"]:
            return self.ok([{"alias": a, "value": v} for a, v in self.aliases.items()])
        if args[:2] == ["alias", "unset"]:
            # Everything after `--` is an operand, as oclif parses it; without it a leading "-" is a flag.
            name = args[args.index("--") + 1] if "--" in args else args[2]
            if "--" not in args and name.startswith("-"):
                raise AssertionError("sf would read {} as flags".format(name))
            value = self.aliases.pop(name, None)
            return self.ok([{"alias": name, "value": value, "success": True}])
        if args[:2] == ["data", "query"]:
            return self.query(args)
        if args[:2] == ["org", "logout"]:
            return self.logout(args[3])
        if args[:2] == ["config", "unset"]:
            if self.unset_works:
                self.clear_config("global" if "--global" in args else "local", lambda k, v: k == "target-org")
            return self.ok({"successes": [{"name": "target-org", "success": True}], "failures": []})
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
        if field == "SignupUsername":  # SOQL compares text without regard to case
            wanted = {v.casefold() for v in values}
            records = [r for r in self.hub_rows if r[field].casefold() in wanted]
        else:
            records = [r for r in self.hub_rows if r[field] in values]
        total = len(records)
        if self.max_query is not None:  # sf cuts the result and still says done
            records = records[:self.max_query]
        return self.ok({"done": True, "totalSize": total, "records": records})

    def config_files(self, scope):
        base = self.home if scope == "global" else self.project
        return base / ".sf" / "config.json", base / ".sfdx" / "sfdx-config.json"

    def clear_config(self, scope, drop):
        """sf's merged config view: unset the matching keys, then rewrite both files from it."""
        sf_file, sfdx_file = self.config_files(scope)
        load = lambda p: json.loads(p.read_text()) if p.exists() else {}  # noqa: E731
        merged = {oc.LEGACY_KEYS.get(k, k): v for k, v in load(sfdx_file).items()}
        merged.update(load(sf_file))
        gone = {k for k, v in merged.items() if drop(k, v)}
        if not gone:
            return
        merged = {k: v for k, v in merged.items() if k not in gone}
        for path, contents in ((sf_file, merged), (sfdx_file, {LEGACY.get(k, k): v for k, v in merged.items()})):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(contents))

    def logout(self, target):
        user = self.aliases.get(target, target)  # one alias, never a chain
        auth = self.home / ".sfdx" / (user + ".json")
        if user in self.fail_logout or not auth.exists():
            return 1, json.dumps({"status": 1, "name": "NoAuthFoundForTargetOrg"})
        held = {user} | {a for a, v in self.aliases.items() if v == user}
        for scope in ("global", "local") if self.logout_clears_config else ():
            self.clear_config(scope, lambda k, v: v in held)
        self.aliases = {a: v for a, v in self.aliases.items() if v != user}
        auth.unlink()
        return self.ok([user])


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
        self.env = {}  # never the developer's own SF_* variables

    def add_auth(self, user, org, **fields):
        data = dict(username=user, orgId=org + "MAA", refreshToken=CANARY, accessToken=CANARY)
        data.update(fields)
        (self.home / ".sfdx" / (user + ".json")).write_text(json.dumps(data))

    def write_config(self, scope, sf=None, sfdx=None):
        base = self.home if scope == "global" else self.project
        for path, data in ((base / ".sf" / "config.json", sf), (base / ".sfdx" / "sfdx-config.json", sfdx)):
            if data is not None:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(data))

    def read_config(self, scope):
        base = self.home if scope == "global" else self.project
        return [json.loads(p.read_text()) if p.exists() else None
                for p in (base / ".sf" / "config.json", base / ".sfdx" / "sfdx-config.json")]

    def plan(self, cli):
        return oc.build_plan(cli, self.home, self.project, TODAY, env=self.env)

    def main(self, argv, cli):
        self.stdout, self.stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(self.stdout), contextlib.redirect_stderr(self.stderr):
            return oc.main(argv, cli, self.home, self.project, TODAY, env=self.env)

    def audit_file(self, cli):
        plan_file = self.project / "plan.json"
        self.assertEqual(self.main(["audit", "--out", str(plan_file)], cli), 0)
        return plan_file

    def apply(self, cli, plan_file, quarantine=None):
        return self.main(["apply", "--plan", str(plan_file), "--quarantine", str(quarantine or self.quarantine)], cli)

    def audit_then_apply(self, cli, plan_cli=None):
        return self.apply(cli, self.audit_file(plan_cli or cli))

    @staticmethod
    def logouts(cli):
        return [c for c in cli.calls if c[1:3] == ["org", "logout"]]

    @staticmethod
    def unsets(cli):
        return [c for c in cli.calls if c[1:3] == ["config", "unset"]]

    def read_cache(self):
        return json.loads((self.home / ".sf" / "deploy-cache.json").read_text())


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
            ([row("x", "Error", "2026-11-05"), row("x", "Error", "2026-12-01")], "unknown"),  # one still runs
            ([row("x", "New", "2026-12-01")], "unknown"),
            ([row("x"), row("x", "Active", "2026-12-01")], "conflict"),
            ([row("x", "Deleted", "2026-12-01"), row("x", "Active", "2026-12-01")], "conflict"),
            ([row("x", "Error", None)], "unknown"),  # a date that is not text is no evidence
        ]
        for rows, expected in cases:
            self.assertEqual(oc.classify(rows, TODAY), expected, rows)

    def test_an_org_id_with_a_trailing_newline_is_not_an_org_id(self):
        self.assertIsNone(oc.ORG_ID.fullmatch(DEAD_ORG + "MAA\n"))
        self.assertIsNone(oc.KNOWN_ENTRY_PATTERN.fullmatch("sf.log\n"))

    def test_sf_login_file_names(self):
        for name in ("rep@x.invalid.json", "test-abc@example.com.json"):
            self.assertTrue(oc.SF_LOGIN_FILE.fullmatch(name), name)
        for name in ("user@localhost.json", ".hidden@x.invalid.json", "rep@x.invalid.json.bak", "alias.json"):
            self.assertFalse(oc.SF_LOGIN_FILE.fullmatch(name), name)


class Evidence(Base):
    def test_only_a_login_on_a_deleted_org_is_removed(self):
        self.add_auth("rep@x.invalid." + DEAD_ORG.lower(), DEAD_ORG, isScratch=False)
        self.add_auth("rep@x.invalid." + LIVE_ORG.lower(), LIVE_ORG, isScratch=False)
        self.add_auth("persistent@x.invalid", NO_ROW_ORG)
        cli = FakeCli(self.home, [row(DEAD_ORG), row(LIVE_ORG, "Active", "2026-12-01")])
        self.assertEqual(self.plan(cli)["remove"]["logout"], ["rep@x.invalid." + DEAD_ORG.lower()])

    def test_a_failed_hub_query_removes_nothing_and_says_so(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)], fail_hubs=[HUB]))
        self.assertEqual(plan["remove"]["logout"], [])
        self.assertEqual(plan["hub_failures"], [HUB])

    def test_a_truncated_hub_answer_is_a_failure_not_evidence(self):
        # sf applies org-max-query-limit and still says done: only totalSize shows the loss.
        rows = [row("00DBB0000000001", user="reused@x.invalid"), row("00DBB0000000002", "Active", "2026-12-01",
                                                                      user="reused@x.invalid")]
        cli = FakeCli(self.home, rows, {"stale": "reused@x.invalid"})
        cli.max_query = 1
        plan = self.plan(cli)
        self.assertEqual(plan["hub_failures"], [HUB])
        self.assertEqual(plan["remove"]["aliases"], [])

    def test_a_partial_hub_answer_is_a_failure_not_evidence(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        cli = FakeCli(self.home, [row(DEAD_ORG)])
        cli.override = lambda cmd: (FakeCli.ok({"done": False, "records": [row(DEAD_ORG)]})
                                    if cmd[1:3] == ["data", "query"] else None)
        plan = self.plan(cli)
        self.assertEqual(plan["hub_failures"], [HUB])
        self.assertEqual(plan["remove"]["logout"], [])

    def test_a_hub_named_like_an_alias_is_not_queried_and_counts_as_failed(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        cli = FakeCli(self.home, [row(DEAD_ORG)], {HUB: "rep@x.invalid"})
        plan = self.plan(cli)
        self.assertEqual([c for c in cli.calls if c[1:3] == ["data", "query"]], [])
        self.assertEqual(plan["hub_failures"], [HUB])
        self.assertEqual(plan["remove"]["logout"], [])

    def test_a_row_on_a_second_hub_counts_and_an_absent_row_elsewhere_does_not_block(self):
        self.add_auth("hub2@x.invalid", "00DHUB000000002", isDevHub=True)
        self.add_auth("rep@x.invalid", DEAD_ORG)
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)], fail_hubs=["hub2@x.invalid"]))
        self.assertEqual(plan["remove"]["logout"], ["rep@x.invalid"])

    def test_a_dev_hub_is_never_logged_out(self):
        self.assertEqual(self.plan(FakeCli(self.home, [row("00DHUB000000001")]))["remove"]["logout"], [])

    def test_a_sandbox_is_never_logged_out(self):
        self.add_auth("sbx@x.invalid", DEAD_ORG, isSandbox=True)
        self.assertEqual(self.plan(FakeCli(self.home, [row(DEAD_ORG)]))["remove"]["logout"], [])

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

    def test_a_jwt_login_is_not_reported_as_expiring(self):
        self.add_auth("jwt@x.invalid", LIVE_ORG, refreshToken="", privateKey="/keys/server.key")
        plan = self.plan(FakeCli(self.home, [row(LIVE_ORG, "Active", "2026-12-01")]))
        self.assertEqual(plan["report"]["logins_with_no_refresh_token"], [])

    def test_18_character_state_matches_on_15(self):
        (self.home / ".sfdx" / (DEAD_ORG + "MAA.json")).write_text("{}")
        (self.project / ".sf" / "orgs" / (DEAD_ORG + "MAA")).mkdir()
        remove = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))["remove"]
        self.assertEqual((len(remove["indexes"]), len(remove["tracking"])), (1, 1))

    def test_a_value_that_could_break_out_of_soql_never_reaches_a_query(self):
        cli = FakeCli(self.home, aliases={"quote": "o'brien@x.invalid", "slash": "back\\slash@x.invalid"})
        self.plan(cli)
        queries = [" ".join(c) for c in cli.calls if c[1:3] == ["data", "query"]]
        self.assertFalse([q for q in queries if "brien" in q or "slash" in q])

    def test_a_nonzero_exit_fails_even_when_the_payload_says_status_0(self):
        self.assertIsNone(oc.sf_json(lambda cmd: (1, json.dumps({"status": 0, "result": []})), "anything"))

    def test_output_that_does_not_decode_does_not_raise(self):
        code, out = oc.run_command([sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'a\\xffb')"])
        self.assertEqual((code, out), (0, "a�b"))


class Logins(Base):
    """Logins are what sf lists: regular files in ~/.sfdx matching its pattern, by username inside."""

    def test_a_copy_in_the_sf_folder_is_not_a_login_and_is_reported(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        copy = self.home / ".sf" / "rep@x.invalid.json"
        copy.write_text(json.dumps({"username": "rep@x.invalid", "orgId": DEAD_ORG + "MAA", "refreshToken": CANARY}))
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(plan["remove"]["logout"], ["rep@x.invalid"])
        self.assertIn(str(copy), [f["path"] for f in plan["report"]["unclassified_files"]])

    def test_after_apply_a_copy_in_the_sf_folder_does_not_replan_the_logout(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        (self.home / ".sf" / "rep@x.invalid.json").write_text(json.dumps({"username": "rep@x.invalid",
                                                                          "orgId": DEAD_ORG + "MAA"}))
        cli = FakeCli(self.home, [row(DEAD_ORG)])
        self.assertEqual(self.audit_then_apply(cli), 0)
        self.assertEqual(self.plan(cli)["remove"]["logout"], [])

    def test_a_file_sf_does_not_list_is_not_a_login(self):
        (self.home / ".sfdx" / "user@localhost.json").write_text(json.dumps({"username": "user@localhost",
                                                                            "orgId": DEAD_ORG + "MAA"}))
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(plan["remove"]["logout"], [])
        self.assertIn("user@localhost.json", [Path(f["path"]).name for f in plan["report"]["unclassified_files"]])

    def test_a_renamed_auth_file_protects_both_names(self):
        (self.home / ".sfdx" / "bob@x.invalid.json").write_text(
            json.dumps({"username": "alice@x.invalid", "orgId": DEAD_ORG + "MAA"}))
        self.add_auth("alice@x.invalid", DEAD_ORG)
        cli = FakeCli(self.home, [row(DEAD_ORG), row("00DBB0000000009", user="bob@x.invalid")], {"b": "bob@x.invalid"})
        plan = self.plan(cli)
        self.assertEqual(plan["remove"]["logout"], [])
        self.assertEqual(plan["remove"]["aliases"], [])
        self.assertIn("bob@x.invalid", plan["report"]["protected"])
        self.assertIn("alice@x.invalid", plan["report"]["protected"])

    def test_auth_files_that_differ_only_by_case_protect_both(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        (self.home / ".sfdx" / "Rep@x.invalid.json").write_text(
            json.dumps({"username": "Rep@x.invalid", "orgId": DEAD_ORG + "MAA"}))
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(plan["remove"]["logout"], [])

    def test_logins_that_differ_only_by_case_protect_both(self):
        # A case-sensitive filesystem can hold both files; this one cannot, so read_logins is stubbed.
        twins = {name: {"username": name, "org": DEAD_ORG, "is_hub": False, "is_sandbox": False, "refreshable": True}
                 for name in ("rep@x.invalid", "Rep@x.invalid")}
        twins[HUB] = {"username": HUB, "org": "00DHUB000000001", "is_hub": True, "is_sandbox": False, "refreshable": True}
        with mock.patch.object(oc, "read_logins", return_value=(twins, set(), [])):
            plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(plan["remove"]["logout"], [])
        self.assertIn("differ only by letter case", plan["report"]["protected"]["rep@x.invalid"])

    def test_a_name_that_opens_an_unread_login_is_judged_doubtful(self):
        (self.home / ".sfdx" / "bob@x.invalid.json").write_text("not json")
        self.env = {"SF_TARGET_ORG": "bob@x.invalid"}
        plan = self.plan(FakeCli(self.home))
        self.assertEqual(plan["report"]["env_defaults"]["SF_TARGET_ORG"]["judged"], "doubt")

    def test_an_unreadable_auth_file_protects_its_name_and_is_reported(self):
        (self.home / ".sfdx" / "bob@x.invalid.json").write_text("not json")
        cli = FakeCli(self.home, [row("00DBB0000000009", user="gone@x.invalid")],
                      {"b": "bob@x.invalid", "bob@x.invalid": "gone@x.invalid"})
        plan = self.plan(cli)
        self.assertEqual(plan["remove"]["aliases"], [])
        self.assertEqual(plan["report"]["unreadable_auth_files"], ["bob@x.invalid.json"])

    def test_an_auth_file_with_values_of_the_wrong_type_is_unreadable_not_a_crash(self):
        for name, data in (("int@x.invalid", {"orgId": 1234}), ("list@x.invalid", {"orgId": DEAD_ORG, "username": ["z"]})):
            (self.home / ".sfdx" / (name + ".json")).write_text(json.dumps(data))
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(sorted(plan["report"]["unreadable_auth_files"]), ["int@x.invalid.json", "list@x.invalid.json"])

    def test_a_symlinked_auth_file_is_not_opened_and_protects_its_name(self):
        target = self.home / "elsewhere.json"
        target.write_text(json.dumps({"username": "bob@x.invalid", "orgId": DEAD_ORG + "MAA"}))
        (self.home / ".sfdx" / "bob@x.invalid.json").symlink_to(target)
        cli = FakeCli(self.home, [row("00DBB0000000009", user="bob@x.invalid")], {"b": "bob@x.invalid"})
        plan = self.plan(cli)
        self.assertEqual(plan["remove"]["aliases"], [])
        self.assertEqual(plan["preserved"]["logins"], 1)  # the hub only: the link is never read

    def test_an_unread_login_may_be_a_hub_so_usernames_are_not_judged(self):
        # sf reads a linked auth file; if it is a Dev Hub, its rows are missing from the evidence.
        target = self.home / "elsewhere.json"
        target.write_text(json.dumps({"username": "hub2@x.invalid", "orgId": "00DHUB000000002MAA", "isDevHub": True}))
        (self.home / ".sfdx" / "hub2@x.invalid.json").symlink_to(target)
        cli = FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")], {"stale": "gone@x.invalid"})
        plan = self.plan(cli)
        self.assertEqual(plan["hub_failures"], ["hub2@x.invalid"])
        self.assertEqual(plan["remove"]["aliases"], [])

    def test_a_login_named_like_an_alias_is_not_logged_out(self):
        self.add_auth("old@x.invalid", DEAD_ORG)
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)], {"old@x.invalid": "live@x.invalid"}))
        self.assertEqual(plan["remove"]["logout"], [])
        self.assertIn("old@x.invalid", plan["report"]["protected"])

    def test_an_alias_naming_the_login_itself_in_another_case_does_not_block_its_logout(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)], {"Rep@x.invalid": "rep@x.invalid"}))
        self.assertEqual(plan["remove"]["logout"], ["rep@x.invalid"])

    def test_a_user_whose_alias_is_named_like_another_login_is_not_logged_out(self):
        # Logout clears the alias "bob@x.invalid", and the name would then mean bob's live login.
        self.add_auth("bob@x.invalid", LIVE_ORG)
        self.add_auth("rep@x.invalid", DEAD_ORG)
        rows = [row(DEAD_ORG), row(LIVE_ORG, "Active", "2026-12-01")]
        for alias in ("bob@x.invalid", "Bob@x.invalid"):
            plan = self.plan(FakeCli(self.home, rows, {alias: "rep@x.invalid"}))
            self.assertEqual(plan["remove"]["logout"], [], alias)
            self.assertIn("rep@x.invalid", plan["report"]["protected"], alias)

    def test_a_user_whose_alias_is_named_like_an_unread_login_is_not_logged_out(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        target = self.home / "elsewhere.json"
        target.write_text("{}")
        (self.home / ".sfdx" / "bob@x.invalid.json").symlink_to(target)
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)], {"bob@x.invalid": "rep@x.invalid"}))
        self.assertEqual(plan["remove"]["logout"], [])


class Names(Base):
    """A name resolves through at most one alias, and finds a login whatever its case."""

    def test_an_orphan_alias_needs_a_deleted_signup_row(self):
        rows = [row("00DBB0000000001", user="gone@x.invalid")]
        remove = self.plan(FakeCli(self.home, rows, {"stale": "gone@x.invalid", "no-row": "unknown@x.invalid"}))["remove"]
        self.assertEqual(remove["aliases"], ["stale"])

    def test_a_chain_of_aliases_is_dangling_and_never_removed(self):
        # sf follows one alias: "chained" means a login file named "base", which does not exist.
        self.add_auth("rep@x.invalid", DEAD_ORG)
        aliases = {"base": "rep@x.invalid", "chained": "base", "deeper": "chained"}
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)], aliases))
        self.assertEqual(plan["remove"]["logout"], ["rep@x.invalid"])
        self.assertEqual(plan["targets"]["logout"]["rep@x.invalid"]["aliases"], ["base"])
        self.assertEqual(plan["remove"]["aliases"], [])
        self.assertEqual(plan["report"]["dangling_aliases"], ["chained", "deeper"])

    def test_a_username_shaped_alias_is_not_followed_to_a_second_name(self):
        # sf resolves x to live@x.invalid (Active), never to the alias of that name.
        (self.project / ".sf" / "config.json").write_text(json.dumps({"target-org": "x"}))
        rows = [row("00DBB0000000001", user="dead@x.invalid"), row("00DBB0000000002", "Active", "2026-12-01",
                                                                    user="live@x.invalid")]
        cli = FakeCli(self.home, rows, {"x": "live@x.invalid", "live@x.invalid": "dead@x.invalid"})
        plan = self.plan(cli)
        self.assertEqual(plan["remove"]["aliases"], ["live@x.invalid"])
        self.assertEqual(plan["remove"]["defaults"], [])

    def test_a_case_variant_name_reaches_the_live_login(self):
        # On a case-insensitive filesystem sf opens bob's file for "Bob@x.invalid".
        self.add_auth("bob@x.invalid", LIVE_ORG)
        (self.project / ".sf" / "config.json").write_text(json.dumps({"target-org": "b"}))
        (self.home / ".sf" / "deploy-cache.json").write_text(json.dumps({"job1": {"target-org": "b"}}))
        rows = [row("00DBB0000000001", user="gone@x.invalid"), row(LIVE_ORG, "Active", "2026-12-01")]
        cli = FakeCli(self.home, rows, {"Bob@x.invalid": "gone@x.invalid", "b": "Bob@x.invalid"})
        remove = self.plan(cli)["remove"]
        for key in ("logout", "aliases", "defaults", "deploy_jobs"):
            self.assertEqual(remove[key], [], key)

    def test_an_alias_named_like_a_login_is_not_unset(self):
        self.add_auth("bob@x.invalid", LIVE_ORG)
        cli = FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid"), row(LIVE_ORG, "Active", "2026-12-01")],
                      {"bob@x.invalid": "gone@x.invalid"})
        plan = self.plan(cli)
        self.assertEqual(plan["remove"]["aliases"], [])
        self.assertIn("bob@x.invalid", plan["report"]["protected"])

    def test_signup_rows_in_another_case_are_judged_together(self):
        # A reused username: the old org's row and the live one's differ only by case.
        rows = [row("00DBB0000000001", user="Demo@Acme.test"),
                row("00DBB0000000002", "Active", "2026-12-01", user="demo@acme.test")]
        plan = self.plan(FakeCli(self.home, rows, {"d": "Demo@Acme.test"}))
        self.assertEqual(plan["remove"]["aliases"], [])
        rows = [row("00DBB0000000001", user="demo@acme.test"),
                row("00DBB0000000002", "Active", "2026-12-01", user="Demo@Acme.test")]
        self.assertEqual(self.plan(FakeCli(self.home, rows, {"d": "x@y.invalid"}))["remove"]["aliases"], [])
        self.assertEqual(self.plan(FakeCli(self.home, rows, {"d": "demo@acme.test"}))["remove"]["aliases"], [])

    def test_a_signup_row_matches_a_name_in_another_case(self):
        rows = [row("00DBB0000000001", user="demo@acme.test")]
        plan = self.plan(FakeCli(self.home, rows, {"d": "Demo@Acme.test"}))
        self.assertEqual(plan["remove"]["aliases"], ["d"])

    def test_aliases_that_lead_nowhere_are_reported_and_never_listed(self):
        aliases = {"lost": "missing", "cycle-a": "cycle-b", "cycle-b": "cycle-a", "fine": HUB}
        plan = self.plan(FakeCli(self.home, aliases=aliases))
        self.assertEqual(plan["report"]["dangling_aliases"], ["cycle-a", "cycle-b", "lost"])
        self.assertEqual(plan["remove"]["aliases"], [])

    def test_a_username_is_not_judged_while_a_hub_has_not_answered(self):
        self.add_auth("hub2@x.invalid", "00DHUB000000002", isDevHub=True)
        cli = FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")], {"stale": "gone@x.invalid"},
                      fail_hubs=["hub2@x.invalid"])
        plan = self.plan(cli)
        self.assertEqual(plan["hub_failures"], ["hub2@x.invalid"])
        self.assertEqual(plan["remove"]["aliases"], [])

    def test_a_username_is_not_judged_while_a_hub_is_named_like_an_alias(self):
        self.add_auth("hub2@x.invalid", "00DHUB000000002", isDevHub=True)
        rows = [row("00DBB0000000001", user="gone@x.invalid")]
        plan = self.plan(FakeCli(self.home, rows, {"stale": "gone@x.invalid", "hub2@x.invalid": HUB}))
        self.assertEqual(plan["remove"]["aliases"], [])

    def test_legacy_username_tracking_needs_a_deleted_signup_row(self):
        for name in ("gone@x.invalid", "unknown@x.invalid"):
            (self.project / ".sfdx" / "orgs" / name).mkdir()
        tracking = self.plan(FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")]))["remove"]["tracking"]
        self.assertEqual([Path(p).name for p in tracking], ["gone@x.invalid"])

    def test_deploy_job_follows_its_target(self):
        cache = {"job1": {"target-org": "gone@x.invalid"}, "job2": {"target-org": "unknown@x.invalid"},
                 "job3": {"target-org": 5}}
        (self.home / ".sf" / "deploy-cache.json").write_text(json.dumps(cache))
        plan = self.plan(FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")]))
        self.assertEqual(plan["remove"]["deploy_jobs"], ["job1"])
        self.assertEqual(plan["report"]["unsafe_deploy_cache_keys"], ["job3"])

    def test_an_unsafe_deploy_cache_key_is_reported_not_planned(self):
        cache = {"../../foo": {"target-org": "gone@x.invalid"}, "job1": {"target-org": "gone@x.invalid"}}
        (self.home / ".sf" / "deploy-cache.json").write_text(json.dumps(cache))
        plan = self.plan(FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")]))
        self.assertEqual(plan["remove"]["deploy_jobs"], ["job1"])
        self.assertEqual(plan["report"]["unsafe_deploy_cache_keys"], ["../../foo"])


class Config(Base):
    """A config scope is the merge of its two files, and a write rewrites both."""

    def test_a_stale_default_is_planned_and_a_valid_one_is_not(self):
        self.write_config("local", sf={"target-org": "stale"})
        self.write_config("global", sf={"target-org": HUB})
        plan = self.plan(FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")], {"stale": "gone@x.invalid"}))
        self.assertEqual(plan["remove"]["defaults"], ["local"])

    def test_the_legacy_default_key_counts(self):
        self.write_config("local", sfdx={"defaultusername": "gone@x.invalid"})
        plan = self.plan(FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")]))
        self.assertEqual(plan["remove"]["defaults"], ["local"])

    def test_a_default_logout_clears_is_shown_as_its_effect_not_unset(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        self.write_config("local", sf={"target-org": "r", "target-dev-hub": "rep@x.invalid"})
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)], {"r": "rep@x.invalid"}))
        self.assertEqual(plan["remove"]["defaults"], [])
        self.assertEqual(plan["targets"]["logout"]["rep@x.invalid"],
                         {"org": DEAD_ORG, "aliases": ["r"], "config": {"local": ["target-dev-hub", "target-org"]}})

    def test_a_config_key_holding_a_list_does_not_stop_the_audit(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        self.write_config("local", sf={"target-org": "rep@x.invalid", "org-custom-metadata-templates": ["x"]})
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(plan["targets"]["logout"]["rep@x.invalid"]["config"], {"local": ["target-org"]})

    def test_files_that_disagree_are_not_modelled_and_block_a_logout_that_writes_them(self):
        # sf's logout would rewrite both files from whichever is newer, losing the other value.
        self.add_auth("rep@x.invalid", DEAD_ORG)
        self.write_config("local", sf={"target-org": HUB}, sfdx={"defaultusername": "rep@x.invalid"})
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(plan["remove"]["logout"], [])
        self.assertIn("disagree on target-org", plan["report"]["unmodelled_config"]["local"])
        self.assertIn("local config", plan["report"]["protected"]["rep@x.invalid"])

    def test_a_scope_that_is_not_modelled_is_never_unset(self):
        self.write_config("local", sf={"target-org": "gone@x.invalid"}, sfdx={"defaultusername": "other@x.invalid"})
        rows = [row("00DBB0000000001", user="gone@x.invalid"), row("00DBB0000000002", user="other@x.invalid")]
        plan = self.plan(FakeCli(self.home, rows))
        self.assertEqual(plan["remove"]["defaults"], [])
        self.assertEqual(plan["report"]["stale_config_values"],
                         [{"scope": "local", "key": "target-org", "value": "gone@x.invalid"},
                          {"scope": "local", "key": "target-org", "value": "other@x.invalid"}])

    def test_a_legacy_key_in_the_sf_file_is_not_modelled(self):
        # sf does not read it there, and unsetting it would also unset target-org.
        self.add_auth("rep@x.invalid", DEAD_ORG)
        self.write_config("local", sf={"target-org": HUB, "defaultusername": "rep@x.invalid"})
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(plan["remove"]["logout"], [])
        self.assertIn("legacy key defaultusername", plan["report"]["unmodelled_config"]["local"])

    def test_an_unknown_key_in_the_sfdx_file_is_not_modelled(self):
        self.write_config("local", sfdx={"defaultusername": "gone@x.invalid", "someKey": "https://x"})
        plan = self.plan(FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")]))
        self.assertEqual(plan["remove"]["defaults"], [])
        self.assertIn("someKey", plan["report"]["unmodelled_config"]["local"])

    def test_a_linked_config_file_is_not_modelled(self):
        shared = self.home.parent / "shared-config.json"
        shared.write_text(json.dumps({"target-org": "gone@x.invalid"}))
        (self.home / ".sf" / "config.json").symlink_to(shared)
        plan = self.plan(FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")]))
        self.assertEqual(plan["remove"]["defaults"], [])
        self.assertIn("is a symlink", plan["report"]["unmodelled_config"]["global"])

    def test_a_linked_config_file_is_read_so_a_logout_that_writes_through_it_is_refused(self):
        # sf follows the link when it rewrites the scope: a shared dotfile would lose its default.
        self.add_auth("rep@x.invalid", DEAD_ORG)
        shared = self.home.parent / "dotfiles-sf-config.json"
        shared.write_text(json.dumps({"target-org": "rep@x.invalid", "org-api-version": "62.0"}))
        (self.home / ".sf" / "config.json").symlink_to(shared)
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(plan["remove"]["logout"], [])
        self.assertIn("global config", plan["report"]["protected"]["rep@x.invalid"])

    def test_a_key_sf_does_not_know_is_not_modelled_in_either_file(self):
        # sf cannot unset it, and its next write turns it into org-instance-url.
        self.add_auth("rep@x.invalid", DEAD_ORG)
        self.write_config("local", sf={"target-org": "rep@x.invalid", "old-plugin-user": "rep@x.invalid"})
        self.write_config("global", sf={"target-org": "gone@x.invalid", "old-plugin-url": "https://other.example"})
        rows = [row(DEAD_ORG), row("00DBB0000000001", user="gone@x.invalid")]
        plan = self.plan(FakeCli(self.home, rows))
        self.assertEqual((plan["remove"]["logout"], plan["remove"]["defaults"]), ([], []))
        self.assertIn("old-plugin-user", plan["report"]["unmodelled_config"]["local"])
        self.assertIn("old-plugin-url", plan["report"]["unmodelled_config"]["global"])

    def test_every_key_sf_knows_is_modelled_in_both_files(self):
        # sf writes org-capitalize-record-types into sfdx-config.json itself, unchanged.
        self.add_auth("rep@x.invalid", DEAD_ORG)
        self.write_config("local", sf={"target-org": "rep@x.invalid", "org-capitalize-record-types": "true"},
                          sfdx={"defaultusername": "rep@x.invalid", "org-capitalize-record-types": "true",
                                "restDeploy": "false"})
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(plan["report"]["unmodelled_config"], {})
        self.assertEqual(plan["remove"]["logout"], ["rep@x.invalid"])

    def test_an_unparsable_or_mistyped_config_is_reported_not_modelled(self):
        (self.project / ".sfdx" / "sfdx-config.json").write_text('{"defaultusername": "live@x.invalid",}')
        self.write_config("global", sf={"target-org": ["a"]})
        plan = self.plan(FakeCli(self.home))
        self.assertIn("does not parse", plan["report"]["unmodelled_config"]["local"])
        self.assertIn("not text", plan["report"]["unmodelled_config"]["global"])

    def test_with_interoperability_off_a_legacy_file_is_not_modelled(self):
        self.env = {"SF_SFDX_INTEROPERABILITY": "false"}
        self.write_config("local", sfdx={"defaultusername": "gone@x.invalid"})
        plan = self.plan(FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")]))
        self.assertEqual(plan["remove"]["defaults"], [])
        self.assertIn("SF_SFDX_INTEROPERABILITY", plan["report"]["unmodelled_config"]["local"])

    def test_a_linked_project_config_folder_is_not_modelled(self):
        shared = self.home.parent / "shared-sf"
        shared.mkdir()
        (shared / "config.json").write_text(json.dumps({"target-org": "gone@x.invalid"}))
        (self.project / ".sf" / "orgs").rmdir()
        (self.project / ".sf").rmdir()
        (self.project / ".sf").symlink_to(shared)
        plan = self.plan(FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")]))
        self.assertEqual(plan["remove"]["defaults"], [])
        self.assertIn("symlink", plan["report"]["unmodelled_config"]["local"])

    def test_a_default_that_leads_nowhere_is_reported_and_never_listed(self):
        self.write_config("local", sf={"target-org": "lost"})
        self.write_config("global", sf={"target-org": "fine"})
        plan = self.plan(FakeCli(self.home, aliases={"fine": HUB}))
        self.assertEqual(plan["report"]["dangling_defaults"], ["local"])
        self.assertEqual(plan["remove"]["defaults"], [])

    def test_a_default_username_is_not_judged_while_a_hub_has_not_answered(self):
        self.add_auth("hub2@x.invalid", "00DHUB000000002", isDevHub=True)
        self.write_config("local", sf={"target-org": "gone@x.invalid"})
        plan = self.plan(FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")], fail_hubs=["hub2@x.invalid"]))
        self.assertEqual(plan["remove"]["defaults"], [])

    def test_an_environment_default_is_reported(self):
        self.env = {"SF_TARGET_ORG": "gone@x.invalid"}
        plan = self.plan(FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")]))
        self.assertEqual(plan["report"]["env_defaults"], {"SF_TARGET_ORG": {"value": "gone@x.invalid", "judged": "stale"}})

    def test_a_stale_dev_hub_default_is_reported_not_unset(self):
        self.write_config("global", sf={"target-dev-hub": "gone@x.invalid"})
        plan = self.plan(FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")]))
        self.assertEqual(plan["remove"]["defaults"], [])
        self.assertEqual(plan["report"]["stale_config_values"],
                         [{"scope": "global", "key": "target-dev-hub", "value": "gone@x.invalid"}])


class PrunePrediction(Base):
    ORGS = [
        cci_org("shape-old", shape=True, expired=True),
        cci_org("old", expired=True, org_id=DEAD_ORG + "MAA"),
        cci_org("other-branch", instantiated=False),
        cci_org("current", active=True, org_id=LIVE_ORG + "MAA"),
        cci_org("connected", scratch=False, instantiated=False),
    ]

    def predict(self, rows=(), orgs=None, default=None):
        return self.plan(FakeCli(self.home, rows, cci=orgs or self.ORGS, default=default))["prune_prediction"]

    def test_matches_what_prune_does(self):
        predicted = self.predict([row(DEAD_ORG)], default="current")
        self.assertEqual(predicted["would_remove_expired"], ["old"])
        self.assertEqual(predicted["would_remove_never_instantiated"], ["other-branch"])
        self.assertEqual(predicted["expired_shape_instances_it_skips"], ["shape-old"])
        self.assertEqual(predicted["would_remove_not_proven_gone"], [])
        self.assertEqual(predicted["default"], "current")

    def test_an_org_the_hub_shows_active_is_not_proven_gone(self):
        self.assertEqual(self.predict([row(DEAD_ORG, "Active", "2026-12-01")])["would_remove_not_proven_gone"], ["old"])

    def test_an_org_with_no_hub_row_is_not_proven_gone(self):
        self.assertEqual(self.predict([])["would_remove_not_proven_gone"], ["old"])

    def test_conflicting_hub_rows_are_not_proof_an_org_is_gone(self):
        for rows in ([row(DEAD_ORG, "Active", "2026-01-01")], [row(DEAD_ORG), row(DEAD_ORG, "Active", "2026-12-01")]):
            self.assertEqual(self.predict(rows)["would_remove_not_proven_gone"], ["old"], rows)

    def test_a_doubted_login_is_not_proof_an_org_is_gone(self):
        (self.home / ".sfdx" / "rep@x.invalid.json").write_text(
            json.dumps({"username": "alice@x.invalid", "orgId": DEAD_ORG + "MAA"}))
        orgs = [cci_org("old", expired=True, username="rep@x.invalid")]
        self.assertEqual(self.predict([row(DEAD_ORG)], orgs)["would_remove_not_proven_gone"], ["old"])

    def test_an_org_is_judged_by_its_own_id_not_by_aliases(self):
        # A stray alias cannot make a live org look gone: the CCI record's org ID decides.
        self.add_auth("bob@x.invalid", LIVE_ORG)
        orgs = [cci_org("old", expired=True, org_id=LIVE_ORG + "MAA")]
        cli = FakeCli(self.home, [row(LIVE_ORG, "Active", "2026-12-01"), row(DEAD_ORG)],
                      {"p__old": "bob@x.invalid", "bob@x.invalid": "rep@x.invalid"}, cci=orgs)
        self.assertEqual(self.plan(cli)["prune_prediction"]["would_remove_not_proven_gone"], ["old"])

    def test_without_an_org_id_the_login_decides(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        self.add_auth("live@x.invalid", LIVE_ORG)
        orgs = [cci_org("old", expired=True, username="rep@x.invalid"), cci_org("blank", expired=True),
                cci_org("live", expired=True, username="live@x.invalid")]
        predicted = self.predict([row(DEAD_ORG), row(LIVE_ORG, "Active", "2026-12-01")], orgs)
        self.assertEqual(predicted["would_remove_not_proven_gone"], ["blank", "live"])

    def test_unavailable_cci_is_not_a_prediction(self):
        self.assertEqual(self.plan(FakeCli(self.home))["prune_prediction"], {"available": False})

    def test_a_malformed_cci_line_is_not_a_prediction(self):
        for line in ("{not json", "{}", '["a"]', '{"orgs": [{"name": "x"}]}', '{"orgs": [], "default": 5}',
                     json.dumps({"orgs": [cci_org(None)]})):
            cli = FakeCli(self.home)
            cli.override = lambda cmd, line=line: ((0, "ORG_CLEANUP_CCI " + line + "\n") if cmd[0] == "cci" else None)
            self.assertEqual(self.plan(cli)["prune_prediction"], {"available": False}, line)

    def test_an_empty_cci_list_is_an_available_prediction(self):
        predicted = self.plan(FakeCli(self.home, cci=[]))["prune_prediction"]
        self.assertTrue(predicted["available"])
        self.assertEqual(predicted["would_remove_expired"], [])

    def test_apply_does_not_run_cci(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        cli = FakeCli(self.home, [row(DEAD_ORG)], cci=self.ORGS)
        plan_file = self.audit_file(cli)
        cli.calls.clear()
        self.assertEqual(self.apply(cli, plan_file), 0)
        self.assertEqual([c for c in cli.calls if c[0] == "cci" or c[1:3] == ["alias", "list"]],
                         [["sf", "alias", "list", "--json"]])  # the re-derived plan's one list


class Secrets(Base):
    def test_auth_inventory_holds_no_token_values(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        self.assertNotIn(CANARY, json.dumps(oc.read_logins(self.home), default=sorted))

    def test_no_token_reaches_the_plan_or_the_output(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        (self.project / ".sfdx" / "saved-auth").write_text(CANARY)
        out = self.project / "plan.json"
        self.assertEqual(self.main(["audit", "--out", str(out)], FakeCli(self.home, [row(DEAD_ORG)])), 0)
        self.assertNotIn(CANARY, self.stdout.getvalue())
        self.assertNotIn(CANARY, out.read_text())
        self.assertEqual(oct(out.stat().st_mode & 0o777), "0o600")

    def test_a_symlinked_or_renamed_credential_file_is_reported(self):
        elsewhere = self.home / "elsewhere.json"
        elsewhere.write_text(CANARY)
        (self.home / ".sfdx" / "linked@x.invalid.json").symlink_to(elsewhere)
        (self.home / ".sfdx" / "backup@x.invalid.json.bak").write_text(CANARY)
        (self.home / ".sfdx" / "saved@x.invalid.sfdxurl").write_text(CANARY)
        (self.home / ".sfdx" / (DEAD_ORG + "MAA.json")).symlink_to(elsewhere)
        (self.home / ".sf" / "copied@x.invalid.json").write_text(CANARY)
        (self.project / ".sfdx" / "copied@x.invalid.json").write_text(CANARY)
        (self.project / ".sf" / (LIVE_ORG + "MAA.json")).write_text(CANARY)
        self.add_auth("plain@x.invalid", LIVE_ORG)  # a regular login is not "unclassified"
        files = self.plan(FakeCli(self.home))["report"]["unclassified_files"]
        self.assertEqual(sorted(Path(f["path"]).name for f in files),
                         sorted(["linked@x.invalid.json", "backup@x.invalid.json.bak", "saved@x.invalid.sfdxurl",
                                 DEAD_ORG + "MAA.json", "copied@x.invalid.json", "copied@x.invalid.json",
                                 LIVE_ORG + "MAA.json"]))
        self.assertNotIn(CANARY, json.dumps(files))

    def test_the_plan_is_created_with_mode_0600(self):
        real_open, modes = os.open, []

        def spy(path, flags, mode=0o777, **kwargs):
            modes.append(mode)
            return real_open(path, flags, mode, **kwargs)

        with mock.patch.object(oc.os, "open", spy):
            self.assertEqual(self.main(["audit", "--out", str(self.project / "plan.json")], FakeCli(self.home)), 0)
        self.assertEqual(modes, [0o600])  # never created under the umask and tightened later

    def test_the_plan_is_never_written_through_a_symlink(self):
        victim = self.project / "victim.txt"
        victim.write_text("keep")
        link = self.project / "plan.json"
        link.symlink_to(victim)
        for patch in (contextlib.nullcontext(), mock.patch.object(os, "O_NOFOLLOW", 0, create=True)):
            with patch:
                self.assertEqual(self.main(["audit", "--out", str(link)], FakeCli(self.home)), 1)
            self.assertEqual(victim.read_text(), "keep")
            self.assertIn("Could not write the plan", self.stderr.getvalue())

    def test_an_entry_that_cannot_be_examined_is_reported_not_raised(self):
        unknown = self.project / ".sfdx" / "saved-auth"
        unknown.write_text("x")
        real = Path.lstat

        def deny(path, *args, **kwargs):
            if path.name == "saved-auth":
                raise PermissionError(errno.EACCES, "Permission denied")
            return real(path, *args, **kwargs)

        with mock.patch.object(Path, "lstat", deny):
            files = self.plan(FakeCli(self.home))["report"]["unclassified_files"]
        self.assertIn({"path": str(unknown), "error": "Permission denied"}, files)

    def test_an_unreadable_state_folder_stops_the_run_whatever_the_python_version(self):
        # From Python 3.14 pathlib answers False here instead of raising; the tool must not.
        real, denied = os.lstat, str(self.project / ".sfdx" / "orgs")

        def deny(path, *args, **kwargs):
            if str(path) == denied:
                raise PermissionError(errno.EACCES, "Permission denied")
            return real(path, *args, **kwargs)

        self.add_auth("rep@x.invalid", DEAD_ORG)
        cli = FakeCli(self.home, [row(DEAD_ORG)])
        with mock.patch.object(oc.os, "lstat", deny):
            self.assertEqual(self.main(["audit"], cli), 1)
        self.assertIn("Nothing was changed", self.stderr.getvalue())

    def test_an_existing_loose_plan_file_is_tightened(self):
        out = self.project / "plan.json"
        out.write_text("old")
        out.chmod(0o644)
        self.assertEqual(self.main(["audit", "--out", str(out)], FakeCli(self.home)), 0)
        self.assertEqual(oct(out.stat().st_mode & 0o777), "0o600")

    def test_an_unknown_file_is_reported_without_being_opened(self):
        unknown = self.project / ".sfdx" / "saved-auth"
        unknown.write_text(CANARY)
        unknown.chmod(0)  # any attempt to read it would raise
        self.addCleanup(unknown.chmod, 0o600)
        files = self.plan(FakeCli(self.home))["report"]["unclassified_files"]
        self.assertEqual([Path(f["path"]).name for f in files], ["saved-auth"])


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

    def test_removes_the_allowlist_moves_rather_than_deletes_and_then_is_a_no_op(self):
        rows = self.setup_stale_org()
        cli = FakeCli(self.home, rows, {"stale-a": "gone@x.invalid", "stale-b": "gone@x.invalid", "r": "rep@x.invalid"})
        self.assertEqual(self.audit_then_apply(cli), 0)
        self.assertFalse((self.home / ".sfdx" / "rep@x.invalid.json").exists())
        self.assertTrue((self.home / ".sfdx" / (HUB + ".json")).exists())
        self.assertFalse(self.index.exists())
        self.assertTrue((self.quarantine / ".sfdx" / self.index.name).exists())
        self.assertTrue((self.quarantine / "orgs" / self.tracking.name / "state").exists())
        self.assertTrue((self.quarantine / "manifestCache" / "job1.xml").exists())
        self.assertTrue(self.other_manifest.exists())
        self.assertEqual(self.read_cache(), {"job2": {"target-org": HUB, "keep": 1}})
        self.assertEqual(cli.aliases, {})
        self.assertIn("'cleared_by_logout': 1", self.stdout.getvalue())
        self.assertEqual({k: v for k, v in self.plan(cli)["remove"].items() if v}, {})

    def test_the_audit_prints_what_each_logout_also_clears(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        self.write_config("local", sf={"target-org": "my-scratch"})
        cli = FakeCli(self.home, [row(DEAD_ORG)], {"my-scratch": "rep@x.invalid", "p__dev": "rep@x.invalid"})
        self.assertEqual(self.main(["audit"], cli), 0)
        out = self.stdout.getvalue()
        self.assertIn("sf also clears its aliases: my-scratch, p__dev", out)
        self.assertIn("sf also clears from the local config: target-org", out)

    def test_a_stale_legacy_tracking_folder_is_moved(self):
        legacy = self.project / ".sfdx" / "orgs" / "gone@x.invalid"
        legacy.mkdir()
        (legacy / "state").write_text("x")
        self.assertEqual(self.audit_then_apply(FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")])), 0)
        self.assertFalse(legacy.exists())
        self.assertTrue((self.quarantine / "orgs" / legacy.name / "state").exists())

    def test_aliases_go_one_per_command(self):
        rows = self.setup_stale_org()
        cli = FakeCli(self.home, rows, {"stale-a": "gone@x.invalid", "stale-b": "gone@x.invalid"})
        self.audit_then_apply(cli)
        unsets = [c for c in cli.calls if c[1:3] == ["alias", "unset"]]
        self.assertEqual(len(unsets), 2)
        self.assertTrue(all(c[3:5] == ["--json", "--"] and len(c) == 6 for c in unsets), unsets)

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
        self.main(["audit"], cli)
        self.assertEqual(sorted(str(p) for p in self.home.rglob("*")), before)
        allowed = (["alias", "list"], ["data", "query"])
        self.assertTrue(all(c[0] == "cci" or c[1:3] in allowed for c in cli.calls), cli.calls)

    def drifted(self, cli, change):
        """Audit, make one change, apply: it must stop with 3 before any logout."""
        plan_file = self.audit_file(cli)
        change(plan_file)
        self.assertEqual(self.apply(cli, plan_file), 3)
        self.assertEqual(self.logouts(cli), [])

    def edit_plan(self, plan_file, edit):
        plan = json.loads(plan_file.read_text())
        edit(plan)
        plan_file.write_text(json.dumps(plan))

    def test_a_plan_reviewed_for_another_project_is_not_applied(self):
        cli = FakeCli(self.home, self.setup_stale_org(), {"stale": "gone@x.invalid"})
        self.drifted(cli, lambda f: self.edit_plan(f, lambda p: p.update(project=str(self.project.parent / "other"))))

    def test_a_changed_alias_target_is_drift_even_when_the_removal_list_matches(self):
        cli = FakeCli(self.home, self.setup_stale_org(), {"stale": "gone@x.invalid"})
        self.drifted(cli, lambda f: self.edit_plan(
            f, lambda p: p["targets"]["aliases"]["stale"].update(value="someone-else@x.invalid")))

    def test_a_default_moved_to_another_stale_username_is_drift(self):
        self.write_config("local", sf={"target-org": "gone@x.invalid"})
        rows = [row("00DBB0000000001", user="gone@x.invalid"), row("00DBB0000000002", user="gone2@x.invalid")]
        cli = FakeCli(self.home, rows)
        self.drifted(cli, lambda f: self.write_config("local", sf={"target-org": "gone2@x.invalid"}))
        self.assertEqual(self.read_config("local")[0], {"target-org": "gone2@x.invalid"})

    def test_a_login_moved_to_another_removable_org_is_drift(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        cli = FakeCli(self.home, [row(DEAD_ORG), row(OTHER_DEAD)])
        self.drifted(cli, lambda f: self.add_auth("rep@x.invalid", OTHER_DEAD))

    def test_an_alias_added_to_a_logged_out_user_since_the_audit_is_drift(self):
        cli = FakeCli(self.home, self.setup_stale_org())
        self.drifted(cli, lambda f: cli.aliases.update({"added-later": "rep@x.invalid"}))
        self.assertIn("added-later", cli.aliases)

    def test_a_default_naming_a_logged_out_user_added_since_the_audit_is_drift(self):
        cli = FakeCli(self.home, self.setup_stale_org(), {"base": "rep@x.invalid"})
        self.drifted(cli, lambda f: self.write_config("global", sf={"target-org": "base"}))

    def test_a_deploy_job_added_since_the_audit_is_drift(self):
        cli = FakeCli(self.home, self.setup_stale_org())
        self.drifted(cli, lambda f: (self.home / ".sf" / "deploy-cache.json").write_text(
            json.dumps({"job9": {"target-org": "rep@x.invalid"}})))

    def test_drift_since_review_stops_before_anything_happens(self):
        rows = self.setup_stale_org()
        self.assertEqual(self.audit_then_apply(FakeCli(self.home, rows), FakeCli(self.home, [])), 3)
        self.assertTrue((self.home / ".sfdx" / "rep@x.invalid.json").exists())
        self.assertTrue(self.index.exists())

    def test_a_protected_login_keeps_its_orgs_state_when_another_login_goes(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        self.add_auth("rep2@x.invalid", DEAD_ORG)  # named like an alias, so never logged out
        (self.home / ".sfdx" / (DEAD_ORG + "MAA.json")).write_text("{}")
        (self.project / ".sf" / "orgs" / (DEAD_ORG + "MAA")).mkdir()
        (self.project / ".sfdx" / "fileResponses" / (DEAD_ORG + "MAA")).mkdir(parents=True)
        (self.project / ".sfdx" / "orgs" / "rep@x.invalid").mkdir()
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)], {"rep2@x.invalid": HUB}))
        self.assertEqual(plan["remove"]["logout"], ["rep@x.invalid"])
        for key in ("indexes", "tracking", "file_responses"):
            self.assertEqual(plan["remove"][key], [], key)

    def test_a_failed_logout_keeps_that_orgs_residual_state(self):
        cli = FakeCli(self.home, self.setup_stale_org(), fail_logout=["rep@x.invalid"])
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertTrue(self.index.exists())
        self.assertTrue(self.tracking.exists())
        self.assertIn("job1", self.read_cache())
        self.assertTrue(self.manifest.exists())
        self.assertIn("FAILED: job1 (skipped because its logout failed)", self.stdout.getvalue())

    def test_a_failed_logout_keeps_everything_reaching_another_login_on_its_org(self):
        rows = self.setup_stale_org()
        self.add_auth("rep2@x.invalid", DEAD_ORG)
        legacy = self.project / ".sfdx" / "orgs" / "rep2@x.invalid"
        legacy.mkdir()
        (self.home / ".sf" / "deploy-cache.json").write_text(json.dumps({"job1": {"target-org": "Rep2@x.invalid"}}))
        self.write_config("local", sf={"target-org": "Rep2@x.invalid"})
        cli = FakeCli(self.home, rows, {"r2": "Rep2@x.invalid"}, fail_logout=["rep@x.invalid"])
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertNotIn("rep2@x.invalid.json", [p.name for p in (self.home / ".sfdx").iterdir()])  # it went
        self.assertTrue(legacy.exists())
        self.assertIn("r2", cli.aliases)
        self.assertIn("job1", self.read_cache())
        self.assertEqual(self.unsets(cli), [])

    def test_a_failed_logout_keeps_a_default_naming_the_user(self):
        rows = self.setup_stale_org()
        self.write_config("local", sf={"target-org": "rep@x.invalid"})
        cli = FakeCli(self.home, rows, {"base": "rep@x.invalid"}, fail_logout=["rep@x.invalid"])
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertEqual(cli.aliases, {"base": "rep@x.invalid"})
        self.assertEqual(self.unsets(cli), [])

    def test_a_logout_that_does_not_name_the_user_counts_as_failed(self):
        cli = FakeCli(self.home, self.setup_stale_org())
        cli.override = lambda cmd: FakeCli.ok([]) if cmd[1:3] == ["org", "logout"] else None
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertIn("rep@x.invalid (logout failed)", self.stdout.getvalue())
        self.assertTrue(self.index.exists())

    def test_a_logout_that_also_removed_another_user_is_reported(self):
        cli = FakeCli(self.home, self.setup_stale_org())
        cli.override = (lambda cmd: FakeCli.ok(["rep@x.invalid", "other@x.invalid"])
                        if cmd[1:3] == ["org", "logout"] else None)
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertIn("sf also logged out other@x.invalid", self.stdout.getvalue())

    def test_an_alias_unset_reporting_no_success_counts_as_failed(self):
        cli = FakeCli(self.home, self.setup_stale_org(), {"stale": "gone@x.invalid"})
        cli.override = lambda cmd: (FakeCli.ok([{"alias": cmd[3], "success": False}])
                                    if cmd[1:3] == ["alias", "unset"] else None)
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertIn("stale (alias unset failed)", self.stdout.getvalue())

    def test_an_alias_unset_answering_for_another_alias_counts_as_failed(self):
        cli = FakeCli(self.home, self.setup_stale_org(), {"stale": "gone@x.invalid"})
        cli.override = lambda cmd: (FakeCli.ok([{"alias": "other", "success": True}])
                                    if cmd[1:3] == ["alias", "unset"] else None)
        self.assertEqual(self.audit_then_apply(cli), 1)

    def test_an_alias_sf_would_read_as_flags_is_passed_after_a_double_dash(self):
        # Unquoted, `-ap` is --all --no-prompt to `sf alias unset`: every alias would go.
        rows = [row("00DBB0000000001", user="gone@x.invalid")]
        cli = FakeCli(self.home, rows, {"-ap": "gone@x.invalid", "keep": HUB})
        self.assertEqual(self.audit_then_apply(cli), 0)
        self.assertEqual(cli.aliases, {"keep": HUB})
        self.assertEqual([c for c in cli.calls if c[1:3] == ["alias", "unset"]],
                         [["sf", "alias", "unset", "--json", "--", "-ap"]])

    def test_a_default_changed_during_the_run_is_not_unset(self):
        rows = self.setup_stale_org()
        self.write_config("local", sf={"target-org": "gone@x.invalid"})
        cli = FakeCli(self.home, rows)
        plan_file = self.audit_file(cli)

        def change(cmd):
            if cmd[1:3] == ["org", "logout"]:
                self.write_config("local", sf={"target-org": "new@x.invalid"})
            return None

        cli.override = change
        self.assertEqual(self.apply(cli, plan_file), 1)
        self.assertEqual(self.unsets(cli), [])
        self.assertIn("local default (changed during this run; not modified)", self.stdout.getvalue())

    def test_an_alias_unset_that_removed_more_than_its_alias_counts_as_failed(self):
        cli = FakeCli(self.home, self.setup_stale_org(), {"stale": "gone@x.invalid"})
        cli.override = lambda cmd: (FakeCli.ok([{"alias": "stale", "success": True}, {"alias": "x", "success": True}])
                                    if cmd[1:3] == ["alias", "unset"] else None)
        self.assertEqual(self.audit_then_apply(cli), 1)

    def test_a_default_on_an_orphan_alias_is_unset_and_checked(self):
        self.write_config("local", sf={"target-org": "stale"}, sfdx={"defaultusername": "stale"})
        cli = FakeCli(self.home, self.setup_stale_org(), {"stale": "gone@x.invalid"})
        self.assertEqual(self.audit_then_apply(cli), 0)
        self.assertEqual(self.unsets(cli), [["sf", "config", "unset", "target-org", "--json"]])
        self.assertEqual(self.read_config("local"), [{}, {}])

    def test_a_global_default_is_unset_globally(self):
        self.write_config("global", sf={"target-org": "gone@x.invalid"})
        self.write_config("local", sf={"target-org": HUB})
        cli = FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")])
        self.assertEqual(self.audit_then_apply(cli), 0)
        self.assertEqual(self.unsets(cli), [["sf", "config", "unset", "target-org", "--global", "--json"]])
        self.assertEqual(self.read_config("local")[0], {"target-org": HUB})

    def test_a_default_still_set_after_the_unset_is_reported(self):
        self.write_config("local", sf={"target-org": "gone@x.invalid"})
        cli = FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")])
        cli.unset_works = False
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertIn("local default (still set after config unset)", self.stdout.getvalue())

    def test_a_failed_config_unset_is_reported(self):
        self.write_config("local", sf={"target-org": "gone@x.invalid"})
        cli = FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")])
        cli.override = lambda cmd: (1, json.dumps({"status": 1})) if cmd[1:3] == ["config", "unset"] else None
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertIn("local default (config unset failed)", self.stdout.getvalue())

    def test_a_default_logout_cleared_is_not_unset_again(self):
        self.write_config("local", sf={"target-org": "rep@x.invalid"})
        cli = FakeCli(self.home, self.setup_stale_org())
        self.assertEqual(self.audit_then_apply(cli), 0)
        self.assertEqual(self.unsets(cli), [])
        self.assertEqual(self.read_config("local"), [{}, {}])

    def test_a_valid_default_survives(self):
        self.write_config("local", sf={"target-org": HUB})
        cli = FakeCli(self.home, self.setup_stale_org())
        self.assertEqual(self.audit_then_apply(cli), 0)
        self.assertEqual(self.unsets(cli), [])
        self.assertEqual(self.read_config("local")[0], {"target-org": HUB})

    def test_an_interrupt_after_a_logout_still_reports_what_ran(self):
        self.setup_stale_org()
        self.add_auth("rep2@x.invalid", OTHER_DEAD)
        cli = FakeCli(self.home, [row(DEAD_ORG), row(OTHER_DEAD)])

        def interrupt(cmd):
            if cmd[1:3] == ["org", "logout"] and cmd[4] == "rep@x.invalid":
                raise KeyboardInterrupt
            return None

        plan_file = self.audit_file(cli)
        cli.override = interrupt
        self.assertEqual(self.apply(cli, plan_file), 130)
        self.assertIn("Done: ", self.stdout.getvalue())
        self.assertIn("Stopped part-way: interrupted", self.stderr.getvalue())

    def test_an_error_after_a_logout_reports_what_ran_not_a_traceback(self):
        cli = FakeCli(self.home, self.setup_stale_org())
        with mock.patch.object(oc, "move_to_quarantine", side_effect=PermissionError(errno.EACCES, "Permission denied")):
            self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertIn("'logout': 1", self.stdout.getvalue())
        self.assertIn("Stopped part-way: Permission denied", self.stderr.getvalue())

    def test_an_unexpected_error_after_a_logout_is_reported_too(self):
        cli = FakeCli(self.home, self.setup_stale_org())
        with mock.patch.object(oc, "remove_deploy_jobs", side_effect=ValueError("bad cache")):
            self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertIn("Stopped part-way: ValueError: bad cache", self.stderr.getvalue())

    def test_an_unreadable_state_folder_stops_apply_before_any_logout(self):
        cli = FakeCli(self.home, self.setup_stale_org())
        plan_file = self.audit_file(cli)
        with mock.patch.object(oc, "survey", side_effect=PermissionError(errno.EACCES, "Permission denied")):
            self.assertEqual(self.apply(cli, plan_file), 1)
        self.assertEqual(self.logouts(cli), [])

    def test_the_rewritten_cache_keeps_its_mode(self):
        self.setup_stale_org()
        cache = self.home / ".sf" / "deploy-cache.json"
        os.chmod(str(cache), 0o644)  # mkstemp would make it 600 if the mode were not carried over
        self.assertEqual(self.audit_then_apply(FakeCli(self.home, [row(DEAD_ORG)])), 0)
        self.assertEqual(cache.stat().st_mode & 0o777, 0o644)

    def test_tracked_state_is_refused(self):
        cli = FakeCli(self.home, self.setup_stale_org())
        cli.tracked.add(str(self.tracking))
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertTrue(self.tracking.exists())

    def test_a_git_failure_refuses_the_move(self):
        cli = FakeCli(self.home, self.setup_stale_org())
        cli.override = lambda cmd: (1, "") if cmd[0] == "git" else None
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertTrue(self.tracking.exists())
        self.assertIn("git could not say", self.stdout.getvalue())


class Quarantine(Base):
    setup_stale_org = Apply.setup_stale_org

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

    @staticmethod
    def files_under(path):
        return sorted(str(p.relative_to(path)) for p in path.rglob("*") if p.is_file())

    def test_a_quarantine_link_is_refused_by_apply_before_any_logout(self):
        cli = FakeCli(self.home, self.setup_stale_org())
        real = self.home / "real-quarantine"
        real.mkdir()
        link = self.home / "linked-quarantine"
        link.symlink_to(real)
        self.assertEqual(self.apply(cli, self.audit_file(cli), link), 1)
        self.assertEqual(Apply.logouts(cli), [])

    def test_a_quarantine_folder_that_is_a_link_or_a_file_is_refused(self):
        elsewhere = self.home.parent / "elsewhere"
        elsewhere.mkdir()
        self.quarantine.mkdir()
        os.symlink(str(elsewhere), str(self.quarantine / "orgs"))
        self.assertIn("symlink", oc.check_quarantine(self.quarantine, self.home))
        item = self.project / ".sf" / "orgs" / "00DAA0000000009MAA"
        item.mkdir()
        why = oc.move_to_quarantine(FakeCli(self.home), item, [self.project / ".sf" / "orgs"], self.quarantine, self.project)
        self.assertIn("symlink", why)
        self.assertEqual(list(elsewhere.iterdir()), [])
        (self.quarantine / "orgs").unlink()
        (self.quarantine / "orgs").write_text("not a folder")
        self.assertIn("not a folder", oc.check_quarantine(self.quarantine, self.home))

    def test_a_quarantine_folder_that_cannot_be_written_is_refused(self):
        if os.name == "nt" or os.geteuid() == 0:
            self.skipTest("needs POSIX permissions that root does not honor")
        (self.quarantine / "orgs").mkdir(parents=True)
        (self.quarantine / "orgs").chmod(0o555)
        self.writable_again(self.quarantine / "orgs")
        self.assertIn("not writable", oc.check_quarantine(self.quarantine, self.home))

    def test_a_quarantine_root_that_becomes_a_link_is_refused_at_the_move(self):
        item = self.project / ".sf" / "orgs" / "00DAA0000000009MAA"
        item.mkdir()
        real = self.home / "real-quarantine"
        real.mkdir()
        os.symlink(str(real), str(self.quarantine))
        why = oc.move_to_quarantine(FakeCli(self.home), item, [self.project / ".sf" / "orgs"], self.quarantine, self.project)
        self.assertIn("symlink", why)
        self.assertTrue(item.exists())

    def test_a_quarantine_that_refuses_files_stops_before_any_logout(self):
        cli = FakeCli(self.home, self.setup_stale_org())
        plan_file = self.audit_file(cli)
        # The folder can be created, as ~/.Trash allows: only moving a file in shows the refusal.
        with mock.patch.object(oc.os, "rename", side_effect=PermissionError(1, "Not permitted")):
            self.assertEqual(self.apply(cli, plan_file), 1)
        self.assertEqual(Apply.logouts(cli), [])
        self.assertTrue(self.index.exists())
        self.assertIn("before any logout", self.stderr.getvalue())
        self.assertFalse(self.quarantine.exists())
        self.assertEqual(list(self.home.glob(".org-cleanup-probe-*")), [])

    def test_a_quarantine_path_that_cannot_be_examined_is_reported_not_raised(self):
        with mock.patch.object(oc.os, "lstat", side_effect=PermissionError(13, "Denied")):
            self.assertEqual(oc.check_quarantine(self.quarantine, self.home), "Denied")
        self.assertFalse(self.quarantine.exists())
        self.assertEqual(list(self.home.glob(".org-cleanup-probe-*")), [])

    def test_the_quarantine_check_is_skipped_when_nothing_needs_moving(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        cli = FakeCli(self.home, [row(DEAD_ORG)])
        plan_file = self.audit_file(cli)
        with mock.patch.object(oc.os, "rename", side_effect=PermissionError(1, "Not permitted")):
            self.assertEqual(self.apply(cli, plan_file), 0)
        self.assertEqual(len(Apply.logouts(cli)), 1)
        self.assertNotIn("Residual files moved", self.stdout.getvalue())

    def test_a_move_that_fails_later_is_reported_and_the_run_continues(self):
        cli = FakeCli(self.home, self.setup_stale_org())
        plan_file = self.audit_file(cli)
        with self.refuse_rename_of(self.index):
            self.assertEqual(self.apply(cli, plan_file), 1)
        self.assertTrue(self.index.exists())
        self.assertIn("could not move into {}: Not permitted".format(self.quarantine / ".sfdx"), self.stdout.getvalue())
        self.assertIn("Residual files moved", self.stdout.getvalue())
        self.assertTrue((self.quarantine / "orgs" / self.tracking.name / "state").exists())
        self.assertEqual(self.read_cache(), {"job2": {"target-org": HUB, "keep": 1}})

    def test_when_every_move_fails_the_quarantine_is_still_named(self):
        rows = self.setup_stale_org()
        (self.home / ".sf" / "deploy-cache.json").unlink()
        self.manifest.unlink()
        cli = FakeCli(self.home, rows)
        cli.tracked.add(str(self.tracking))
        plan_file = self.audit_file(cli)
        with self.refuse_rename_of(self.index):
            self.assertEqual(self.apply(cli, plan_file), 1)
        self.assertNotIn("Residual files moved", self.stdout.getvalue())
        self.assertIn("partial copy in: {}".format(self.quarantine), self.stdout.getvalue())

    def test_a_refused_rename_leaves_no_copy_and_a_retry_succeeds(self):
        cli = FakeCli(self.home, self.setup_stale_org())
        with self.refuse_rename_of(self.index):
            self.assertEqual(self.apply(cli, self.audit_file(cli)), 1)
        self.assertEqual(list(self.quarantine.rglob(self.index.name)), [])
        self.assertEqual(self.audit_then_apply(FakeCli(self.home, [row(DEAD_ORG)])), 0)
        self.assertFalse(self.index.exists())

    def test_a_move_across_volumes_still_works(self):
        source, dest = self.home / "file", self.home / "moved"
        source.write_text("x")
        with self.across_volumes(), mock.patch.object(oc.shutil, "move") as copy_move:
            oc.move_path(str(source), str(dest))
        copy_move.assert_called_once_with(str(source), str(dest))

    def test_a_failed_delete_across_volumes_loses_nothing_and_a_retry_finishes(self):
        if os.name == "nt" or os.geteuid() == 0:
            self.skipTest("needs POSIX permissions that root does not honor")
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
            self.assertIsNone(oc.move_to_quarantine(FakeCli(self.home), item, [root], self.quarantine, self.project))
        self.assertFalse(item.exists())
        self.assertEqual(self.files_under(copy), ["a", "b", "sub/held"])
        self.assertEqual(self.files_under(copy.with_name(item.name + ".1")), left)

    def test_a_failed_copy_across_volumes_leaves_the_source_and_a_retry_finishes(self):
        if os.name == "nt" or os.geteuid() == 0:
            self.skipTest("needs POSIX permissions that root does not honor")
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
            self.assertLess(len(why), 330 + len(str(self.quarantine)))  # shutil.Error lists every path
            self.assertEqual(self.files_under(item), ["a", secret])
            (item / secret).chmod(0o644)
            self.assertIsNone(oc.move_to_quarantine(FakeCli(self.home), item, [root], self.quarantine, self.project))
        self.assertFalse(item.exists())
        self.assertEqual(self.files_under(self.quarantine / "orgs" / (item.name + ".1")), ["a", secret])

    def test_the_same_name_in_both_tracking_layouts_moves_without_a_collision(self):
        name, results = "00DAA0000000009MAA", []
        for layout in (".sf", ".sfdx"):
            root = self.project / layout / "orgs"
            (root / name).mkdir(parents=True)
            (root / name / layout).write_text("x")
            results.append(oc.move_to_quarantine(FakeCli(self.home), root / name, [root], self.quarantine, self.project))
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
        self.assertEqual(self.files_under(link.with_name(item.name + ".1")), ["state"])

    def test_a_symlink_that_appears_after_the_audit_is_refused(self):
        target = self.project / "elsewhere"
        target.mkdir()
        link = self.project / ".sf" / "orgs" / "00DAA0000000009MAA"
        link.symlink_to(target)
        self.assertEqual(oc.move_to_quarantine(FakeCli(self.home), link, [link.parent], self.quarantine, self.project),
                         "symlink")
        self.assertTrue(link.is_symlink())

    def test_a_path_outside_the_state_roots_is_refused(self):
        stray = self.project / "keep.txt"
        stray.write_text("x")
        why = oc.move_to_quarantine(FakeCli(self.home), stray, [self.project / ".sf" / "orgs"], self.quarantine,
                                    self.project)
        self.assertEqual(why, "outside the expected state roots")


class DeployCache(Base):
    setup_stale_org = Apply.setup_stale_org

    def test_a_refused_manifest_keeps_its_cache_entry(self):
        cli = FakeCli(self.home, self.setup_stale_org())
        plan_file = self.audit_file(cli)
        with Quarantine.refuse_rename_of(self, self.manifest):
            self.assertEqual(self.apply(cli, plan_file), 1)
        self.assertIn("job1", self.read_cache())
        self.assertTrue(self.manifest.exists())

    def test_a_failed_cache_write_is_reported_and_leaves_the_cache_intact(self):
        cli = FakeCli(self.home, self.setup_stale_org())
        before = self.read_cache()
        plan_file = self.audit_file(cli)
        with mock.patch.object(oc.os, "replace", side_effect=PermissionError(1, "Not permitted")):
            self.assertEqual(self.apply(cli, plan_file), 1)
        self.assertEqual(self.read_cache(), before)
        self.assertIn("could not write: Not permitted", self.stdout.getvalue())
        self.assertEqual(list((self.home / ".sf").glob(".deploy-cache.*")), [])

    def test_an_interrupted_cache_write_leaves_no_temp_file(self):
        self.setup_stale_org()
        with mock.patch.object(oc.json, "dump", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                oc.replace_json(self.home / ".sf" / "deploy-cache.json", {})
        self.assertEqual(list((self.home / ".sf").glob(".deploy-cache.*")), [])

    def test_a_job_gone_from_the_cache_since_the_audit_reports_its_manifest(self):
        self.setup_stale_org()
        (self.home / ".sf" / "deploy-cache.json").write_text(json.dumps({"job2": {"target-org": HUB}}))
        failures = []
        result = oc.remove_deploy_jobs(FakeCli(self.home), ["job1"], self.home, self.quarantine, self.project, failures)
        self.assertEqual(result, (0, 0))
        self.assertEqual(failures, [("job1", "no longer in the deploy cache; its manifest was left in place")])

    def test_a_linked_deploy_cache_is_reported_and_never_rewritten(self):
        target = self.home / "shared-cache.json"
        target.write_text(json.dumps({"job1": {"target-org": "gone@x.invalid"}}))
        (self.home / ".sf" / "deploy-cache.json").symlink_to(target)
        plan = self.plan(FakeCli(self.home))
        self.assertEqual(plan["remove"]["deploy_jobs"], [])
        self.assertIn(str(self.home / ".sf" / "deploy-cache.json"), plan["report"]["symlinks_left_alone"])
        failures = []
        oc.remove_deploy_jobs(FakeCli(self.home), ["job1"], self.home, self.quarantine, self.project, failures)
        self.assertEqual(failures, [(str(self.home / ".sf" / "deploy-cache.json"), "symlink")])
        self.assertIn("job1", json.loads(target.read_text()))

    def test_a_linked_manifest_cache_is_not_state_to_move(self):
        outside = self.home.parent / "outside"
        outside.mkdir()
        (outside / "job1.xml").write_text("<x/>")
        (self.home / ".sf" / "manifestCache").rmdir()
        os.symlink(str(outside), str(self.home / ".sf" / "manifestCache"))
        (self.home / ".sf" / "deploy-cache.json").write_text(json.dumps({"job1": {"target-org": "gone@x.invalid"}}))
        plan = self.plan(FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")]))
        self.assertEqual(plan["remove"]["deploy_jobs"], [])
        self.assertIn(str(self.home / ".sf" / "manifestCache"), plan["report"]["symlinks_left_alone"])
        failures = []
        self.assertEqual(oc.remove_deploy_jobs(FakeCli(self.home), ["job1"], self.home, self.quarantine,
                                               self.project, failures), (0, 0))
        self.assertTrue((outside / "job1.xml").exists())
        self.assertEqual([f[1] for f in failures], ["symlink"])

    def test_a_cache_key_that_is_not_a_plain_job_id_is_refused(self):
        outside = self.home / "foo.xml"
        outside.write_text("<x/>")
        (self.home / ".sf" / "deploy-cache.json").write_text(json.dumps({"../../foo": {"target-org": "x"}}))
        failures = []
        self.assertEqual(oc.remove_deploy_jobs(FakeCli(self.home), ["../../foo"], self.home, self.quarantine,
                                               self.project, failures), (0, 0))
        self.assertEqual([f[0] for f in failures], ["../../foo"])
        self.assertTrue(outside.exists())
        self.assertIn("../../foo", self.read_cache())

    def test_an_unreadable_cache_is_reported(self):
        (self.home / ".sf" / "deploy-cache.json").write_text("not json")
        failures = []
        self.assertEqual(oc.remove_deploy_jobs(FakeCli(self.home), ["job1"], self.home, self.quarantine,
                                               self.project, failures), (0, 0))
        self.assertEqual(failures, [("deploy-cache", "unreadable")])


class CheckLogins(Base):
    def answer(self, cli, failing=()):
        cli.override = lambda cmd: ((1, json.dumps({"status": 1})) if set(cmd) & set(failing) else
                                    FakeCli.ok({"done": True, "totalSize": 0, "records": []})
                                    if cmd[1:3] == ["data", "query"] else None)

    def test_a_login_that_does_not_answer_is_named_and_fails_the_check(self):
        self.add_auth("rep@x.invalid", LIVE_ORG)
        cli = FakeCli(self.home)
        self.answer(cli, failing=["rep@x.invalid"])
        self.assertEqual(self.main(["audit", "--check-logins"], cli), 1)
        self.assertIn("Logins that did not answer a query: ['rep@x.invalid']", self.stdout.getvalue())

    def test_all_logins_answering_passes(self):
        self.add_auth("rep@x.invalid", LIVE_ORG)
        cli = FakeCli(self.home)
        self.answer(cli)
        self.assertEqual(self.main(["audit", "--check-logins"], cli), 0)

    def test_a_login_named_like_an_alias_is_not_queried_and_is_named(self):
        self.add_auth("rep@x.invalid", LIVE_ORG)
        cli = FakeCli(self.home, aliases={"rep@x.invalid": HUB})
        self.answer(cli)
        self.assertEqual(self.main(["audit", "--check-logins"], cli), 0)
        self.assertFalse([c for c in cli.calls if "SELECT Id FROM Organization" in c and "rep@x.invalid" in c])
        self.assertIn("Not queried: rep@x.invalid", self.stdout.getvalue())

    def test_a_linked_login_sf_uses_is_queried(self):
        target = self.home / "elsewhere.json"
        target.write_text("{}")
        (self.home / ".sfdx" / "link@x.invalid.json").symlink_to(target)
        cli = FakeCli(self.home)
        self.answer(cli)
        self.main(["audit", "--check-logins"], cli)
        self.assertTrue([c for c in cli.calls if "SELECT Id FROM Organization" in c and "link@x.invalid" in c])


class ModelEdges(Base):
    """Cases the first review round of the sf model found; each pins a guard."""

    setup_stale_org = Apply.setup_stale_org

    def test_an_alias_list_of_an_unexpected_shape_stops_the_audit(self):
        self.add_auth("old@x.invalid", DEAD_ORG)
        for result in ({"old@x.invalid": "live@x.invalid"}, [{"name": "old@x.invalid"}], None,
                       [{"alias": "a", "value": 5}]):
            cli = FakeCli(self.home, [row(DEAD_ORG)])
            cli.override = lambda cmd, result=result: FakeCli.ok(result) if cmd[1:3] == ["alias", "list"] else None
            self.assertEqual(self.main(["audit"], cli), 1, result)
            self.assertIn("unexpected shape", self.stderr.getvalue())

    def test_a_name_that_is_both_an_alias_and_a_login_keeps_its_default_and_jobs(self):
        # The alias shadows a live login's name. sf resolves the alias first, but what the name was
        # meant to reach is in doubt, so whatever uses it is kept.
        self.add_auth("bob@x.invalid", LIVE_ORG)
        self.write_config("local", sf={"target-org": "bob@x.invalid"})
        (self.home / ".sf" / "deploy-cache.json").write_text(json.dumps({"job1": {"target-org": "bob@x.invalid"}}))
        rows = [row("00DBB0000000001", user="gone@x.invalid"), row(LIVE_ORG, "Active", "2026-12-01")]
        plan = self.plan(FakeCli(self.home, rows, {"bob@x.invalid": "gone@x.invalid"}))
        for key in ("logout", "aliases", "defaults", "deploy_jobs"):
            self.assertEqual(plan["remove"][key], [], key)
        self.assertIn("bob@x.invalid", plan["report"]["protected"])

    def test_a_deploy_cache_value_is_resolved_through_one_alias_as_sf_reads_it(self):
        # deploy report/resume pass the stored value to Org.create, which resolves an alias first.
        (self.home / ".sf" / "deploy-cache.json").write_text(json.dumps({"job1": {"target-org": "stale"}}))
        plan = self.plan(FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")], {"stale": "gone@x.invalid"}))
        self.assertEqual(plan["remove"]["deploy_jobs"], ["job1"])

    def test_an_alias_named_like_an_unread_login_is_kept_on_org_evidence_too(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        (self.home / ".sfdx" / "bob@x.invalid.json").write_text("not json")
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)], {"bob@x.invalid": "Rep@x.invalid"}))
        self.assertEqual(plan["remove"]["aliases"], [])
        self.assertIn("named like a login", plan["report"]["protected"]["bob@x.invalid"])

    def test_an_unread_login_is_listed_as_protected(self):
        (self.home / ".sfdx" / "bob@x.invalid.json").write_text("not json")
        self.assertIn("bob@x.invalid", self.plan(FakeCli(self.home))["report"]["protected"])

    def test_legacy_tracking_of_a_signup_user_stays_while_a_login_on_its_org_stays(self):
        self.add_auth("rep2@x.invalid", DEAD_ORG)  # kept: an alias is named like it
        (self.project / ".sfdx" / "orgs" / "admin@x.invalid").mkdir()
        rows = [row(DEAD_ORG, user="admin@x.invalid")]
        plan = self.plan(FakeCli(self.home, rows, {"rep2@x.invalid": HUB}))
        self.assertEqual(plan["remove"]["tracking"], [])

    def test_legacy_tracking_of_a_signup_user_waits_for_its_orgs_logouts(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        legacy = self.project / ".sfdx" / "orgs" / "admin@x.invalid"
        legacy.mkdir()
        cli = FakeCli(self.home, [row(DEAD_ORG, user="admin@x.invalid")], fail_logout=["rep@x.invalid"])
        plan_file = self.audit_file(cli)
        self.assertEqual(json.loads(plan_file.read_text())["targets"]["files"][str(legacy)],
                         {"login": None, "org": DEAD_ORG})
        self.assertEqual(self.apply(cli, plan_file), 1)
        self.assertTrue(legacy.exists())

    def test_conflicting_rows_are_reported_for_state_and_usernames_too(self):
        (self.home / ".sfdx" / (OTHER_DEAD + "MAA.json")).write_text("{}")
        rows = [row(OTHER_DEAD), row(OTHER_DEAD, "Active", "2026-12-01"),
                row("00DBB0000000003", user="reused@x.invalid"),
                row("00DBB0000000004", "Active", "2026-12-01", user="reused@x.invalid")]
        plan = self.plan(FakeCli(self.home, rows, {"a": "reused@x.invalid"}))
        self.assertEqual(plan["report"]["conflicting_evidence"], [OTHER_DEAD, "reused@x.invalid"])
        self.assertEqual((plan["remove"]["indexes"], plan["remove"]["aliases"]), ([], []))

    def test_a_config_path_that_is_not_a_file_is_not_modelled(self):
        (self.project / ".sf" / "config.json").mkdir()
        self.write_config("local", sfdx={"defaultusername": "gone@x.invalid"})
        plan = self.plan(FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")]))
        self.assertEqual(plan["remove"]["defaults"], [])
        self.assertIn("not a regular file", plan["report"]["unmodelled_config"]["local"])

    def test_a_hub_that_fails_only_the_username_query_blocks_username_judgment(self):
        self.add_auth("hub2@x.invalid", "00DHUB000000002", isDevHub=True)
        cli = FakeCli(self.home, [row("00DBB0000000001", user="gone@x.invalid")], {"stale": "gone@x.invalid"})
        cli.override = lambda cmd: ((10, json.dumps({"status": 10})) if "hub2@x.invalid" in cmd
                                    and any("SignupUsername IN" in c for c in cmd) else None)
        plan = self.plan(cli)
        self.assertEqual(plan["hub_failures"], ["hub2@x.invalid"])
        self.assertEqual(plan["remove"]["aliases"], [])

    def test_a_dangling_default_is_reported_only_where_the_scope_is_modelled(self):
        self.write_config("local", sf={"target-org": HUB}, sfdx={"defaultusername": "lost"})
        plan = self.plan(FakeCli(self.home))
        self.assertEqual(plan["report"]["dangling_defaults"], [])
        self.assertIn("local", plan["report"]["unmodelled_config"])

    def test_a_logout_whose_config_write_did_not_land_is_a_failure(self):
        rows = self.setup_stale_org()
        self.write_config("local", sf={"target-org": "rep@x.invalid"})
        cli = FakeCli(self.home, rows)
        cli.logout_clears_config = False
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertIn("rep@x.invalid (logout left target-org in the local config)", self.stdout.getvalue())
        self.assertTrue(self.index.exists())  # its org's state waits, as after a failed logout

    def test_a_scope_that_stops_being_modelled_during_the_run_is_not_unset(self):
        # The legacy file still holds the reviewed value, but sf would act on the newer .sf file.
        rows = self.setup_stale_org()
        self.write_config("local", sf={"target-org": "gone@x.invalid"}, sfdx={"defaultusername": "gone@x.invalid"})
        cli = FakeCli(self.home, rows)
        plan_file = self.audit_file(cli)

        def diverge(cmd):
            if cmd[1:3] == ["org", "logout"]:
                self.write_config("local", sf={"target-org": "live@x.invalid"})
            return None

        cli.override = diverge
        self.assertEqual(self.apply(cli, plan_file), 1)
        self.assertEqual(self.unsets(cli), [])

    def test_an_interrupt_during_the_deploy_cache_step_still_counts_the_moved_manifest(self):
        cli = FakeCli(self.home, self.setup_stale_org())
        plan_file = self.audit_file(cli)
        with mock.patch.object(oc, "replace_json", side_effect=KeyboardInterrupt):
            self.assertEqual(self.apply(cli, plan_file), 130)
        self.assertIn("'manifests': 1", self.stdout.getvalue())
        self.assertIn("Residual files moved", self.stdout.getvalue())

    def test_a_logout_that_removed_someone_else_instead_names_them(self):
        cli = FakeCli(self.home, self.setup_stale_org())
        cli.override = lambda cmd: FakeCli.ok(["live@x.invalid"]) if cmd[1:3] == ["org", "logout"] else None
        self.assertEqual(self.audit_then_apply(cli), 1)
        self.assertIn("sf also logged out live@x.invalid", self.stdout.getvalue())
        self.assertIn("rep@x.invalid (logout failed)", self.stdout.getvalue())

    def test_a_plan_file_that_cannot_be_read_is_not_drift(self):
        cli = FakeCli(self.home, self.setup_stale_org())
        self.assertEqual(self.apply(cli, self.project / "no-such-plan.json"), 1)
        self.assertIn("Could not read a plan", self.stderr.getvalue())
        self.assertEqual(self.logouts(cli), [])

    def test_an_alias_in_another_unicode_normalization_still_means_the_login(self):
        # APFS ignores normalization: the NFD spelling opens the NFC login's file.
        self.add_auth("josé@x.invalid", LIVE_ORG)
        self.add_auth("rep@x.invalid", DEAD_ORG)
        rows = [row(DEAD_ORG), row(LIVE_ORG, "Active", "2026-12-01")]
        plan = self.plan(FakeCli(self.home, rows, {"josé@x.invalid": "rep@x.invalid"}))
        self.assertEqual(plan["remove"]["logout"], [])

    def test_state_files_are_read_as_utf8_whatever_the_locale(self):
        data = self.home / "cache.json"
        data.write_bytes(json.dumps({"m": "/Users/josé/p.xml"}, ensure_ascii=False).encode("utf-8"))
        probe = ("import sys; sys.path.insert(0, {!r}); import org_cleanup as oc; "
                 "print(ascii(oc.read_json({!r}, None)))").format(str(REPO / "scripts" / "ai"), str(data))
        env = dict(os.environ, LC_ALL="en_US.ISO8859-1", LANG="en_US.ISO8859-1", PYTHONUTF8="0")
        out = subprocess.run([sys.executable, "-B", "-c", probe], env=env, capture_output=True, text=True).stdout
        self.assertEqual(out.strip(), ascii({"m": "/Users/josé/p.xml"}))

    def test_login_file_names_use_javascripts_whitespace(self):
        self.assertTrue(oc.SF_LOGIN_FILE.fullmatch("hub2@x.inval\u0085id.json"))
        self.assertFalse(oc.SF_LOGIN_FILE.fullmatch("hub2@x.inval﻿id.json"))

    def test_preserved_aliases_exclude_those_a_logout_clears(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        aliases = {"base": "rep@x.invalid", "keep": HUB, "keep2": "keep"}
        self.assertEqual(self.plan(FakeCli(self.home, [row(DEAD_ORG)], aliases))["preserved"]["aliases"], 2)

    def test_a_username_alias_with_no_row_is_unknown_not_dangling(self):
        plan = self.plan(FakeCli(self.home, aliases={"no-auth": "gone@x.invalid"}))
        self.assertEqual((plan["report"]["dangling_aliases"], plan["remove"]["aliases"]), ([], []))

    def test_residual_line_names_the_quarantine_for_each_kind_of_move(self):
        for make in (lambda: (self.project / ".sf" / "orgs" / DEAD_ORG).mkdir(),
                     lambda: (self.home / ".sfdx" / (DEAD_ORG + ".json")).write_text("{}"),
                     lambda: ((self.home / ".sf" / "deploy-cache.json").write_text(
                         json.dumps({"job1": {"target-org": "gone@x.invalid"}})),
                         (self.home / ".sf" / "manifestCache" / "job1.xml").write_text("<x/>"))):
            make()
            rows = [row(DEAD_ORG), row("00DBB0000000001", user="gone@x.invalid")]
            self.assertEqual(self.audit_then_apply(FakeCli(self.home, rows)), 0)
            self.assertIn("Residual files moved", self.stdout.getvalue())


class DocStaysInStep(Base):
    DOC = (REPO / ".cursor" / "skills" / "cci-orchestration" / "org-cleanup.md").read_text()

    def test_every_key_the_tool_reports_is_explained(self):
        plan = self.plan(FakeCli(self.home, cci=PrunePrediction.ORGS))
        keys = ["hub_failures", "prune_prediction", "preserved"] + list(plan["report"]) + list(plan["prune_prediction"])
        for key in keys:
            self.assertIn(key, self.DOC, key)

    def test_doc_names_the_commands_it_depends_on(self):
        for command in ("org_cleanup.py audit", "org_cleanup.py apply", "--check-logins"):
            self.assertIn(command, self.DOC)

    def test_the_tool_never_offers_a_remote_delete(self):
        code = (REPO / "scripts" / "ai" / "org_cleanup.py").read_text().split('"""', 2)[2]
        for banned in ('"delete"', "org delete", "--clean", "ActiveScratchOrg"):
            self.assertNotIn(banned, code)


class EvidenceEdges(Base):
    def audit_output(self):
        self.assertEqual(self.main(["audit"], FakeCli(self.home, [row(DEAD_ORG)])), 0)
        return self.stdout.getvalue()

    def test_no_connected_dev_hub_is_said_out_loud(self):
        (self.home / ".sfdx" / (HUB + ".json")).unlink()
        self.add_auth("rep@x.invalid", DEAD_ORG)
        self.assertIn("NO CONNECTED DEV HUB", self.audit_output())

    def test_a_connected_dev_hub_gets_no_such_warning(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        self.assertNotIn("NO CONNECTED DEV HUB", self.audit_output())

    def test_an_index_for_a_live_or_unknown_org_stays(self):
        for org in (LIVE_ORG, NO_ROW_ORG):
            (self.home / ".sfdx" / (org + "MAA.json")).write_text("{}")
        plan = self.plan(FakeCli(self.home, [row(LIVE_ORG, "Active", "2026-12-01")]))
        self.assertEqual(plan["remove"]["indexes"], [])
        self.assertEqual(plan["preserved"]["indexes"], 2)

    def test_a_symlinked_index_is_not_listed(self):
        target = self.home / "elsewhere.json"
        target.write_text("{}")
        (self.home / ".sfdx" / (DEAD_ORG + "MAA.json")).symlink_to(target)
        self.assertEqual(self.plan(FakeCli(self.home, [row(DEAD_ORG)]))["remove"]["indexes"], [])

    def test_a_symlinked_tracking_dir_is_reported_and_not_listed(self):
        target = self.home / "elsewhere"
        target.mkdir()
        link = self.project / ".sf" / "orgs" / (DEAD_ORG + "MAA")
        link.symlink_to(target)
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(plan["remove"]["tracking"], [])
        self.assertEqual(plan["report"]["symlinks_left_alone"], [str(link)])

    def test_a_tracking_name_with_a_trailing_newline_is_not_org_state(self):
        odd = self.project / ".sf" / "orgs" / (DEAD_ORG + "MAA\n")
        odd.mkdir()
        self.assertEqual(self.plan(FakeCli(self.home, [row(DEAD_ORG)]))["remove"]["tracking"], [])


class Usage(Base):
    def test_refuses_to_run_outside_a_project_root(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = oc.main(["audit"], FakeCli(self.home), self.home, self.home, TODAY, env={})
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

    def test_a_linked_home_state_folder_is_still_read(self):
        """In the Docker image ~/.sfdx links to the state volume."""
        volume = self.home.parent / "volume-sfdx"
        (self.home / ".sfdx").rename(volume)
        (self.home / ".sfdx").symlink_to(volume)
        self.add_auth("rep@x.invalid", DEAD_ORG)
        self.assertEqual(self.plan(FakeCli(self.home, [row(DEAD_ORG)]))["remove"]["logout"], ["rep@x.invalid"])


class FileResponses(Base):
    """`<project>/.sf[dx]/fileResponses/<orgId>`: response logs keyed by org, with no login."""

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
        self.assertEqual((plan["remove"]["file_responses"], plan["preserved"]["file_responses"]), ([], 1))

    def test_a_name_that_is_not_an_org_id_is_reported_and_never_planned(self):
        odd = self.project / ".sfdx" / "fileResponses" / "not-an-org"
        odd.mkdir(parents=True)
        stray = self.project / ".sfdx" / "fileResponses" / (DEAD_ORG + "MAA.json")
        stray.write_text("{}")
        plain = self.project / ".sfdx" / "fileResponses" / (DEAD_ORG + "MAB")
        plain.write_text("{}")  # an org-ID name, but a file rather than a directory
        plan = self.plan(FakeCli(self.home, [row(DEAD_ORG)]))
        self.assertEqual(plan["remove"]["file_responses"], [])
        self.assertEqual(sorted(plan["report"]["unrecognized_file_responses"]),
                         sorted([str(odd), str(stray), str(plain)]))

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
                         sorted([str(entry / (DEAD_ORG + "MAA")), str(self.project / ".sf" / "fileResponses")]))

    def test_a_symlinked_state_folder_or_parent_is_never_followed(self):
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
        self.assertEqual((plan["remove"]["tracking"], plan["remove"]["file_responses"]), ([], []))
        self.assertEqual(sorted(plan["report"]["symlinks_left_alone"]),
                         sorted([str(self.project / ".sfdx"), str(self.project / ".sf" / "orgs"),
                                 str(self.project / ".sf" / "fileResponses")]))

    def test_a_folder_swapped_for_a_link_after_the_audit_is_refused_at_the_move(self):
        outside = self.home / "outside"
        (outside / (DEAD_ORG + "MAA")).mkdir(parents=True)
        linked = self.project / ".sf" / "linked"
        self.assertEqual(oc.move_to_quarantine(FakeCli(self.home), linked / (DEAD_ORG + "MAA"), [linked],
                                               self.quarantine, self.project), "missing")
        linked.symlink_to(outside)
        self.assertEqual(oc.move_to_quarantine(FakeCli(self.home), linked / (DEAD_ORG + "MAA"), [linked],
                                               self.quarantine, self.project), "symlink")
        self.assertTrue((outside / (DEAD_ORG + "MAA")).exists())

    def test_a_state_folder_swapped_for_a_link_after_the_audit_is_refused_at_the_move(self):
        outside = self.home / "outside"
        (outside / "orgs" / (DEAD_ORG + "MAA")).mkdir(parents=True)
        (self.project / ".sf" / "orgs").rmdir()
        (self.project / ".sf").rmdir()
        (self.project / ".sf").symlink_to(outside)
        self.assertEqual(oc.move_to_quarantine(FakeCli(self.home), self.project / ".sf" / "orgs" / (DEAD_ORG + "MAA"),
                                               [self.project / ".sf" / "orgs"], self.quarantine, self.project), "symlink")

    def test_a_quarantine_that_refuses_files_stops_before_any_logout_for_responses_alone(self):
        self.add_auth("rep@x.invalid", DEAD_ORG)
        dead = self.responses()
        cli = FakeCli(self.home, [row(DEAD_ORG)])
        plan_file = self.audit_file(cli)
        with mock.patch.object(oc.os, "rename", side_effect=PermissionError(1, "Not permitted")):
            self.assertEqual(self.apply(cli, plan_file), 1)
        self.assertEqual(Apply.logouts(cli), [])
        self.assertTrue(dead.exists())

    def test_the_directory_is_not_reported_as_unclassified(self):
        self.responses()
        self.assertEqual(self.plan(FakeCli(self.home))["report"]["unclassified_files"], [])

    def test_apply_moves_them_to_the_quarantine_and_a_re_audit_is_empty(self):
        for state in (".sf", ".sfdx"):
            dead = self.responses(state=state)
            cli = FakeCli(self.home, [row(DEAD_ORG)])
            self.assertEqual(self.audit_then_apply(cli), 0)
            self.assertFalse(dead.exists())
            self.assertIn("Residual files moved", self.stdout.getvalue())
            self.assertEqual(self.plan(cli)["remove"]["file_responses"], [])
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
        self.assertEqual(self.audit_then_apply(FakeCli(self.home, [row(DEAD_ORG)], fail_logout={"rep@x.invalid"})), 1)
        self.assertTrue(dead.exists())


if __name__ == "__main__":
    unittest.main()
