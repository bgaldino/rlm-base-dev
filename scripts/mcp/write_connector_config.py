#!/usr/bin/env python3
"""write_connector_config.py — write a folder's .mcp.json so an agent opened there
gets the org's MCP servers with no hand-wiring.

    python3 scripts/mcp/write_connector_config.py <sf-alias>              # into $PWD
    python3 scripts/mcp/write_connector_config.py <sf-alias> <dir> [dir…] # into each
    python3 scripts/mcp/write_connector_config.py <sf-alias> --prime      # …and warm the cache

WHY A PROJECT-SCOPED FILE AT ALL
    A .mcp.json auto-loads for the directory the agent opens, so there is no scope or
    directory mismatch to fight. But it needs an ABSOLUTE path to the proxy plus the
    org's resolved environment, and hand-writing that is the most error-prone step in
    the whole setup — a wrong path fails as a silent "no MCP server" rather than an
    error. Everything here is derived instead: the proxy path from this file's location,
    and SF_INSTANCE / SF_CID / RLM_MCP_AUTH_DIR from mcp_org.py.

AUTH MODE
    PKCE by default, which needs `mcp_auth.py login` once per workstation. With
    SF_AUTH_MODE=client_credentials exported AND a consumer secret available (SF_CSEC, or
    cached in the org profile), the file is written for client_credentials instead: no
    browser login, no Keychain, no cached refresh token. That is opt-in because the
    shipped ECA has the client credentials flow off; enable it in Setup first.

    The gateway base is the org-pinned form derived from the instance URL
    (mcp_org.gateway_bases), so the file targets exactly one org.

ONE SERVER, NO PROXY
    The proxy exists to fan the hosted server and the custom one into a single
    connector. With the custom server off (RLM_MCP_CUSTOM_SERVER=0, or SF_MCP_SERVERS
    naming one server) and PKCE auth, the file instead points the client straight at
    that server over HTTP with the ECA's consumer key, and the client runs the OAuth
    login itself on localhost:8080 (a callback the ECA registers). No proxy, no
    `mcp_auth.py login`, no --prime. client_credentials still goes through the proxy,
    which is what mints those tokens.

    .mcp.json is gitignored on purpose. With a secret in it, that matters more, not less.
    Never commit one.
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PROXY = os.path.join(HERE, "mcp_multiplex_proxy.py")
RESOLVER = os.path.join(HERE, "mcp_org.py")

# One connector name, because the proxy is what fans several upstream servers into it.
CONNECTOR_NAME = "revenue-cloud"
# Direct (no-proxy) mode: the ECA registers http://localhost:8080/callback exactly.
DIRECT_CALLBACK_PORT = 8080


def resolve(alias):
    """Resolve in-process (not via `mcp_org.py json`): the secret is never printed, so it
    cannot be read from a subprocess's stdout -- ask mcp_org for it directly."""
    sys.path.insert(0, HERE)
    import mcp_org
    resolved = mcp_org.resolve(alias)
    resolved["consumer_secret"] = mcp_org.get_consumer_secret(alias)
    return resolved


def build_env(resolved):
    env = {
        "SF_INSTANCE": resolved["instance"],
        "SF_CID": resolved["consumer_key"],
        "SF_USER_ID": resolved["user_id"],
        "SF_MCP_BASES": resolved["bases"],
        "SF_MCP_SERVERS": resolved["servers"],
        "RLM_MCP_AUTH_DIR": resolved["auth_dir"],
    }
    if resolved.get("client_credentials") and resolved.get("consumer_secret"):
        env["SF_CSEC"] = resolved["consumer_secret"]
        env["SF_AUTH_MODE"] = "client_credentials"
    return env


def _write_private(path, text):
    """Create `path` as 0600 from the first byte (mkstemp temp in the same dir + atomic
    os.replace), so a secret in it is never readable at the process umask and an existing
    looser-mode file is replaced rather than rewritten in place."""
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix=".mcp-", suffix=".part")
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def servers(resolved):
    return [s.strip() for s in resolved["servers"].split(",") if s.strip()]


