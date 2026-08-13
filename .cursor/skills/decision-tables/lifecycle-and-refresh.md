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
| Deploy workaround | `exclude_active_decision_tables` moves active tables' XML into `.skip/` before a deploy, then `restore_decision_tables` restores it — the deactivate-then-redeploy pattern for the active-edit restriction |

### The active-edit restriction — deactivate first

**An Active table's definition cannot be modified in place.** An update is
platform-blocked with `FIELD_NOT_UPDATABLE` / "Can't edit an active Decision
Table". An active delete can instead return `INVALID_OPERATION` plus
`DEPENDENCY_EXISTS`. To edit:

```
deactivate  →  edit/redeploy the definition  →  reactivate  →  refresh
```

This is why `exclude_active_decision_tables`/`.skip/` exists: a redeploy over an
active table would otherwise fail. The toolkit does not reproduce this platform
guard or compose lifecycle transitions. `update_decision_table.py` sends one
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
  **incremental refresh** advances `LastIncrementalSyncDate` and does not advance
  `LastSyncDate`. `list`/`describe` surface both fields.
- The response carries `outputValues.Status = "Queued"` and no tracker id. Poll
  the appropriate timestamp rather than treating the response as completion.

Incremental refresh is meaningful only when `isIncrementalSyncEnabled` is true.
When it is false the action still returns `isSuccess=true` / `Status=Queued`
and syncs nothing — measured false on all four tables this repo ships and on
all 45 in a built org, so a silent no-op is the **default** outcome of asking
for incremental, not an edge case. Both callers refuse rather than queue it:
`refresh_decision_table.py --incremental` (override with
`--allow-disabled-incremental`) and the in-org Decision Table Manager
(`RLM_DecisionTableManagerController.refreshTables`). Read the flag from
`describe_decision_table.py` → `incrSync`.

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
  `tasks/rlm_exclude_active_decision_tables.py`,
  `tasks/rlm_configure_pricing_recipe_table_mappings.py`.
