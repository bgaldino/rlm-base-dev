# Workaround: CCI `INVALID_AUTH_HEADER` on healthy scratch orgs (sf CLI token redaction)

> **Status:** resolved in **CumulusCI 4.10.1**. When `sf org display` redacts the token,
> 4.10.1 falls back to `sf org auth show-access-token`, so `SF_TEMP_SHOW_SECRETS` is no
> longer needed. The repo no longer sets it: `.envrc`, the Docker image and
> `prepare-rlm-org.yml` (now pinned to 4.10.1) all dropped it. **Fix: upgrade CumulusCI**
> (`pipx upgrade cumulusci`), then remove any personal copy of the flag
> ([Removal steps](#removal-steps-once-the-official-fix-lands)). The rest of this page is
> kept for anyone still on CumulusCI 4.10.0 or earlier.

## Symptom

Any CumulusCI command that touches an org fails with an expired-session / invalid-auth error,
**even on a brand-new scratch org**:

```
$ cci org info pr182
Error: Expired session for https://...scratch.my.salesforce.com/services/data/v68.0/...
Response content: [{'message': 'INVALID_AUTH_HEADER', 'errorCode': 'INVALID_AUTH_HEADER'}]
```

It is not org-specific — it hits every scratch org, and a full `cci flow run prepare_rlm_org`
dies on the first org-touching step. In an IDE (Cursor / VS Code) it can look like the auth
"randomly breaks," and relaunching the IDE only helps until the next time.

## How to confirm it's this bug

The org is healthy; only CumulusCI can't authenticate. The `sf` CLI reaches it fine:

```bash
# Works (sf refreshes its own token):
sf data query -q "SELECT Id FROM Organization LIMIT 1" --target-org USERNAME_OR_SF_ALIAS

# Fails with INVALID_AUTH_HEADER (CCI):
cci org info CCI_ALIAS
```

If `sf` succeeds and `cci` fails, it's this bug — **do not delete or recreate the org.**
(Note: `cci org remove SCRATCH_ALIAS` runs `sf org delete scratch -p` and **deletes** the
org — never use it to "refresh" a token.)

## Root cause

CumulusCI **4.10.0** (the version affected by this bug — the workflow's `BASELINE`) reads an
org's access token by parsing the output of `sf org display`. Salesforce CLI **2.145+** (the May 2026 change, forcedotcom/cli#3560) **redacts secrets** from that
output by default:

```
Warning: Secrets are now hidden from 'sf org display' command output.
... set SF_TEMP_SHOW_SECRETS=true to render these secrets.
```

CCI receives the redacted placeholder instead of the real token and sends a malformed
`Authorization` header → `INVALID_AUTH_HEADER`.

## The fix

**Upgrade CumulusCI to 4.10.1 or later** (`pipx upgrade cumulusci`). This project now
requires it (`minimum_cumulusci_version: "4.10.1"` in `cumulusci.yml`), so an older CCI
stops with a version error rather than `INVALID_AUTH_HEADER`.

### Legacy only: CumulusCI 4.10.0 and earlier

Everything from here to *Security note* is kept for CumulusCI 4.10.0 and earlier, outside
this project. The repo no longer applies the flag anywhere: `.envrc` no longer exports it,
so **direnv does not cover you**. If you must run an old CumulusCI, set
`SF_TEMP_SHOW_SECRETS=true` yourself in one of the scopes below.

### Quick / one-off

Prefix any CCI command:

```bash
SF_TEMP_SHOW_SECRETS=true cci org info pr182
SF_TEMP_SHOW_SECRETS=true cci flow run prepare_rlm_org --org pr182
```

Env vars propagate to CCI's child processes, so prefixing the top-level command covers the
whole flow.

### Durable — terminals (POSIX shells: macOS / Linux)

Add it to `~/.zshenv`. Per this repo's shell setup
(`docs/guides/dev-environment-setup.md`), `~/.zshenv` is sourced by **every** zsh shell you
start — interactive, login, and **non-interactive** (e.g. an IDE's integrated terminal) —
whereas `~/.zshrc` is sourced only by interactive shells. Any CCI command you run from such a
shell then has the variable, and CCI's own child subprocesses inherit it from that shell's
environment (they don't re-source `~/.zshenv` themselves). Note this is a personal-shell
mechanism: a **CI** runner uses its own (often non-zsh) shell and won't read your `~/.zshenv`
— there, export the variable in the job environment instead (see below).

```bash
echo 'export SF_TEMP_SHOW_SECRETS=true' >> ~/.zshenv   # bash: use ~/.bashrc for interactive shells; non-interactive bash reads only the file named by the $BASH_ENV variable
```

On Linux / CI runners this is all you need — export the variable in the job environment.

On **Windows**, set it as a user environment variable instead — `setx SF_TEMP_SHOW_SECRETS true`
(PowerShell or cmd), then reopen the terminal/IDE so it picks up the new value.

### Durable — IDE launched from the macOS Dock

Neither a shell profile nor direnv covers an app launched from the Dock (Cursor / VS Code):
macOS GUI apps don't source `~/.zshenv`/`~/.zshrc`, and direnv only fires inside a hooked
shell. To cover the IDE process itself and anything it spawns, set the variable in the GUI
login session with a LaunchAgent.

Create `~/Library/LaunchAgents/com.example.sf-temp-show-secrets.plist` (replace `example`
with your own identifier — e.g. your username — keeping the filename and the `Label` below
identical):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.example.sf-temp-show-secrets</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/launchctl</string>
        <string>setenv</string>
        <string>SF_TEMP_SHOW_SECRETS</string>
        <string>true</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

Load it and set it immediately for the current session:

```bash
launchctl setenv SF_TEMP_SHOW_SECRETS true                                   # current session
launchctl load -w ~/Library/LaunchAgents/com.example.sf-temp-show-secrets.plist # every login
```

**Relaunch the IDE once** afterward — an already-running app does not inherit a freshly-set
`launchctl` variable. It is permanent after that (the LaunchAgent re-applies it at every login).

Verify:

```bash
launchctl getenv SF_TEMP_SHOW_SECRETS    # -> true
cci org info CCI_ALIAS                     # -> instance_url, no INVALID_AUTH_HEADER
```

### Robot E2E suites need no flag

`robot/rlm-base/resources/SalesforceAPI.py` (the REST library every E2E suite under
`robot/rlm-base/tests/e2e/` uses) also authenticates by parsing `sf org display --json`, and
without the flag its suite setup failed with `SOQL query failed: 401 INVALID_AUTH_HEADER`. It now
checks the token it gets back — a real one starts with the org's `00D` Id prefix — and when it
doesn't, it fetches one with `sf org auth show-access-token -o <ORG_ALIAS> --json`, which `sf`
never redacts. The token is never logged. This covers only the library's own REST calls; CCI's
other tasks still need the fix above. Offline tests: `tests/test_robot_salesforce_api_auth.py`.

### Repo scripts need no flag

Scripts that call Salesforce REST themselves get the token from `scripts/sf_token.py`
(`org_auth(alias)`). It takes the instance URL from `sf org display`, checks the token
(a real one starts with the org's `00D` Id prefix), and when it isn't real fetches it with
`sf org auth show-access-token --json`, which `sf` never redacts. The token is never logged or
put in an error. `scripts/cml/export_cml.py`, `scripts/cml/import_cml.py` and
`scripts/docgen/docgen_template_manage.py` use it; `scripts/txn_data_harness/auth.py` already
used `show-access-token`. New scripts that need a token should use the helper rather than
parsing `sf org display`. Offline tests: `tests/test_sf_token.py`. CumulusCI's own token reads
are covered by CumulusCI 4.10.1 itself (see the status note at the top).

### Security note

`SF_TEMP_SHOW_SECRETS=true` makes `sf org display` print access tokens in **plaintext**. That's
acceptable for local scratch-org development, but it means tokens can appear in `sf` output,
logs, screen shares, and CI artifacts. Don't commit logs produced with it set, and prefer the
narrowest scope that solves your case.

## When can we remove this?

This workaround relies on a flag Salesforce documents as **temporary** (`SF_TEMP_SHOW_SECRETS`
"will be removed in an upcoming release"). There are two clocks — remove the workaround when the
**first** of these happens:

1. **CumulusCI ships a release that reads the token via `sf org auth show-access-token`** (the
   non-redacted API) instead of parsing `sf org display`. Then upgrade CCI and drop the flag.
2. **The Salesforce CLI removes `SF_TEMP_SHOW_SECRETS`** — this *breaks* the workaround and
   forces option 1. Watch the `sf` release notes.

> **Done:** condition 1 was met by CumulusCI 4.10.1. The weekly
> `check-cci-token-fix.yml` watcher that tracked it has been removed.

### How to check (run periodically)

```bash
# Print the latest CumulusCI on PyPI; compare it against the baseline yourself.
BASELINE=4.10.0
LATEST=$(curl -fsSL https://pypi.org/pypi/cumulusci/json | python3 -c 'import sys,json; print(json.load(sys.stdin)["info"]["version"])')
echo "Latest CumulusCI on PyPI: $LATEST   (workaround baseline: $BASELINE)"
echo "If $LATEST is newer than $BASELINE, check its changelog for the sf-token / 'show-access-token' fix:"
echo "  https://github.com/SFDO-Tooling/CumulusCI/releases"
```

If a newer release exists, confirm from its changelog that it addresses the
`sf org display` token-redaction issue, then:

### Removal steps (once the official fix lands)

```bash
pipx upgrade cumulusci                       # or to a specific fixed version
# then remove the workaround:
launchctl unload -w ~/Library/LaunchAgents/com.example.sf-temp-show-secrets.plist   # -w mirrors the -w used on load
rm ~/Library/LaunchAgents/com.example.sf-temp-show-secrets.plist
launchctl unsetenv SF_TEMP_SHOW_SECRETS
# remove the `export SF_TEMP_SHOW_SECRETS=true` line from ~/.zshenv (personal scope)
```

**Repo scope:** done. The `.envrc` export, the Docker image's `ENV` and the CI step
`env:` entries were removed when CI moved to CumulusCI 4.10.1, and the watcher workflow
was deleted.

Verify `cci org info CCI_ALIAS` still works **without** the flag. (The troubleshooting
skill's entry already points at the upgrade rather than the flag.)

## Related

- `.cursor/skills/troubleshooting/SKILL.md` → Environment & Setup Errors
- `docs/guides/dev-environment-setup.md` (toolchain setup)
