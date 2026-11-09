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

## How the tool reads state

It judges local state the way sf reads it, checked against the sf CLI's own source, and
preserves anything that model cannot explain:

- **Logins** are the files in `~/.sfdx` whose names sf lists (`<username>.json`), under the
  username inside the file. Nothing in `~/.sf` is a login; a credential file there is reported.
- **A name** (an alias, a default or a deploy-cache target) goes through at most one alias, as
  in sf: an alias whose value is another alias's name reaches the login file of that name, if
  any, and is otherwise dangling. A name that is both an alias and a login's name is in doubt,
  and whatever uses it is kept.
- **A login file is found by name**, and macOS filesystems ignore case and Unicode normalization,
  so usernames are compared without regard to either. On a case-sensitive filesystem (Linux,
  the Docker image) that only makes the tool more cautious.
- **A config scope** (`global`, or `local` for the project) is `.sf/config.json` merged with
  `.sfdx/sfdx-config.json`, and sf rewrites both files on any change. The tool acts on a scope
  only when that merge is unambiguous; otherwise it reports why under `unmodelled_config`.
- **`sf org logout`** also clears every alias whose value is that user, and every config key in
  both scopes that holds the user or one of those aliases. The plan lists these under each
  logout, the audit prints them, and `apply` checks afterwards that they are gone.

## 1. Audit

```bash
python scripts/ai/org_cleanup.py audit --out <plan-path-outside-the-repo>
```

The tool reads local auth, alias, tracking, `fileResponses`, config and cache state, then queries
`ScratchOrgInfo` on every connected Dev Hub, by org ID and, for names with no login, by signup
username. Only a removable class goes on the plan:

| Hub evidence | Class | Result |
|--------------|-------|--------|
| `Deleted` | deleted | Removed |
| Past expiration, not `Active` | expired | Removed |
| `Active`, not past expiration | active | Preserved |
| `Active` with a past date, or different statuses across rows | conflict | Preserved, reported |
| No row, or the hub did not answer | unknown | Preserved |

An expiration date of today is not past. Dev Hubs and sandboxes are never logged out, and a
login on a removable org is logged out only if nothing in `protected` keeps it.

It removes nothing, though `cci` writes a `.org` file for any declared shape that lacks one,
and a hub query can refresh that hub's auth file. The plan holds usernames but no tokens, and
is created readable only by the user; it refuses to write through a symlink. Keep it out of the
repo: the tool does not check where `--out` points. `Dev Hubs: 0` with a "NO CONNECTED DEV HUB"
warning means no hub was queried, so an empty plan is not evidence that the state is clean;
authorize the hub with `isDevHub` set and audit again.

Every `cci` command rolls `~/.cumulusci/logs` over and keeps 5 backups, including the ones this
procedure runs. Copy a log you are debugging before starting.

Review with the user, including the aliases and config keys printed under each logout:

| Output | Meaning |
|--------|---------|
| `hub_failures` | Gave no full evidence: a hub that failed or returned a cut-short result (sf's `org-max-query-limit`), a hub named like an alias (sf would ask the alias's org), or a login whose auth file the tool did not read (it may be a Dev Hub). While any is listed no username is judged, so the plan may be incomplete. Fix access and re-audit. |
| `protected` | Names kept, each with the reason. A login whose auth file the tool cannot read or tie to one org (unreadable, a link, a renamed file, files that differ only by case). A login on a gone org that is not logged out because an alias has its name, because logout would clear an alias whose name would then mean another login, or because logout would rewrite a config scope the tool cannot model. An alias on a gone org that is not unset because a login has its name. Stop on these; resolve each by hand. |
| `conflicting_evidence` | Hub rows that disagree, or show `Active` past the date, for a login, an org whose index, tracking or `fileResponses` is local, or a username an alias, default or tracking folder names. Kept. |
| `logins_with_no_refresh_token` | An access-token-only login: it stops working when its session expires (JWT logins re-sign and are not listed). It is not on the plan, which does not mean its org is live. Report it; log out only with explicit approval. |
| `unreadable_auth_files`, `symlinks_left_alone` | Left alone. Report them. A link counts at the entry, at `orgs` or `fileResponses`, or at the project's `.sf` or `.sfdx` above them: nothing under a linked folder is moved. A linked `~/.sf/manifestCache` is listed too, and then no deploy-cache entry is planned. A linked `~/.sf/deploy-cache.json` is listed and never read or rewritten through the link. |
| `unrecognized_file_responses` | An entry under `fileResponses` that is not an org-ID directory. It has no org to check, so it stays. Report it. |
| `dangling_aliases`, `dangling_defaults` | Reach no login and no username, so no hub row can list them. Left alone. Report them; with the user's approval use `sf alias unset -- <name>` (the `--` keeps a name such as `-ap` from being read as `--all --no-prompt`), or `sf config unset target-org` (add `--global` for the `global` scope; see the note below the table). |
| `unsafe_deploy_cache_keys` | Deploy-cache keys that are not plain file names (such as `../x`), or entries whose target is not text. Never planned. Report them. |
| `unmodelled_config` | Config scopes the tool cannot model, with the reason: a file that does not parse, is a link (sf writes through it; the tool reads it to decide which logouts to refuse) or is not a regular file; files that disagree; a key sf does not know (sf cannot unset it, and its next write turns it into `org-instance-url`); a legacy key in `.sf/config.json`; a default that is not text; interoperability turned off; or a linked project `.sf`/`.sfdx`. The tool never writes such a scope and refuses any logout that would. Report it; the user fixes the files, then re-audit. |
| `stale_config_values` | A stale default the tool does not unset: a `target-dev-hub`, or a value in an unmodelled scope. With the user's approval unset it by hand (see the note below the table). |
| `env_defaults` | `SF_TARGET_ORG`/`SFDX_DEFAULTUSERNAME` (and the dev hub pair) override both scopes. Reported with how the tool judges the value; the tool never changes the environment. |
| `unclassified_files` | Not owned by the CLIs, and not opened: a linked login or index file, a credential backup such as `user@x.json.bak`, an auth-shaped file in `~/.sf` or the project, a name sf does not list. A saved auth URL stays usable until the org expires or the token is revoked, independently of local logins. An entry the tool cannot examine is listed with an `error`. Report it and let the user decide. |
| `preserved` | Counts of what stays in each category. |
| `prune_prediction` | See step 3. |

