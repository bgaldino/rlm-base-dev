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
import errno
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
REMOVE_KEYS = ("logout", "aliases", "indexes", "tracking", "file_responses", "deploy_jobs",
               "defaults")

# Entries the CLIs own (`fileResponses` is handled as org-keyed state below). Anything else in a
# state root is reported, unopened, for the user.
KNOWN_ENTRIES = {
    "alias.json", "config.json", "deploy-cache.json", "fileResponses", "indexes", "key.json",
    "manifestCache", "orgs", "scratch-create-cache.json", "sfdx-config.json", "stash.json",
    "tools", "typings", "vscode-extensions-telemetry",
}
KNOWN_ENTRY_PATTERN = re.compile(r"^(sf|sfdx)(-[\d-]+)?\.log(\.\d+)?$")

CCI_KEYS = {"name", "shape", "active", "scratch", "expired", "instantiated", "default", "alias"}

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


def linked_ancestor(base):
    """The symlink at `base` or at the `.sf`/`.sfdx` folder above it, if any. Never followed."""
    for path in (base, base.parent):
        if path.is_symlink():
            return path
    return None


def read_tracking(project):
    """Tracking directories: `.sf/orgs/<orgId>` and legacy `.sfdx/orgs/<username>`."""
    found, symlinks = [], []
    for base in (project / ".sf" / "orgs", project / ".sfdx" / "orgs"):
        link = linked_ancestor(base)
        if link:
            symlinks.append(link)
            continue
        if not base.is_dir():
            continue
        for path in sorted(base.iterdir()):
            (symlinks if path.is_symlink() else found).append(path)
    return found, symlinks


def read_file_responses(project):
    """Deploy/retrieve response logs, `<project>/.sf[dx]/fileResponses/<orgId>`.

    Returns the org-ID directories, the names that are not org IDs, and symlinks (left alone).
    """
    found, unrecognized, symlinks = [], [], []
    for state in (project / ".sf", project / ".sfdx"):
        base = state / "fileResponses"
        link = linked_ancestor(base)
        if link:
            symlinks.append(link)
        elif base.is_dir():
            for path in sorted(base.iterdir()):
                if path.is_symlink():
                    symlinks.append(path)
                elif path.is_dir() and ORG_ID.match(path.name):
                    found.append(path)
                else:
                    unrecognized.append(path)
    return found, unrecognized, symlinks


def read_unclassified(home, project):
    """Name, size and mode of what the CLIs do not own. These files are never opened."""
    found = []
    home_roots = state_roots(home)
    for root in home_roots + [project / ".sf", project / ".sfdx"]:
        if not root.is_dir():
            continue
        for path in sorted(root.iterdir()):
            # Skip only what read_auth and read_indexes consume, and they read the home roots only:
            # a regular .json file there. A symlink, a backup such as `user@x.json.bak`, or any auth
            # or index file inside the project is not consumed, so it is reported here.
            consumed = (root in home_roots and path.suffix == ".json" and not path.is_symlink()
                        and ("@" in path.name or ORG_ID.match(path.stem)))
            if path.name in KNOWN_ENTRIES or KNOWN_ENTRY_PATTERN.match(path.name) or consumed:
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
            try:
                orgs = json.loads(line.split(" ", 1)[1])
            except ValueError:
                return None
            # Anything but the shape the snippet emits is not a prediction, rather than a crash.
            ok = isinstance(orgs, list) and all(isinstance(o, dict) and CCI_KEYS <= o.keys()
                                                for o in orgs)
            return orgs if ok else None
    return None


def predict_prune(orgs, resolve, user_class):
    """What `cci org prune` would do, and whether any of it touches a live org."""
    if orgs is None:
        return {"available": False}
    gone = [o for o in orgs if not o["shape"] and not o["active"] and o["scratch"]]
    # "conflict" is a hub row that is Active past its date, or rows that disagree: possibly live.
    live = [o["name"] for o in gone if o["instantiated"]
            and user_class(resolve(o["alias"])) in ("active", "conflict")]
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


def follow_aliases(aliases, name):
    """What a name ends at, following alias to alias. A cycle ends at one of its own members."""
    seen = set()
    while name in aliases and name not in seen:
        seen.add(name)
        name = aliases[name]
    return name


