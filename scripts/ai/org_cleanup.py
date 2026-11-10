#!/usr/bin/env python3
"""Evidence-gated audit and cleanup of local CCI and sf org state.

Procedure and rationale: .cursor/skills/cci-orchestration/org-cleanup.md

  python scripts/ai/org_cleanup.py audit --out <plan.json>   # local reads and hub queries
  python scripts/ai/org_cleanup.py apply --plan <plan.json>  # acts on that reviewed plan

An entry is removed only when a Dev Hub record says its org is gone. No row, a failed
query, or conflicting evidence all preserve it. `audit` builds its inventory from local
files rather than `sf org list`, which silently omits secondary users, and omits every
scratch org when a hub is unreachable.

Local state is judged the way sf reads it: logins only from ~/.sfdx, a name through at most
one alias, a name meaning a login whose file it opens (folded as a case- and normalization-
insensitive filesystem folds it, where that opens the same file), and each config scope as the merge of its two files. Every effect of a planned `sf org
logout` (the aliases and config keys sf clears with it) is predicted, printed, bound in the plan
and checked against the state before and after it runs. Anything that view cannot explain is preserved and reported, never
acted on.

`apply` re-derives the plan and stops if it differs from the reviewed one. It runs targeted
`sf org logout`, single-alias `sf alias unset` and `sf config unset target-org`, rewrites the
deploy cache without the removed entries, and moves residual files to a quarantine folder
instead of deleting them. It never runs `cci org prune`, `cci org remove`, `cci org
default`, or any remote delete: `audit` predicts what prune would do, and acting on that is
the user's call.

Credentials are never printed or written: auth files are reduced to identity fields as soon
as they are parsed, and a file this tool does not recognize is reported without being opened.

Exit status: 0 success, 1 a step failed, 2 usage, wrong directory, a plan path inside the project
or the CLI state, or a quarantine inside or holding one of them, 3 the plan drifted, 130 interrupted. An audit with hub failures still exits 0: it prints
them, and the plan it writes is incomplete, not wrong. Stdlib only and Python 3.9-safe.
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
import time
import unicodedata
from pathlib import Path

ORG_ID = re.compile(r"00D[0-9A-Za-z]{12}(?:[0-9A-Za-z]{3})?")  # always used with fullmatch
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")  # ScratchOrgInfo.ExpirationDate; always used with fullmatch
# JavaScript's whitespace (its \s and String.trim), spelled out: Python's \s and str.strip() cover
# a different set. The names sf lists as logins in ~/.sfdx (@salesforce/core orgAccessor.getFileRegex).
JS_SPACE_CHARS = ("\t\n\x0b\x0c\r \u00a0\u1680" + "".join(map(chr, range(0x2000, 0x200b)))
                  + "\u2028\u2029\u202f\u205f\u3000\ufeff")
SF_LOGIN_FILE = re.compile(r"[^.][^@]*@[^.]+(?:\.[^." + re.escape(JS_SPACE_CHARS) + r"]+)+\.json")
BATCH = 50
REMOVABLE = ("deleted", "expired")
REMOVE_KEYS = ("logout", "aliases", "indexes", "tracking", "file_responses", "deploy_jobs",
               "defaults")
DONE_KEYS = REMOVE_KEYS + ("manifests", "cleared_by_logout")
DOUBT = object()  # login_for: the name may mean a login the tool cannot read or tie to one org

# Entries the CLIs own (`fileResponses` is handled as org-keyed state below). Anything else in a
# state root is reported, unopened, for the user.
KNOWN_ENTRIES = {
    "alias.json", "config.json", "deploy-cache.json", "fileResponses", "indexes", "key.json",
    "manifestCache", "orgs", "scratch-create-cache.json", "sfdx-config.json", "stash.json",
    "tools", "typings", "vscode-extensions-telemetry",
}
KNOWN_ENTRY_PATTERN = re.compile(r"(sf|sfdx)(-[\d-]+)?\.log(\.\d+)?")  # always used with fullmatch
SANDBOX_FILE = re.compile(r"(00D.*?)\.sandbox\.json")  # sf's SandboxAccessor, in ~/.sfdx; used with fullmatch

# sf's legacy config keys and the keys they translate to (@salesforce/core config.js), and every key
# sf 2.157.8 registers (core's allowed properties plus bundled plugins' configMeta). sf cannot unset a
# key it does not know, and its next write turns one into org-instance-url, so a scope holding any
# other key is not modelled.
LEGACY_KEYS = {
    "defaultusername": "target-org", "defaultdevhubusername": "target-dev-hub",
    "instanceUrl": "org-instance-url", "apiVersion": "org-api-version",
    "isvDebuggerSid": "org-isv-debugger-sid", "isvDebuggerUrl": "org-isv-debugger-url",
    "disableTelemetry": "disable-telemetry", "customOrgMetadataTemplates": "org-custom-metadata-templates",
    "maxQueryLimit": "org-max-query-limit", "restDeploy": "org-metadata-rest-deploy",
}
CURRENT_KEYS = set(LEGACY_KEYS.values()) | {"org-capitalize-record-types"}
LOGOUT_SHORT_FLAGS = "acopu"  # `sf org logout`'s one-letter flags and aliases; oclif reads "-a..." as -a
ENV_DEFAULTS = ("SF_TARGET_ORG", "SFDX_DEFAULTUSERNAME", "SF_TARGET_DEV_HUB", "SFDX_DEFAULTDEVHUBUSERNAME")
FILE_KEYS = ("indexes", "tracking", "file_responses")  # plan keys whose items are moved to the quarantine
QUARANTINE_FOLDERS = ("orgs", "fileResponses", "manifestCache", ".sfdx")  # where those moves land

CCI_KEYS = {"name": str, "shape": bool, "active": bool, "scratch": bool, "expired": bool,
            "instantiated": bool, "org_id": str, "username": str}

# Run inside `cci shell`: names and flags only, and the same predicate `cci org prune` uses.
CCI_SNIPPET = """
import json
from cumulusci.core.config import ScratchOrgConfig
shapes = project_config.lookup("orgs__scratch", {})
keychain = runtime.keychain
orgs, flagged = [], []
for name in keychain.list_orgs():
    org = keychain.get_org(name)
    orgs.append(dict(name=name, shape=name in shapes, active=bool(org.active),
                     scratch=isinstance(org, ScratchOrgConfig), expired=bool(getattr(org, "expired", False)),
                     instantiated=bool(org.config.get("date_created")), org_id=str(org.config.get("org_id") or ""),
                     username=str(org.config.get("username") or "")))
    if org.default:
        flagged.append(name)
# CCI's default is DEFAULT_ORG.txt. Read it directly: get_default_org() can run sf config commands.
path = getattr(keychain, "_default_org_path", None)
default = path.read_text().strip() if path and path.exists() else (flagged[0] if flagged else "")
print("ORG_CLEANUP_CCI " + json.dumps(dict(orgs=orgs, default=default or None)))
"""


def run_command(cmd):
    """Run one command, returning (exit code, stdout). Stderr may carry payloads: drop it."""
    try:
        done = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding="utf-8",
                              errors="replace", timeout=300, check=False)
    except (OSError, ValueError, subprocess.TimeoutExpired):  # ValueError: a name argv cannot carry (NUL)
        return 127, ""
    return done.returncode, done.stdout


def sf_cannot_pass(text):
    """A lone surrogate reaches a child as raw bytes, which Node reads as U+FFFD, so sf would act on
    another name than the one the plan shows; a NUL cannot be passed at all."""
    return "\0" in text or any(0xD800 <= ord(c) <= 0xDFFF for c in text)


def redirects(aliases, name):
    """Whether sf resolves this name to another one: it follows an alias of that exact name, unless
    the alias's value is null or the name itself (`getUsername(n) ?? n`)."""
    value = aliases.get(name)
    return value is not None and value != name


def sf_json(run, *args, operands=()):
    """Run an sf command with --json. Returns the parsed payload, or None if it failed.

    `operands` follow `--`, so a name that starts with "-" is never read as a flag (`-ap` would be
    `--all --no-prompt` to `sf alias unset`). An argument sf would read as another name fails the
    command instead (see sf_cannot_pass)."""
    if any(sf_cannot_pass(arg) for arg in list(args) + list(operands)):
        return None
    code, out = run(["sf"] + list(args) + ["--json"] + (["--"] + list(operands) if operands else []))
    try:
        payload = json.loads(out)
    except ValueError:
        return None
    if code != 0 or not isinstance(payload, dict) or payload.get("status") != 0:
        return None
    return payload


def reason(error):
    """An OSError as short text. shutil.Error's own text lists every path, so it is capped."""
    return error.strerror or str(error)[:300] or type(error).__name__


def _refuse_constant(name):
    raise ValueError("{} is not JSON".format(name))


