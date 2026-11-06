#!/usr/bin/env python3
"""Evidence-gated audit and cleanup of local CCI and sf org state.

Procedure and rationale: .cursor/skills/cci-orchestration/org-cleanup.md

  python scripts/ai/org_cleanup.py audit --out <plan.json>   # local reads and hub queries
  python scripts/ai/org_cleanup.py apply --plan <plan.json>  # acts on that reviewed plan

An entry is removed only when a Dev Hub record says its org is gone. No row, a failed
query, or conflicting evidence all preserve it. `audit` builds its inventory from local
files rather than `sf org list`, which silently omits secondary users, and omits every
scratch org when a hub is unreachable.

`apply` re-derives the plan and stops if it differs from the reviewed one. It runs targeted
`sf org logout` and single-alias `sf alias unset`, and moves residual files to a quarantine
folder instead of deleting them. It never runs `cci org prune`, `cci org remove`, `cci org
default`, or any remote delete: `audit` predicts what prune would do, and acting on that is
the user's call.

Credentials are never printed or written: auth files are reduced to identity fields as soon
as they are parsed, and a file this tool does not recognize is reported without being opened.

Exit status: 0 success, 1 a step failed, 2 usage or wrong directory, 3 the plan drifted.
Stdlib only and Python 3.9-safe.
"""
import argparse
import datetime
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

ORG_ID = re.compile(r"^00D[0-9A-Za-z]{12}(?:[0-9A-Za-z]{3})?$")
BATCH = 50
REMOVABLE = ("deleted", "expired")
REMOVE_KEYS = ("logout", "aliases", "indexes", "tracking", "deploy_jobs", "defaults")

# Entries the CLIs own. Anything else in a state root is reported, unopened, for the user.
KNOWN_ENTRIES = {
    "alias.json", "config.json", "deploy-cache.json", "indexes", "key.json", "manifestCache",
    "orgs", "scratch-create-cache.json", "sfdx-config.json", "stash.json", "tools", "typings",
    "vscode-extensions-telemetry",
}
KNOWN_ENTRY_PATTERN = re.compile(r"^(sf|sfdx)(-[\d-]+)?\.log(\.\d+)?$")

# Run inside `cci shell`: names and flags only, and the same predicate `cci org prune` uses.
CCI_SNIPPET = """
import json
from cumulusci.core.config import ScratchOrgConfig
shapes = project_config.lookup("orgs__scratch", {})
orgs = []
for name in runtime.keychain.list_orgs():
    org = runtime.keychain.get_org(name)
    orgs.append(dict(name=name, shape=name in shapes, active=bool(org.active),
                     scratch=isinstance(org, ScratchOrgConfig), expired=bool(getattr(org, "expired", False)),
                     instantiated=bool(org.config.get("date_created")), default=bool(org.default),
                     alias=org.config.get("sfdx_alias") or ""))
print("ORG_CLEANUP_CCI " + json.dumps(orgs))
"""


def run_command(cmd):
    """Run one command, returning (exit code, stdout). Stderr may carry payloads: drop it."""
    try:
        done = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                              universal_newlines=True, timeout=300, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return 127, ""
    return done.returncode, done.stdout


def sf_json(run, *args):
    """Run an sf command with --json. Returns the parsed payload, or None if it failed."""
    code, out = run(["sf"] + list(args) + ["--json"])
    try:
        payload = json.loads(out)
    except ValueError:
        return None
    if code != 0 or payload.get("status") != 0:
        return None
    return payload


def read_json(path, default):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return default


def state_roots(home):
    return [home / ".sfdx", home / ".sf"]


def read_auth(home):
    """Identity fields from every local auth file. Token values never leave this function."""
    auth, unreadable = {}, []
    for root in state_roots(home):
        if not root.is_dir():
            continue
        for path in sorted(root.iterdir()):
            if "@" not in path.name or path.suffix != ".json" or path.is_symlink():
                continue
            data = read_json(path, None)
            if not isinstance(data, dict) or not data.get("orgId"):
                unreadable.append(path.name)
                continue
            username = data.get("username") or path.stem
            auth[username] = {
                "org": data["orgId"][:15],
                "is_hub": bool(data.get("isDevHub")),
                "is_sandbox": bool(data.get("isSandbox")),
                "refreshable": bool(data.get("refreshToken")),
            }
    return auth, unreadable


