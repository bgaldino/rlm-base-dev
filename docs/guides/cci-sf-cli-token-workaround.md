# Workaround: CCI `INVALID_AUTH_HEADER` on healthy scratch orgs (sf CLI token redaction)

> **Status:** temporary workaround. Track the removal conditions in
> [When can we remove this?](#when-can-we-remove-this) and drop it as soon as an
> official fix ships.

## Symptom

Any CumulusCI command that touches an org fails with an expired-session / invalid-auth error,
**even on a brand-new scratch org**:

```
$ cci org info pr182
Error: Expired session for https://...scratch.my.salesforce.com/services/data/v67.0/...
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
org's access token by parsing the output of `sf org display`. Salesforce CLI **>= 2.13.0** now **redacts secrets** from that
output by default:

```
Warning: Secrets are now hidden from 'sf org display' command output.
... set SF_TEMP_SHOW_SECRETS=true to render these secrets.
```

CCI receives the redacted placeholder instead of the real token and sends a malformed
`Authorization` header → `INVALID_AUTH_HEADER`.

## The fix

Set `SF_TEMP_SHOW_SECRETS=true` in the environment so `sf` exposes the token to CCI. Pick the
scope that matches how you run CCI.

### Already handled in-repo via direnv

This repo's tracked **`.envrc`** already exports `SF_TEMP_SHOW_SECRETS=true` (see the
*Salesforce CLI token redaction opt-out* block, `.envrc:34-47`). If you use **direnv**
(the repo's standard setup — see `docs/guides/dev-environment-setup.md`), the flag is
applied automatically whenever your shell is inside the repo, and any CCI command you run
there inherits it. The scopes below are for processes direnv doesn't reach — a shell where
direnv isn't hooked, or a GUI-launched IDE that never triggers `.envrc`.

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
(`docs/guides/dev-environment-setup.md`), `~/.zshenv` runs for **every** zsh shell —
interactive, login, and **non-interactive** (CCI subprocesses, IDE integrated terminals,
CI) — whereas `~/.zshrc` is interactive-only and is skipped in exactly the non-interactive
contexts CCI runs in:

```bash
echo 'export SF_TEMP_SHOW_SECRETS=true' >> ~/.zshenv   # bash: ~/.bashrc (interactive) or the BASH_ENV file (non-interactive)
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

> **Automated:** the `.github/workflows/check-cci-token-fix.yml` workflow runs this check
> weekly (and on demand via *Run workflow*) and opens a tracking issue when a newer CumulusCI
> release appears — so nobody has to remember. The manual command below is the same check.

### How to check (run periodically)

```bash
# Is there a CumulusCI release newer than the one with the bug? (same logic as the workflow)
BASELINE=4.10.0
LATEST=$(curl -fsSL https://pypi.org/pypi/cumulusci/json | python3 -c 'import sys,json; print(json.load(sys.stdin)["info"]["version"])')
echo "Latest CumulusCI on PyPI: $LATEST (workaround baseline: $BASELINE)"
# "newer" = larger of {baseline, latest} under version sort, and != baseline.
NEWER=$(printf '%s\n%s\n' "$BASELINE" "$LATEST" | sort -V | tail -1)
if [ "$LATEST" != "$BASELINE" ] && [ "$NEWER" = "$LATEST" ]; then
  echo "NEW RELEASE — check its changelog for the sf-token / 'show-access-token' fix:
  https://github.com/SFDO-Tooling/CumulusCI/releases"
fi
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

**Repo scope:** the in-repo `.envrc` export (`.envrc:34-47`) is the shared, committed
copy — remove that block in the same PR that upgrades CumulusCI (and delete the
`.github/workflows/check-cci-token-fix.yml` watcher), so it stops applying for everyone.

Verify `cci org info CCI_ALIAS` still works **without** the flag, then delete this note's entry
from the troubleshooting skill.

## Related

- `.cursor/skills/troubleshooting/SKILL.md` → Environment & Setup Errors
- `docs/guides/dev-environment-setup.md` (toolchain setup)
