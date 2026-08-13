#!/usr/bin/env python3
"""write_connector_config.py — write a folder's .mcp.json so an agent opened there
gets the org's MCP servers with no hand-wiring.

    python3 scripts/mcp/write_connector_config.py <sf-alias>              # into $PWD
    python3 scripts/mcp/write_connector_config.py <sf-alias> <dir> [dir…] # into each
    python3 scripts/mcp/write_connector_config.py <sf-alias> --prime      # …and warm the cache

WHY THIS IS NOT VENDORED
    The other three scripts here are byte-identical copies of ramp-demo-kit's (see
    README.md). Its equivalent, setup/link_demo.py, is the one that could not be: it
    writes into a fixed demos/native and demos/cohort layout that Foundations has no
    counterpart for. This does the same job against any directory you name.

WHY A PROJECT-SCOPED FILE AT ALL
    A .mcp.json auto-loads for the directory the agent opens, so there is no scope or
    directory mismatch to fight. But it needs an ABSOLUTE path to the proxy plus the
    org's resolved environment, and hand-writing that is the most error-prone step in
    the whole setup — a wrong path fails as a silent "no MCP server" rather than an
    error. Everything here is derived instead: the proxy path from this file's location,
    and SF_INSTANCE / SF_CID / RAMP_AUTH_DIR from ramp_org.py.

AUTH MODE
    With a consumer secret available — SF_CSEC in the environment, or cached in the org
    profile from an earlier run — the file is written for client_credentials: no browser
    login, no Keychain, no cached refresh token, so it works on a workstation that has
    never run any of this. Without one it falls back to PKCE, which needs
    `ramp_auth.py login` once per workstation.

    .mcp.json is gitignored on purpose. With a secret in it, that matters more, not less.
    Never commit one.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
PROXY = os.path.join(HERE, "mcp_multiplex_proxy.py")
RESOLVER = os.path.join(HERE, "ramp_org.py")

# One connector name, because the proxy is what fans several upstream servers into it.
CONNECTOR_NAME = "revenue-cloud"


def resolve(alias):
    result = subprocess.run(
        [sys.executable, RESOLVER, "json", alias], capture_output=True, text=True
    )
    if result.returncode != 0:
        raise SystemExit(
            f"FATAL: ramp_org.py could not resolve '{alias}':\n"
            f"{result.stderr.strip()[:400]}"
        )
    return json.loads(result.stdout[result.stdout.find("{"):])


def build_env(resolved):
    env = {
        "SF_INSTANCE": resolved["instance"],
        "SF_CID": resolved["consumer_key"],
        "SF_MCP_BASES": resolved["bases"],
        "SF_MCP_SERVERS": resolved["servers"],
        "RAMP_AUTH_DIR": resolved["auth_dir"],
    }
    if resolved.get("consumer_secret"):
        env["SF_CSEC"] = resolved["consumer_secret"]
        env["SF_AUTH_MODE"] = "client_credentials"
    return env


def write_config(directory, env):
    target = os.path.abspath(directory)
    if not os.path.isdir(target):
        raise SystemExit(f"FATAL: not a directory: {target}")

    config = {
        "mcpServers": {
            CONNECTOR_NAME: {
                "command": sys.executable,
                "args": [PROXY],
                "env": env,
            }
        }
    }
    path = os.path.join(target, ".mcp.json")
    try:
        with open(path, "w") as handle:
            json.dump(config, handle, indent=2)
        os.chmod(path, 0o600)
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

    if not os.path.exists(PROXY):
        raise SystemExit(f"FATAL: proxy not found at {PROXY}")

    resolved = resolve(alias)
    env = build_env(resolved)

    print(f"  org {resolved['alias']} ({resolved['org_id']})  ->  {resolved['instance']}")
    print(
        "  auth: "
        + (
            "client_credentials (no login needed)"
            if resolved.get("consumer_secret")
            else "PKCE (needs `ramp_auth.py login` once)"
        )
    )
    written = [write_config(directory, env) for directory in directories]
    for path in written:
        print(f"  wrote {display(path)}")

    if "--prime" in argv:
        print("  priming tool-list cache…")
        proxy_env = dict(os.environ, **env)
        if not resolved.get("consumer_secret"):
            proxy_env.pop("SF_CSEC", None)
        code = subprocess.run(
            [sys.executable, PROXY, "--prime"], env=proxy_env
        ).returncode
        if code != 0:
            print(
                "  prime FAILED — run `ramp_auth.py login` first, then check the gateway."
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
