# Decision Tables — Lifecycle & Refresh

> Sub-file of `.cursor/skills/decision-tables/SKILL.md`. **Pinned to Release 262 /
> API v67.0.** Read this when you need the deploy paths + source locations, the
> active-edit restriction, activate/deactivate, refresh in depth (the
> live-verified payload field name, async + rate limit), recipe-table mappings +
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

The shipped definitions live in metadata and deploy via the Metadata API:

| Source location | Deployed by | Contents |
|---|---|---|
| `unpackaged/pre/5_decisiontables/` | `deploy_decision_tables` | Core tables: `RLM_CostBookEntries`, `RLM_ProductQualification`, `RLM_ProductCategoryQualification` |
| `unpackaged/post_prm_pricing/decisionTables/` | `deploy_post_prm_pricing_decision_tables` | PRM-pricing: `RLM_Channel_Program_Level_Partner` (uses `replace_record_id_query` to resolve `DecisionTable` Ids) |

Both are step-5-era deploys in `prepare_rlm_org`. A one-off / out-of-build deploy
uses `sf project deploy start --target-org <sf_alias>`; the toolkit's
`create_decision_table.py --path metadata` generates the XML into an **OS temp
dir outside the repo** and deploys it (cleaned up after), so no generated churn
lands in `git status`.

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
`DEPENDENCY_EXISTS` (live-confirmed on a scratch org). To edit:

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
`FIELD_INTEGRITY_EXCEPTION: Required field is missing: status`, live-confirmed on
a Draft scratch table). `update` stamps the status returned by its table-resolution
query onto `_payload.tooling_metadata_only(spec, live_status=…)`; the spec's own
status is dropped. Salesforce then accepts or rejects the single complete PATCH.
Raw Connect Definitions mutations are reference-only and are not exposed as
toolkit definition-write paths.

## Refresh (data sync) — in depth

The `refreshDecisionTable` **standard invocable action** syncs source rows into
the BRE engine cache. It is how a data change (or a redeployed definition) becomes
live to the engine.

- **Endpoint:** `POST /services/data/v67.0/actions/standard/refreshDecisionTable`
- **Action-describe inputs** (`GET …/actions/standard/refreshDecisionTable`):

  | Input | Type | Required |
  |---|---|---|
  | `DecisionTableApiName` | STRING | **true** |
  | **`isDecisionTableIncremental`** | BOOLEAN | false |
  | `VersionNumber` | INTEGER | false * |

  > \* `VersionNumber` is action-describe-optional but **required for versioned
  > CSV-based tables** — omitting it there fails `INVALID_API_INPUT: Enter a valid
  > versionNumber for versioned CSV-based decision tables.` (live-verified). See
  > *CSV Based tables* below.

> ⚠ **The accepted incremental flag is `isDecisionTableIncremental`.** The
> existing CCI tasks send **`isIncremental`** instead —
> `tasks/rlm_refresh_decision_table.py` posts
> `{"decisionTableApiName": …, "isIncremental": is_incremental}` (and
> `rlm_manage_decision_tables.py`'s refresh op likewise). That flag name does not
> match the action-describe input, so incremental almost certainly falls back to
> a full refresh silently. The toolkit's `refresh_decision_table.py` CLI uses the
> **correct** `isDecisionTableIncremental` name (live-verified); **fixing the CCI
> tasks is a candidate follow-up** (behavioral change — verify on a live org
> before merging).

- **Async + rate-limited.** The action is asynchronous. Full refreshes use
  separate hourly pools: **40 Standard** and **60 Advanced**; CSV-based tables
  inherit the Advanced pool. Do **not** loop refreshes in a tight build step.
- A completed **full refresh** advances `LastSyncDate`; a completed
  **incremental refresh** advances `LastIncrementalSyncDate` and does not advance
  `LastSyncDate`. `list`/`describe` surface both fields.
- The async-response shape is live-verified: the action returns an invocable-action
  envelope carrying `outputValues.Status = "Queued"` (no synchronous result, and no
  `AsyncOperationTracker` row was observed for the refresh on the probed scratch
  org). No tracker ID is returned. Poll the appropriate timestamp/status field
  rather than expecting a tracker resource. The hourly rejection behavior was not
  exercised (the probe stayed well under both pools).

Incremental refresh is only meaningful when `isIncrementalSyncEnabled` is true on
the table (observed `false` on the shipped SObject-backed tables).

## CSV Based tables — upload + version lifecycle (✅ live-verified)

A `CsvUpload` table's data layer is loaded from an uploaded CSV rather than a
source SObject, so its lifecycle has an extra step between deploy and refresh:
**upload the rows**. The full sequence:

```
create (auto-mints version 1)  →  upload CSV (two-phase, append)
  →  activate (table Status → Active)  →  refresh
```

1. **Create** a `CsvUpload` definition (`sourceObject:"CSV"`); this auto-mints
   version 1. A generic `usageType=Bre` live probe returned **Draft**; Salesforce
   Pricing documentation describes the initial Pricing version as **Inactive**.
   Preserve that product/surface distinction. Re-uploading does **not** mint a v2 (see the version note
   below) — every upload targets version 1.
2. **Upload** the rows with `upload_decision_table_data.py` — a two-phase load
   (insert a `ContentVersion` with the base64 CSV → POST its `068…` id to the
   table's Connect `/file` sub-resource). The loader **appends only** — rows are
   added to the table's current (single) version. Overwrite (`deleteAllRows:true`)
   FAILS on 262/v67.0 (`uploadStatus=Failed`, 0 rows, existing rows kept), so the
   toolkit doesn't expose it; for Salesforce Pricing, multiple CSV versions aren't
   supported, so replace rows with a **fresh table** plus append. The import is
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
   **versioned** CSV table `VersionNumber` is **required** (not optional as the
   action-describe implies), and the two version failures differ (live-verified):
   - **Absent** `VersionNumber` → `INVALID_API_INPUT: Enter a valid versionNumber
     for versioned CSV-based decision tables.`
   - **Non-existent** `--version-number 99` → `INVALID_ID_FIELD: The decision table
     version number is invalid. Specify a valid version number of an active
     decision table…` (a distinct error code from the absent case).

   So pass a real `refresh_decision_table.py --version-number N`.

> **No v2 on re-upload (✅ live-verified for a generic BRE table).** Create
> auto-minted Draft version 1 in that probe;
> re-uploading (append or overwrite, with or without `--version-number`) does NOT
> mint a v2 — the version list stays `[{versionNumber:1}]` and every upload targets
> v1. There is no scripted multi-version fan-out via this toolkit; uploading to a
> non-existent version (`?versionNumber=2` when only v1 exists) → `INVALID_API_INPUT`.

> ⚠ **The `/data` POST (row-by-row edit) is non-functional** on the probed
> release — load and replace rows through the `/file` upload, not the data POST.
> Read the rows back with `dump_decision_table_data.py` (Connect `/data` GET),
> optionally `--filter Field:Value` (exact/case-sensitive) or `--version-number N`.

> ⚠ **Teardown order — deactivate the VERSION before the table (✅ live-verified).**
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
