# MCP client tooling

The org-side MCP surface — the External Client Application, the clone invocable, the
server activations — is built by this repo: `unpackaged/post_mcp/`,
`unpackaged/post_mcp_264/`, and `tasks/rlm_mcp.py`, orchestrated by the `prepare_mcp`
flow. That gets an org *serving* MCP. These scripts are what makes a workstation able to
*talk* to it: resolve an org, authenticate, and present several servers to an agent as
one connector.

Read `.cursor/skills/mcp-integration/SKILL.md` first — it covers the surface, the release
skew behind the two copies of the clone invocable, and the validation commands.

## Contents

| Script | Role | Origin |
|---|---|---|
| `ramp_org.py` | Resolve an org from one env var (`RAMP_MCP_ORG`) or an argument: instance URL, ECA consumer key, per-org state dir | vendored |
| `ramp_auth.py` | PKCE login against the ECA, refresh-token cache, access tokens for scripts | vendored |
| `mcp_multiplex_proxy.py` | Fan several hosted servers plus the custom server into a single connector over one warm token | vendored |
| `write_connector_config.py` | Write a folder's `.mcp.json` pointing at the proxy | this repo |

## Vendored, not forked

The three scripts marked *vendored* are **byte-identical copies** of `ramp-demo-kit`'s
`tools/ramp_org.py`, `tools/ramp_auth.py`, and `tools/mcp_multiplex_proxy.py`. That is
deliberate, and so is keeping their original filenames: identical names and identical
bytes mean drift is a one-line `diff`, and either copy can be updated from the other
without a merge. Renaming them would have bought tidier names at the cost of making the
two copies impossible to compare mechanically — a bad trade for code that must stay in
step across two repos.

Consequences worth knowing:

- **Do not "clean up" a vendored file here.** Fix it in the kit, then re-vendor, or fix
  it here and port the identical change back. `tests/test_mcp_tooling_vendored.py` fails
  when a copy drifts and the kit's clone is resolvable.
- Their internal env var names stay in the `RAMP_*` / `SF_*` namespace the kit
  established (`RAMP_MCP_ORG`, `RAMP_AUTH_DIR`, `SF_CID`, `SF_MCP_SERVERS`), because both
  copies must honour the same environment.
- `write_connector_config.py` is **ours**, not vendored. The kit's equivalent
  (`setup/link_demo.py`) writes into its fixed `demos/native` and `demos/cohort` layout,
  which Foundations has no counterpart for; this one takes any directory.

## Usage

```bash
# 1. Resolve an org into the environment (sf CLI alias, not the cci alias)
eval "$(python3 scripts/mcp/ramp_org.py env <sf-alias>)"
python3 scripts/mcp/ramp_org.py show <sf-alias>     # inspect; key fingerprinted, not printed

# 2. Authenticate — one browser click, once per workstation per org
python3 scripts/mcp/ramp_auth.py login
python3 scripts/mcp/ramp_auth.py status

# 3. Wire an agent connector for a folder, and warm the tool-list cache
python3 scripts/mcp/write_connector_config.py <sf-alias> --prime

# Or drive the proxy directly
python3 scripts/mcp/mcp_multiplex_proxy.py --prime
```

The consumer key is read from the org at run time, so there is no secret to distribute.
`.mcp.json` is gitignored: it embeds a resolved instance URL and consumer key, plus a
consumer secret when running in `client_credentials` mode.

## Prerequisites

The org must already have the surface — `cci flow run prepare_mcp --org <cci-alias>`, or
the three tasks individually — and the `mcp` feature flag is **off** by default precisely
because the flow cannot perform step 2 above for anyone. `ramp_org.py` fails with a clear
message when the ECA is not deployed, since that is where it reads the consumer key.
