# Decision Tables — Lifecycle & Refresh

> Sub-file of `.cursor/skills/decision-tables/SKILL.md`. **Pinned to Release 264 /
> API v68.0.** Read this when you need the deploy paths + source locations, the
> active-edit restriction, activate/deactivate, refresh inputs and limits,
> recipe-table mappings +
> `validate_lists`, a brief runtime-execution note, or why the CCI refresh tasks are
> built as they are (read that before changing them). The exhaustive reference
> is `docs/references/decision-table-api-reference.md`; the CCI ops cookbook is
> `docs/references/decision-table-examples.md`.

## Lifecycle at a glance

```
author/deploy  →  activate  →  deactivate  →  edit  →  activate  →  refresh (async)
 .decisionTable    Status=        explicit, separate commands        rows sync into cache
 -meta.xml         Active
```

The **definition** is deployed and activated; the **data** becomes live only
after a successful refresh. These are independent — see the two-layer model in
`authoring-and-data-model.md`.

## Deploy paths + source locations

Project definitions live in metadata and deploy through the Metadata API:

| Source location | Deployed by |
|---|---|
| `unpackaged/pre/5_decisiontables/` | `deploy_pre` |
| `unpackaged/post_prm_pricing/decisionTables/` | `deploy_post_prm_pricing_decision_tables` |

`deploy_pre` runs through `prepare_core`; the PRM bundle runs later through
`prepare_prm`. A one-off / out-of-build deploy uses `sf project deploy start`.

## Activate / deactivate

Activation state is the `Status` field (Active ↔ Inactive/Draft;
`ActivationInProgress` is a transient reported during activation). The repo
manages it three ways:

| Path | Mechanism |
|---|---|
| CCI task | `manage_decision_tables -o operation activate` / `deactivate` (Tooling `Status` update) |
| Apex | `scripts/apex/deactivateDecisionTables.apex` (`deactivate_decision_tables` task — bulk) |
| Build (deploy path) | `deactivate_changed_decision_tables` (before `deploy_pre`) and `deactivate_changed_post_prm_pricing_decision_tables` (before the PRM table deploy) check-only deploy the repo's Active tables, deactivate only those the platform rejects, and deploy them at once (which reactivates them; on failure it tries to reactivate them, names any left Inactive, and the step fails) |

### The active-edit restriction — deactivate first

**An Active table's definition cannot be structurally modified in place.** An
update is platform-blocked with `FIELD_NOT_UPDATABLE` / "Can't edit an active
Decision Table". An active delete can instead return `INVALID_OPERATION` plus
`DEPENDENCY_EXISTS`. To edit:

```
deactivate  →  edit/redeploy the definition  →  reactivate  →  refresh
```

