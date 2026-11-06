# Local CCI and Salesforce Org/Auth Cleanup

## Entry Conditions

Use for "clean up my CCI and SF orgs", "purge expired/deleted scratch orgs",
"remove invalid auth", or "clean stale .sf/.sfdx state". This is a local
registry cleanup, not permission to delete live Salesforce orgs.
For tool installation/PATH problems, use the toolchain skill instead.

Default scope: global SF auth/aliases, the current CCI project's keychain,
and the current project's `.sf`/`.sfdx` org state. Do not sweep other projects
or worktrees unless requested. An audit/dry-run request permits inventory only,
using the non-rewriting commands in step 1. Run every command from the project root:
`cci` and local `sf` configuration resolve the project from the working directory, and
`cci org list` elsewhere shows none of the project's orgs, without an error.

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
- Do not treat `cci org remove` as a local command. For any entry with a created
  date it runs `sf org delete scratch -p` with no prompt, then drops the record.
  Step 3 gives the only conditions for using it.
- Do not use `sf org list --clean`. It selects by status rather than the allowlist,
  and on deleted orgs it returned status 0, warned, and removed nothing. Its warning
  suggests the remote-delete command; use targeted logout instead.
- Do not run `cci org info`, or target an entry with `--org`, during cleanup. On an
  expired or uninstantiated scratch entry CCI creates a new scratch org, and
  `cci org info --json` prints tokens.
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
COLUMNS=200 cci org list --plain
cci org prune --help
cci org remove --help
cci org default --help
sf org list --help
sf org logout --help
sf config unset --help
```

Capture `sf org list --all --skip-connection-status --json` and
`sf org list auth --json` inside a subprocess; parse in memory and print an
allowlist of fields only: `alias`, `username`, `orgId`, `status`,
`expirationDate`, `devHubUsername`, `isDevHub`, and default indicators. Inspect
errors and warnings without dumping credential-bearing payloads or raw stderr.
Avoid unfiltered `sf org display`.

Read that output with these behaviors in mind:

- Without `--skip-connection-status`, `sf org list` checks each non-scratch org
  and can rewrite its auth file. No credential is lost, but it is a state change:
  use that form only outside an audit, and only when connection status is needed.
- `nonScratchOrgs` includes the `other`, `sandboxes`, and `devHubs` entries, so
  dedupe by username before counting.
- If a Dev Hub query fails, `sf org list` drops that hub's scratch orgs and still
  returns status 0 with no warning. Compare against `sf org list auth` and the auth
  files; an entry missing from the list is Unknown, not absent.
- `cci org list` is not strictly read-only. Any `cci` command writes a `.org` file
  for a shape declared in the checked-out `cumulusci.yml` that lacks one, and the
  table form removes cache directories for orgs it no longer knows. `--json` skips
  that cleanup but can fail (`Object of type date is not JSON serializable`, seen
  on CCI 4.11.0). Disclose any such change in an audit report.

Inventory filenames and immediate child directory names in:

- Global `~/.sf/` and `~/.sfdx/`: user auth, `<orgId>.json` user indexes,
  aliases, credential backups, configuration, and deployment caches.
- Current project `.sf/` and `.sfdx/`: configuration and tracking state. Both may
  exist with different keys: `.sf/orgs/<orgId>/` and legacy
  `.sfdx/orgs/<username>/`.
- CCI's current-project registry: use CCI commands, not encrypted `.org`
  contents. Uninstantiated org shapes are not stale auth. An instantiated entry's
  SF alias is `<project-name>__<entry-name>`, with the project name from
  `cumulusci.yml`; resolve it to a username. No alias means its identity is unknown.

Parse local SF auth files only for identity/lifecycle fields. Never print
`accessToken`, `refreshToken`, `password`, client secrets, or auth URLs.
List tracking roots, counts, and sizes rather than every Git object file.
Report any other credential-like file in these roots by name, size, and mode
without opening it, and leave it alone.
Snapshot usernames, org IDs, aliases, and defaults in memory before logout
removes the evidence needed to match residual files.

## 2. Establish the removal allowlist

Discover connected Dev Hubs from the inventory; use their SF usernames, not CCI
aliases. Query the hub recorded in `devHubUsername`. Secondary users, user indexes,
tracking directories, and aliases record no hub, so query every connected hub for
those. A failed query means that hub gave no evidence; it is not an empty result.

For orphaned auth, indexes, backups, and tracking, collect their org IDs and issue
a targeted query in bounded batches:

```bash
sf data query --target-org <dev-hub-username> \
  --query "SELECT ScratchOrg, SignupUsername, Status, ExpirationDate FROM ScratchOrgInfo WHERE ScratchOrg IN ('<15-character-org-id>')" \
  --json
