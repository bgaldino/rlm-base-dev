# MCP client tooling

The org-side MCP surface — the External Client Application, the clone invocable, the
server activations — is built by this repo: `unpackaged/post_mcp/`,
`unpackaged/post_mcp_custom/` and `tasks/rlm_mcp.py`, orchestrated by the `prepare_mcp` flow. That gets an org *serving* MCP. These scripts are what makes a workstation able to
*talk* to it: resolve an org, authenticate, and present several servers to an agent as
one connector.

Read `.cursor/skills/mcp-integration/SKILL.md` first — it covers the surface, why the
clone invocable needs a 264 org, and the validation commands.

## Contents

| Script | Role |
|---|---|
| `mcp_org.py` | Resolve an org from one env var (`RLM_MCP_ORG`) or an argument: instance URL, ECA consumer key, org-pinned gateway bases, per-org state dir |
| `mcp_auth.py` | PKCE login against the ECA, refresh-token cache, access tokens for scripts |
| `mcp_multiplex_proxy.py` | Fan the hosted `industries/revenue-cloud` server plus the custom `custom/RLMSalesTransactions` server into a single connector over one warm token |
| `write_connector_config.py` | Write a folder's `.mcp.json` pointing at the proxy, or straight at the one server when the custom server is off |

## Environment

| Variable | Meaning | Default |
|---|---|---|
| `RLM_MCP_ORG` | sf CLI alias of the target org | none (or pass as argument) |
| `RLM_MCP_ECA` | ECA developer name used to read the consumer key | `RLM_McpClient` |
| `RLM_MCP_PROFILES` | Per-alias profile cache (0600) | `~/.rlm_mcp_orgs.json` |
| `RLM_MCP_STATE` | Base dir for per-org state | `~/.config/rlm-mcp` |
| `RLM_MCP_AUTH_DIR` | Token cache and tool-list cache dir; `mcp_org.py env` sets it per org id | `~/.config/rlm-mcp` |
| `SF_INSTANCE`, `SF_CID` | Org instance URL and ECA consumer key (emitted by `mcp_org.py env`) | resolved |
| `SF_USER_ID` | Id of the alias's user (emitted by `mcp_org.py env`). The token cache is keyed on it, and a login as anyone else is refused | resolved |
| `SF_MCP_SERVERS` | Explicit comma list of gateway server suffixes; honoured only while `SF_INSTANCE` names the same org (or is unset); not exported by `mcp_org.py env`, which unsets one left from another org | `industries/revenue-cloud,custom/RLMSalesTransactions` |
| `RLM_MCP_CUSTOM_SERVER` | `0`/`false`/`no`/`off` drops the custom server from the default list (an explicit `SF_MCP_SERVERS` still wins) | on |
| `SF_MCP_BASES` / `SF_MCP_BASE` | Explicit gateway base override. `mcp_org.py env` re-exports `SF_MCP_BASES` and unsets an `SF_MCP_BASE` left from another org | derived from `SF_INSTANCE` |
| `SF_AUTH_MODE` | `client_credentials` to opt in to that flow | unset (PKCE) |
| `SF_CSEC` | Consumer secret, only used with `client_credentials` | unset |

## Without the custom server

The custom `RLMSalesTransactions` server is a stopgap until the hosted `revenue-cloud`
server covers place and clone, so it is optional at both ends. On the org, set the
`mcp_custom_server` flag to `false` (only the ECA and hosted activations are built). On
the workstation, export `RLM_MCP_CUSTOM_SERVER=0` before running
`write_connector_config.py` or the proxy. With one server and PKCE, `.mcp.json` is an HTTP entry
pointing the client straight at that server with the ECA consumer key and callback port
8080, so the client runs the OAuth login itself: no proxy, no `mcp_auth.py login`, no
`--prime`. When the org has fallback gateway bases only the first is used; set
`SF_MCP_BASES` to the one that works if the client cannot connect. `client_credentials`
still goes through the proxy. Direct mode is not yet verified live: only the shape of
the entry is tested, not Claude Code's own OAuth against the gateway.

## Gateway endpoint

By default the proxy targets the org-pinned endpoint,
`https://api.salesforce.com/platform/mcp/v1/d/<My Domain prefix>/<namespace>/<server>`,
derived from `SF_INSTANCE` by `mcp_org.gateway_bases`, so a config targets exactly one org.
Production My Domains get only the pinned base. Sandbox and scratch orgs also list the
legacy `/v1/sandbox` base as a fallback; other enhanced-domain types (`develop`, `demo`, …)
list the plain `/v1` base. A host that is not a My Domain uses the legacy base. Set
`SF_MCP_BASES` (or `SF_MCP_BASE`) to override all of it.