def read_indexes(home):
    found = []
    for root in state_roots(home):
        if root.is_dir():
            found += [p for p in sorted(root.iterdir())
                      if p.suffix == ".json" and ORG_ID.match(p.stem) and not p.is_symlink()]
    return found


def read_tracking(project):
    """Tracking directories: `.sf/orgs/<orgId>` and legacy `.sfdx/orgs/<username>`."""
    found, symlinks = [], []
    for base in (project / ".sf" / "orgs", project / ".sfdx" / "orgs"):
        if not base.is_dir():
            continue
        for path in sorted(base.iterdir()):
            (symlinks if path.is_symlink() else found).append(path)
    return found, symlinks


def read_unclassified(home, project):
    """Name, size and mode of what the CLIs do not own. These files are never opened."""
    found = []
    for root in state_roots(home) + [project / ".sf", project / ".sfdx"]:
        if not root.is_dir():
            continue
        for path in sorted(root.iterdir()):
            if (path.name in KNOWN_ENTRIES or KNOWN_ENTRY_PATTERN.match(path.name)
                    or "@" in path.name or ORG_ID.match(path.stem)):
                continue
            info = path.lstat()
            found.append({"path": str(path), "size": info.st_size,
                          "mode": stat.filemode(info.st_mode)})
    return found


def query_hubs(run, hubs, field, values):
    """ScratchOrgInfo rows per value across every hub, plus the hubs that gave no answer."""
    rows, failed = {}, []
    safe = sorted(v for v in values if "'" not in v and "\\" not in v)
    for hub in hubs:
        for start in range(0, len(safe), BATCH):
            quoted = "','".join(safe[start:start + BATCH])
            soql = ("SELECT ScratchOrg, SignupUsername, Status, ExpirationDate FROM ScratchOrgInfo "
                    "WHERE {} IN ('{}')".format(field, quoted))
            payload = sf_json(run, "data", "query", "--target-org", hub, "--query", soql)
            result = (payload or {}).get("result") or {}
            if payload is None or result.get("done") is False:
                failed.append(hub)
                continue
            for record in result.get("records") or []:
                rows.setdefault(record[field], []).append(record)
    return rows, sorted(set(failed))


def classify(rows, today):
    """Lifecycle class from hub rows: deleted, expired, active, conflict, or unknown."""
    if not rows:
        return "unknown"
    statuses = {row.get("Status") for row in rows}
    if len(statuses) > 1:
        return "conflict"
    status = statuses.pop()
    if status == "Deleted":
        return "deleted"
    past = any(row.get("ExpirationDate") and row["ExpirationDate"] < today for row in rows)
    if status == "Active":
        return "conflict" if past else "active"
    return "expired" if past else "unknown"


def read_cci(run):
    code, out = run(["cci", "shell", "--python", CCI_SNIPPET])
    for line in out.splitlines() if code == 0 else []:
        if line.startswith("ORG_CLEANUP_CCI "):
            return json.loads(line.split(" ", 1)[1])
    return None


def predict_prune(orgs, resolve, user_class):
    """What `cci org prune` would do, and whether any of it touches a live org."""
    if orgs is None:
        return {"available": False}
    gone = [o for o in orgs if not o["shape"] and not o["active"] and o["scratch"]]
    live = [o["name"] for o in gone if o["instantiated"]
            and user_class(resolve(o["alias"])) == "active"]
    return {
        "available": True,
        "would_remove_expired": sorted(o["name"] for o in gone if o["instantiated"]),
        "would_remove_never_instantiated": sorted(o["name"] for o in gone if not o["instantiated"]),
        "would_remove_but_active_on_hub": sorted(live),
        "expired_shape_instances_it_skips": sorted(o["name"] for o in orgs
                                                   if o["shape"] and o["expired"]),
        "default": next((o["name"] for o in orgs if o["default"]), None),
    }