def _js_int(text):
    """A JSON integer as JavaScript reads it: past Python's digit limit, a float, as JS has."""
    try:
        return int(text)
    except ValueError:
        return float(text)


def read_json(path, default):
    """A JSON file read the way sf reads its own (@salesforce/kit parseJson on Node's UTF-8 text):
    bad bytes replaced, surrounding JavaScript whitespace (a byte-order mark too) trimmed, and
    NaN or Infinity refused. A file sf can read must not be one this tool cannot."""
    try:
        text = Path(path).read_bytes().decode("utf-8", "replace").strip(JS_SPACE_CHARS)
        return json.loads(text, parse_constant=_refuse_constant, parse_int=_js_int)
    except (OSError, ValueError, RecursionError):
        return default


def fold(name):
    """A name as a case- and normalization-insensitive filesystem (APFS) compares it: the canonical
    caseless form, as far as this Python's Unicode tables go."""
    return unicodedata.normalize("NFD", unicodedata.normalize("NFD", name).casefold())


def beyond_tables(name):
    """Whether a name holds characters this Python's Unicode tables do not assign, which the
    filesystem may fold all the same (Unicode never changes an assigned character's folding)."""
    return any(unicodedata.category(c) == "Cn" for c in name)


def lstat_or_none(path):
    """lstat, or None if nothing is there. Any other error is raised: from Python 3.14 pathlib's
    is_dir() and is_symlink() answer False instead, which would hide a folder it cannot search."""
    try:
        return os.lstat(str(path))
    except (FileNotFoundError, NotADirectoryError):
        return None


def opens_same_file(a, b):
    """Whether two spellings open one file, as they do on a case- and normalization-insensitive
    filesystem; False when either opens nothing."""
    try:
        return os.path.samefile(str(a), str(b))
    except (OSError, ValueError):
        return False


def linked_entry(info):
    """A symlink, or a regular file with another hard link: what sf reads, writes or removes there is
    also something another name holds, so the tool treats both kinds of link alike."""
    return stat.S_ISLNK(info.st_mode) or (stat.S_ISREG(info.st_mode) and info.st_nlink > 1)


def is_link(path):
    info = lstat_or_none(path)
    return bool(info) and linked_entry(info)


def is_dir(path, follow=False):
    """A directory (through a link only when follow is set), raising on anything but absence."""
    try:
        info = os.stat(str(path)) if follow else os.lstat(str(path))
    except (FileNotFoundError, NotADirectoryError):
        return False
    return stat.S_ISDIR(info.st_mode)


def is_regular_file(path):
    info = lstat_or_none(path)
    return bool(info) and stat.S_ISREG(info.st_mode)


def listing(root, follow=False):
    """Sorted entries of a directory, or [] if it is absent. A home root may be a link, as in the
    Docker image; a project root is listed only as itself."""
    return sorted(root.iterdir()) if is_dir(root, follow) else []


def login_files(home):
    """(stem, path) for each file in ~/.sfdx whose name matches sf's login pattern."""
    for path in listing(home / ".sfdx", follow=True):
        if SF_LOGIN_FILE.fullmatch(path.name):
            yield path.name[:-len(".json")], path


def read_logins(home):
    """sf's logins: the files in ~/.sfdx whose names match sf's own pattern. Token values never
    leave this function. Returns:

    - logins: the identity fields of each file sf reads as a login, keyed by file stem (the name sf
      opens). One sf reads through a link is marked `linked`: its identity counts (its org, a Dev
      Hub to query), but it is never logged out, since sf's logout would remove only the link.
    - unread: the stems sf may use that the tool cannot act on, each with the reason.
    - unreadable: the names of regular files that do not parse as a login.
    - blocks: why sf could not log anyone out now, or ''. sf lists every login by the username
      inside its file, so one non-empty file whose username is not text, or is empty, stops every
      logout.
    - listed: for each unread file that names one, the username sf lists it by (it is in doubt).
    - maybe_hubs: the unread names that may be a Dev Hub. That includes what sf cannot open now (a
      link to nothing or a loop, a folder): a link to a volume not mounted now may be a live hub.
    """
    logins, unread, unreadable, blocks, listed, maybe_hubs = {}, {}, [], [], {}, []
    for name, path in login_files(home):
        info = lstat_or_none(path)
        if info is None:
            continue
        linked, data = linked_entry(info), None
        if path.name.replace(".json", "", 1) != name:  # sf's parseUsername drops the first ".json"
            why = "sf reads this file as the login {}, so it cannot log it out by this name".format(
                path.name.replace(".json", "", 1))
        elif sf_cannot_pass(name):  # a byte that is not UTF-8
            why = "its name is not valid UTF-8, so sf reads it under another name"
        else:
            try:
                target = os.stat(str(path)) if linked else info
            except OSError:
                target = None
            if target is None or not stat.S_ISREG(target.st_mode):
                why = "its auth file is not a file sf can read now (a link to nothing, a loop, a folder)"
            else:
                data = read_json(path, None)
                username = data.get("username") if isinstance(data, dict) else None
                org = data.get("orgId") if isinstance(data, dict) else None
                if isinstance(data, dict) and data and not (isinstance(username, str) and username):
                    blocks.append("{} names no username, so sf cannot list its logins".format(path.name))
                if isinstance(org, str) and ORG_ID.fullmatch(org) and isinstance(username, str) and username:
                    logins[name] = {
                        "username": username,
                        "org": org[:15],
                        "linked": linked,
                        "is_hub": bool(data.get("isDevHub")),
                        "is_sandbox": bool(data.get("isSandbox")),
                        # A JWT login re-signs with its key, so only one with neither expires with its session.
                        "refreshable": bool(data.get("refreshToken") or data.get("privateKey")),
                    }
                    continue
                why = "its auth file does not parse, or names no org or username"
                if isinstance(username, str) and username:
                    listed[name] = username
                unreadable.append(path.name)
        unread[name] = why
        if not (isinstance(data, dict) and isinstance(data.get("username"), str) and not data.get("isDevHub")):
            maybe_hubs.append(name)
    # sf counts an org with a `<orgId>.sandbox.json` as a sandbox too (listAllAuthorizations).
    sandboxes = {m.group(1)[:15] for m in map(SANDBOX_FILE.fullmatch, (p.name for p in listing(home / ".sfdx", follow=True)))
                 if m}
    for info in logins.values():
        info["is_sandbox"] = info["is_sandbox"] or info["org"] in sandboxes
    return logins, unread, unreadable, "; ".join(blocks), listed, maybe_hubs


def read_aliases(payload):
    """The alias map from `sf alias list`. Every protection depends on it, so an answer of any
    other shape stops the run rather than reading as "no aliases"."""
    rows = payload.get("result")
    if not isinstance(rows, list) or not all(
            isinstance(row, dict) and isinstance(row.get("alias"), str) and "value" in row
            and (row["value"] is None or isinstance(row["value"], str)) for row in rows):
        raise RuntimeError("sf alias list returned an answer of an unexpected shape")
    return {row["alias"]: row["value"] for row in rows}  # None stays None: sf resolves it to the name


def read_alias_store(home):
    """`~/.sfdx/alias.json`, parsed as sf parses it (plain JSON.parse, then `orgs ?? {}`): {} when
    there is none, None when it is not in a shape sf writes ({"orgs": {alias: username}})."""
    path = home / ".sfdx" / "alias.json"
    if lstat_or_none(path) is None:
        return {}
    try:
        store = json.loads(path.read_bytes().decode("utf-8", "replace"), parse_constant=_refuse_constant,
                           parse_int=_js_int)
    except (OSError, ValueError, RecursionError):
        return None
    if not isinstance(store, dict) or set(store) - {"orgs"}:  # sf rewrites only orgs, dropping the rest
        return None
    orgs = store.get("orgs")
    if orgs is None:
        return {}
    return orgs if isinstance(orgs, dict) and all(v is None or isinstance(v, str) for v in orgs.values()) else None


