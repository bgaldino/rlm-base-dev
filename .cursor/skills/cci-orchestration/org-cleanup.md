# Local CCI and Salesforce Org/Auth Cleanup

## Entry Conditions

Use for "clean up my CCI and SF orgs", "purge expired/deleted scratch orgs",
"remove invalid auth", or "clean stale .sf/.sfdx state". This is a local
registry cleanup, not permission to delete live Salesforce orgs.
For tool installation/PATH problems, use the toolchain skill instead.

Default scope: global SF auth/aliases, the current CCI project's keychain,
and the current project's `.sf`/`.sfdx` org state. Do not sweep other projects
or worktrees unless requested. An audit/dry-run request permits inventory only.

## Quick Rules

1. Inventory and classify before removing anything; show a non-secret summary.
2. Use Dev Hub `ScratchOrgInfo` lifecycle evidence for orphaned scratch users
   and tracking directories, even when the main admin auth has disappeared.
3. Preserve connected Dev Hubs, active orgs, and reusable CCI org shapes.
4. Use supported CCI/SF cleanup commands first; inspect warnings and exit codes.
5. Remove residual files only through an explicit, verified stale-ID/user allowlist.
6. Never print credentials or raw auth JSON. Do not copy credentials into reports,
   evaluation fixtures, backups, or tracked files.
7. End with counts, preserved/uncertain entries, default changes, and verification.

## DO NOT

- Do not use `cci org prune --include-active`, `sf org logout --all`, or
  `sf org delete scratch` for routine cleanup. The last command can delete
  a live org; removing local authorization does not require remote deletion.
- Do not infer deletion from age, a username/domain pattern, `isScratch: false`,
  missing admin auth, DNS failure, timeout, or an arbitrary nonzero CLI exit.
  Secondary scratch users may be misclassified and omitted by `sf org list`.
- Do not remove a sandbox/production/Dev Hub authorization merely because it
  needs login again. Report it and obtain explicit approval for local logout.
- Do not bulk-delete `.sf`, `.sfdx`, `.cumulusci`, CCI services, or macOS
  Keychain items. Preserve the CLI's shared encryption key and unrelated secrets.
  Supported logout handles auth storage; do not dump the macOS Keychain.
- Do not delete tracked files, follow directory symlinks, clear valid defaults,
  remove reusable shapes, or change the default target to the Dev Hub.
- Do not uninstall/reinstall tools or change interpreters to perform cleanup;
  use the working CCI installation.

## 1. Discover and inventory

Read installed command help rather than assuming flags:

```bash
command -v cci sf python3
cci org list
cci org prune --help
cci org remove --help
cci org default --help
sf org list --help
sf org logout --help
sf config unset --help
```

Capture `sf org list --all --json` and `sf org list auth --json` inside a
subprocess; parse in memory and print an allowlist of fields only:
`alias`, `username`, `orgId`, `status`, `connectedStatus`, `expirationDate`,
`devHubUsername`, `isDevHub`, and default indicators. Inspect errors and
warnings without dumping credential-bearing payloads or raw stderr.
Avoid unfiltered `sf org display` and `cci org info`.

Inventory filenames and immediate child directory names in:

- Global `~/.sf/` and `~/.sfdx/`: user auth, `<orgId>.json` user indexes,
  aliases, credential backups, configuration, and deployment caches.
- Current project `.sf/` and `.sfdx/`: configuration and `orgs/<orgId>/`
  tracking state (both layouts may exist).
- CCI's current-project registry: use CCI commands, not encrypted `.org`
  contents. Uninstantiated org shapes are not stale auth.

Parse local SF auth files only for identity/lifecycle fields. Never print
`accessToken`, `refreshToken`, `password`, client secrets, or auth URLs.
List tracking roots, counts, and sizes rather than every Git object file.
Snapshot usernames, org IDs, aliases, and defaults in memory before logout
removes the evidence needed to match residual files.

## 2. Establish the removal allowlist

Discover the appropriate connected Dev Hub from the inventory; use its SF
username, not a CCI alias. For orphaned auth, indexes, backups, and tracking,
collect their org IDs and issue a targeted query in bounded batches:

```bash
sf data query --target-org <dev-hub-username> \
  --query "SELECT ScratchOrg, SignupUsername, Status, ExpirationDate FROM ScratchOrgInfo WHERE ScratchOrg IN ('<15-character-org-id>')" \
  --json
```

Compare the first 15 characters of org IDs, preserving case. Query only
locally referenced IDs, not an arbitrary LIMIT of recent shared-hub orgs.
Check command success, JSON status, and complete results before using them.
For multiple hubs, query the relevant hubs; an absent row is not deletion evidence.

Classify each candidate:

