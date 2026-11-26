# Sandboxed agents: `sf`, deploys and a browser from the Claude Code sandbox

Read this when an agent (a spawned subagent, or any session whose Bash runs in the
Claude Code sandbox) must query, run Apex, write records, deploy metadata or open a
browser on a scratch org. Everything below was measured; each section carries its
tag. The sandbox is a boundary, not an obstacle: do not retry a failing `sf` call
unsandboxed. The recipes make that retry unnecessary, except for the browser.

## 1. `sf` inside the sandbox

[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build; sf CLI 2.x]

```bash
export SF_DISABLE_LOG_FILE=true SF_DISABLE_TELEMETRY=true SF_AUTOUPDATE_DISABLE=true
sf data query -q "SELECT COUNT() FROM Account" --target-org <sf alias or username>
```

- Bash `allowed_domains` must include the org's `<host>.my.salesforce.com`,
  `*.my.salesforce.com` and `*.salesforce.com`. Without them the calls fail on the
  network, not on a permission.
- `SF_DISABLE_LOG_FILE=true` is required. Without it sf tries to write
  `~/.sf/sf-<date>.log`, which the sandbox denies (it also crashed once on the date
  rollover).
- Use `--target-org <username or sf alias>` (see AGENTS.md, Org Identity). A
  `failed to copy trust settings of system certificate` stderr line is harmless;
  filter it (`2>&1 | rg -v trust`) and parse JSON from stdout only (`2>/dev/null`).
- `cci` cannot run sandboxed (it writes `~/.cumulusci`). Use `sf`, or have the
  coordinating session run the cci task.

What works sandboxed (all measured):

| Need | Command |
|------|---------|
| SOQL | `sf data query -q "..." --target-org <o>` (`--use-tooling-api` for Tooling objects) |
| Anonymous Apex | `sf apex run -f script.apex --target-org <o>`; read `USER_DEBUG` lines from the log it prints |
| Create a record | `sf data create record -s Account -v "Name='x'" --target-org <o>` |
| Any REST call | `sf api request rest "/services/data/v68.0/..." --target-org <o>` |
| Frontdoor URL for a browser | `sf org open --url-only --json --target-org <o>` (a live session: keep it in the process, never write it down) |

## 2. Metadata deploys: EPERM, and the readback route

[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build]

`sf project deploy start` is **submitted** and then dies with
`EPERM: operation not permitted, mkdir '~/.sf/deploy-cache.json.lock'`. The deploy
runs on the server regardless. So a sandboxed deploy is: submit, ignore the EPERM,
read the outcome from the org.

1. Build a metadata-format directory with a `package.xml` (without it the deploy
   records `Failed` with 0 components) and submit it:
   `sf project deploy start --metadata-dir <dir> --target-org <o> --wait 5`.
   [Open: `--source-dir` deploys were reported to hit the same EPERM; not re-measured.]
2. Find the request: `sf data query --use-tooling-api -q "SELECT Id,Status,NumberComponentsDeployed,NumberComponentErrors FROM DeployRequest ORDER BY CreatedDate DESC LIMIT 1" --target-org <o>`.
   Wait until `Status` is `Succeeded` or `Failed`.
3. Read the failures: `sf api request rest "/services/data/v68.0/metadata/deployRequest/<id>?includeDetails=true" --target-org <o> 2>/dev/null | jq '.deployResult.details.componentFailures'`.
4. Confirm the artefact exists with a query (for example Tooling `ApexClass`).

Other routes that need no deploy: Tooling API `create` (Apex, custom fields) and
REST/Tooling PATCH. [Open: reported by earlier runs, not re-measured here: a profile
partial deploy can fail with "1 conflicts detected" from source tracking
(`--ignore-conflicts` clears it); a Tooling roll-up field needs `summaryOperation`
upper-case `COUNT`; `sf project deploy report` reads the same cache, so use step 2.]

Running the deploy unsandboxed through the permission prompt also works; it is the
user's choice, never an agent's retry.

## 3. A browser (Selenium + Chrome for Testing)

[Measured: 2026-11-26, Chrome for Testing 157, macOS]

- Regular Chrome is blocked by policy; use Chrome for Testing under `~/.cache/cft/`
  and set the pair `CHROME_BINARY` and `CHROMEDRIVER_PATH` (see
  `docs/guides/local-installation.md`, Chrome for Testing). Selenium: the CumulusCI
  pipx venv's Python has it; the repo `.venv` has a selenium 3 that conflicts with
  urllib3 2.
- chromedriver needs `sandbox.network.allowLocalBinding: true` in the user's
  gitignored `.claude/settings.local.json` (it applies without a restart).
- That is **not enough** to run it sandboxed: Chrome creates its extension-unpack
  directory under the macOS per-user temp directory (`getconf DARWIN_USER_TEMP_DIR`),
  which the sandbox denies, so the session fails with `cannot create temp dir for
  unpacking extensions` whatever `TMPDIR`, `--disable-extensions` or a scratch
  `--user-data-dir` says. Opening that directory (and the Unix socket and mach
  lookups Chrome also needs) would widen the sandbox; the owner chose not to.
- So browser steps run unsandboxed through the permission prompt, one command at a
  time, and only where the user allows it. A subagent's auto-mode classifier may
  refuse the unsandboxed call: then delegated browser checks need a standing
  permission rule, or stay in the main session.

The helper that does this, `scripts/ui_check/ui_check.py`, is documented in
`robot-testing/live-ui-checks.md`.