def read_scope(sf_file, sfdx_file, linked, env):
    """One config scope as sf merges it, or the reason the tool cannot model it.

    sf merges the two files key by key (the newer file wins) and rewrites both on any write. The
    scope is modelled only when that merge is unambiguous, so no write can change a value the
    reviewer did not see. A file the tool will not write (a link) is still read: sf writes through
    it, so its values decide which logouts are refused.
    """
    merged, pairs, problems = {}, set(), []
    if linked:
        problems.append("{} is a symlink, so sf writes this config through it".format(linked))
    interop = str(env.get("SF_SFDX_INTEROPERABILITY", "true")).lower() in ("true", "1")
    for path, legacy in ((sf_file, False), (sfdx_file, True)):
        info = lstat_or_none(path)
        if info is None:
            continue
        if linked_entry(info):
            problems.append("{} is a link (symbolic or hard), so sf writes this config through it".format(path))
        elif not stat.S_ISREG(info.st_mode):
            problems.append("{} is not a regular file".format(path))
            continue
        data = read_json(path, None)
        if not isinstance(data, dict):
            problems.append("{} does not parse as a JSON object".format(path))
            continue
        if legacy and not interop:
            if data:
                problems.append("SF_SFDX_INTEROPERABILITY is off, so sf ignores {}".format(path))
            continue
        for key, value in data.items():
            if not legacy and key in LEGACY_KEYS:
                problems.append("{} holds the legacy key {}, which sf does not read there".format(path, key))
            elif key not in CURRENT_KEYS and not (legacy and key in LEGACY_KEYS):
                problems.append("{} holds {}, which is not among the keys sf and its bundled plugins define. A "
                                "plugin may define it; if nothing does, sf cannot unset it and its next write "
                                "turns it into org-instance-url".format(path, key))
            key = LEGACY_KEYS.get(key, key) if legacy else key
            if isinstance(value, str):
                pairs.add((key, value))
            if key in merged and merged[key] != value:
                problems.append("the two config files disagree on {}".format(key))
            merged[key] = value
    for key in ("target-org", "target-dev-hub"):
        if key in merged and not isinstance(merged[key], str):
            problems.append("{} is not text".format(key))
    # pairs: every text value either file gives a key, so a scope the tool cannot model still reports them.
    return {"merged": merged, "pairs": sorted(pairs), "why": "; ".join(problems)}


def config_scopes(home, project, env):
    linked = next((str(p) for p in (project / ".sf", project / ".sfdx") if is_link(p)), "")
    return {"global": read_scope(home / ".sf" / "config.json", home / ".sfdx" / "sfdx-config.json", "", env),
            "local": read_scope(project / ".sf" / "config.json", project / ".sfdx" / "sfdx-config.json",
                                linked, env)}


def read_indexes(home):
    """User indexes, `~/.sfdx/<orgId>.json`, where sf keeps them. A linked one (symbolic or hard) is
    left alone, so it is reported with the unclassified files rather than planned and then refused."""
    return [p for p in listing(home / ".sfdx", follow=True)
            if p.suffix == ".json" and ORG_ID.fullmatch(p.stem) and is_regular_file(p) and not is_link(p)]


def linked_ancestor(base):
    """The symlink at `base` or at the `.sf`/`.sfdx` folder above it, if any. Never followed."""
    for path in (base, base.parent):
        if is_link(path):
            return path
    return None


def read_project_dirs(project, name):
    """Entries of `<project>/.sf/<name>` and `.sfdx/<name>`, and the links among them (left alone)."""
    found, symlinks = [], []
    for base in (project / ".sf" / name, project / ".sfdx" / name):
        link = linked_ancestor(base)
        if link:
            symlinks.append(link)
            continue
        for path in listing(base):
            (symlinks if is_link(path) else found).append(path)
    return found, symlinks


def read_unclassified(home, project, consumed):
    """Name, size and mode of what the CLIs do not own. These files are never opened.

    `consumed` is exactly what read_logins and read_indexes took, so a link, a backup such as
    `user@x.json.bak`, and any auth-shaped file in ~/.sf or the project is reported.
    """
    found = []
    for root in (home / ".sfdx", home / ".sf", project / ".sf", project / ".sfdx"):
        for path in listing(root, follow=root.parent == home):
            if (path.name in KNOWN_ENTRIES or KNOWN_ENTRY_PATTERN.fullmatch(path.name) or path in consumed
                    or (root == home / ".sfdx" and SANDBOX_FILE.fullmatch(path.name))):
                continue
            try:
                info = path.lstat()
            except OSError as error:  # one entry we cannot examine must not stop the audit
                found.append({"path": str(path), "error": reason(error)})
                continue
            found.append({"path": str(path), "size": info.st_size,
                          "mode": stat.filemode(info.st_mode)})
    return found


def query_safe(value):
    """Whether a value can go into the SOQL `IN` list as written: no quote, backslash, or text sf
    would read as another name."""
    return "'" not in value and "\\" not in value and not sf_cannot_pass(value)


def query_hubs(run, hubs, field, values):
    """ScratchOrgInfo rows per value across every hub, plus the hubs that gave no full answer.

    SOQL matches text without regard to case, so signup usernames are keyed folded. A result cut
    short (by `org-max-query-limit`, which sf applies while still reporting done) is a failure.
    """
    rows, failed = {}, []
    by_name = field == "SignupUsername"
    safe = sorted(v for v in values if query_safe(v))
    for hub in hubs:
        for start in range(0, len(safe), BATCH):
            quoted = "','".join(safe[start:start + BATCH])
            soql = ("SELECT ScratchOrg, SignupUsername, Status, ExpirationDate FROM ScratchOrgInfo "
                    "WHERE {} IN ('{}')".format(field, quoted))
            payload = sf_json(run, "data", "query", "--target-org", hub, "--query", soql)
            result = (payload or {}).get("result")
            records = result.get("records") if isinstance(result, dict) else None
            total = result.get("totalSize") if isinstance(result, dict) else None
            if (payload is None or not isinstance(records, list) or result.get("done") is False
                    or (isinstance(total, int) and total > len(records))):
                failed.append(hub)
                continue
            for record in records:
                value = record.get(field) if isinstance(record, dict) else None
                if isinstance(value, str):
                    rows.setdefault(fold(value) if by_name else value[:15], []).append(record)
    return rows, sorted(set(failed))


def classify(rows, today):
    """Lifecycle class from hub rows: deleted, expired, active, conflict, or unknown."""
    if not rows or not all(isinstance(row.get("Status"), str) for row in rows):
        return "unknown"  # a row without a status is not evidence of anything
    statuses = {row.get("Status") for row in rows}
    if len(statuses) > 1:
        return "conflict"
    status = statuses.pop()
    if status == "Deleted":
        return "deleted"

    def past(row):
        date = row.get("ExpirationDate")
        return isinstance(date, str) and DATE.fullmatch(date) is not None and date < today

    if status == "Active":
        return "conflict" if any(map(past, rows)) else "active"
    # A reused signup username can name several orgs: each one must show it has expired.
    return "expired" if all(map(past, rows)) else "unknown"


def read_cci(run):
    """CCI's orgs and default, or None when there is no valid answer (not a prediction)."""
    code, out = run(["cci", "shell", "--python", CCI_SNIPPET])
    for line in out.splitlines() if code == 0 else []:
        if line.startswith("ORG_CLEANUP_CCI "):
            try:
                payload = json.loads(line.split(" ", 1)[1])
            except ValueError:
                return None
            orgs = payload.get("orgs") if isinstance(payload, dict) else None
            default = payload.get("default") if isinstance(payload, dict) else None
            ok = (isinstance(orgs, list) and (default is None or isinstance(default, str))
                  and all(isinstance(o, dict) and all(isinstance(o.get(k), t) for k, t in CCI_KEYS.items())
                          for o in orgs))
            return {"orgs": orgs, "default": default} if ok else None
    return None


def predict_prune(cci, proven_gone):
    """What `cci org prune` would do, and which of the orgs it removes are not proven gone."""
    if cci is None:
        return {"available": False}
    orgs = cci["orgs"]
    gone = [o for o in orgs if not o["shape"] and not o["active"] and o["scratch"]]
    return {
        "available": True,
        "would_remove_expired": sorted(o["name"] for o in gone if o["instantiated"]),
        "would_remove_never_instantiated": sorted(o["name"] for o in gone if not o["instantiated"]),
        "would_remove_not_proven_gone": sorted(o["name"] for o in gone
                                               if o["instantiated"] and not proven_gone(o)),
        "expired_shape_instances_it_skips": sorted(o["name"] for o in orgs if o["shape"] and o["expired"]),
        "default": cci["default"],
    }


def plain_job_id(job):
    """A cache key that names one manifest file: a bare name the filesystem can hold."""
    return (bool(job) and os.path.basename(job) == job and job not in (".", "..") and not sf_cannot_pass(job)
            and len((job + ".xml").encode("utf-8")) <= 255)


def within(path, root):
    """Whether a path is the root or inside it, compared by file identity: a case-insensitive
    filesystem (APFS) can spell the same folder differently, and a link anywhere on the way can
    reach it, so the path is resolved as the OS would reach it first."""
    path = Path(os.path.realpath(os.path.abspath(str(path))))
    for candidate in [path] + list(path.parents):
        try:
            if os.path.samefile(str(candidate), str(root)):
                return True
        except (OSError, ValueError):
            continue
    return False