**Unsetting a default by hand:** `sf config unset target-org` (add `--global` for the `global`
scope) clears the scope's key in both files, whatever value each holds. If either file holds a
valid default, note it first and restore it afterwards with `sf config set target-org=<value>`
(again with `--global` for the `global` scope).

While a login the tool reads stays on an org, that org's index, tracking (including legacy
`.sfdx/orgs/<username>`, whose org is the one its signup row names) and `fileResponses` stay too.
An unreadable or linked login is never opened, so its org is not known and it cannot protect that
org's files; files are planned only when a hub row for that org ID shows it gone, so such a login
cannot be on a live org.

An audit request ends here.

## 2. Apply the reviewed plan

```bash
python scripts/ai/org_cleanup.py apply --plan <plan-path>
```

Do not run `apply` while another `sf` or `cci` process is running: the deploy cache is read and
rewritten without a lock, so a concurrent deploy's entry could be lost.

`apply` re-derives the plan and exits 3 without changing anything if it differs from the
reviewed one: its project, every removal, each logout's org and the aliases and config keys it
clears, and the value and login each alias, default, deploy job and file reaches. It does not run
`cci`. An unreadable state folder, or a plan file it cannot read, stops the run with exit 1
before anything changes. Before any
logout, if the plan moves files, it checks the quarantine (no linked root or folder, no file
where a folder belongs) and moves a temp file in, and exits 1 if that fails. The quarantine is a
dated folder in the user's Trash, or with no Trash, beside the real CLI state, which in the Docker
image is the `rlm-state` volume; `--quarantine <dir>` chooses another folder.

It then runs targeted `sf org logout` per user and checks that the auth file and every config
value naming the user or its aliases are gone: sf reports which logins it selected, not what it
removed, and a config write it cannot make (a read-only file) fails silently. A logout that left
anything is a failure. It runs `sf alias unset -- <alias>` per alias, and `sf config unset
target-org` (with `--global` for the global scope) for each planned default, after confirming the
scope still holds the reviewed value and can still be modelled, and re-reading it to confirm the
default is gone. It moves user indexes, tracking directories, `fileResponses`
directories, and matched deploy-cache manifests to the quarantine. It refuses symlinks, paths
outside the state roots, and project files tracked by git (home state is not checked against git).

If a logout fails, every item that reaches that login or another login on its org stays: aliases,
defaults, files and deploy-cache entries. `sf` clears the user's aliases and config keys before it
can fail, so those may already be gone. Fix the cause and re-audit; the login is listed again. A
logout that reports logging out anyone else is a failure, and names them. An error or Ctrl-C after the logouts
start stops the run: it prints what ran (`cleared_by_logout` counts the aliases and config keys
sf cleared with them) and each `FAILED` line, then "Stopped part-way" with exit 1, or 130 when
interrupted. Compare the plan with that output, because a fresh audit cannot list a logged-out
secondary user's remaining state.

Each result is checked. Exit 1 means something failed: report each `FAILED` line. A warning
about losing access is routine for a scratch-org login. The user empties the quarantine when
satisfied; logouts and alias removals cannot be restored from it.

