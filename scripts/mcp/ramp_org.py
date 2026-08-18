#!/usr/bin/env python3
"""ramp_org.py — resolve a target org for the ramp MCP tooling from ONE env var.

    RAMP_MCP_ORG=<sf-cli alias>

Deliberately NOT `SF_ORG`, for two reasons: the `SF_*` namespace belongs to the Salesforce
CLI (`SF_TARGET_ORG`, `SF_ORG_API_VERSION`, `SF_ORG_INSTANCE_URL`, …) where a collision could
silently retarget the CLI itself; and `SF_ORG` is ALREADY taken inside this toolkit — it is
the sf-CLI alias read by mcp_invoke_ramp.py / mcp_invoke_clone.py / ramp_planner.py for
read-back SOQL. `RAMP_MCP_ORG` is the user-facing switch; `env` still EMITS `SF_ORG` (same
value) so those existing consumers work unchanged.

WHAT IT RESOLVES (and why no secret is needed)
    instance URL  <- `sf org display --target-org <alias>`  (authoritative, always current)
    consumer key  <- profile cache, else a one-time Metadata retrieve of
                     ExtlClntAppGlobalOauthSettings:<eca>_glbloauth from the org
    consumer secret — NOT resolved and NOT required. The ECA sets
                     isConsumerSecretOptional=true, so authorization_code + PKCE (S256)
                     completes with the consumer key alone. Verified live on 264-upgrade.
    refresh token <- already namespaced by ramp_auth.py on (instance, client_id), so two
                     orgs never share a cached token. Nothing to do here.

Emits `SF_INSTANCE` / `SF_CID` so the EXISTING mcp_multiplex_proxy.py and ramp_auth.py work
unchanged — this is a resolver in front of them, not a rewrite.

USAGE
    python3 ramp_org.py env  [alias]     # shell exports:  eval "$(ramp_org.py env sdb39-revmcp)"
    python3 ramp_org.py show [alias]     # human-readable, key fingerprinted not printed
    python3 ramp_org.py json [alias]     # machine-readable
    python3 ramp_org.py list             # every alias with a cached profile
Alias precedence: argv[2] > $RAMP_MCP_ORG.
"""
import hashlib, json, os, re, subprocess, sys, tempfile, zipfile

# Restricted sandboxes (e.g. Claude Code's Bash tool) forbid writes outside the workdir
# and $TMPDIR. The `sf` CLI otherwise tries to write ~/.sf/sf-<date>.log, gets EPERM, and
# dies before emitting JSON — which reads to callers as "org not authenticated" (a false
# negative that once made bootstrap --check lie). Default the CLI's own kill-switch on;
# a user who needs the log can still export SF_DISABLE_LOG_FILE=false to override.
os.environ.setdefault("SF_DISABLE_LOG_FILE", "true")

ENV_VAR   = "RAMP_MCP_ORG"
ECA_NAME  = os.environ.get("RAMP_MCP_ECA", "ClaudeMcpClientRC")
PROFILES  = os.path.expanduser(os.environ.get("RAMP_MCP_PROFILES", "~/.ramp_mcp_orgs.json"))
# PROD ONLY by default. `revenue-cloud` is published only on the prod gateway — test.api
# answers `404 Server definition not found` for it, so listing test.api as a fallback just
# buys a wasted probe on startup and a confusing 404 in the logs. A single candidate also
# lets the proxy skip base-probing entirely. Override with SF_MCP_BASES for an internal /
# pc-rnd org that genuinely routes via test.api (needs Zscaler) — see kit CLAUDE.md §5.
BASES     = os.environ.get("SF_MCP_BASES", "https://api.salesforce.com/platform/mcp/v1")
SERVERS   = os.environ.get("SF_MCP_SERVERS", "industries/revenue-cloud,custom/rampdealsconnect")


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