def survey(run, home, project, today, predict=True, env=None):
    """Inventory plus hub evidence, judged the way sf reads it. Returns (plan, view).

    Mutates nothing beyond what the CLIs themselves do.
    """
    env = os.environ if env is None else env
    scopes = config_scopes(home, project, env)
    state = facts(home, project, env, scopes)  # first: apply checks that nothing changes from here on
    logins, unread, unreadable, blocks, listed, maybe_hubs = read_logins(home)
    alias_payload = sf_json(run, "alias", "list")
    if alias_payload is None:
        raise RuntimeError("sf alias list failed")
    aliases = read_aliases(alias_payload)
    # The plan and apply's checks read ~/.sfdx/alias.json; the protections read sf's own answer. They
    # must be the same map, or a check could not see what sf does.
    if ("alias-store", "unreadable") in state or aliases != {f[1]: f[2] for f in state if f[0] == "alias"}:
        raise RuntimeError("~/.sfdx/alias.json is not in the shape sf writes, or differs from what `sf alias "
                           "list` reports; fix the file, then audit again")

    # sf opens `~/.sfdx/<name>.json`, which a case- and normalization-insensitive filesystem (APFS)
    # finds whatever the spelling, so names are compared folded. A spelling that differs from the
    # file's means that login only where it opens the same file; on a case-sensitive filesystem it
    # opens nothing, so it has no login and is judged like any other such name. A name is in doubt
    # when it may mean a login the tool cannot read or tie to one org.
    folded, doubt = {}, {}
    for name in sorted(logins) + sorted(unread):
        folded.setdefault(fold(name), []).append(name)
    for name, why in unread.items():
        doubt[fold(name)] = why
    for name, username in listed.items():  # sf selects an unread file by the username inside it too
        doubt.setdefault(fold(username), "{}.json, which the tool does not act on, holds this login".format(name))
    for key, names in folded.items():
        if len(names) > 1:
            doubt[key] = "auth files whose names differ only by letter case or Unicode form: {}".format(
                ", ".join(names))
    for name, info in logins.items():
        if info["username"] != name:
            why = "{}.json holds the login {}".format(name, info["username"])
            doubt.setdefault(fold(name), why)
            doubt.setdefault(fold(info["username"]), why)

    def login_for(text):
        """The login a name opens: its stem, DOUBT, or None."""
        key = fold(text)
        if key in doubt or ("@" in text and beyond_tables(text)):  # only a name with "@" names a login file
            return DOUBT
        names = folded.get(key)
        if not names:
            return None
        sfdx = home / ".sfdx"
        if names[0] != text and not opens_same_file(sfdx / (text + ".json"), sfdx / (names[0] + ".json")):
            return None  # sf opens no file for this spelling
        return names[0]

    cci = read_cci(run) if predict else None
    indexes = read_indexes(home)
    tracking, symlinks = read_project_dirs(project, "orgs")
    entries, response_symlinks = read_project_dirs(project, "fileResponses")
    responses, unrecognized_responses = [], []
    for path in entries:
        (responses if is_dir(path) and ORG_ID.fullmatch(path.name) else unrecognized_responses).append(path)
    symlinks = list(dict.fromkeys(symlinks + response_symlinks))  # a linked .sfdx shows up in both
    # sf writes the alias store with writeFile, which follows a link: an unset there would rewrite a
    # store other homes may share, so nothing writes it (as for a linked config scope or cache).
    alias_store = home / ".sfdx" / "alias.json"
    alias_store_linked = is_link(alias_store)
    if alias_store_linked:
        symlinks.append(alias_store)

    cache_path = home / ".sf" / "deploy-cache.json"
    if is_link(cache_path):  # a shared cache: read nothing through the link, rewrite nothing
        symlinks.append(cache_path)
        deploy_cache = {}
    else:
        deploy_cache = read_json(cache_path, None) if lstat_or_none(cache_path) else {}
    cache_unread = [] if isinstance(deploy_cache, dict) else [str(cache_path)]  # nothing in it is planned
    cache_known = isinstance(deploy_cache, dict) and not is_link(cache_path)
    deploy_cache = deploy_cache if isinstance(deploy_cache, dict) else {}
    # sf stores the username a deploy ran against, and resolves it through an alias again when it
    # reads the entry (deploy report/resume), so a target is judged like any other name.
    # An entry that is not an object has no target, so it is reported with the other unsafe ones.
    deploy_raw = {job: entry.get("target-org") if isinstance(entry, dict) else None
                  for job, entry in deploy_cache.items()}
    manifest_dir = home / ".sf" / "manifestCache"
    manifest_linked = is_link(manifest_dir)
    if manifest_linked:  # its files are not ours to move, so no deploy job is planned
        symlinks.append(manifest_dir)
    # Nor is a job whose own manifest is a link: apply would refuse the move after the logout.
    linked_manifests = set() if manifest_linked else {
        job for job in deploy_raw if plain_job_id(job) and is_link(manifest_dir / (job + ".xml"))}
    symlinks += [manifest_dir / (job + ".xml") for job in sorted(linked_manifests)]
    # sf drops a cache entry when its 3-day TTL lapses but leaves the manifest; nothing names it now
    orphan_manifests = [] if manifest_linked or not cache_known else sorted(
        p.name for p in listing(manifest_dir) if p.suffix == ".xml" and p.stem not in deploy_cache)

    env_values = {var: env[var] for var in ENV_DEFAULTS if isinstance(env.get(var), str) and env[var]}

    # Hubs are queried by name, which sf resolves to an alias first: a hub named like one is not queried.
    hubs = sorted(n for n, info in logins.items() if info["is_hub"])
    aliased_hubs = [hub for hub in hubs if redirects(aliases, hub)]
    queried = [hub for hub in hubs if not redirects(aliases, hub)]
    state_orgs = {p.stem[:15] for p in indexes} | {p.name[:15] for p in responses}
    state_orgs |= {p.name[:15] for p in tracking if ORG_ID.fullmatch(p.name)}
    org_ids = {info["org"] for info in logins.values()} | state_orgs
    org_ids |= {o["org_id"][:15] for o in (cci or {}).get("orgs", []) if ORG_ID.fullmatch(o["org_id"])}
    id_rows, id_failed = query_hubs(run, queried, "ScratchOrg", org_ids)

    def target(name):
        """sf follows one alias, never a chain; an alias whose value is null means its own name."""
        value = aliases.get(name)
        return name if value is None else value

    # Names with no login to give an org ID are judged by signup username, and only when every hub
    # answered in full: a reused username may sit on a hub that did not answer, one named like an
    # alias, or one whose auth file the tool did not read.
    named = [target(a) for a in aliases] + [p.name for p in tracking if "@" in p.name]
    named += [target(v) for v in deploy_raw.values() if isinstance(v, str)]
    named += [target(v) for s in scopes.values() for _, v in s["pairs"]]
    named += [target(v) for v in env_values.values()]
    orphans = {n for n in named if "@" in n and login_for(n) is None}
    incomplete = set(id_failed + aliased_hubs) | set(maybe_hubs)
    user_rows, user_failed = ({}, []) if incomplete else query_hubs(run, queried, "SignupUsername", orphans)
    hub_failures = sorted(incomplete | set(user_failed))

    def org_class(org):
        return classify(id_rows.get(org[:15], []), today)

    def user_class(username):
        return "unknown" if hub_failures else classify(user_rows.get(fold(username), []), today)

    def user_orgs(username):
        return sorted({r["ScratchOrg"][:15] for r in user_rows.get(fold(username), [])
                       if isinstance(r.get("ScratchOrg"), str)})

    def effects(name):  # from the same rule apply checks each logout against
        rule = logout_rule(state, name)
        config = {}
        for f in sorted(f for f in rule if f[0] == "config"):
            config.setdefault(f[1], []).append(f[2])
        return {"aliases": sorted(f[1] for f in rule if f[0] == "alias"), "config": config}

    def clears(name):
        """The names sf's logout of this login removes, and whose config keys it unsets."""
        return {name} | set(effects(name)["aliases"])

    def logout_refused(name):
        """Why sf's logout of this login could do something the plan cannot show, or ''."""
        if blocks:
            return "sf cannot log anyone out as planned while " + blocks
        if login_for(name) is DOUBT:
            return doubt.get(fold(name), "its name has characters this Python's Unicode tables do not know, "
                                         "so the tool cannot tell which names the filesystem treats as the same")
        if name[:1] == "-" and name[1:2] in LOGOUT_SHORT_FLAGS:
            return "sf reads a --target-org value that starts with -{} as its own -{} flag".format(name[1], name[1])
        # An alias with the login's name, other than one naming the login itself (which logout clears):
        # sf looks a name up among aliases exactly, before it opens any file.
        if redirects(aliases, name):
            return "an alias is named like this login, so sf could resolve the name to the alias"
        for alias in effects(name)["aliases"]:
            if fold(alias) != fold(name) and login_for(alias) is not None:
                return "logout clears its alias {}, and that name would then mean another login".format(alias)
        if alias_store_linked and effects(name)["aliases"]:
            return "logout clears aliases in ~/.sfdx/alias.json, a link sf writes through"
        rewrites = unmodelled_scopes(state, set(effects(name)["config"]))
        if rewrites:
            return "logout rewrites the {} config, which the tool cannot model: {}".format(*rewrites[0])
        return ""

    protected, stale_logins = {}, set()

    def protect(name, why):  # a login and an alias can share a name, so a name can have two reasons
        protected.setdefault(name, []).append(why)

    for name, info in sorted(logins.items()):
        if info["linked"]:  # read for its identity, whatever its org, and never logged out
            protect(name, "its auth file is a link, and sf's logout would remove only the link")
            continue
        if org_class(info["org"]) not in REMOVABLE or info["is_hub"] or info["is_sandbox"]:
            continue
        why = logout_refused(name)
        if why:
            protect(name, why)
        else:
            stale_logins.add(name)
    for name, why in sorted(unread.items()):
        protect(name, why)

    in_doubt = {}  # every name kept because of a doubt, with why, so the report shows it

    def reach(name, resolve=True):
        """What sf reaches through a name: (verdict, login, orgs). The verdict is stale, live, doubt,
        unknown or dangling; orgs are those a failed logout there must hold the name's items for."""
        if resolve and redirects(aliases, name) and login_for(name) is not None:
            in_doubt[name] = "an alias of this name shadows a login's name, so which org it means is unclear"
            return "doubt", None, []
        text = target(name) if resolve else name
        login = login_for(text)
        if login is DOUBT:
            in_doubt[name] = doubt.get(fold(text), "it has characters this Python's Unicode tables do not "
                                                   "know, so the tool cannot tell which login file it opens")
            return "doubt", None, []
        if login is not None:
            return ("stale" if login in stale_logins else "live"), login, [logins[login]["org"]]
        if "@" not in text:
            return "dangling", None, []
        return ("stale" if user_class(text) in REMOVABLE else "unknown"), None, user_orgs(text)

    def judge(name, resolve=True):
        return reach(name, resolve)[0]

    def owner(name, resolve=True):
        """The orgs an item reaches, bound in the plan: a failed logout on any of them keeps it."""
        return {"orgs": reach(name, resolve)[2]}

    cleared = set().union(*map(clears, stale_logins))

    remove_aliases = []
    for alias in sorted(aliases):
        if alias in cleared:
            continue
        if sf_cannot_pass(alias):
            protect(alias, "its name is not valid UTF-8, so sf would unset another name")
        elif "@" in alias and beyond_tables(alias) and fold(alias) not in folded:
            protect(alias, "its name has characters this Python's Unicode tables do not know, so the tool cannot "
                           "tell whether the filesystem treats it as a login's name")
        elif login_for(alias) is not None:  # it shadows a login's name; unsetting it would re-point the name
            protect(alias, "this alias has a login's name, so sf resolves that name to the alias, not the login; "
                           "the tool never unsets it")
        elif judge(alias) == "stale":
            if alias_store_linked:
                protect(alias, "~/.sfdx/alias.json is a link, and sf would unset it through the link")
            else:
                remove_aliases.append(alias)

    defaults, stale_values = [], []
    for scope_name, scope in sorted(scopes.items()):
        for key, value in scope["pairs"]:
            if key not in ("target-org", "target-dev-hub") or value in cleared or judge(value) != "stale":
                continue
            if key == "target-org" and not scope["why"]:
                defaults.append(scope_name)
            else:  # reported: the tool does not unset a dev hub default, nor write a scope it cannot model
                stale_values.append({"scope": scope_name, "key": key, "value": value})

    kept_orgs = {info["org"] for name, info in logins.items() if name not in stale_logins}

    def gone_org(org):
        return org_class(org) in REMOVABLE and org[:15] not in kept_orgs

    def gone_user_dir(username):  # legacy `.sfdx/orgs/<username>`, named by username, not alias
        verdict, _, orgs = reach(username, resolve=False)  # stale means every org it names is gone
        return verdict == "stale" and bool(orgs) and not set(orgs) & kept_orgs

    jobs = [] if manifest_linked else sorted(
        job for job, value in deploy_raw.items()
        if isinstance(value, str) and value and plain_job_id(job) and job not in linked_manifests
        and judge(value) == "stale")
    remove = {
        "logout": sorted(stale_logins),
        "aliases": remove_aliases,
        "indexes": sorted(str(p) for p in indexes if gone_org(p.stem)),
        "tracking": sorted(str(p) for p in tracking
                           if (ORG_ID.fullmatch(p.name) and gone_org(p.name))
                           or ("@" in p.name and gone_user_dir(p.name))),
        "file_responses": sorted(str(p) for p in responses if gone_org(p.name)),
        "deploy_jobs": jobs,
        "defaults": defaults,
    }

    def file_owner(item):
        if ORG_ID.fullmatch(Path(item).stem):
            return {"orgs": [Path(item).stem[:15]]}
        return owner(Path(item).name, resolve=False)

    def proven_gone(org):
        if ORG_ID.fullmatch(org["org_id"]):
            return org_class(org["org_id"]) in REMOVABLE
        _, login, orgs = reach(org["username"], resolve=False) if org["username"] else (None, None, [])
        return login is not None and org_class(orgs[0]) in REMOVABLE

    consumed = ({home / ".sfdx" / (name + ".json") for name in logins} | set(indexes)
                | {home / ".sfdx" / name for name in unreadable})
    plan = {
        "schema": 2,
        "today": today,
        "project": str(project),
        "hubs": hubs,
        "hub_failures": hub_failures,
        "remove": remove,
        # Everything apply will touch or cause, bound so that any change since review is drift.
        "targets": {
            "logout": {n: dict(org=logins[n]["org"], **effects(n)) for n in remove["logout"]},
            "aliases": {a: dict(value=aliases[a], **owner(a)) for a in remove_aliases},
            "defaults": {s: dict(value=scopes[s]["merged"]["target-org"],
                                 **owner(scopes[s]["merged"]["target-org"])) for s in defaults},
            "deploy_jobs": {j: dict(value=deploy_raw[j], **owner(deploy_raw[j])) for j in jobs},
            "files": {item: file_owner(item) for key in FILE_KEYS for item in remove[key]},
        },
        "preserved": {
            "logins": len(logins) - len(stale_logins),
            "aliases": len(aliases) - len(remove_aliases) - len(cleared & set(aliases)),
            "indexes": len(indexes) - len(remove["indexes"]),
            "tracking": len(tracking) - len(remove["tracking"]),
            "file_responses": len(responses) - len(remove["file_responses"]),
            "deploy_jobs": len(deploy_raw) - len(jobs),
        },
        "report": {
            "protected": {name: "; ".join(why) for name, why in sorted(protected.items())},
            # Hub rows that disagree, or show Active past the date: a login, an org's local state, or a username.
            "conflicting_evidence": sorted(
                {n for n, info in logins.items() if org_class(info["org"]) == "conflict"}
                | {org for org in state_orgs if org_class(org) == "conflict"}
                | {n for n in orphans if user_class(n) == "conflict"}),
            "logins_with_no_refresh_token": sorted(
                n for n, info in logins.items()
                if not info["refreshable"] and not info["linked"] and n not in stale_logins),
            "unreadable_auth_files": unreadable,
            "symlinks_left_alone": [str(p) for p in symlinks],
            "unrecognized_file_responses": [str(p) for p in unrecognized_responses],
            # A key that is not a plain file name has no manifest to look for, and a target that is not
            # text names no org, so neither is ever planned.
            # Never queried, so never judged: a clean plan says nothing about them.
            "usernames_not_queried": sorted(n for n in orphans if not query_safe(n)),
            "unsafe_deploy_cache_keys": sorted(j for j, v in deploy_raw.items()
                                               if not plain_job_id(j) or not isinstance(v, str)),
            "unreadable_deploy_cache": cache_unread,
            "manifests_without_cache_entry": orphan_manifests,
            "unclassified_files": read_unclassified(home, project, consumed),
            # Lead to no login and no username, so no hub row can ever put them on the plan.
            "dangling_aliases": sorted(a for a in aliases if judge(a) == "dangling"),
            "dangling_defaults": sorted(s for s, scope in scopes.items()
                                        if not scope["why"] and isinstance(scope["merged"].get("target-org"), str)
                                        and judge(scope["merged"]["target-org"]) == "dangling"),
            "unmodelled_config": {s: scope["why"] for s, scope in sorted(scopes.items()) if scope["why"]},
            "stale_config_values": stale_values,
            "env_defaults": {var: {"value": v, "judged": judge(v)} for var, v in sorted(env_values.items())},
        },
        "prune_prediction": predict_prune(cci, proven_gone),
    }
    plan["report"]["names_in_doubt"] = dict(sorted(in_doubt.items()))  # after every judgment, prune's too
    return plan, {"logins": logins, "unread": unread, "listed": listed, "aliases": aliases, "state": state}


