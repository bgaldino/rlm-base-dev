# Local CCI and Salesforce Org/Auth Cleanup

## Entry Conditions

Use for "clean up my CCI and SF orgs", "purge expired/deleted scratch orgs",
"remove invalid auth", or "clean stale .sf/.sfdx state". This is a local
registry cleanup, not permission to delete live Salesforce orgs.
For tool installation/PATH problems, use the toolchain skill instead.

Default scope: global SF auth/aliases, the current CCI project's keychain, and the current
project's `.sf`/`.sfdx` org state. Do not sweep other projects or worktrees unless
requested. An audit/dry-run request stops after step 1. Run everything from the project
root: `cci` and local `sf` configuration resolve the project from the working directory,
and `cci org list` elsewhere exits 0 showing only CCI's built-in shapes.

## Quick Rules

1. Audit before removing anything, and show the user what the audit found.
2. Remove only what a Dev Hub record shows is gone. Missing evidence preserves.
3. Use [`scripts/ai/org_cleanup.py`](../../../scripts/ai/org_cleanup.py) rather than
   writing cleanup code or deleting state by hand. If it lacks a case, fix the tool.
4. Preserve connected Dev Hubs, active orgs, and reusable CCI org shapes.
5. Never print credentials or raw auth JSON, or copy them into reports or fixtures.
6. End with counts, preserved/uncertain entries, default changes, and verification.

## DO NOT

- Do not treat `cci org remove` as a local command. For any entry with a created date it
  runs `sf org delete scratch -p` with no prompt, and a live org is deleted. Step 3 gives
  the only conditions for using it.
- Do not use `sf org delete scratch`, `cci org prune --include-active`, or
  `sf org logout --all`. Removing local authorization does not require remote deletion.
- Do not use `sf org list --clean`. It selects by status rather than evidence the user
  reviewed, and on deleted orgs it returned status 0, warned, and removed nothing. Its
  warning suggests the remote-delete command.
- Do not run `cci org info`, or target an entry with `--org`, during cleanup. On an expired
  or uninstantiated scratch entry CCI creates a new scratch org, and `cci org info --json`
  prints tokens. Avoid unfiltered `sf org display` for the same reason.
- Do not infer deletion from age, a username/domain pattern, `isScratch: false`, missing
  admin auth, DNS failure, timeout, or an arbitrary nonzero CLI exit.
- Do not treat `sf org list` as the inventory. It omits secondary users, and when a hub is
  unreachable it returns status 0 with no warning and no scratch orgs.
- Do not remove a sandbox/production/Dev Hub authorization merely because it needs login
  again. Report it and obtain explicit approval for local logout.
- Do not bulk-delete `.sf`, `.sfdx`, `.cumulusci`, CCI services, or macOS Keychain items.
  Preserve the CLI's shared encryption key and unrelated secrets.
- Do not uninstall/reinstall tools or change interpreters to perform cleanup.

## 1. Audit

```bash
python scripts/ai/org_cleanup.py audit --out <plan-path-outside-the-repo>
```

The tool reads local auth, alias, tracking and cache state, then queries `ScratchOrgInfo` on
every connected Dev Hub, by org ID and, for state with only a username, by signup username.
Only a removable class goes on the plan:

| Hub evidence | Class | Result |
|--------------|-------|--------|
| `Deleted` | deleted | Removed |
| Past expiration, not `Active` | expired | Removed |
| `Active`, not past expiration | active | Preserved |
| `Active` with a past date, or different statuses across rows | conflict | Preserved, reported |
| No row, or the hub did not answer | unknown | Preserved |

An expiration date of today is not past. Every login on a removable org is included,
regardless of its local `isScratch`. Dev Hubs and sandboxes are never logged out.

It removes nothing, though `cci` writes a `.org` file for any declared shape that lacks one,
and a hub query can refresh that hub's auth file. The plan holds usernames but no tokens, and
is written readable only by the user. Keep it out of the repo.

Every `cci` command rolls `~/.cumulusci/logs` over and keeps 5 backups, including the ones this
procedure runs. Copy a log you are debugging before starting.

Review with the user:

| Output | Meaning |
|--------|---------|
| `hub_failures` | Those hubs gave no evidence, so the plan may be incomplete. Fix access and re-audit. |
| `conflicting_evidence` | Stop on those entries. |
| `logins_with_no_refresh_token` | Stops working when its session expires, even though its org is live. Report it; log out only with explicit approval. |
| `unreadable_auth_files`, `symlinks_left_alone` | Left alone. Report them. |
| `dangling_aliases` | Lead to no username, so no hub row can list them. Left alone. Report them, and `sf alias unset <name>` only with the user's approval. |
| `unclassified_files` | Not owned by the CLIs, and not opened. A saved auth URL stays usable until the org expires or the token is revoked, independently of local logins. Report it and let the user decide. |
| `prune_prediction` | See step 3. |

An audit request ends here.

## 2. Apply the reviewed plan

```bash
python scripts/ai/org_cleanup.py apply --plan <plan-path>
```

