#!/usr/bin/env python3
"""mcp_org.py — resolve a target org for the MCP client tooling from ONE env var.

    RLM_MCP_ORG=<sf-cli alias>

Deliberately NOT `SF_ORG`: the `SF_*` namespace belongs to the Salesforce CLI
(`SF_TARGET_ORG`, `SF_ORG_API_VERSION`, `SF_ORG_INSTANCE_URL`, …) where a collision could
silently retarget the CLI itself.

WHAT IT RESOLVES (and why no secret is needed)
    instance URL  <- `sf org display --target-org <alias>`  (authoritative, always current)
    consumer key  <- profile cache, else a one-time Metadata retrieve of
                     ExtlClntAppGlobalOauthSettings:<eca>_glbloauth from the org
    consumer secret — NOT resolved and NOT required. The ECA sets
                     isConsumerSecretOptional=true, so authorization_code + PKCE (S256)
                     completes with the consumer key alone. Verified live on 264-upgrade.
    refresh token <- already namespaced by mcp_auth.py on (instance, client_id), so two
                     orgs never share a cached token. Nothing to do here.

Emits `SF_INSTANCE` / `SF_CID` for mcp_multiplex_proxy.py and mcp_auth.py, which read
them — this is a resolver in front of them.

USAGE
    python3 mcp_org.py env  [alias]     # shell exports:  eval "$(mcp_org.py env sdb39-revmcp)"
                                         # (never prints a consumer secret; needs `jq` if the
                                         #  secret lives only in the profile file)
    python3 mcp_org.py show [alias]     # human-readable, key fingerprinted not printed
    python3 mcp_org.py json [alias]     # machine-readable
    python3 mcp_org.py list             # every alias with a cached profile
Alias precedence: argv[2] > $RLM_MCP_ORG.
"""
import hashlib, json, os, re, shlex, subprocess, sys, tempfile, urllib.parse, zipfile

# Restricted sandboxes (e.g. Claude Code's Bash tool) forbid writes outside the workdir
# and $TMPDIR. The `sf` CLI otherwise tries to write ~/.sf/sf-<date>.log, gets EPERM, and
# dies before emitting JSON — which reads to callers as "org not authenticated" (a false
# negative that once made bootstrap --check lie). Default the CLI's own kill-switch on;
# a user who needs the log can still export SF_DISABLE_LOG_FILE=false to override.
os.environ.setdefault("SF_DISABLE_LOG_FILE", "true")

ENV_VAR   = "RLM_MCP_ORG"
ECA_NAME  = os.environ.get("RLM_MCP_ECA", "RLM_McpClient")
PROFILES  = os.path.expanduser(os.environ.get("RLM_MCP_PROFILES", "~/.rlm_mcp_orgs.json"))
# The prod gateway only: `revenue-cloud` is not published on test.api, which answers
# `404 Server definition not found`. Override with SF_MCP_BASES for an internal / pc-rnd
# org that genuinely routes via test.api (needs Zscaler).
GATEWAY   = "https://api.salesforce.com/platform/mcp/v1"
HOSTED_SERVER = "industries/revenue-cloud"
# The custom server is a single constant so renaming it later is a one-line change. It is
# optional (RLM_MCP_CUSTOM_SERVER=0, matching the mcp_custom_server build flag): a stopgap
# until the hosted server covers place and clone. Without it there is one server and no
# multiplex proxy (write_connector_config.py connects the client to it directly).
CUSTOM_SERVER = "custom/RLMSalesTransactions"
CUSTOM_ENABLED = os.environ.get("RLM_MCP_CUSTOM_SERVER", "1").strip().lower() not in (
    "0", "false", "no", "off")
DEFAULT_SERVERS = HOSTED_SERVER + (f",{CUSTOM_SERVER}" if CUSTOM_ENABLED else "")


# Enhanced-domain org-type labels the legacy gateway routes under /sandbox.
_SANDBOX_KINDS = {"sandbox", "scratch"}