def build_plan(run, home, project, today, predict=True, env=None):
    return survey(run, home, project, today, predict, env)[0]


def check_logins(run, view):
    """Read-only query per login sf lists. A refresh can rewrite an auth file, so this is opt-in.
    Returns the logins that did not answer, and those not queried with the reason."""
    failed, skipped = [], {}
    for name in sorted(set(view["logins"]) | set(view["unread"])):
        if name not in view["logins"] and name not in view["listed"]:
            skipped[name] = "sf lists it under no username the tool can query"
        elif redirects(view["aliases"], name):
            skipped[name] = "named like an alias, so sf would answer through the alias's org"
        elif sf_json(run, "data", "query", "--target-org", name,
                     "--query", "SELECT Id FROM Organization") is None:
            failed.append(name)
    return failed, skipped


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


def check_quarantine(quarantine, source):
    """Move a temp file in from `source`, a folder planned items leave, and remove it, returning
    why that failed, or None if it worked.

    Creating the folder is not proof: macOS can allow a mkdir in ~/.Trash while refusing to list
    it. This runs before the first logout, because a logout cannot be restored.
    """
    created, temp = [], None
    try:
        if is_link(quarantine):  # a linked root would send every move somewhere else
            return "{} is a symlink".format(quarantine)
        for name in QUARANTINE_FOLDERS:
            folder = quarantine / name
            if is_link(folder):  # a move into it would land outside the quarantine
                return "{} is a symlink".format(folder)
            if lstat_or_none(folder) is not None and not is_dir(folder):
                return "{} is not a folder".format(folder)
            if is_dir(folder) and not os.access(str(folder), os.W_OK | os.X_OK):
                return "{} is not writable".format(folder)
        created = [p for p in [quarantine] + list(quarantine.parents) if lstat_or_none(p) is None]
        handle, temp = tempfile.mkstemp(dir=str(source), prefix=".org-cleanup-probe-")
        os.close(handle)
        quarantine.mkdir(parents=True, exist_ok=True)
        dest = quarantine / os.path.basename(temp)
        move_path(temp, str(dest))
        os.remove(str(dest))
        return None
    except OSError as error:
        return reason(error)
    finally:
        if temp and os.path.lexists(temp):
            os.remove(temp)
        for path in created:  # deepest first; a folder that still holds anything stays
            try:
                os.rmdir(str(path))
            except OSError:
                break