def config_targets(home, project):
    """Default-org values per scope, from both config layouts."""
    files = {"global": [home / ".sf" / "config.json", home / ".sfdx" / "sfdx-config.json"],
             "local": [project / ".sf" / "config.json", project / ".sfdx" / "sfdx-config.json"]}
    targets = {}
    for scope, paths in files.items():
        values = set()
        for path in paths:
            data = read_json(path, {})
            if isinstance(data, dict):
                values |= {data[k] for k in ("target-org", "defaultusername") if data.get(k)}
        targets[scope] = sorted(values)
    return targets


def build_plan(run, home, project, today):
    """Inventory plus hub evidence. Mutates nothing beyond what the CLIs themselves do."""
    auth, unreadable = read_auth(home)
    hubs = sorted(user for user, info in auth.items() if info["is_hub"])
    alias_payload = sf_json(run, "alias", "list")
    if alias_payload is None:
        raise RuntimeError("sf alias list failed")
    aliases = {row["alias"]: row.get("value") or "" for row in alias_payload.get("result") or []}

    def resolve(name):
        seen = set()
        while name in aliases and name not in seen:
            seen.add(name)
            name = aliases[name]
        return name

    indexes = read_indexes(home)
    tracking, symlinks = read_tracking(project)
    deploy_cache = read_json(home / ".sf" / "deploy-cache.json", {})
    deploy_cache = deploy_cache if isinstance(deploy_cache, dict) else {}
    deploy_targets = {job: resolve(entry.get("target-org") or "")
                      for job, entry in deploy_cache.items() if isinstance(entry, dict)}

    org_ids = {info["org"] for info in auth.values()} | {p.stem[:15] for p in indexes}
    org_ids |= {p.name[:15] for p in tracking if ORG_ID.match(p.name)}
    id_rows, id_failed = query_hubs(run, hubs, "ScratchOrg", org_ids)

    # State with a username and no local auth has no org ID to check, so ask by signup username.
    orphans = {u for u in map(resolve, aliases) if "@" in u and u not in auth}
    orphans |= {p.name for p in tracking if "@" in p.name and p.name not in auth}
    orphans |= {u for u in deploy_targets.values() if "@" in u and u not in auth}
    user_rows, user_failed = query_hubs(run, hubs, "SignupUsername", orphans)

    def org_class(org):
        return classify(id_rows.get(org[:15], []), today)

    def user_class(username):
        if username in auth:
            return org_class(auth[username]["org"])
        return classify(user_rows.get(username, []), today)

    stale_users = {u for u, info in auth.items() if org_class(info["org"]) in REMOVABLE
                   and not info["is_hub"] and not info["is_sandbox"]}

    def stale(username):
        return username in stale_users or (username not in auth and user_class(username) in REMOVABLE)

    remove = {
        "logout": sorted(stale_users),
        # Logout already clears aliases of the users it removes, so list only the orphans.
        "aliases": sorted(a for a in aliases if resolve(a) not in auth and stale(resolve(a))),
        "indexes": sorted(str(p) for p in indexes if org_class(p.stem) in REMOVABLE),
        "tracking": sorted(str(p) for p in tracking
                           if (ORG_ID.match(p.name) and org_class(p.name) in REMOVABLE)
                           or ("@" in p.name and stale(p.name))),
        "deploy_jobs": sorted(job for job, user in deploy_targets.items() if user and stale(user)),
        "defaults": sorted(scope for scope, values in config_targets(home, project).items()
                           if any(stale(resolve(v)) for v in values)),
    }
    removing = {str(p) for k in ("indexes", "tracking") for p in remove[k]}
    conflict = sorted(u for u in auth if org_class(auth[u]["org"]) == "conflict")
    return {
        "schema": 1,
        "today": today,
        "project": str(project),
        "hubs": hubs,
        "hub_failures": sorted(set(id_failed + user_failed)),
        "remove": remove,
        "preserved": {
            "logins": len(auth) - len(stale_users),
            "aliases": len(aliases) - len(remove["aliases"]),
            "indexes": sum(str(p) not in removing for p in indexes),
            "tracking": sum(str(p) not in removing for p in tracking),
            "deploy_jobs": len(deploy_targets) - len(remove["deploy_jobs"]),
        },
        "report": {
            "conflicting_evidence": conflict,
            "logins_with_no_refresh_token": sorted(
                u for u, info in auth.items() if not info["refreshable"] and u not in stale_users),
            "unreadable_auth_files": unreadable,
            "symlinks_left_alone": [str(p) for p in symlinks],
            "unclassified_files": read_unclassified(home, project),
        },
        "prune_prediction": predict_prune(read_cci(run), resolve, user_class),
    }