`apply` re-derives the plan and exits 3 without changing anything if it differs from the
reviewed one. It then moves a temp file into the quarantine, a dated folder in the user's Trash,
and exits 1 before any logout if that fails; `--quarantine <dir>` chooses another folder. It
then runs targeted `sf org logout` per user, `sf alias unset` per alias, and `sf config unset
target-org` for a default still pointing at a removed user, and moves user indexes, tracking
directories, and matched deploy-cache manifests to the quarantine. It refuses symlinks, tracked
files, and paths outside the state roots. If a logout fails, that org's index, tracking and
deploy-cache entries stay, and so does a chained alias that still reaches the login. `sf` clears
the user's direct aliases and defaults before it can fail, so those may already be gone, and a
chain left leading nowhere is removed. Fix the cause and re-audit; the login is listed again.

Each result is checked. Exit 1 means something failed: report each `FAILED` line. A warning
about losing access is routine for a scratch-org login. The user empties the Trash folder
when satisfied; logouts and alias removals cannot be restored from it.

The tool does not handle credential backups: report them from `unclassified_files`, and
remove one only when the user can tie it to a confirmed stale org.

## 3. CCI registry (the user's decision)

The tool never runs these. Each is a separate decision for the user.

**`cci org prune`** has no dry run and cannot be limited to some entries. The audit predicts
its result from CCI's own logic:

| Entry | Prune result | `prune_prediction` key |
|-------|--------------|------------------------|
| Name in CCI's merged shapes (project and built-in) | Skipped, **even if its instance expired** | `expired_shape_instances_it_skips` |
| Not a shape, never instantiated | **Removed and reported as "expired"** | `would_remove_never_instantiated` |
| Not a shape, past CCI's expiry | Removed | `would_remove_expired` |
| Not a shape, not expired | Skipped as active | |
| Connected (non-scratch) org | Untouched | |

Do not run it if `would_remove_but_active_on_hub` is non-empty: CCI computes expiry locally
as created date plus days, which can lapse before the hub's date. That check has no evidence
when `hub_failures` is non-empty. A never-instantiated entry is usually a shape declared only
on another branch, and CCI recreates it on a checkout that declares it; describe it that way,
not as an expired org.

Prune drops only the CCI record. A removed org's login and alias stay, and the next audit lists
them once the hub shows that org gone.

An expired instance under a shape name stays listed. A later command targeting it, by
`--org` or as the default, creates a new scratch org.

**`cci org default --unset`**: only when the default is a removal candidate. It also runs
`sf config unset target-org` in the current project, even when the SF default points at a
different, valid org. Note `target-org` first, and if it is still valid restore it with
`sf config set target-org=<value>`, which updates both config layouts. `cci org default
<name>` likewise moves the SF default to that org.

**`cci org remove`**: only when the entry's `<project-name>__<entry-name>` alias resolves to
a username, a hub row from this run shows that exact username `Deleted`, and the user approved
that entry by name. The delete then fails harmlessly and CCI drops the record, but it can leave
the alias behind, so re-audit afterward. Never bypass global-org protection automatically.

## Validation Checks

1. Re-run the audit. Every list under `remove` must be empty. That does not clear an earlier
   `FAILED` line: after its logout, a secondary user's residual state has no link to a hub
   row, so it reads as unknown and stays off the plan. Resolve each `FAILED` item by name.
2. Run `python scripts/ai/org_cleanup.py audit --check-logins`, which queries each preserved
   login and can rewrite auth files through a token refresh. For a failure, compare that
   login's auth file with the pre-cleanup state before attributing it to cleanup.
3. Run `COLUMNS=200 cci org list --plain` (narrower output wraps long names). Removed records
   are gone and shapes remain. `--json` can fail with `Object of type date is not JSON
   serializable`; the table form also removes cache directories for orgs CCI no longer knows.
4. Confirm `git status --short` has no new tracked changes attributable to cleanup.
5. Report removals by category, preserved auth, unresolved items, scope, and whether any
   defaults were cleared. Do not claim Keychain enumeration or removal: supported logout
   handled auth storage.

## Examples

- **Repeat cleanup:** "Clean up my CCI and SF orgs; purge expired scratch orgs and stale auth."
  Audit, review, apply, validate. A repeat on a clean workstation has an empty plan.
- **Hidden secondary user:** main auth is absent but a sales-rep login and tracking directory
  remain. If the hub shows the org deleted, the plan logs out that user and moves only the
  matched state. If the org is active, the same-looking user stays.
- **Orphaned alias:** an alias points at a username with no auth file. The plan unsets it only
  if a signup-username row shows that org deleted. An alias of a valid alias stays.
- **Chained alias:** an alias points at another alias of a user being logged out. Logout clears
  only the direct alias, so the plan lists the chained one too.
- **Shape from another branch:** `would_remove_never_instantiated` lists an entry absent from
  this checkout. Describe it as a shape and let the user decide before pruning.
- **Unavailable hub:** `hub_failures` lists it and its entries stay. Do not reinterpret failure
  as deleted; report the blocker.
- **Audit only:** "Show what you would remove, but don't change anything." Run step 1 and
  stop.