def move_blocker(run, path, project):
    """Why `path` cannot leave or be replaced in its folder, or None. apply asks this of every
    planned item and of the deploy cache before any logout, and again at the move. It checks what a
    rename needs: write access on the folder, and on a moved directory itself, whose `..` the rename
    rewrites (a `sudo sf` can take either away). A move across volumes copies, then deletes, and can
    still fail on what is inside; nothing is lost then (see move_path). Links are left to the audit,
    which plans none."""
    for folder in [path.parent] + ([path] if is_dir(path) else []):
        if not os.access(str(folder), os.W_OK | os.X_OK):
            return "no write access to {}".format(folder)
    if project in path.parents:
        code, out = run(["git", "-C", str(project), "ls-files", "--", str(path)])
        if code != 0 or out.strip():
            return "tracked by git, or git could not say"
    return None


def move_to_quarantine(run, path, roots, quarantine, project):
    """Move one allowlisted path, or return why it was refused."""
    if lstat_or_none(path) is None:
        return "missing"
    if is_link(path):
        return "symlink"
    if not any(path.parent == root for root in roots):
        return "outside the expected state roots"
    if project in path.parents and linked_ancestor(path.parent):
        return "symlink"
    why = move_blocker(run, path, project)
    if why:
        return why
    dest = quarantine / path.parent.name / path.name
    try:
        for folder in (quarantine, dest.parent):  # a linked root or folder would redirect the move
            if is_link(folder):
                return "the quarantine folder {} is a symlink".format(folder)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest = free_name(dest)
        move_path(str(path), str(dest))
    except OSError as error:
        return "could not move it to {}: {}".format(dest.parent, reason(error))
    print("Moved {} -> {}".format(path, dest))  # the quarantine is shared, so say where each item came from
    return None


def replace_json(path, data):
    """Rewrite a JSON file atomically, keeping its mode. The temp file goes on any interruption."""
    mode = stat.S_IMODE(path.stat().st_mode)
    handle, temp = tempfile.mkstemp(dir=str(path.parent), prefix=".deploy-cache.")
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as out:
            if hasattr(os, "fchmod"):  # POSIX; Windows Python before 3.13 has none
                os.fchmod(out.fileno(), mode)
            out.write(json.dumps(data, indent=4, allow_nan=False))  # the encoder remove_deploy_jobs checks with
            out.flush()
            os.fsync(out.fileno())  # so a crash cannot leave sf an empty or cut-short cache
        os.replace(temp, str(path))
    except BaseException:
        if os.path.lexists(temp):
            os.remove(temp)
        raise


def remove_deploy_jobs(run, jobs, home, quarantine, project, failures, done=None):
    """Drop named cache entries, keeping every other key. Returns (entries, manifests moved).

    The cache is rewritten first; if it cannot be, every entry and manifest stays. A manifest that
    then cannot move stays without its entry and is reported. Each step is counted into `done` as
    it happens, so an interruption still reports it.
    """
    done = {} if done is None else done
    if not jobs:  # no cache file is normal, and only a failure if something had to change in it
        return 0, 0
    path = home / ".sf" / "deploy-cache.json"
    manifests = home / ".sf" / "manifestCache"
    for linked in (path, manifests):  # checked here too: a link made after the audit is not ours
        if is_link(linked):
            failures.append((str(linked), "symlink"))
            return 0, 0
    # sf writes the cache under its own lock. The tool does not take it: it leaves the cache to an
    # sf command that holds it, and rewrites it straight after this check.
    if lock_held(cache_lock(home)):
        failures.append((str(path), "not modified: an sf command holds its lock"))
        return 0, 0
    return rewrite_deploy_cache(run, jobs, path, manifests, quarantine, project, failures, done)


LOCK_STALE_SECONDS = 10  # @salesforce/core lockOptions: proper-lockfile treats an older lock as abandoned


def cache_lock(home):
    """sf's lock on the deploy cache: a folder proper-lockfile makes with mkdir beside the file, and
    refreshes while it writes."""
    return home / ".sf" / "deploy-cache.json.lock"


def lock_held(lock):
    """Whether an sf command holds the lock now: it exists and was refreshed within sf's stale window."""
    info = lstat_or_none(lock)
    return info is not None and time.time() - info.st_mtime < LOCK_STALE_SECONDS


def rewrite_deploy_cache(run, jobs, path, manifests, quarantine, project, failures, done):
    """remove_deploy_jobs' work: rewrite the cache without the jobs' entries, then move their
    manifests. A manifest that cannot move stays without an entry, as sf leaves one whose entry
    lapsed, and the next audit lists it under manifests_without_cache_entry."""
    cache = read_json(path, None)
    if not isinstance(cache, dict):
        failures.append(("deploy-cache", "unreadable"))
        return 0, 0
    try:  # checked before anything changes, with the write's own encoder
        json.dumps(cache, indent=4, allow_nan=False)
    except (ValueError, RecursionError):
        failures.append(("deploy-cache", "holds a value this tool cannot write back; not modified"))
        return 0, 0
    gone = []
    for job in jobs:
        if not plain_job_id(job):
            failures.append((job, "cache key is not a plain job id; its manifest was not looked for"))
        elif job in cache:
            del cache[job]
            gone.append(job)
        elif lstat_or_none(manifests / (job + ".xml")) is not None:
            failures.append((job, "no longer in the deploy cache; its manifest was left in place"))
    if not gone:
        return 0, 0
    try:
        replace_json(path, cache)
    except OSError as error:
        failures.append((str(path), "could not write: {}".format(reason(error))))
        return 0, 0
    except BaseException:
        if read_json(path, None) == cache:  # interrupted after the rewrite landed
            done["deploy_jobs"] = done.get("deploy_jobs", 0) + len(gone)
        raise
    done["deploy_jobs"] = done.get("deploy_jobs", 0) + len(gone)
    moved = 0
    for job in gone:
        manifest = manifests / (job + ".xml")
        if lstat_or_none(manifest) is None:
            continue
        why = move_to_quarantine(run, manifest, [manifests], quarantine, project)
        if why:
            failures.append((str(manifest), why))
            continue
        moved += 1
        done["manifests"] = done.get("manifests", 0) + 1
    return len(gone), moved


class Unexpected(Exception):
    """The state is not what the plan said, so nothing more is run."""


ENCRYPTED_KEYS = {"org-isv-debugger-sid"}  # sf re-encrypts these, with a fresh IV, on every config write