def is_direct(resolved, env):
    """One upstream and PKCE: connect the client to it directly, without the proxy."""
    return len(servers(resolved)) == 1 and "SF_CSEC" not in env


def proxy_entry(env):
    return {"command": sys.executable, "args": [PROXY], "env": env}


def direct_entry(resolved):
    """HTTP entry for the single server. The first gateway base is the most specific one
    (mcp_org.gateway_bases); a multi-base org has no proxy here to probe the others."""
    base = resolved["bases"].split(",")[0].strip().rstrip("/")
    return {"type": "http", "url": f"{base}/{servers(resolved)[0]}",
            "oauth": {"clientId": resolved["consumer_key"],
                      "callbackPort": DIRECT_CALLBACK_PORT}}


def write_config(directory, entry):
    target = os.path.abspath(directory)
    if not os.path.isdir(target):
        raise SystemExit(f"FATAL: not a directory: {target}")

    config = {"mcpServers": {CONNECTOR_NAME: entry}}
    path = os.path.join(target, ".mcp.json")
    try:
        _write_private(path, json.dumps(config, indent=2))
    except PermissionError:
        # Some agent harnesses specifically forbid an agent from writing any .mcp.json,
        # as a guard against an agent rewiring its own connectors. A human running the
        # same command in a normal shell writes it fine.
        raise SystemExit(
            f"FATAL: cannot write {path} — the agent harness blocks agents from writing\n"
            f"       .mcp.json. Run this same command yourself in a normal terminal, then\n"
            f"       reopen the agent on that folder."
        )
    return path


def display(path):
    """Show a repo-relative path when inside the repo, else an absolute one."""
    relative = os.path.relpath(path, REPO)
    return relative if not relative.startswith("..") else path


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("-")]
    if not args:
        raise SystemExit(__doc__)

    alias = args[0]
    directories = args[1:] or [os.getcwd()]

    resolved = resolve(alias)
    env = build_env(resolved)
    direct = is_direct(resolved, env)
    if not direct and not os.path.exists(PROXY):
        raise SystemExit(f"FATAL: proxy not found at {PROXY}")
    entry = direct_entry(resolved) if direct else proxy_entry(env)

    print(f"  org {resolved['alias']} ({resolved['org_id']})  ->  {resolved['instance']}")
    if direct:
        print(f"  server {entry['url']}  (direct, no proxy)")
        if "," in resolved["bases"]:
            print(f"  NOTE: this org has fallback gateway bases ({resolved['bases']}); without\n"
                  f"        the proxy only the first is used. If the client cannot connect,\n"
                  f"        export SF_MCP_BASES=<the base that works> and re-run.")
    else:
        print(f"  gateway {resolved['bases']}")
        print(f"  servers {resolved['servers']}")
    if "SF_CSEC" in env:
        auth = "client_credentials (no login needed)"
    elif direct:
        auth = f"PKCE, the client logs in on first use (callback localhost:{DIRECT_CALLBACK_PORT})"
    else:
        auth = "PKCE (needs `mcp_auth.py login` once)"
    print(f"  auth: {auth}")
    written = [write_config(directory, entry) for directory in directories]
    for path in written:
        print(f"  wrote {display(path)}")

    if "--prime" in argv and direct:
        print("  --prime skipped: it warms the proxy's cache, and there is no proxy here.")
    elif "--prime" in argv:
        print("  priming tool-list cache…")
        proxy_env = dict(os.environ, **env)
        if "SF_CSEC" not in env:
            proxy_env.pop("SF_CSEC", None)
            proxy_env.pop("SF_AUTH_MODE", None)
        code = subprocess.run(
            [sys.executable, PROXY, "--prime"], env=proxy_env
        ).returncode
        if code != 0:
            print(
                "  prime FAILED — run `mcp_auth.py login` first, then check the gateway."
            )
            return code

    print(
        f"""
  Next: QUIT the agent and REOPEN it on {display(written[0])[:-len('/.mcp.json')] or '.'}
  Connectors do not hot-reload, and a folder without a .mcp.json loads none at all."""
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