```

Some state records a username and no org ID, usually because its auth was removed
earlier: aliases, `.sfdx/orgs/<username>/`, and deployment-cache `target-org` values.
Query those by signup username, which matches only the org's original admin:

```bash
sf data query --target-org <dev-hub-username> \
  --query "SELECT SignupUsername, ScratchOrg, Status, ExpirationDate FROM ScratchOrgInfo WHERE SignupUsername IN ('<username>')" \
  --json
```

Resolve aliases first: an alias value can be another alias, and one that resolves to
a current auth is valid even though its literal value has no auth file.

Compare the first 15 characters of org IDs, preserving case. Query only
locally referenced IDs, not an arbitrary LIMIT of recent shared-hub orgs.
Check command success, JSON status, and complete results before using them.
An absent row is not deletion evidence, on one hub or across all of them.

Classify each candidate:

- **Confirmed deleted/expired scratch:** a hub row with explicit deleted lifecycle
  status, or a scratch-org expiration strictly before today's date with no contrary
  status. Treat an expiration date of today conservatively. A local auth file's
  expiration alone is not enough. Include every secondary user with that org ID,
  regardless of local `isScratch`.
- **Active/valid:** preserve, including active remote scratch orgs not
  authenticated on this workstation.
- **Invalid scratch auth, org still active:** preserve by default and report
  for reauthentication; obtain explicit approval before local logout. An auth with
  `oauthMethod: token` has no refresh token, so it stops working when its session
  expires even though its org is live.
- **Unknown:** preserve and report. Missing hub access/rows, network problems,
  malformed metadata, or authentication errors alone do not authorize deletion.

Before mutation, summarize candidates and exclusions. If lifecycle evidence
conflicts, including `Active` status with a past expiration, stop on those entries.
Do not run broad prune/clean operations when they would touch entries that have not
been classified.

## 3. Remove registry entries through supported commands

Only clear a CCI default if it points to a removal candidate:

```bash
cci org default --unset
```

That also runs `sf config unset target-org` in the current project, even when the SF
default points at a different, valid org. Note `target-org` first, and if it is still
valid restore it with `sf config set target-org=<value>`, which updates both config
layouts. `cci org default <name>` likewise moves the SF default to that org.

`cci org prune` has no dry run. Without `--include-active`, predict what it will do
from the table below. Shape names are the **merged** `orgs.scratch`, which includes
CCI's built-in shapes as well as the project's, so read them from CCI rather than from
`cumulusci.yml`. This prints names only:

```bash
cci shell --python 'print(*sorted(project_config.lookup("orgs__scratch", {})), sep="\n")'
```

In `COLUMNS=200 cci org list --plain` (narrower output wraps long names), a
never-instantiated row has a plain number under Days, no Expired mark, and no Domain;
an instantiated one shows days as `alive/total`.

| Entry | Prune result |
|-------|--------------|
| Merged shape name | Skipped as a shape, **even if its instance has expired** |
| Not a shape name, never instantiated | **Removed and reported as "expired"** |
| Not a shape name, past CCI's expiry | Removed |
| Not a shape name, not expired | Skipped as active |
| Connected (non-scratch) org | Untouched |

Run it only if every predicted removal is acceptable; it cannot be limited to some
entries. Do not run it if a predicted removal is `Active` on its hub: CCI computes
expiry locally as created date plus days, which can lapse before the hub's date. A
never-instantiated entry is usually a shape declared only on another branch, and CCI
recreates it on a checkout that declares it; report it as that, not as an expired org.
Inspect the named removals and skipped shapes.

Leave an expired instance under a shape name and report it. A later command that
targets it, by `--org` or as the default, creates a new scratch org.

Use `cci org remove` only when all of these hold, because it attempts remote deletion:
the entry's alias resolves to a username, a hub row from this run shows `Deleted` for
that exact username, and the user approved that entry by name. Otherwise report the
entry and leave it. Do not bypass global-org protection automatically.

For each allowlisted username, including secondary users:

```bash
sf org logout --target-org <stale-username> --no-prompt --json
```

Check every result; do not silently unlink credentials when supported logout fails.
Report failures for investigation. A warning about losing access is routine for a
scratch-org login. Logout also clears that user's aliases and any global or
current-project config key pointing at it, in both layouts, but leaves user indexes and
tracking directories.

## 4. Remove verified residual local state

Re-inventory after logout, then match against the retained removal allowlist:

- Remove orphaned `<orgId>.json` user indexes and `.sf/orgs/<orgId>/` tracking
  directories only for confirmed deleted/expired scratch IDs, and legacy
  `.sfdx/orgs/<username>/` directories only for confirmed usernames.
- Remove obsolete credential backups only when their identity can be tied
  to a confirmed stale org; leave unidentifiable backups for explicit review.
- Remove aliases that still map to a confirmed stale username, including one whose
  auth was removed in an earlier cleanup, using `sf alias unset` after checking its
  help. Pass one alias per command and check each result: the command handles several
  aliases in parallel, and a batch can leave some set and return status 1. Preserve
  valid aliases, including multiple aliases for the same Dev Hub.
- Clear `target-org` via `sf config unset target-org`, using `--global`
  only for a stale global value. Check both global and local `.sf/config.json`
  and legacy `.sfdx/sfdx-config.json`; supported unset may update both.
  If it does not, remove only the matching legacy `defaultusername` key.
  Preserve `target-dev-hub`/`defaultdevhubusername` unless separately stale.
  Supported unset can drop or rewrite keys it does not recognize, so note other
  keys first, compare afterward, and report any difference.
- Remove deployment-cache entries only when their `target-org` resolves to
  a confirmed stale user/alias. Remove corresponding manifest files by matching job
  ID; a manifest with no cache entry has no evidence, so leave it, and do not purge
  manifests based on age. Leave unrelated logs, telemetry, indexes, tools, typings,
  and deployment history alone.

Use explicit paths within discovered state roots. Reject symlinks, verify
path containment, and check that project files are untracked before deletion. Move
residual files to a dated folder in the user's Trash rather than deleting them, so the
user can review them and decide when they are gone.
When rewriting JSON, preserve unrelated keys and permissions and use an
atomic replacement. No bulk glob deletion and no persisted credentials.
If another process changes auth/state during cleanup, re-inventory first.

## Validation Checks

1. Re-run sanitized `sf org list --all --skip-connection-status --json` and
   `sf org list auth --json`. Require no remaining allowlisted users or stale
   aliases; valid orgs must remain. Investigate warnings even when exit status is 0.
   Run a read-only query against each preserved login. For one that fails, compare its
   auth file with the pre-cleanup inventory before attributing the failure to cleanup.
2. Re-run `COLUMNS=200 cci org list --plain`; confirm removed records are gone and shapes remain.
   A second prune should report no removals, but run it only in execution mode, not
   an audit. It skips expired shape instances, so check the Expired column as well.
3. Check global/project defaults, auth files, user indexes, credential backups,
   org tracking roots, and relevant deployment-cache entries against the
   allowlist. Report uncertain leftovers rather than claiming a complete purge.
4. Confirm preserved Dev Hubs still answer a query and `git status --short` has no
   new tracked changes attributable to cleanup.
5. Report actual removals by category, preserved auth, unresolved items, scope,
   and whether any defaults were cleared. Do not claim raw macOS Keychain
   enumeration or removal when only supported CLI logout was used.
6. After an audit, confirm no auth, alias, default, or registry entry was removed, and
   disclose any file the commands themselves changed.

## Examples

- **Repeat cleanup:** "Clean up my CCI and SF orgs; purge expired scratch orgs
  and stale auth." Inventory, verify lifecycle, apply the allowlist, verify.
  A repeat on a clean workstation makes no further changes.
- **Hidden secondary user:** main auth is absent but a sales-rep auth file and
  tracking directory remain. Query their org ID; if deleted, log out that
  username and remove only the matched residual state. If the org is active, the
  same-looking user stays.
- **Orphaned alias:** an alias points at a username with no auth file. Resolve it,
  query by signup username, and unset it only if that row shows it deleted.
- **Shape from another branch:** prune is predicted to remove a never-instantiated
  entry absent from this checkout's `cumulusci.yml`. Report it as a shape, not an
  expired org, and let the user decide before pruning.
- **Unavailable hub:** "Clean up stale orgs" with DNS/auth failures and no
  reliable expiration evidence. Preserve those candidates and report the
  blocker; do not reinterpret failure as deleted.
- **Audit only:** "Show what you would remove, but don't change anything."
  Produce candidates and evidence; do not run prune, clean, logout, unset,
  or filesystem deletion.