**Metadata deploy is narrower than that** — measured on a 264 org, 2026-10-02.
Redeploying over an Active table succeeds when the XML is unchanged or the change
is non-structural (a description), and the change applies. Only a structural
change (e.g. a parameter's `isRequired`) fails. After deactivating, the same
deploy succeeds and — because the repo XML carries `<status>Active</status>` —
reactivates the table and syncs it (`LastSyncDate` = deploy time). So the build
does not exclude Active tables: `deactivate_changed_decision_tables` check-only
deploys the repo's Active tables, deactivates only the ones rejected for the
active-edit restriction, and deploys those itself straight away. It does not leave
the reactivation to `deploy_pre`, which deploys the earlier numbered bundles first —
a failure there would strand the tables Inactive. If deactivation or its own deploy
fails, it tries to reactivate the tables it deactivated and fails, logging any it
could not reactivate with the manual activate command. The later bundle deploy
then sees unchanged XML on an Active table, which is accepted. Any other check-only
failure is logged and left for the bundle deploy to report, and while one remains
the task deactivates nothing. (It replaced `exclude_active_decision_tables` /
`restore_decision_tables`, which parked every Active table in `.skip/` and so
silently dropped repo changes on an already-prepared org.)

The toolkit does not reproduce this platform guard or compose lifecycle transitions. `update_decision_table.py` sends one
Tooling PATCH and `delete_decision_table.py` sends one Tooling DELETE; Salesforce
returns its own lifecycle/dependency errors when the table is Active. Run
`deactivate_decision_table.py`, the requested mutation, and
`activate_decision_table.py` as separate commands. Crucially, **the spec's
`status` never drives an update** — a create spec or describe round-trip cannot
change lifecycle state during the definition PATCH.

The toolkit updates definitions only through **Tooling `Metadata` PATCH**.
`status` is a **required field** (a status-free body is rejected with
`FIELD_INTEGRITY_EXCEPTION: Required field is missing: status`). `update` stamps
the status returned by its table-resolution query; the spec's own status is
dropped. Salesforce then accepts or rejects the single complete PATCH.
Raw Connect Definitions mutations are reference-only and are not exposed as
toolkit definition-write paths.

## Refresh (data sync) — in depth

The `refreshDecisionTable` **standard invocable action** syncs source rows into
the BRE engine cache. It is how a data change (or a redeployed definition) becomes
live to the engine.

- **Endpoint:** `POST /services/data/v68.0/actions/standard/refreshDecisionTable`
- **Action-describe inputs** (`GET …/actions/standard/refreshDecisionTable`):

  | Input | Type | Required |
  |---|---|---|
  | `DecisionTableApiName` | STRING | **true** |
  | **`isDecisionTableIncremental`** | BOOLEAN | false |
  | `VersionNumber` | INTEGER | false * |

  > \* `VersionNumber` is action-describe-optional but **required for versioned
  > CSV-based tables** — omitting it there fails `INVALID_API_INPUT: Enter a valid
  > versionNumber for versioned CSV-based decision tables.` See *CSV Based
  > tables* below.

> ⚠ The action input is `isDecisionTableIncremental`, not `isIncremental`.

> **Casing is not the trap; the name is.** Input names match
> **case-insensitively** — `DecisionTableApiName` (the describe spelling, used by
> the flows and `scripts/decision_tables/`) and `decisionTableApiName` (the
> Salesforce doc sample, used by `tasks/rlm_*.py`) both refresh correctly,
> verified live on v67.0 by confirming `LastSyncDate` advanced to
> `RefreshStatus=Completed` for each. Prefer the describe spelling in new code.
> A wrong *name* is a different matter: `isIncremental` is silently ignored.

- **Async + rate-limited.** The action is asynchronous. Full refreshes use
  separate hourly pools: **40 Standard** and **60 Advanced**; CSV-based tables
  inherit the Advanced pool. Do **not** loop refreshes in a tight build step.
- A completed **full refresh** advances `LastSyncDate`; a completed
  **incremental refresh** advances `LastIncrementalSyncDate` and usually not
  `LastSyncDate`. `list`/`describe` surface both fields.
- The response carries `outputValues.Status = "Queued"` and no tracker id. Poll
  the later of the two timestamps rather than treating the response as
  completion: in Release 264 the request does not decide which one moves.

### After editing setup data — what refreshes what

Measured on a fresh 264 build (pack 290), 40 tables:
- **17** are refreshed at runtime by flows: contract activation, the asset Platform Event flow,
  Account reset and Commerce.
- **9** more are covered only by Sync Pricing Data (Setup → Salesforce Pricing Setup). It
  refreshes all 11 DefaultPricing and 2 PricingDiscovery tables, so some of its 13 overlap the 17.
- **14** are refreshed by nothing after the build:
  - 11 rating tables (rate card entries, tier/volume/attribute rate adjustments, the price book
    rate card table);
  - the 2 qualification tables (usage types ProductQualification and
    ProductCategoryQualification);
  - `StandardTax`.

Their sources change only by admin edits: rates, qualification rules, tax setup. An Active
`RateCardEntry` only allows its status to change; any other change is a new entry.

**After such an edit, refresh in the Decision Table Manager:**
1. **Refresh stale only.** The edit turns Stale every table that reads the edited object and
   could change because of it. Measured: retiring one rate card entry turned 8 of the 11 tables
   that read `RateCardEntry` Stale, and the other 29 tables stayed Fresh. The 3 that stayed Fresh
   are the Binding Object rate tables. Their own source objects hold no rows, so they are empty
   whatever `RateCardEntry` holds, and the verdict says so.
2. When a table reads **Not comparable** or **Unknown**, or the edit is outside what you can
   see (the verdict is judged on what the running user can read), use the **Reads object**
   filter instead.
   - Clear the other filters, pick the object you edited, then **Refresh all shown**.
   - It lists every table that reads the object, whatever its verdict.
   - It matches exact API names, so `RateCardEntry` doesn't pull in `AssetRateCardEntry` tables.
   - Objects reached only through a traversing source criterion are not listed, nor are a
     table's column objects when its parameter scan failed (the verdict then withholds
     Fresh).