def check_logins(run, home):
    """Read-only query per login. A refresh can rewrite an auth file, so this is opt-in."""
    failed = []
    for username in sorted(read_auth(home)[0]):
        if sf_json(run, "data", "query", "--target-org", username,
                   "--query", "SELECT Id FROM Organization") is None:
            failed.append(username)
    return failed


def default_quarantine(home, today):
    trash = home / ".Trash"
    if trash.is_dir():
        return trash / "rlm-org-cleanup-{}".format(today)
    return home / ".rlm-org-cleanup-quarantine" / today


def move_to_quarantine(run, path, roots, quarantine, project):
    """Move one allowlisted path, or return why it was refused."""
    if not os.path.lexists(str(path)):
        return "missing"
    if path.is_symlink():
        return "symlink"
    if not any(path.parent == root for root in roots):
        return "outside the expected state roots"
    if project in path.parents:
        code, out = run(["git", "-C", str(project), "ls-files", "--", str(path)])
        if code != 0 or out.strip():
            return "tracked by git, or git could not say"
    dest = quarantine / path.parent.name / path.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(str(dest)):
        return "already in quarantine"
    shutil.move(str(path), str(dest))
    return None


def remove_deploy_jobs(run, jobs, home, quarantine, project, failures):
    """Drop named cache entries atomically, keeping mode and every other key."""
    path = home / ".sf" / "deploy-cache.json"
    cache = read_json(path, None)
    if not isinstance(cache, dict):
        failures.append(("deploy-cache", "unreadable"))
        return 0
    removed = [job for job in jobs if job in cache]
    for job in removed:
        del cache[job]
        manifest = home / ".sf" / "manifestCache" / (job + ".xml")
        if os.path.lexists(str(manifest)):
            why = move_to_quarantine(run, manifest, [manifest.parent], quarantine, project)
            if why:
                failures.append((str(manifest), why))
    if removed:
        mode = stat.S_IMODE(path.stat().st_mode)
        handle, temp = tempfile.mkstemp(dir=str(path.parent), prefix=".deploy-cache.")
        os.fchmod(handle, mode)
        with os.fdopen(handle, "w") as out:
            json.dump(cache, out, indent=4)
        os.replace(temp, str(path))
    return len(removed)