def facts(home, project, env, scopes=None):
    """What an sf command run by apply can change, as a set: the login files, the aliases
    (`~/.sfdx/alias.json`), each config scope's values (an encrypted one only as present, None) and
    why a scope cannot be modelled, if it cannot."""
    found = {("login", name) for name, _ in login_files(home)}
    store = read_alias_store(home)
    found |= {("alias-store", "unreadable")} if store is None else {("alias", a, v) for a, v in store.items()}
    for scope_name, scope in (scopes or config_scopes(home, project, env)).items():
        found |= {("config", scope_name, k, None if k in ENCRYPTED_KEYS else v) for k, v in scope["pairs"]}
        if scope["why"]:
            found.add(("unmodelled", scope_name, scope["why"]))
    return found


def describe(fact):
    if fact[0] == "config":
        return "{} in the {} config".format(fact[2], fact[1])
    if fact[0] == "unmodelled":
        return "whether the {} config can be modelled".format(fact[1])
    if fact[0] == "alias-store":
        return "~/.sfdx/alias.json (unreadable)"
    return "{} {}".format(fact[0], fact[1])


def logout_rule(state, name):
    """What sf's logout of a login removes: its file, the aliases valued exactly the user, and the
    config values naming either. The plan's effects come from this too."""
    held = {name} | {f[1] for f in state if f[0] == "alias" and f[2] == name}
    return {f for f in state if f == ("login", name) or (f[0] == "alias" and f[2] == name)
            or (f[0] == "config" and f[3] in held)}


def unmodelled_scopes(state, scopes):
    """(scope, why) for each of these scopes that the state says cannot be modelled."""
    return sorted((f[1], f[2]) for f in state if f[0] == "unmodelled" and f[1] in scopes)


def apply_plan(run, plan, home, project, quarantine, done, failures, env=None, state=None):
    """Carry out a reviewed plan, counting into done and collecting per-item failures, never hiding them.

    The caller owns both, so what ran is still reported if a step raises. Every item carries the
    orgs it reaches (bound in the reviewed plan), so a failed logout blocks exactly what depends on
    it without asking sf again.

    `state` is what apply's own audit read first (read now if not given). Before each sf command
    the state must still be that, less what earlier commands removed, and the command's effects
    must be the ones the plan shows. After it, even when interrupted, what it removed is counted
    from the state, not from sf's answer; what it should have removed and did not is a failure;
    anything else it changed is recorded and stops the run.
    """
    env = os.environ if env is None else env
    remove, targets = plan["remove"], plan["targets"]
    failed_orgs = set()
    state = facts(home, project, env) if state is None else set(state)

    def blocked(owner):
        return bool(set(owner["orgs"]) & failed_orgs)

    def check(label):
        """The state a command starts from: an unexplained change stops the run before it."""
        try:
            now = facts(home, project, env)
        except OSError as error:
            raise Unexpected("could not read the state before {}: {}".format(label, reason(error)))
        changed = now ^ state
        if changed:
            failures.append((label, "not run: {} changed after the audit".format(
                ", ".join(sorted(set(map(describe, changed)))))))
            raise Unexpected("the state changed during this run, so {} and the steps after it did not run".format(label))
        return now

    def settle(label, expected, record, after):
        """Count what a command did from the state after it; return anything else it changed."""
        nonlocal state
        before, state = state, after
        # A store that became unreadable hides what happened to its facts: they are unknown, neither
        # removed nor changed. Its becoming unreadable is the change reported.
        unreadable = {f[1] for f in after - before if f[0] == "unmodelled"}
        unknown = {f for f in before | expected if (f[0] == "alias" and ("alias-store", "unreadable") in after)
                   or (f[0] == "config" and f[1] in unreadable)}
        record(expected - after - unknown, expected & after, expected & unknown)
        other = (before - after - expected - unknown) | (after - before)
        if other:
            failures.append((label, "sf also changed {}".format(", ".join(sorted(set(map(describe, other)))))))
        return other

    def run_checked(command, label, expected, record):
        """Run one sf command whose reviewed effects are `expected`, then record(gone, left, unknown) from the
        state, stopped part-way or not, with what it cannot tell. Anything else it changed is recorded
        and stops the run."""
        try:
            command()
            after = facts(home, project, env)
        except OSError as error:  # sf ran (sf_json never raises it); the state read failed
            failures.append((label, "ran, but its effects could not be checked"))
            raise Unexpected("{} ran, but its effects could not be checked: {}".format(label, reason(error)))
        except BaseException as error:  # interrupted, while sf ran or just after it
            failures.append((label, "stopped while sf ran or just after; it may have completed"))
            try:
                after = facts(home, project, env)
            except BaseException:  # an unreadable state, or a second interrupt: the line above stands
                raise error
            failures[-1] = (label, "stopped while sf ran or just after; counted from what it left")
            settle(label, expected, record, after)
            raise error
        if settle(label, expected, record, after):
            raise Unexpected("{} changed more than the plan said, so nothing more was run".format(label))

    for name in remove["logout"]:
        planned = targets["logout"][name]
        before = check(name)
        expected = logout_rule(before, name)
        shown = {("login", name)} | {("alias", a) for a in planned["aliases"]}
        shown |= {("config", s, k) for s, keys in planned["config"].items() for k in keys}
        if ({f[:3] if f[0] == "config" else f[:2] for f in expected} != shown
                or unmodelled_scopes(before, {f[1] for f in expected if f[0] == "config"})):
            failures.append((name, "its effects are not the ones the plan shows; not logged out"))
            failed_orgs.add(planned["org"])
            continue

        def record_logout(gone, left, unknown):
            if ("login", name) in gone:
                done["logout"] += 1
            done["cleared_by_logout"] += sum(1 for f in gone if f[0] != "login")
            if left:
                failures.append((name, "logout failed" if ("login", name) in left else
                                 "logout left {}".format(", ".join(sorted(map(describe, left))))))
            if unknown:
                failures.append((name, "cannot tell whether it cleared {}: the file is unreadable now".format(
                    ", ".join(sorted(map(describe, unknown))))))
            if left or unknown:
                failed_orgs.add(planned["org"])

        run_checked(lambda: sf_json(run, "org", "logout", "--target-org", name, "--no-prompt"), name, expected,
                    record_logout)

    # One alias per command: sf handles several in parallel, and a batch can fail partway.
    for alias in remove["aliases"]:
        planned = targets["aliases"][alias]
        if blocked(planned):
            failures.append((alias, "skipped because its logout failed"))
            continue
        bound = ("alias", alias, planned["value"])
        if bound not in check(alias):
            failures.append((alias, "changed during this run; not modified"))
            continue

        def record_alias(gone, left, unknown):
            if gone:
                done["aliases"] += 1
            else:
                failures.append((alias, "may have been unset: ~/.sfdx/alias.json is unreadable now" if unknown
                                 else "alias unset failed"))

        run_checked(lambda: sf_json(run, "alias", "unset", operands=[alias]), alias, {bound}, record_alias)

    for scope in remove["defaults"]:
        planned = targets["defaults"][scope]
        label = scope + " default"
        if blocked(planned):
            failures.append((label, "skipped because its logout failed"))
            continue
        before = check(label)
        expected = {f for f in before if f[0] == "config" and f[1] == scope and f[2] == "target-org"}
        if expected != {("config", scope, "target-org", planned["value"])} or unmodelled_scopes(before, {scope}):
            failures.append((label, "changed during this run; not modified"))
            continue

        def record_default(gone, left, unknown):
            if gone:
                done["defaults"] += 1
            else:
                failures.append((label, "may have been unset: the config file is unreadable now" if unknown
                                 else "config unset failed"))

        args = ["config", "unset", "target-org"] + (["--global"] if scope == "global" else [])
        run_checked(lambda: sf_json(run, *args), label, expected, record_default)

    roots = {"indexes": [home / ".sfdx"],
             "tracking": [project / ".sf" / "orgs", project / ".sfdx" / "orgs"],
             "file_responses": [project / ".sf" / "fileResponses", project / ".sfdx" / "fileResponses"]}
    for key in FILE_KEYS:
        for item in remove[key]:
            if blocked(targets["files"][item]):
                failures.append((item, "skipped because its logout failed"))
                continue
            why = move_to_quarantine(run, Path(item), roots[key], quarantine, project)
            if why:
                failures.append((item, why))
            else:
                done[key] += 1

    jobs = []
    for job in remove["deploy_jobs"]:
        if blocked(targets["deploy_jobs"][job]):
            failures.append((job, "skipped because its logout failed"))
        else:
            jobs.append(job)
    remove_deploy_jobs(run, jobs, home, quarantine, project, failures, done)