There is deliberately no automatic refresh for these:
- A scheduled flow would spend 14 full refreshes a night against the 40/h pool, for edits that
  are rare and made by someone already in Setup.
- A record-triggered refresh on rate objects would spend up to 11 refreshes per saved row in a
  bulk edit.

### Release 264 chooses the refresh type (`AutoSelectRefreshDT`)

⭐ **In 264 the request does not fix the type that runs.** Read from Core source
(`DecisionTableMediumVolumeBuilderJob` on the 264 patch branch — implementation, not a
documented contract, and the 264 Help does not describe it) and confirmed on a fresh
264 build, 2026-10-27:

- `isDecisionTableIncremental = true` is honored: an incremental runs. Two cases force a
  full anyway: the table's last incremental failed (`HasIncrementalSyncFailed`), or its
  source object hard-deletes records.
- `false` and **omitted are the same**: the platform chooses. It runs **full** when the
  last full refresh is more than 24 hours old, when the table is not an sObject-sourced
  MediumVolume (HBase) table (CSV upload, LowVolume, Data Cloud), or when nothing can be
  counted. Otherwise it runs **incremental** if under `IncrementalRefreshThreshold`
  (an org value, default 20%) of the rows changed since the later of the two stamps,
  and full above it.
- Measured: a full request on all 40 tables of a fresh build, 2 hours after the first
  refresh, ran as **incremental on 12** — `LastIncrementalSyncDate` moved and
  `LastSyncDate` did not. An explicit incremental request on a table with no
  incremental history (`LastIncrementalSyncDate` null) stamped **both** fields at the
  same instant — so do not infer the type that ran from which stamp moved.
