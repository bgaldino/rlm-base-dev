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
author/deploy  →  activate  →  (edit needs deactivate-first)  →  refresh (async, 100/hr)
 .decisionTable    Status=      deactivate → edit → reactivate     rows sync into engine cache
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

**An Active table's definition cannot be modified in place.** Modifying or
deleting an existing artifact on an **Active** table is platform-blocked
(consistent with Context Service's `RECORD_UPDATE_FAILED` deactivate-first rule —
the DT error is `FIELD_NOT_UPDATABLE` / "Can't edit an active Decision Table",
live-confirmed on a scratch org). To edit:

```
deactivate  →  edit/redeploy the definition  →  reactivate  →  refresh
```

This is why `exclude_active_decision_tables`/`.skip/` exists: a redeploy over an
active table would otherwise fail. The toolkit's `update_decision_table.py` /
`delete_decision_table.py` mutators enforce the same guard: they refuse to mutate
an Active table up front unless `--deactivate-first` runs the guarded
deactivate → mutate → reactivate sequence. Crucially, **the spec's `status` never
drives the update** — so a `status` of `Active` carried over from a create spec or
a describe round-trip can't re-activate the table mid-sequence and silently defeat
`--leave-deactivated`. The mechanism differs by path:

- **Connect PATCH** — `update` drops `status` from the flat body outright.
- **Tooling `Metadata` PATCH** — `status` is a **required field** (a status-free
  body is rejected with `FIELD_INTEGRITY_EXCEPTION: Required field is missing:
  status`, live-confirmed on a Draft scratch table). So `update` reads the table's
  **current live** `status` at PATCH time (via `LifecycleEngine.get_status`) and
  stamps *that* onto `_payload.tooling_metadata_only(spec, live_status=…)` — during
  a deactivate-first sequence the engine has already flipped it to `Inactive`, so
  the definition edit merely re-asserts the status the table already has. The
  spec's own `status` is dropped first regardless.

Either way, the lifecycle engine (`_lifecycle.LifecycleEngine`) alone owns the
Active↔Inactive transitions. Add-only inserts (a new parameter, say) may apply in
place — confirm per path.

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

- **Async + rate-limited.** The action is asynchronous and capped at **~100
  refreshes/hour**. It returns a tracker, not a synchronous result; rows are not
  live until it completes. Do **not** loop refreshes in a tight build step.
- **`LastSyncDate`** on the `DecisionTable` advances when a refresh completes —
  `list`/`describe` surface it, and it's the cheap signal that a refresh landed.
- The async-response shape is live-verified: the action returns an invocable-action
  envelope carrying `outputValues.Status = "Queued"` (no synchronous result, and no
  `AsyncOperationTracker` row was observed for the refresh on the probed scratch
  org). The `LastSyncDate` advance is the completion signal. The ~100/hr limit is
  doc-grounded; its exact rejection text was not exercised (the probe stayed well
  under the cap).

Incremental refresh is only meaningful when `isIncrementalSyncEnabled` is true on
the table (observed `false` on the shipped SObject-backed tables).

## CSV Based tables — upload + version lifecycle (✅ live-verified)

A `CsvUpload` table's data layer is loaded from an uploaded CSV rather than a
source SObject, so its lifecycle has an extra step between deploy and refresh:
**upload the rows**. The full sequence:

```
create (auto-mints Draft version 1)  →  upload CSV (two-phase)  →  activate the version
  →  activate the table  →  refresh
```

1. **Create** a `CsvUpload` definition (`sourceObject:"CSV"`); this auto-mints a
   **Draft version 1**. Re-uploading does **not** mint a v2 (see the version note
   below) — every upload targets version 1.
2. **Upload** the rows with `upload_decision_table_data.py` — a two-phase load
   (insert a `ContentVersion` with the base64 CSV → POST its `068…` id to the
   table's Connect `/file` sub-resource). **`deleteAllRows:false` (append) is the
   only reliable write** — `--overwrite` (`deleteAllRows:true`) FAILS on 262/v67.0
   (`uploadStatus=Failed`, 0 rows, existing rows kept; to replace rows, use a fresh
   version/table + append). The import is **async** and rows with a cell that
   doesn't match a column's `dataType` drop silently → `CompletedWithErrors`; opt
   into `--wait-for-status` to catch that. See the full upload contract in
   `authoring-and-data-model.md` → *CSV Based tables*.
3. **Activate the version** before the table:
   `PATCH connect/business-rules/decision-table/definitions/{id}/versions/{N}`
   `{"versionStatus":"Active"}`. `upload_decision_table_data.py --activate-version N`
   does this in the same run.
4. **Activate the table** (same `Status` mechanism as any other table — the
   version must be Active first, else activation fails).
5. **Refresh** — `refreshDecisionTable` requires an **Active** table; run it after
   activation, with the same `isDecisionTableIncremental` flag as above. For a
   **versioned** CSV table `VersionNumber` is **required** (not optional as the
   action-describe implies), and the two version failures differ (live-verified):
   - **Absent** `VersionNumber` → `INVALID_API_INPUT: Enter a valid versionNumber
     for versioned CSV-based decision tables.`
   - **Non-existent** `--version-number 99` → `INVALID_ID_FIELD: The decision table
     version number is invalid. Specify a valid version number of an active
     decision table…` (a distinct error code from the absent case).

   So pass a real `refresh_decision_table.py --version-number N`.

> **No v2 on re-upload (✅ live-verified).** Create auto-mints Draft version 1;
> re-uploading (append or overwrite, with or without `--version-number`) does NOT
> mint a v2 — the version list stays `[{versionNumber:1}]` and every upload targets
> v1. There is no scripted multi-version fan-out via this toolkit; uploading to a
> non-existent version (`?versionNumber=2` when only v1 exists) → `INVALID_API_INPUT`.

> ⚠ **The `/data` POST (row-by-row edit) is non-functional** on the probed
> release — load and replace rows through the `/file` upload, not the data POST.
> Read the rows back with `dump_decision_table_data.py` (Connect `/data` GET),
> optionally `--filter Field:Value` (exact/case-sensitive) or `--version-number N`.

> ⚠ **Teardown order — deactivate the VERSION before the table (✅ live-verified).**
> `delete_decision_table.py --deactivate-first` deactivates the **table**, but the
> platform refuses to make a CSV table Inactive while its **version** is still
> Active: `INVALID_INPUT: "A version cannot be in the Active status when the
> decision table's status is not active."` Deactivate the version first
> (`PATCH …/versions/{N}` `{"versionStatus":"Inactive"}`) — this **cascades the
> table to Inactive** — then delete. (The inverse of the activate order: version
> Active → table Active on the way up; version Inactive → table Inactive on the way
> down.)

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