def _save_profiles(p):
    try:
        with open(PROFILES, "w") as f:
            json.dump(p, f, indent=2)
        os.chmod(PROFILES, 0o600)
    except OSError:
        # A restricted sandbox may forbid writes outside the workdir/$TMPDIR (PermissionError),
        # or the redirected parent dir may not exist (FileNotFoundError) — both are OSError.
        # The default ~/.ramp_mcp_orgs.json is then unwritable. Point the two home-dir stores at
        # a writable dir instead — both honour env overrides, no code change needed.
        raise SystemExit(
            f"FATAL: cannot write {PROFILES} (sandbox write block?).\n"
            f"       Redirect the kit's home-dir state to a writable dir, e.g.:\n"
            f"         export RAMP_MCP_PROFILES=\"$PWD/.ramp/orgs.json\"\n"
            f"         export RAMP_MCP_STATE=\"$PWD/.ramp/state\"   # proxy tool-list cache\n"
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
        cid = _retrieve_consumer_key(alias)
        profiles[alias] = {"instance": instance, "consumer_key": cid,
                           "eca": ECA_NAME, "org_id": res.get("id"),
                           "username": res.get("username")}
        _save_profiles(profiles)

    # Per-org state dir. The proxy's tool-list cache is keyed on SERVER NAME only
    # (toollist-<server>.json), and every org exposes the same server names — so without
    # this, org A's cached tools are served for org B. The proxy already honours
    # RAMP_AUTH_DIR, so namespacing it is the whole fix: no proxy change needed.
    # Keyed on org id, not alias: an alias can be re-pointed at a different org.
    base_dir = os.path.expanduser(os.environ.get("RAMP_MCP_STATE", "~/.config/rlm-ramp"))
    auth_dir = os.path.join(base_dir, res.get("id") or alias)

    # Consumer SECRET, only for SF_AUTH_MODE=client_credentials. Unlike the key it is NOT
    # retrievable from the org (metadata masks it), so it can only arrive from the
    # environment or a prior profile entry — copied by hand from Setup > External Client
    # Apps > ClaudeMcpClientRC > Consumer Details the first time.
    csec = os.environ.get("SF_CSEC") or prof.get("consumer_secret")
    if csec and prof.get("consumer_secret") != csec:
        profiles.setdefault(alias, {}).update(instance=instance, consumer_key=cid,
                                              consumer_secret=csec)
        _save_profiles(profiles)

    return {"alias": alias, "instance": instance, "consumer_key": cid, "auth_dir": auth_dir,
            "consumer_secret": csec, "auth_mode": os.environ.get("SF_AUTH_MODE", ""),
            "org_id": res.get("id"), "username": res.get("username"),
            "api_version": res.get("apiVersion"), "eca": ECA_NAME,
            "bases": BASES, "servers": SERVERS,
            # ramp_auth.py namespaces its Keychain entry on exactly this pair
            "keychain_account": f"{instance.split('//')[-1]}|{cid[:60]}"}


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
        print(json.dumps(r, indent=2))
    elif cmd == "env":
        print(f"export SF_INSTANCE={r['instance']!r}")
        # SF_ORG is this toolkit's PRE-EXISTING name for the sf-CLI alias (mcp_invoke_ramp,
        # mcp_invoke_clone, ramp_planner all read it for read-back SOQL). Emit it so those
        # keep working untouched — RAMP_MCP_ORG is the user-facing switch, SF_ORG is derived.
        print(f"export SF_ORG={r['alias']!r}")
        print(f"export SF_CID={r['consumer_key']!r}")
        print(f"export SF_MCP_BASES={r['bases']!r}")
        print(f"export SF_MCP_SERVERS={r['servers']!r}")
        print(f"export RAMP_AUTH_DIR={r['auth_dir']!r}")
        if r.get("consumer_secret"):
            print(f"export SF_CSEC={r['consumer_secret']!r}")
            print("export SF_AUTH_MODE=client_credentials   # no browser, no Keychain")
        else:
            print("unset SF_CSEC   # PKCE only: isConsumerSecretOptional=true")
    else:
        print(f"  alias        : {r['alias']}")
        print(f"  org id       : {r['org_id']}   api v{r['api_version']}")
        print(f"  username     : {r['username']}")
        print(f"  instance     : {r['instance']}")
        print(f"  ECA          : {r['eca']}")
        print(f"  consumer key : <resolved> fingerprint {_fp(r['consumer_key'])} (len {len(r['consumer_key'])})")
        if r.get("consumer_secret"):
            print(f"  secret       : present, fingerprint {_fp(r['consumer_secret'])} "
                  f"-> client_credentials available (no browser)")
        else:
            print(f"  secret       : not set (PKCE path; pass SF_CSEC once for "
                  f"client_credentials)")
        print(f"  keychain acct: {r['keychain_account'][:48]}…")
        print(f"  state dir    : {r['auth_dir']}")
        print(f"  servers      : {r['servers']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
