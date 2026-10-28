# Decision Tables — Lifecycle & Refresh

> Sub-file of `.cursor/skills/decision-tables/SKILL.md`. **Pinned to Release 264 /
> API v68.0.** Read this when you need the deploy paths + source locations, the
> active-edit restriction, activate/deactivate, refresh inputs and limits,
> recipe-table mappings +
> `validate_lists`, or a brief runtime-execution note. The exhaustive reference
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