def gateway_bases(instance):
    """Gateway base URL(s) for an org, most specific first, comma-joined. With more than
    one, the proxy probes them in order; with one it skips probing.

    The org-pinned form, GATEWAY/d/<My Domain prefix>/<namespace>/<server>, names the org
    in the path and is where the platform is heading. Verified live on a production My
    Domain for platform/headless-360, industries/revenue-cloud and custom/<name>
    (2026-10-17).

    Enhanced domains put an org-type label between the prefix and my.salesforce.com, and
    that label is not part of the prefix:
        acme.my.salesforce.com                    production         -> pinned only
        acme--uat.sandbox.my.salesforce.com       sandbox
        <name>.scratch.my.salesforce.com          scratch (or .sandbox.)
        acme-dev-ed.develop.my.salesforce.com     Developer Edition (also demo, trailblaze, ...)
    Pinned routing is unverified for every non-production type, so those also list the
    legacy base as a fallback: /sandbox for sandbox and scratch, the plain base otherwise.
    Pre-enhanced hosts: any `--` prefix is a sandbox (acme--uat.my.salesforce.com,
    acme--uat.cs42.my.salesforce.com), and a `-dev-ed` prefix is a Developer Edition.
    A host that is not a My Domain gets the legacy base. SF_MCP_BASES overrides all of it,
    but only for the org it was exported with (see _env_is_for).
    """
    override = os.environ.get("SF_MCP_BASES")
    if override and _env_is_for(instance):
        return override
    host = (urllib.parse.urlparse(instance).hostname or "").lower()
    suffix = ".my.salesforce.com"
    if not host.endswith(suffix):
        return GATEWAY
    labels = host[: -len(suffix)].split(".")
    prefix, kind = labels[0], (labels[1] if len(labels) > 1 else "")
    if "--" in prefix:
        kind = "sandbox"
    elif not kind and prefix.endswith("-dev-ed"):
        kind = "develop"
    pinned = f"{GATEWAY}/d/{prefix}"
    if not kind:
        return pinned
    legacy = f"{GATEWAY}/sandbox" if kind in _SANDBOX_KINDS else GATEWAY
    return f"{pinned},{legacy}"


def _env_is_for(instance):
    """True when per-org env (SF_MCP_BASES, SF_MCP_SERVERS, SF_CSEC) belongs to `instance`.

    `env` exports SF_INSTANCE next to them, so in a shell that already eval'd org A, a
    lookup for org B must not inherit A's bases or secret. Unset SF_INSTANCE means the
    user set the override by hand for whatever org they are resolving."""
    current = os.environ.get("SF_INSTANCE", "").rstrip("/").lower()
    return not current or current == (instance or "").rstrip("/").lower()


def servers_for(instance):
    """Comma list of gateway servers for `instance`. SF_MCP_SERVERS overrides the default
    only for the org it was set for (see _env_is_for); `env` does not export it, so an
    eval'd shell never pins a list that RLM_MCP_CUSTOM_SERVER can no longer change."""
    override = os.environ.get("SF_MCP_SERVERS")
    return override if override and _env_is_for(instance) else DEFAULT_SERVERS


def _auth_mode():
    return os.environ.get("SF_AUTH_MODE", "").strip().lower().replace("-", "_")


def _sf_json(args):
    out = subprocess.run(args, capture_output=True, text=True).stdout
    i = out.find("{")                      # CLI warnings prepend non-JSON noise
    if i < 0:
        raise SystemExit(f"FATAL: no JSON from: {' '.join(args)}")
    return json.loads(out[i:])


def _load_profiles():
    try:
        with open(PROFILES) as f:
            return json.load(f)
    except Exception:
        return {}


def write_private(path, text):
    """Write `text` to `path` so it is NEVER readable by other users, not even briefly.

    The profile file can hold a consumer secret. open(...,"w") then chmod leaves a window
    at the process umask, and does nothing for a pre-existing looser file. Instead create
    a mkstemp temp file (O_CREAT|O_EXCL, mode 0600) in the same directory, fsync, then
    atomically os.replace() it over the target -- the target is only ever the 0600 inode.
    """
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".tmp-", suffix=".part")
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _save_profiles(p):
    try:
        write_private(PROFILES, json.dumps(p, indent=2))
    except OSError:
        # A restricted sandbox may forbid writes outside the workdir/$TMPDIR (PermissionError),
        # or the redirected parent dir may not exist (FileNotFoundError) — both are OSError.
        # The default ~/.rlm_mcp_orgs.json is then unwritable. Point the two home-dir stores at
        # a writable dir instead — both honour env overrides, no code change needed.
        raise SystemExit(
            f"FATAL: cannot write {PROFILES} (sandbox write block?).\n"
            f"       Redirect the home-dir state to a writable dir, e.g.:\n"
            f"         mkdir -p \"$PWD/.mcp-state\"   # gitignored\n"
            f"         export RLM_MCP_PROFILES=\"$PWD/.mcp-state/orgs.json\"\n"
            f"         export RLM_MCP_STATE=\"$PWD/.mcp-state/state\"   # proxy tool-list cache\n"
            f"       then re-run.")