def build_plan(run, home, project, today):
    """Inventory plus hub evidence. Mutates nothing beyond what the CLIs themselves do."""
    auth, unreadable = read_auth(home)
    hubs = sorted(user for user, info in auth.items() if info["is_hub"])
    alias_payload = sf_json(run, "alias", "list")
    if alias_payload is None:
        raise RuntimeError("sf alias list failed")
    aliases = {row["alias"]: row.get("value") or "" for row in alias_payload.get("result") or []}

    def resolve(name):
        return follow_aliases(aliases, name)

    indexes = read_indexes(home)
    tracking, symlinks = read_tracking(project)
    responses, unrecognized_responses, response_symlinks = read_file_responses(project)
    symlinks = list(dict.fromkeys(symlinks + response_symlinks))  # a linked .sfdx shows up in both
    deploy_cache = read_json(home / ".sf" / "deploy-cache.json", {})
    deploy_cache = deploy_cache if isinstance(deploy_cache, dict) else {}
    deploy_targets = {job: resolve(entry.get("target-org") or "")
                      for job, entry in deploy_cache.items() if isinstance(entry, dict)}

    org_ids = {info["org"] for info in auth.values()} | {p.stem[:15] for p in indexes}
    org_ids |= {p.name[:15] for p in tracking if ORG_ID.match(p.name)}
    org_ids |= {p.name[:15] for p in responses}
    id_rows, id_failed = query_hubs(run, hubs, "ScratchOrg", org_ids)

    # State with a username and no local auth has no org ID to check, so ask by signup username.
    orphans = {u for u in map(resolve, aliases) if "@" in u and u not in auth}
    orphans |= {p.name for p in tracking if "@" in p.name and p.name not in auth}
    orphans |= {u for u in deploy_targets.values() if "@" in u and u not in auth}
    orphans |= {resolve(v) for values in config_targets(home, project).values() for v in values
                if "@" in resolve(v) and resolve(v) not in auth}
    user_rows, user_failed = query_hubs(run, hubs, "SignupUsername", orphans)

    def org_class(org):
        return classify(id_rows.get(org[:15], []), today)

    def user_class(username):
        if username in auth:
            return org_class(auth[username]["org"])
        # A signup username can be reused by a later org, which may sit on the hub that failed.
        return "unknown" if user_failed else classify(user_rows.get(username, []), today)

    stale_users = {u for u, info in auth.items() if org_class(info["org"]) in REMOVABLE
                   and not info["is_hub"] and not info["is_sandbox"]}

    def stale(username):
        return username in stale_users or (username not in auth and user_class(username) in REMOVABLE)

    remove = {
        "logout": sorted(stale_users),
        # Logout clears only aliases whose value is exactly the user, so list the orphans and any
        # alias that reaches a removed user through another alias.
        "aliases": sorted(a for a in aliases if stale(resolve(a))
                          and (resolve(a) not in auth or aliases[a] != resolve(a))),
        "indexes": sorted(str(p) for p in indexes if org_class(p.stem) in REMOVABLE),
        "tracking": sorted(str(p) for p in tracking
                           if (ORG_ID.match(p.name) and org_class(p.name) in REMOVABLE)
                           or ("@" in p.name and stale(p.name))),
        "file_responses": sorted(str(p) for p in responses if org_class(p.name) in REMOVABLE),
        "deploy_jobs": sorted(job for job, user in deploy_targets.items()
                              if user and stale(user) and plain_job_id(job)),
        # `config unset target-org` clears the scope's key whatever it names, so a scope that also
        # holds a value that is not stale is reported, not unset.
        "defaults": sorted(scope for scope, values in config_targets(home, project).items()
                           if any(stale(resolve(v)) for v in values)
                           and all(stale(resolve(v)) for v in values)),
    }
    removing = {str(p) for k in ("indexes", "tracking", "file_responses") for p in remove[k]}
    conflict = sorted(u for u in auth if org_class(auth[u]["org"]) == "conflict")
    return {
        "schema": 1,
        "today": today,
        "project": str(project),
        "hubs": hubs,
        "hub_failures": sorted(set(id_failed + user_failed)),
        "remove": remove,
        # Resolved now: a logout removes the alias that a later step would need to resolve these.
        "targets": {
            "aliases": {a: resolve(a) for a in remove["aliases"]},
            "deploy_jobs": {job: deploy_targets[job] for job in remove["deploy_jobs"]},
        },
        "preserved": {
            "logins": len(auth) - len(stale_users),
            # Not len - listed: logout also clears direct aliases, which are never listed.
            "aliases": sum(not stale(resolve(a)) for a in aliases),
            "indexes": sum(str(p) not in removing for p in indexes),
            "tracking": sum(str(p) not in removing for p in tracking),
            "file_responses": sum(str(p) not in removing for p in responses),
            "deploy_jobs": len(deploy_targets) - len(remove["deploy_jobs"]),
        },
        "report": {
            "conflicting_evidence": conflict,
            "logins_with_no_refresh_token": sorted(
                u for u, info in auth.items() if not info["refreshable"] and u not in stale_users),
            "unreadable_auth_files": unreadable,
            "symlinks_left_alone": [str(p) for p in symlinks],
            "unrecognized_file_responses": [str(p) for p in unrecognized_responses],
            # A key that is not a plain file name has no manifest to look for, so it is never planned.
            "unsafe_deploy_cache_keys": sorted(j for j in deploy_targets if not plain_job_id(j)),
            "unclassified_files": read_unclassified(home, project),
            # Lead to no username, so no hub row can ever put them on the plan.
            "dangling_aliases": sorted(a for a in aliases if "@" not in resolve(a)),
            "mixed_defaults": sorted(scope for scope, values in config_targets(home, project).items()
                                     if any(stale(resolve(v)) for v in values)
                                     and not all(stale(resolve(v)) for v in values)),
            "dangling_defaults": sorted(scope for scope, values in config_targets(home, project).items()
                                        if any("@" not in resolve(v) for v in values)),
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
    """The user's Trash, or else beside the real CLI state.

    A container's home goes with the container, and ~/.sf links to the volume that outlives it.
    """
    trash = home / ".Trash"
    if trash.is_dir():
        return trash / "rlm-org-cleanup-{}".format(today)
    state = Path(os.path.realpath(str(home / ".sf"))).parent
    return state / ".rlm-org-cleanup-quarantine" / today


def free_name(path):
    """Return path, or path with a number added if something already has that name.

    What is there stays: another project's item, or an earlier attempt's copy. After a failed
    delete across volumes that copy can be the only complete one, so it is never reused or removed.
    """
    candidate, number = path, 1
    while os.path.lexists(str(candidate)):
        candidate = path.with_name("{}.{}".format(path.name, number))
        number += 1
    return candidate


def move_path(source, dest):
    """Rename, copying only across volumes.

    shutil.move falls back to copy-then-delete on any rename error, so limiting it to a real
    cross-volume move keeps a refused rename from leaving a second copy behind. Across volumes it
    still can: a failed copy leaves a partial copy and an intact source, and a failed delete leaves
    a complete copy and a partial source.
    """
    try:
        os.rename(source, dest)
    except OSError as error:
        if error.errno != errno.EXDEV:
            raise
        shutil.move(source, dest)


def check_quarantine(quarantine, home):
    """Move a temp file in and remove it, returning why that failed, or None if it worked.

    Creating the folder is not proof: macOS can allow a mkdir in ~/.Trash while refusing to list
    it. This runs before the first logout, because a logout cannot be restored.
    """
    created, temp = [], None
    try:
        # Inside the try: before Python 3.14, exists() raises on a parent it cannot search.
        created = [p for p in [quarantine] + list(quarantine.parents) if not p.exists()]
        handle, temp = tempfile.mkstemp(dir=str(home), prefix=".org-cleanup-probe-")
        os.close(handle)
        quarantine.mkdir(parents=True, exist_ok=True)
        dest = quarantine / os.path.basename(temp)
        move_path(temp, str(dest))
        os.remove(str(dest))
        return None
    except OSError as error:
        return error.strerror or str(error)
    finally:
        if temp and os.path.lexists(temp):
            os.remove(temp)
        for path in created:  # deepest first; a folder that still holds anything stays
            try:
                os.rmdir(str(path))
            except OSError:
                break


def move_to_quarantine(run, path, roots, quarantine, project):
    """Move one allowlisted path, or return why it was refused."""
    if not os.path.lexists(str(path)):
        return "missing"
    if path.is_symlink():
        return "symlink"
    if not any(path.parent == root for root in roots):
        return "outside the expected state roots"
    if project in path.parents and linked_ancestor(path.parent):
        return "symlink"
    if project in path.parents:
        code, out = run(["git", "-C", str(project), "ls-files", "--", str(path)])
        if code != 0 or out.strip():
            return "tracked by git, or git could not say"
    dest = quarantine / path.parent.name / path.name
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        move_path(str(path), str(free_name(dest)))
    except OSError as error:
        return "could not move: {}".format(error.strerror or str(error)[:300])
    return None


def replace_json(path, data):
    """Rewrite a JSON file atomically, keeping its mode."""
    mode = stat.S_IMODE(path.stat().st_mode)
    handle, temp = tempfile.mkstemp(dir=str(path.parent), prefix=".deploy-cache.")
    try:
        with os.fdopen(handle, "w") as out:
            os.fchmod(out.fileno(), mode)
            json.dump(data, out, indent=4)
        os.replace(temp, str(path))
    except OSError:
        os.remove(temp)
        raise


def plain_job_id(job):
    return bool(job) and os.path.basename(job) == job and job not in (".", "..")


def remove_deploy_jobs(run, jobs, home, quarantine, project, failures):
    """Drop named cache entries, keeping every other key. Returns (entries, manifests moved).

    An entry stays if its manifest could not be moved. If the cache cannot be written, every entry
    stays and is reported, while manifests already moved remain in the quarantine.
    """
    if not jobs:  # no cache file is normal, and only a failure if something had to change in it
        return 0, 0
    path = home / ".sf" / "deploy-cache.json"
    cache = read_json(path, None)
    if not isinstance(cache, dict):
        failures.append(("deploy-cache", "unreadable"))
        return 0, 0
    removed, moved = 0, 0
    for job in jobs:
        if job not in cache:
            continue
        if not plain_job_id(job):
            failures.append((job, "cache key is not a plain job id; its manifest was not looked for"))
            continue
        manifest = home / ".sf" / "manifestCache" / (job + ".xml")
        if os.path.lexists(str(manifest)):
            why = move_to_quarantine(run, manifest, [home / ".sf" / "manifestCache"], quarantine, project)
            if why:
                failures.append((str(manifest), why))
                continue
            moved += 1
        del cache[job]
        removed += 1
    if removed:
        try:
            replace_json(path, cache)
        except OSError as error:
            failures.append((str(path), "could not write: {}".format(error.strerror or error)))
            return 0, moved
    return removed, moved


def apply_plan(run, plan, home, project, quarantine):
    """Carry out a reviewed plan. Per-item failures are collected, never hidden."""
    remove, targets, failures = plan["remove"], plan["targets"], []
    done = dict.fromkeys(REMOVE_KEYS, 0)
    auth = read_auth(home)[0]
    failed_orgs, failed_users = set(), set()

    def logout_failed_for(username):
        """True if this user's logout, or the logout of another user on its org, failed."""
        org = auth.get(username, {}).get("org")
        return username in failed_users or bool(org and org in failed_orgs)

    for username in remove["logout"]:
        payload = sf_json(run, "org", "logout", "--target-org", username, "--no-prompt")
        if payload is None or username not in (payload.get("result") or []):
            failures.append((username, "logout failed"))
            failed_users.add(username)
            failed_orgs.add(auth.get(username, {}).get("org"))
        else:
            done["logout"] += 1

    # sf clears a user's direct aliases before it can fail, so a chain may now lead nowhere, and a
    # later audit could not list it. Keep only a chain that still reaches a login.
    listed = sf_json(run, "alias", "list")
    current = {r["alias"]: r.get("value") or "" for r in (listed or {}).get("result") or []}
    logins = read_auth(home)[0]

    # One alias per command: sf handles several in parallel, and a batch can fail partway.
    kept_aliases = set()
    for alias in remove["aliases"]:
        if logout_failed_for(targets["aliases"][alias]) and (
                listed is None or follow_aliases(current, alias) in logins):
            failures.append((alias, "skipped because its logout failed"))
            kept_aliases.add(alias)
            continue
        payload = sf_json(run, "alias", "unset", alias)
        rows = (payload or {}).get("result") or [{}]
        if payload is None or not rows[0].get("success"):
            failures.append((alias, "alias unset failed"))
        else:
            done["aliases"] += 1

    # Logout normally clears these, so only unset what still points at a removed user.
    defaults = config_targets(home, project)
    aliases = sf_json(run, "alias", "list")
    alias_map = {r["alias"]: r.get("value") for r in (aliases or {}).get("result") or []}
    gone = (set(remove["logout"]) - failed_users) | (set(remove["aliases"]) - kept_aliases)
    for scope in remove["defaults"]:
        still_set = [v for v in defaults.get(scope, [])
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
                       ("tracking", [project / ".sf" / "orgs", project / ".sfdx" / "orgs"]),
                       ("file_responses", [project / ".sf" / "fileResponses",
                                           project / ".sfdx" / "fileResponses"])):
        for item in remove[key]:
            path = Path(item)
            if (path.stem[:15] in failed_orgs or path.name[:15] in failed_orgs
                    or logout_failed_for(path.name)):
                failures.append((item, "skipped because its logout failed"))
                continue
            why = move_to_quarantine(run, path, roots, quarantine, project)
            if why:
                failures.append((item, why))
            else:
                done[key] += 1

    jobs = []
    for job in remove["deploy_jobs"]:
        if logout_failed_for(targets["deploy_jobs"][job]):
            failures.append((job, "skipped because its logout failed"))
        else:
            jobs.append(job)
    done["deploy_jobs"], done["manifests"] = remove_deploy_jobs(run, jobs, home, quarantine,
                                                                project, failures)
    return done, failures


def print_plan(plan):
    print("Dev Hubs: {}".format(len(plan["hubs"])))
    if not plan["hubs"]:
        print("NO CONNECTED DEV HUB WAS FOUND. No hub was queried, so every entry is unknown and "
              "an empty plan below is not evidence that the state is clean.")
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


def write_private(path, text):
    """Write a file only the user can read, from the first byte, and never through a symlink."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(str(path), flags, 0o600)
    with os.fdopen(fd, "w") as handle:
        os.fchmod(handle.fileno(), 0o600)  # a file that already existed keeps its old mode
        handle.write(text)


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
            try:
                write_private(args.out, json.dumps(plan, indent=1) + "\n")
            except OSError as error:
                print("Could not write the plan to {}: {}".format(
                    args.out, error.strerror or str(error)[:300]), file=sys.stderr)
                return 1
        if args.check_logins:
            failed = check_logins(run, home)
            print("\nLogins that did not answer a query: {}".format(failed or "none"))
        return 0

    reviewed = read_json(args.plan, None)
    if (not isinstance(reviewed, dict) or reviewed.get("remove") != plan["remove"]
            or reviewed.get("project") != plan["project"]):
        print("The plan differs from the current state. Review a fresh audit before applying.",
              file=sys.stderr)
        return 3
    quarantine = Path(args.quarantine) if args.quarantine else default_quarantine(home, today)
    if any(plan["remove"][key] for key in ("indexes", "tracking", "file_responses", "deploy_jobs")):
        why = check_quarantine(quarantine, home)
        if why:
            print("Stopped before any logout; nothing was changed. Cannot move files into {}: {}. "
                  "Use --quarantine <dir> to choose another folder.".format(quarantine, why),
                  file=sys.stderr)
            return 1
    done, failures = apply_plan(run, plan, home, project, quarantine)
    print("Done: {}".format(done))
    if done["indexes"] or done["tracking"] or done["file_responses"] or done["manifests"]:
        print("Residual files moved to: {}".format(quarantine))
    for item, why in failures:
        print("FAILED: {} ({})".format(item, why))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