- `IsIncrementalSyncEnabled` is **not consulted** (a Salesforce engineer: "not
  consequential"). LowVolume tables reject an explicit incremental request.
- The org preference **`AutoSelectRefreshDT`** turns this **off**. Its Setup toggle,
  "Auto Select Refresh for Decision Tables" (Setup → Decision Tables → Settings), is
  an **opt-out**: ON suppresses auto-selection, and the request decides again. Core
  plans to rename it `SuppressAutoSelectRefreshDT` in 266.
- **Freshness is the later of `LastSyncDate` and `LastIncrementalSyncDate`**, the rule
  the Decision Table app page uses. 264 Setup shows only the full date; GUS W-24264525
  fixes that in 266. GUS W-24425582 ("[264] Incremental refresh is not updating Price
  book Entry Decision Table") is fixed in 266, so an incremental stamp on a price book
  table can be trusted less until then.

No caller here refuses or rewrites the request: the CCI tasks, the Decision Table
Manager and `refresh_decision_table.py` all send it as given. The Manager and
`check_decision_table_freshness` judge freshness by the later of the two stamps; the
template-spin check alone stays on `LastSyncDate`, because an incremental applies
changes on top of rows that may have been built in another org.

## CSV Based tables — upload + version lifecycle

A `CsvUpload` table's data layer is loaded from an uploaded CSV rather than a
source SObject, so its lifecycle has an extra step between deploy and refresh:
**upload the rows**. The full sequence:

```
create (auto-mints version 1)  →  upload CSV (two-phase, append)
  →  activate (table Status → Active)  →  refresh
```

1. **Create** a `CsvUpload` definition (`sourceObject:"CSV"`); the platform
   creates its initial file-import version.
2. **Upload** the rows with `upload_decision_table_data.py` — a two-phase load
   (insert a `ContentVersion` with the base64 CSV → POST its `068…` id to the
   table's Connect `/file` sub-resource). The loader **appends only** — rows are
   added to the current version. The toolkit does not expose overwrite; replace
   rows with a **fresh table** plus append. The import is
   **async**. The loader waits for `uploadStatus` and exits nonzero on
   `CompletedWithErrors` / `Failed`; the platform does not identify individual
   rejected rows, so dump the rows only when row-level inspection is needed.
   See the full upload contract in `authoring-and-data-model.md` → *CSV Based tables*.
3. **Activate** with `activate_decision_table.py`. For a CsvUpload table the
   lifecycle engine PATCHes the unambiguous file-import version's
   `versionStatus` through Connect; the table's own `Status` cascades to
   **Active**. Activation is **async** — the tool polls past
   `ActivationInProgress` (raise `--max-wait` for slow orgs).
4. **Refresh** — `refreshDecisionTable` requires an **Active** table; run it after
   activation, with the same `isDecisionTableIncremental` flag as above. For a
   **versioned** CSV table `VersionNumber` is required. Pass a valid
   `refresh_decision_table.py --version-number N`.

Read rows with `dump_decision_table_data.py` (Connect `/data` GET), optionally
using `--filter Field:Value` for exact, case-sensitive matching.

> ⚠ **Teardown order — deactivate the version before the table.**
> `deactivate_decision_table.py` uses the version-aware lifecycle engine: it
> resolves and deactivates the CSV version first
> (`PATCH …/versions/{N}` `{"versionStatus":"Inactive"}`). That **cascades the
> table to Inactive**, after which `delete_decision_table.py` can proceed. A
> direct table status PATCH while a version remains Active is rejected with
> `INVALID_INPUT`.

## Recipe-table mappings + `validate_lists`

A pricing recipe consults a table through a `PricingRecipeTableMapping` row
(normal REST — **not** Tooling):

- Fields: `PricingRecipeId`, `PricingComponentType` (ListPrice, VolumeDiscount,
  VolumeTierDiscount, AttributeDiscount, BundleDiscount, PriceAdjustmentMatrix, …),
  `LookupTableId`, `IsInternal`, `FileBasedDecisionTableName`.
- **There is no `DecisionTableId` field.** For SObject-backed tables,
  `LookupTableId` == `DecisionTable.Id`; for file/CSV-backed tables, correlate via
  `FileBasedDecisionTableName` == DeveloperName.

The mappings are wired by `configure_pricing_recipe_table_mappings` (PRM) and
`configure_core_pricing_recipe_table_mappings` (core) — Tooling create/update, no
deploy. To read them:

- **Introspect** — `trace_decision_table.py` (read-only): *what recipes use this
  table?* — resolves the DT via Tooling, queries the mappings via REST, and
  correlates in Python.
- **Validate** — `manage_decision_tables -o operation validate_lists` is the
  **authoritative** project-list validator (compares the org to the project list
  anchors). `trace` introspects; `validate_lists` validates — they don't
  duplicate logic.

Where DTs sit in the broader pricing layering (recipes → recipe-table mappings →
procedure plans → context) is `.cursor/skills/pricing-wiring/SKILL.md`.

## Runtime execution (brief — secondary)

At pricing time the BRE evaluates the table against the hydrated context: INPUT
columns are matched (per `conditionType` / `conditionCriteria`), the hit policy
(`filterResultBy`) selects the winning row(s), and OUTPUT columns are returned to
the calling expression set / pricing procedure. Direct runtime invocation is
available via the Connect Decision Table **Lookup / Invocation / Execution**
resources (`lookup_table_resources.htm`) and `ConnectApi` from Apex — out of scope
for this setup/authoring toolkit; see the reference doc's *Runtime resources*
note. The expression sets that consume a table's output are covered in
`.cursor/skills/expression-sets/SKILL.md`.

---

## The CCI refresh tasks — why they are built this way

The single record of the design reasons behind `tasks/rlm_manage_decision_tables.py`
(`manage_decision_tables`) and `tasks/rlm_refresh_decision_table.py` (every `refresh_dt_*`
task). The code carries one-line pointers to these subsections. Change the reasoning here,
not in the code. Option names differ: `manage_decision_tables` takes `developer_names` and
`is_incremental`, and `refresh_dt_*` takes `developerNames` and `isIncremental`.

### Auth and the token refresh

`salesforce_task = True` gives each task its `--org` option and missing-org guard. Without it,
the CLI builds no `--org` option: `cci task run refresh_dt_commerce --org <alias>` fails with
"No such option: --org", and a run without `--org` silently uses the CCI default org (issue #320;
`tests/test_cci_task_org_option.py` asserts the flag).

The flag does **not** refresh the token. `BaseTask` defines `_update_credentials` as a bare
`pass`, and both `ManageDecisionTables(BaseTask)` and `RefreshDecisionTable(SFDXBaseTask)`
inherit it; only `BaseSalesforceTask` overrides it. Both tasks call the REST API directly, so
per `cci-orchestration/custom-task-authoring.md` they override it to call `refresh_oauth_token`
inside `save_if_changed()`, as `BaseSalesforceTask` does. Without the wrapper, the user and org
info that `refresh_oauth_token` reloads is discarded on exit. For `refresh_dt_*` the consequence
of a stale token is concrete: it builds its own `Authorization: Bearer` header from
`org_config.access_token`, `_make_request` returns None on any non-2xx, and the DecisionTable
status query then fails the step.

Scope that risk honestly. A stale token needs a plain `OrgConfig`, the `cci org connect` shape.
This project has none: the sf CLI manages auth, so every org is an `SfdxOrgConfig` (or its
`ScratchOrgConfig` subclass). It resolves `access_token` through `sf org display` behind a TTL
cache, so the token is always fresh. It also overrides `refresh_oauth_token` to shell
`sf org display`, with no OAuth flow and no connected app, which is why there is no
connected-app handling and `ServiceNotConfigured` cannot be raised. Verified against the
keychain on 2026-07-27: zero plain `OrgConfig`. The override is insurance for the class, not a
fix for anything seen here.

### Queued is not refreshed

`refreshDecisionTable` is asynchronous. `isSuccess` means the request was **accepted**, and
Salesforce documents `outputValues.Status` as `Queued` or `Failed`. So both tasks:

- log "queued", never "refreshed". An old log line said "Refresh Process Success: True" above
  "Refresh Status: Queued", which an operator scrolling a 32-step build log reads as done.
- **fail closed**: only an explicit `Queued` counts. A missing, empty or unrecognised Status is
  not evidence of acceptance and counts as not queued. An earlier version accepted anything
  but `Failed`, which let a malformed or version-drifted response claim a queue.
- apply the `'Unknown'` fallback **after** stripping the Status, because a whitespace-only Status
  is truthy and would otherwise print as an empty string. The two tasks' gates are kept
  identical.
- never point at `DecisionTable.RefreshStatus`: an unresolvable name leaves no record to stamp
  (`pricing-wiring/SKILL.md`). The accepted-but-not-Queued message names
  `check_decision_table_freshness`, whose later-sync-stamp signal holds in every case.
- report "not queued", not "failed to refresh": neither task observes a refresh completing.
  "Not queued" covers a rejected request and one accepted with another Status.

`queued_guidance()` gives one rule for both modes, because Release 264 may run a full request as
incremental (*Release 264 chooses the refresh type*). It exists in both files, and
`tests/test_decision_table_tasks.py` holds the two copies together.

### The API-version pin (`manage_decision_tables`)

`org_config.salesforce_client` uses `latest_api_version`, the last entry of `/services/data`,
so it moves up as soon as an org is upgraded ahead of the project. `_pinned_salesforce_client`
builds the client on `project__package__api_version` instead. Its instance normalisation is
exactly what CCI's `OrgConfig.salesforce_client` does, so My Domain, sandbox and enhanced-domain
hosts behave the same.

With no pin, or without `simple_salesforce`, it falls back to the unpinned client and logs a
warning. That path is unreachable today (`cumulusci.yml` pins `api_version: "68.0"`), which is
why it must not be silent: a fix that stops the damage without propagating the signal is the
shape `REVIEW.md` calls out.

**Every call goes through `_sf`**: query, refresh, and the activate/deactivate write. An
earlier version pinned only the refresh, leaving the query and the one write on the org's newest
API. Writes are where a version bump is most likely to change validation, so a new operation
must use `self._sf`.

`refresh_dt_*` builds its URL from the same project version.

### Request shape

- The action input is `isDecisionTableIncremental`. The action ignores unknown keys, so the
  old `isIncremental` ran every incremental request as a full one (issue #351). The task options
  keep their old names.
- `simple_salesforce`'s `restful()` takes a path relative to `/services/data/v<version>/`. An
  absolute path doubled the prefix and returned 404.

### CLI option parsing

- **Booleans:** CCI passes CLI options as strings, so `-o is_incremental false` (or
  `-o isIncremental false`) arrives as the truthy `"false"`. Unparsed, `manage_decision_tables`
  selected an incremental refresh while logging "full", and `refresh_dt_*` sent a string into a
  Boolean REST field. Both tasks parse with `process_bool_arg`. YAML callers pass real booleans.
- **Name lists:** `-o developer_names "A,B"` (or `-o developerNames "A,B"`) arrives as one string.
  Both tasks split on commas. Before 2026-07-27, `manage_decision_tables` operated on one table
  named `A,B` while reporting "1 decision table(s)", and `refresh_dt_*` skipped it as missing,
  passing while the real tables never refreshed.

### Missing, inactive and failed tables (`refresh_dt_*`)

Names are de-duplicated case-insensitively first, because each refresh draws on the hourly pool.
The task then partitions **before** refreshing. A configured table that is missing or inactive
in the org is a list/org mismatch (the `cumulusci.yml` lists are not org-scoped, and
`refresh_dt_default_pricing` runs unconditionally in `refresh_all_decision_tables`), so it is
skipped and reported. An active table that does not queue is a real failure and fails the task;
before, the step exited 0 even when every refresh failed. One table's exception does not abandon
the tables after it. The org's spelling of each name is sent, since SOQL matched
case-insensitively and nothing establishes that the action does.

### Dropped connections (`refresh_dt_*`)

A full build's `refresh_dt_rating` measured two "Connection reset by peer" in 22 POSTs, and those
tables stayed unrefreshed. Each request is retried on a connection error or timeout (3 attempts).
Resending is harmless: at worst a table is queued twice.

### Importing without CumulusCI

Both modules guard their CumulusCI imports, as `tasks/rlm_apex_file.py` does and
`cci-orchestration/custom-task-authoring.md` prescribes, so `tests/test_decision_table_tasks.py`
runs without CumulusCI installed. `rlm_refresh_decision_table.py` once lacked the guard, and the
suite died on its import before a single check ran. The offline `process_bool_arg` uses the same
vocabulary and raises the same `TypeError` as CCI's. It is not identical: CCI also emits two
DeprecationWarnings for `None`, but both call sites pass `or False`, so that path is unreachable.
An earlier fallback returned `bool(arg)` for anything unrecognised, so "maybe" was True offline
and raised under CCI, and tests using it proved the wrong thing.

---

## Related

- Parent skill: `.cursor/skills/decision-tables/SKILL.md`.
- Companion sub-file: `authoring-and-data-model.md` (setup objects, metadata
  shape, enums, two-layer model).
- Exhaustive reference: `docs/references/decision-table-api-reference.md`.
- CCI ops cookbook: `docs/references/decision-table-examples.md`.
- Pricing layering: `.cursor/skills/pricing-wiring/SKILL.md`.
- CCI tasks: `tasks/rlm_manage_decision_tables.py`,
  `tasks/rlm_refresh_decision_table.py`,
  `tasks/rlm_deactivate_changed_decision_tables.py`,
  `tasks/rlm_configure_pricing_recipe_table_mappings.py`.