def _retrieve_consumer_key(alias):
    """One-time: pull the ECA's consumerKey out of the org. Not a secret."""
    with tempfile.TemporaryDirectory() as td:
        r = subprocess.run(
            ["sf", "project", "retrieve", "start",
             "--metadata", f"ExtlClntAppGlobalOauthSettings:{ECA_NAME}_glbloauth",
             "--target-metadata-dir", td, "--target-org", alias, "--json"],
            capture_output=True, text=True)
        zp = os.path.join(td, "unpackaged.zip")
        if not os.path.exists(zp):
            raise SystemExit(
                f"FATAL: could not retrieve {ECA_NAME}_glbloauth from '{alias}'.\n"
                f"       Is the ECA deployed there? {r.stderr[:200]}")
        with zipfile.ZipFile(zp) as z:
            for n in z.namelist():
                if n.endswith(".ecaGlblOauth"):
                    m = re.search(r"<consumerKey>(.*?)</consumerKey>",
                                  z.read(n).decode(), re.S)
                    if m:
                        return m.group(1).strip()
    raise SystemExit(f"FATAL: no consumerKey in {ECA_NAME}_glbloauth on '{alias}'")


def resolve(alias=None, refresh=False):
    alias = alias or os.environ.get(ENV_VAR)
    if not alias:
        raise SystemExit(f"FATAL: set {ENV_VAR}=<sf alias> (or pass one as an argument)")
    d = _sf_json(["sf", "org", "display", "--target-org", alias, "--json"])
    if d.get("status") != 0:
        raise SystemExit(f"FATAL: '{alias}' is not an authenticated sf alias")
    res = d["result"]
    instance = res["instanceUrl"].rstrip("/")

    profiles = _load_profiles()
    prof = profiles.get(alias, {})
    cid = None if refresh else prof.get("consumer_key")
    if not cid or prof.get("instance") != instance:
        old = prof
        cid = _retrieve_consumer_key(alias)
        profiles[alias] = {"instance": instance, "consumer_key": cid,
                           "eca": ECA_NAME, "org_id": res.get("id"),
                           "username": res.get("username")}
        # Carry the secret over only if it still belongs to this exact instance + key
        # (a `refresh` of the same org keeps it; a repointed alias must not inherit it).
        if (old.get("consumer_secret") and old.get("instance") == instance
                and old.get("consumer_key") == cid):
            profiles[alias]["consumer_secret"] = old["consumer_secret"]
        _save_profiles(profiles)
        prof = profiles[alias]      # the OLD profile (and its secret) belonged to another org

    # Per-org state dir. The proxy's tool-list cache is keyed on SERVER NAME only
    # (toollist-<server>.json), and every org exposes the same server names — so without
    # this, org A's cached tools are served for org B. The proxy already honours
    # RLM_MCP_AUTH_DIR, so namespacing it is the whole fix: no proxy change needed.
    # Keyed on org id, not alias: an alias can be re-pointed at a different org.
    base_dir = os.path.expanduser(os.environ.get("RLM_MCP_STATE", "~/.config/rlm-mcp"))
    auth_dir = os.path.join(base_dir, res.get("id") or alias)

    # Consumer SECRET, only for SF_AUTH_MODE=client_credentials, which must be set
    # explicitly: the shipped ECA has the client credentials flow OFF, so a cached secret
    # alone must not switch an org's tooling to a flow its ECA refuses. Unlike the key it is NOT
    # retrievable from the org (metadata masks it), so it can only arrive from the
    # environment or a prior profile entry — copied by hand from Setup > External Client
    # Apps > RLM_McpClient > Consumer Details the first time.
    # Reuse a cached secret only if the profile still matches this instance AND key
    # (`prof` was reset above whenever the alias was repointed or the key re-retrieved).
    cached = prof.get("consumer_secret") if (
        prof.get("instance") == instance and prof.get("consumer_key") == cid) else None
    env_csec = os.environ.get("SF_CSEC") if _env_is_for(instance) else None
    csec = env_csec or cached
    if csec and cached != csec:
        profiles.setdefault(alias, {}).update(instance=instance, consumer_key=cid,
                                              consumer_secret=csec)
        _save_profiles(profiles)
    # The secret is deliberately NOT part of the returned dict: that dict is printed by
    # `json`/`show`. Callers that need it ask get_consumer_secret().

    return {"alias": alias, "instance": instance, "consumer_key": cid, "auth_dir": auth_dir,
            "has_secret": bool(csec), "secret_in_env": bool(env_csec),
            "auth_mode": _auth_mode(),
            "client_credentials": bool(csec) and _auth_mode() in ("client_credentials", "cc"),
            "org_id": res.get("id"), "username": res.get("username"),
            "api_version": res.get("apiVersion"), "eca": ECA_NAME,
            "bases": gateway_bases(instance), "servers": servers_for(instance),
            # mcp_auth.py namespaces its Keychain entry on exactly this pair
            "keychain_account": f"{instance.split('//')[-1]}|{cid}"}