## Authentication

PKCE (`authorization_code`) is the default: the ECA has `isConsumerSecretOptional=true`,
so the consumer key alone suffices, one browser login per workstation per org, then silent
refresh.

`client_credentials` is an explicit opt-in: export `SF_AUTH_MODE=client_credentials` and
provide a consumer secret (`SF_CSEC`, or cached in the profile). A cached secret alone never
switches modes. The shipped ECA has the client credentials flow **off**, so you must first
enable it on the ECA (OAuth policy: client credentials flow plus a run-as user) or the
token request will be refused.

## Usage

```bash
# 1. Resolve an org into the environment (sf CLI alias, not the cci alias)
eval "$(python3 scripts/mcp/mcp_org.py env <sf-alias>)"
python3 scripts/mcp/mcp_org.py show <sf-alias>     # inspect; key fingerprinted, not printed

# 2. Authenticate — one browser click, once per workstation per org
python3 scripts/mcp/mcp_auth.py login
python3 scripts/mcp/mcp_auth.py status

# 3. Wire an agent connector for a folder, and warm the tool-list cache (refetched once
#    it is a day old; re-run --prime to pick up a server change sooner)
python3 scripts/mcp/write_connector_config.py <sf-alias> --prime

# Or drive the proxy directly
python3 scripts/mcp/mcp_multiplex_proxy.py --prime
```

The consumer key is read from the org at run time, so there is no secret to distribute.
`.mcp.json` is gitignored: it embeds a resolved instance URL and consumer key, plus a
consumer secret when running in `client_credentials` mode.
Files that can hold a secret (`.mcp.json`, `~/.rlm_mcp_orgs.json`, the file token cache) are
created `0600` atomically (temp file + `os.replace`), never written then chmodded. `mcp_org.py`
`json`/`show`/`env` never print the consumer secret; `env` emits a `jq` line that reads it from
the profile at `eval` time instead. Refresh tokens rotate, so refresh is serialised across
processes with a per-account `flock` under the cache dir. The file token cache is shared
by every account, so its read-modify-replace also takes a file-wide lock (inside the
account lock); `mcp_org.py` locks its update of the shared profile file the same way
(the lock file, `<profiles>.lock`, stays beside it and is safe to delete when idle). A
profile's cached consumer key is re-retrieved when the alias's instance or `RLM_MCP_ECA`
changes. On the PKCE path (`mcp_auth.py` and the proxy) a cached credential belongs to one
(org, ECA, user): two aliases for different users of the same org hold separate tokens, and
`mcp_auth.py login` refuses, caching nothing, when the browser signs in as someone other
than the alias's user (`SF_USER_ID`), which is usually a browser already signed in to the
org. The tool-list cache stays per org. A direct-mode entry uses the client's own OAuth
and token store instead, and `client_credentials` always acts as the ECA's run-as user.
Without `SF_USER_ID` (a shell or `.mcp.json` from before it existed) the cache falls back
to one entry per org and `mcp_auth.py` warns; re-run `mcp_org.py env` or
`write_connector_config.py`, then `mcp_auth.py login`. The old per-org entry is not
removed by `logout`; delete it by hand (macOS:
`security delete-generic-password -s rlm-mcp -a '<host>|<consumer key>'`, elsewhere its key
in `refresh-tokens.json`). The ECA's refresh-token policy is a 365-day `SpecificLifetime`, and with
`isSecretRequiredForRefreshToken=false` the refresh grant sends no `client_secret` (PKCE,
key only).

## Prerequisites

The org must already have the surface — `cci flow run prepare_mcp --org <cci-alias>`, or
the tasks individually — and the `mcp` feature flag is **off** by default precisely
because the flow cannot perform step 2 above for anyone. `mcp_org.py` fails with a clear
message when the ECA is not deployed, since that is where it reads the consumer key.

`prepare_mcp` grants `RLM_McpSalesTransactions` (class access to the clone invocable) to
the user who runs it, and nobody else. Any other user who logs in to the custom server keeps
the other tools (subject to their normal Revenue Cloud permissions) but gets an
authorization failure on `cloneSalesTransaction` until they hold it. Assign it per MCP user:

```bash
sf org assign permset --name RLM_McpSalesTransactions --on-behalf-of <username> --target-org <sf-alias>
```