def print_plan(plan):
    print("Dev Hubs: {}".format(len(plan["hubs"])))
    if not plan["hubs"]:
        print("NO CONNECTED DEV HUB WAS FOUND. No hub was queried, so every entry is unknown and "
              "an empty plan below is not evidence that the state is clean.")
    if plan["hub_failures"]:
        print("HUBS OR LOGINS THAT GAVE NO EVIDENCE: {}".format(plan["hub_failures"]))
        print("No username is judged while any is listed, so this plan and the prune check may be incomplete.")
    print("\nWould remove:")
    for key in REMOVE_KEYS:
        items = plan["remove"][key]
        print("  {}: {}".format(key, len(items)))
        bound = {"aliases": "aliases", "defaults": "defaults", "deploy_jobs": "deploy_jobs"}.get(key)
        for item in items:
            value = plan["targets"][bound][item]["value"] if bound else None
            print("    {}".format(item) if not bound else "    {} -> {}".format(
                item + " target-org" if key == "defaults" else item, value))
            effects = plan["targets"]["logout"].get(item) if key == "logout" else None
            if effects and effects["aliases"]:
                print("      sf also clears its aliases: {}".format(", ".join(effects["aliases"])))
            for scope, keys in sorted((effects or {}).get("config", {}).items()):
                print("      sf also clears from the {} config: {}".format(scope, ", ".join(keys)))
    print("\nPreserved: {}".format(plan["preserved"]))
    print("\nFor the user to review:")
    for key, value in plan["report"].items():
        if value:
            print("  {}: {}".format(key, json.dumps(value)))
    print("\ncci org prune prediction (never run by this tool):")
    for key, value in plan["prune_prediction"].items():
        print("  {}: {}".format(key, value))


def write_private(path, text):
    """Write a file only the user can read, from the first byte, never through a symlink, and never
    into a file with other hard links, which would rewrite whatever else that file is."""
    if os.path.islink(str(path)):  # O_NOFOLLOW is missing on some platforms, so do not rely on it alone
        raise OSError(errno.ELOOP, "is a symlink")
    info = lstat_or_none(path)
    if info is not None and not stat.S_ISREG(info.st_mode):  # a FIFO would block the open; a device take the plan
        raise OSError(errno.EINVAL, "is not a regular file")
    flags = os.O_WRONLY | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    fd = os.open(str(path), flags, 0o600)  # not O_TRUNC: what was opened is checked before it is emptied
    opened = os.fstat(fd)
    if not stat.S_ISREG(opened.st_mode) or opened.st_nlink > 1:
        os.close(fd)
        raise OSError(errno.EINVAL, "is not a regular file with a single name")
    os.ftruncate(fd, 0)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        if hasattr(os, "fchmod"):  # a file that already existed keeps its old mode; POSIX only
            os.fchmod(handle.fileno(), 0o600)
        handle.write(text)


def in_project_root(project):
    return (project / "cumulusci.yml").is_file() and (project / "sfdx-project.json").is_file()


def main(argv=None, run=run_command, home=None, project=None, today=None, env=None):
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
    for flag in ("--out", "--plan", "--quarantine"):
        value = getattr(args, flag[2:], None)
        if value is not None and not value.strip():
            parser.error("{} needs a path".format(flag))
        if value is not None:  # `--out=~/plan.json` reaches here unexpanded
            setattr(args, flag[2:], os.path.expanduser(value))

    home = home or Path.home()
    project = project or Path.cwd()
    today = today or datetime.date.today().isoformat()
    env = os.environ if env is None else env
    for stream in (sys.stdout, sys.stderr):  # a report that cannot be encoded must still print
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    if not in_project_root(project):
        print("Run this from the project root: cci and local sf config resolve the project "
              "from the working directory.", file=sys.stderr)
        return 2

    # Checked before any audit work. A plan holds usernames and org IDs; a quarantine inside a root
    # leaves residue where it was, and one that holds a root takes it along when the user empties it.
    roots = (project, home / ".sf", home / ".sfdx")
    out = quarantine = None
    if args.command == "audit" and args.out:
        # The folder as the OS reaches it (links and ".." followed), checked and written as one path;
        # the file itself may be a link, which write_private refuses.
        out = Path(os.path.realpath(os.path.dirname(args.out) or ".")) / os.path.basename(args.out)
        for root in roots:
            if within(out.parent, root):
                print("The plan holds usernames and org IDs: write it outside {}.".format(root), file=sys.stderr)
                return 2
    if args.command == "apply":
        reviewed = read_json(args.plan, None)
        if not isinstance(reviewed, dict):
            print("Could not read a plan from {}. Nothing was changed.".format(args.plan), file=sys.stderr)
            return 1
        quarantine = Path(os.path.abspath(args.quarantine)) if args.quarantine else default_quarantine(home, today)
        for root in roots:
            if within(root, quarantine) or within(quarantine, root):
                print("The quarantine must be outside {}, and must not hold it; nothing was changed.".format(root),
                      file=sys.stderr)
                return 2

    try:  # apply never asks cci: the prune prediction is for review only and is not compared
        plan, view = survey(run, home, project, today, predict=args.command == "audit", env=env)
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        return 1
    except OSError as error:  # an unreadable folder means an incomplete inventory, so change nothing
        print("Could not read local state: {}. Nothing was changed.".format(reason(error)), file=sys.stderr)
        return 1

    if args.command == "audit":
        unwritten = None
        if out:  # first, so a closed output pipe cannot lose the plan
            try:
                write_private(out, json.dumps(plan, indent=1) + "\n")
            except OSError as error:
                unwritten = "Could not write the plan to {}: {}".format(out, reason(error))
        print_plan(plan)
        if unwritten:
            print(unwritten, file=sys.stderr)
            return 1
        if args.check_logins:
            failed, skipped = check_logins(run, view)
            print("\nLogins that did not answer a query: {}".format(failed or "none"))
            for name, why in sorted(skipped.items()):
                print("Not queried: {} ({})".format(name, why))
            return 1 if failed else 0
        return 0

    drifted = [key for key in ("schema", "project", "remove", "targets") if reviewed.get(key) != plan[key]]
    if drifted:
        print("The plan differs from the current state ({}). Review a fresh audit before applying.".format(
            ", ".join(drifted)), file=sys.stderr)
        if plan["hub_failures"]:
            print("Hubs or logins that gave no evidence now: {}".format(plan["hub_failures"]), file=sys.stderr)
        return 3
    moves = any(plan["remove"][key] for key in FILE_KEYS + ("deploy_jobs",))
    if moves:
        items = [Path(item) for key in FILE_KEYS for item in plan["remove"][key]]
        if plan["remove"]["deploy_jobs"]:  # the cache is replaced in its folder, the manifests moved
            items.append(home / ".sf" / "deploy-cache.json")
            items += [home / ".sf" / "manifestCache" / (job + ".xml") for job in plan["remove"]["deploy_jobs"]
                      if plain_job_id(job)]
        stuck = []
        for item in items:  # a missing item has nothing to move
            why = None if lstat_or_none(item) is None else move_blocker(run, item, project)
            if why:
                stuck.append("{} ({})".format(item, why))
        if stuck:
            print("Stopped before any logout; nothing was changed. These files cannot be moved or rewritten: "
                  "{}. Fix their ownership or git, then apply again.".format("; ".join(stuck)),
                  file=sys.stderr)
            return 1
        source = next((item.parent for item in items if lstat_or_none(item) is not None), home)
        why = check_quarantine(quarantine, source)  # from a folder checked above, as the moves will go
        if why:
            print("Stopped before any logout; nothing was changed. Cannot move files into {}: {}. "
                  "Use --quarantine <dir> to choose another folder.".format(quarantine, why),
                  file=sys.stderr)
            return 1
    if plan["remove"]["deploy_jobs"] and lock_held(cache_lock(home)):
        print("Stopped before any logout; nothing was changed. An sf command holds the deploy cache's lock "
              "({}); run apply again when it has finished.".format(cache_lock(home)), file=sys.stderr)
        return 1
    done, failures, stopped, code = dict.fromkeys(DONE_KEYS, 0), [], None, 0
    try:
        apply_plan(run, plan, home, project, quarantine, done, failures, env, view["state"])
    except KeyboardInterrupt:  # logouts already done cannot be undone, so report what ran
        stopped, code = "interrupted", 130
    except Unexpected as error:
        stopped = str(error)
    except Exception as error:  # noqa: BLE001 - reported below, with what ran, instead of a traceback
        stopped = reason(error) if isinstance(error, OSError) else "{}: {}".format(
            type(error).__name__, str(error)[:300])
    print("Done: {}".format(done))
    if any(done[key] for key in FILE_KEYS + ("manifests",)):
        print("Residual files moved to: {}".format(quarantine))
    elif moves and (failures or stopped):
        print("No file was moved. A failed move can leave a partial copy in: {}".format(quarantine))
    for item, why in failures:
        print("FAILED: {} ({})".format(item, why))
    if stopped:
        print("Stopped part-way: {}. The steps after it did not run, and a logout that ran cannot be "
              "undone. Compare the plan with Done above: a fresh audit cannot list a logged-out secondary "
              "user's remaining state.".format(stopped), file=sys.stderr)
        return code or 1
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