def get_consumer_secret(alias=None):
    """The consumer secret for `alias` (env SF_CSEC, else the matching cached profile), or
    None. The only way to obtain it -- resolve()/json/show/env never carry or print it."""
    r = resolve(alias)
    if not r["has_secret"]:
        return None
    # Same scoping as resolve(): an SF_CSEC eval'd for another org must not be handed out
    # (or baked into a connector config) for this one.
    env_csec = os.environ.get("SF_CSEC") if _env_is_for(r["instance"]) else None
    return env_csec or _load_profiles().get(r["alias"], {}).get("consumer_secret")


def _fp(s):
    return hashlib.sha256(s.encode()).hexdigest()[:12]


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "show"
    alias = argv[2] if len(argv) > 2 else None
    if cmd == "list":
        for a, p in sorted(_load_profiles().items()):
            print(f"  {a:20s} {p.get('instance','')}  key:{_fp(p.get('consumer_key',''))}")
        return 0
    r = resolve(alias, refresh=(cmd == "refresh"))
    if cmd == "json":
        print(json.dumps(r, indent=2))   # no secret: resolve() never includes it
    elif cmd == "env":
        print(f"export SF_INSTANCE={r['instance']!r}")
        print(f"export SF_CID={r['consumer_key']!r}")
        print(f"export SF_MCP_BASES={r['bases']!r}")
        print(f"export RLM_MCP_AUTH_DIR={r['auth_dir']!r}")
        if r.get("client_credentials"):
            # NEVER echo the secret. If it is already in the environment, nothing to export;
            # otherwise emit a line that READS it from the 0600 profile at eval time.
            if not r["secret_in_env"]:
                jq_path = '.["%s"].consumer_secret' % r["alias"].replace("\\", "\\\\").replace('"', '\\"')
                print('export SF_CSEC="$(jq -r %s %s)"' % (shlex.quote(jq_path),
                                                          shlex.quote(PROFILES)))
            print("export SF_AUTH_MODE=client_credentials   # no browser, no Keychain")
        else:
            print("unset SF_CSEC SF_AUTH_MODE   # PKCE: isConsumerSecretOptional=true")
    else:
        print(f"  alias        : {r['alias']}")
        print(f"  org id       : {r['org_id']}   api v{r['api_version']}")
        print(f"  username     : {r['username']}")
        print(f"  instance     : {r['instance']}")
        print(f"  ECA          : {r['eca']}")
        print(f"  consumer key : <resolved> fingerprint {_fp(r['consumer_key'])} (len {len(r['consumer_key'])})")
        if r.get("client_credentials"):
            print("  auth         : client_credentials (secret present, not shown)")
        elif r.get("has_secret"):
            print("  auth         : PKCE (secret cached, not shown; export "
                  "SF_AUTH_MODE=client_credentials to use it — the ECA must allow that flow)")
        else:
            print("  auth         : PKCE (no secret)")
        print(f"  gateway      : {r['bases']}")
        print(f"  keychain acct: {r['keychain_account'][:48]}…")
        print(f"  state dir    : {r['auth_dir']}")
        print(f"  servers      : {r['servers']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