- **Confirmed deleted/expired scratch:** explicit deleted lifecycle status,
  or reliable scratch-org expiration strictly before today's date. Treat an
  expiration date of today conservatively. Include every secondary user with
  that org ID, regardless of local `isScratch`.
- **Active/valid:** preserve, including active remote scratch orgs not
  authenticated on this workstation.
- **Invalid scratch auth, org still active:** preserve by default and report
  for reauthentication; obtain explicit approval before local logout.
- **Unknown:** preserve and report. Missing hub access/rows, network problems,
  malformed metadata, or authentication errors alone do not authorize deletion.

Before mutation, summarize candidates and exclusions. If lifecycle evidence
conflicts, stop on those entries. Do not run broad prune/clean operations when
they would touch entries that have not been classified.

## 3. Remove registry entries through supported commands

Only clear a CCI default if it points to a removal candidate:

```bash
cci org default --unset
```

After confirming its candidates, run `cci org prune` (without
`--include-active`). It operates on the current project and skips reusable
shapes; the number pruned can exceed the instantiated orgs displayed in
`cci org list`. Inspect its named removals and skipped shapes.
For individual stale entries not covered by pruning, use
`cci org remove <cci-alias>`; do not bypass global-org protection automatically.

After confirming its candidates, run:

```bash
sf org list --clean --no-prompt --json
```

This may warn that cleaning an org failed even when the returned scratch
list is empty. Do not equate an empty list or status 0 with successful
removal. Inspect auth files and `sf org list auth` afterward.
For each allowlisted username still present, including secondary users:

```bash
sf org logout --target-org <stale-username> --no-prompt --json
```

Use targeted logout instead of the remote-delete command suggested by some
clean warnings. Check every result; do not silently unlink credentials
when supported logout fails. Report failures for investigation.

## 4. Remove verified residual local state

Re-inventory after logout, then match against the retained removal allowlist:

- Remove orphaned `<orgId>.json` user indexes and `orgs/<orgId>/` tracking
  directories only for confirmed deleted/expired scratch IDs.
- Remove obsolete credential backups only when their identity can be tied
  to a confirmed stale org; leave unidentifiable backups for explicit review.
- Remove aliases that still map to removed usernames using `sf alias unset`
  after checking its help. Preserve valid aliases, including multiple aliases
  for the same Dev Hub.
- Clear `target-org` via `sf config unset target-org`, using `--global`
  only for a stale global value. Check both global and local `.sf/config.json`
  and legacy `.sfdx/sfdx-config.json`; supported unset may update both.
  If it does not, remove only the matching legacy `defaultusername` key.
  Preserve `target-dev-hub`/`defaultdevhubusername` unless separately stale.
- Remove deployment-cache entries only when their `target-org` resolves to
  a removed user/alias. Remove corresponding manifest files by matching job ID;
  do not purge all manifests based on age. Leave unrelated logs, telemetry,
  indexes, tools, typings, and deployment history alone.

Use explicit paths within discovered state roots. Reject symlinks, verify
path containment, and check that project files are untracked before deletion.
When rewriting JSON, preserve unrelated keys and permissions and use an
atomic replacement. No bulk glob deletion and no persisted credentials.
If another process changes auth/state during cleanup, re-inventory first.

## Validation Checks

1. Re-run sanitized `sf org list --all --json` and `sf org list auth --json`.
   Require no remaining allowlisted users or stale aliases; valid orgs must
   remain. Investigate warnings even when exit status is 0.
2. Re-run `cci org list`; confirm removed records are gone and shapes remain.
   A second prune should report no expired records, but run it only in
   execution mode, not an audit.
3. Check global/project defaults, auth files, user indexes, credential backups,
   org tracking roots, and relevant deployment-cache entries against the
   allowlist. Report uncertain leftovers rather than claiming a complete purge.
4. Confirm preserved Dev Hubs are connected and `git status --short` has no
   new tracked changes attributable to cleanup.
5. Report actual removals by category, preserved auth, unresolved items, scope,
   and whether any defaults were cleared. Do not claim raw macOS Keychain
   enumeration or removal when only supported CLI logout was used.

## Examples

- **Repeat cleanup:** "Clean up my CCI and SF orgs; purge expired scratch orgs
  and stale auth." Inventory, verify lifecycle, apply the allowlist, verify.
  A repeat on a clean workstation makes no further changes.
- **Hidden secondary user:** main auth is absent but a sales-rep auth file and
  tracking directory remain. Query their org ID; if deleted, log out that
  username and remove only the matched residual state.
- **Unavailable hub:** "Clean up stale orgs" with DNS/auth failures and no
  reliable expiration evidence. Preserve those candidates and report the
  blocker; do not reinterpret failure as deleted.
- **Audit only:** "Show what you would remove, but don't change anything."
  Produce candidates and evidence; do not run prune, clean, logout, unset,
  or filesystem deletion.