An item whose name is already in the quarantine takes a numbered name, such as `<name>.1`. A failed
move across volumes, such as a project on another drive or in the Docker image, can leave a copy
in the quarantine and all or part of the source in place; the output names the quarantine even
when no move succeeded. Keep both: the copy can be the only complete one. Fix the cause and
re-audit, and the retry takes a numbered name.

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

Do not run it unless `would_remove_not_proven_gone` is empty, `hub_failures` is empty, and the
prediction is available (not `{"available": false}`). `would_remove_not_proven_gone` lists every
instantiated entry prune would remove whose org a hub row does not show gone, judged by the org
ID CCI stored for it (or, without one, the login of its stored username): an active org, a
conflict, no row at all, or no org ID and no login. CCI computes expiry locally as created date
plus days, which can lapse before the hub's date. `default` is CCI's default org
(`DEFAULT_ORG.txt`), which can name an org whose record is gone.

A never-instantiated entry is usually a shape declared on another branch or an earlier commit,
and CCI recreates it on a checkout that declares it; describe it that way, not as an expired org.

Prune drops only the CCI record. A removed org's login and alias stay, and the next audit lists
them once the hub shows that org gone.

An expired instance under a shape name stays listed. A later command targeting it, by
`--org` or as the default, creates a new scratch org.

**`cci org default --unset`**: only when the default is a removal candidate. It also runs
`sf config unset target-org` in the current project, even when the SF default points at a
different, valid org. Note `target-org` first, and if it is still valid restore it with
`sf config set target-org=<value>`, which updates both config layouts. `cci org default
<name>` likewise moves the SF default to that org.

**`cci org remove`**: not part of the normal path. Use it only when all of these hold, checked
**before step 2**, because `sf org logout` clears the user's direct alias: the entry's
`<project-name>__<entry-name>` alias resolves to a username; a hub query you run for that exact
username shows `Deleted` (the plan records no per-user status, and `remove.logout` mixes deleted
and expired); and the user approved that entry by name and confirmed it is the org the alias names,
since CCI deletes by its own stored record and a re-pointed alias would prove nothing about it.
The delete then fails harmlessly and CCI drops the record, but it can leave the alias behind, so
re-audit afterward. Never bypass global-org protection automatically.

## Validation Checks

1. Run `python scripts/ai/org_cleanup.py audit --check-logins`. Every list under `remove` must be
   empty. That does not clear an earlier `FAILED` line: after its logout, a secondary user's
   residual state has no link to a hub row, so it reads as unknown and stays off the plan.
   Resolve each `FAILED` item by name. The same run queries each login sf lists (it can rewrite
   auth files through a token refresh) and exits 1 if any did not answer; a login named like an
   alias is listed as not queried, because sf would answer through the alias's org. For a failure,
   compare that login's auth file with the pre-cleanup state before attributing it to cleanup.
2. Run `COLUMNS=200 cci org list --plain` (narrower output wraps long names). Removed records
   are gone and shapes remain. `--json` can fail with `Object of type date is not JSON
   serializable`; the table form also removes cache directories for orgs CCI no longer knows.
3. Confirm `git status --short` has no new tracked changes attributable to cleanup.
4. Report removals by category, what each logout cleared, preserved auth, unresolved items,
   scope, and whether any defaults were cleared. Do not claim Keychain enumeration or removal:
   supported logout handled auth storage.

## Examples

- **Repeat cleanup:** "Clean up my CCI and SF orgs; purge expired scratch orgs and stale auth."
  Audit, review, apply, validate. A repeat on a clean workstation has an empty plan.
- **Hidden secondary user:** main auth is absent but a sales-rep login and tracking directory
  remain. If the hub shows the org deleted, the plan logs out that user and moves only the
  matched state. If the org is active, the same-looking user stays.
- **Orphaned alias:** an alias points at a username with no auth file. The plan unsets it only
  if a signup-username row shows that org deleted or expired, and every hub answered.
- **Chained alias:** an alias points at another alias's name. sf does not follow the second
  alias: it opens a login file of that name. With none, and no `@` in the name, the alias is in
  `dangling_aliases`: reported, never unset by the tool.
- **CCI alias:** a logged-out scratch org's `<project>__<org>` alias is cleared by sf with the
  logout; the audit prints it under that logout.
- **Shape from another branch:** `would_remove_never_instantiated` lists an entry absent from
  this checkout. Describe it as a shape and let the user decide before pruning.
- **Unavailable hub:** `hub_failures` lists it and its entries stay. Do not reinterpret failure
  as deleted; report the blocker.
- **Audit only:** "Show what you would remove, but don't change anything." Run step 1 and
  stop.