def apply_plan(run, plan, home, project, quarantine):
    """Carry out a reviewed plan. Per-item failures are collected, never hidden."""
    remove, failures = plan["remove"], []
    done = dict.fromkeys(REMOVE_KEYS, 0)
    auth = read_auth(home)[0]
    failed_orgs, failed_users = set(), set()

    for username in remove["logout"]:
        payload = sf_json(run, "org", "logout", "--target-org", username, "--no-prompt")
        if payload is None or username not in (payload.get("result") or []):
            failures.append((username, "logout failed"))
            failed_users.add(username)
            failed_orgs.add(auth.get(username, {}).get("org"))
        else:
            done["logout"] += 1

    # One alias per command: sf handles several in parallel, and a batch can fail partway.
    for alias in remove["aliases"]:
        payload = sf_json(run, "alias", "unset", alias)
        rows = (payload or {}).get("result") or [{}]
        if payload is None or not rows[0].get("success"):
            failures.append((alias, "alias unset failed"))
        else:
            done["aliases"] += 1

    # Logout normally clears these, so only unset what still points at a removed user.
    targets = config_targets(home, project)
    aliases = sf_json(run, "alias", "list")
    alias_map = {r["alias"]: r.get("value") for r in (aliases or {}).get("result") or []}
    gone = set(remove["logout"]) | set(remove["aliases"])
    for scope in remove["defaults"]:
        still_set = [v for v in targets.get(scope, [])
                     if v in gone or v not in alias_map and "@" in v and v not in read_auth(home)[0]]
        if not still_set:
            continue
        args = ["config", "unset", "target-org"] + (["--global"] if scope == "global" else [])
        if sf_json(run, *args) is None:
            failures.append((scope + " default", "config unset failed"))
        else:
            done["defaults"] += 1

    state = state_roots(home)
    for key, roots in (("indexes", state),
                       ("tracking", [project / ".sf" / "orgs", project / ".sfdx" / "orgs"])):
        for item in remove[key]:
            path = Path(item)
            if (path.stem[:15] in failed_orgs or path.name[:15] in failed_orgs
                    or path.name in failed_users):
                failures.append((item, "skipped because its logout failed"))
                continue
            why = move_to_quarantine(run, path, roots, quarantine, project)
            if why:
                failures.append((item, why))
            else:
                done[key] += 1

    done["deploy_jobs"] = remove_deploy_jobs(run, remove["deploy_jobs"], home, quarantine,
                                             project, failures)
    return done, failures


def print_plan(plan):
    print("Dev Hubs: {}".format(len(plan["hubs"])))
    if plan["hub_failures"]:
        print("HUBS THAT DID NOT ANSWER: {}".format(plan["hub_failures"]))
        print("They gave no evidence, so this plan and the active-on-hub check may be incomplete.")
    print("\nWould remove:")
    for key in REMOVE_KEYS:
        items = plan["remove"][key]
        print("  {}: {}".format(key, len(items)))
        for item in items:
            print("    {}".format(item))
    print("\nPreserved: {}".format(plan["preserved"]))
    print("\nFor the user to review:")
    for key, value in plan["report"].items():
        if value:
            print("  {}: {}".format(key, json.dumps(value)))
    print("\ncci org prune prediction (never run by this tool):")
    for key, value in plan["prune_prediction"].items():
        print("  {}: {}".format(key, value))


def in_project_root(project):
    return (project / "cumulusci.yml").is_file() and (project / "sfdx-project.json").is_file()


def main(argv=None, run=run_command, home=None, project=None, today=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    commands = parser.add_subparsers(dest="command", required=True)
    audit = commands.add_parser("audit", help="classify local state; removes nothing")
    audit.add_argument("--out", help="write the plan as JSON, for review and apply")
    audit.add_argument("--check-logins", action="store_true",
                       help="also query each login; a token refresh can rewrite its auth file")
    do = commands.add_parser("apply", help="carry out a reviewed plan")
    do.add_argument("--plan", required=True)
    do.add_argument("--quarantine", help="where to move residual files")
    args = parser.parse_args(argv)

    home = home or Path.home()
    project = project or Path.cwd()
    today = today or datetime.date.today().isoformat()
    if not in_project_root(project):
        print("Run this from the project root: cci and local sf config resolve the project "
              "from the working directory.", file=sys.stderr)
        return 2

    try:
        plan = build_plan(run, home, project, today)
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1

    if args.command == "audit":
        print_plan(plan)
        if args.out:
            Path(args.out).write_text(json.dumps(plan, indent=1) + "\n")
            os.chmod(args.out, 0o600)
        if args.check_logins:
            failed = check_logins(run, home)
            print("\nLogins that did not answer a query: {}".format(failed or "none"))
        return 0

    reviewed = read_json(args.plan, None)
    if not isinstance(reviewed, dict) or reviewed.get("remove") != plan["remove"]:
        print("The plan differs from the current state. Review a fresh audit before applying.",
              file=sys.stderr)
        return 3
    quarantine = Path(args.quarantine) if args.quarantine else default_quarantine(home, today)
    done, failures = apply_plan(run, plan, home, project, quarantine)
    print("Done: {}".format(done))
    print("Residual files moved to: {}".format(quarantine))
    for item, why in failures:
        print("FAILED: {} ({})".format(item, why))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
