---
name: decision-tables
description: >-
  Inspect, author, deploy, refresh, and verify Revenue Cloud decision tables. Use when
  lookup data is stale, pricing differs from source data, adding table definitions or
  CSV uploads, comparing orgs, or wiring refresh after catalog, pricing, rate, or
  contract changes.
---

# Decision Tables — Manage, Refresh and Verify

Decision tables are materialised lookups. A refresh reads their source objects and
**copies** rows in; nothing re-reads the source afterwards. So a decision table is a
cache with no invalidation, and every symptom below is the same bug:

> pricing is right in the data and wrong in the quote · a tier does not apply · a
> contracted price is ignored · a new SKU prices as if it did not exist

Use this skill when refreshing, diagnosing, adding, or wiring a decision table, and
whenever an agent is maintaining an org this toolchain built and needs to know whether
its lookups still reflect the data.

It also routes definition authoring, cross-org comparison, CSV upload, and explicit
lifecycle work through the standalone `scripts/decision_tables/` toolkit. Read
`authoring-and-data-model.md` for the definition layer and API vocabularies; read
`lifecycle-and-refresh.md` for deploy, activation, data loading, and refresh details.

## Quick Rules

1. **Refresh after any catalog, pricing, rate or contract change.** `prepare_rlm_org`
   ends with `refresh_all_decision_tables` then `rebuild_search_index` for this reason.
   A build that loads data after those steps leaves stale tables behind.
   **The refresh flow returns before the tables are fresh, so wait before pricing**: rerun
   `check_decision_table_freshness` until the tables your pricing reads are no longer Stale
   (see *Refreshing*).
   Rating setup, qualification and tax tables have no runtime refresh: after editing that
   setup data, use the Manager's **Refresh stale only**, or its **Reads object** filter.
   The exception is the tables named in the order-activation flow
   `RLM_Platform_Event_CreateAssetOrderEvent_Stamp_Asset_Renewal_Info` (the asset and
   binding-object tables and `Commitment_based_Rate_Adjustment`), which that flow queues
   for refresh on order activation. Its start element sets `flowRunAsUser` TriggeringUser
   [Repo], and the flow ran as the user who activated the order: debug logs showed the event
   process switch from Automated Process to that user before the flow ran, for an admin and
   for a sales rep [Measured: 2026-11-18, 264, scratch, one org]. When the sales rep, without
   Modify All Data or Customize Application, activated an order with the refresh queue empty,
   every table the flow names refreshed within about four minutes (*Asset Action Source Entries
   V2* moved `LastIncrementalSyncDate`, the other 13 `LastSyncDate`) [Measured: 2026-11-18, 264,
   scratch, one org], so the admin check below didn't stop this flow. Inferred: although it runs as
   the activating user, it runs in system context without sharing (*In a flow, run mode decides…*,
   below).
   *Asset Action Source Entries V2* still read Stale six minutes after one activation and an
   amendment priced in that window was wrong [Measured: 2026-11-16, 264, scratch]: refresh once
   (*Refreshing*), then poll until Fresh and don't re-trigger before the next change
   (`asset-lifecycle-changes/verification.md` step 7). [Open: whether a busy refresh queue
   explains that delay] See
   `lifecycle-and-refresh.md` → *After editing setup data*.
   **The Refresh Decision Table action is admin-only, with measured exceptions.** It refreshed for
   a non-admin in a flow running in System Context Without Sharing, in the Default-mode
   `RLM_Refresh_Decision_Tables_Bulk` started from `without sharing` Apex, and in the repo's
   contract- and order-activation flows (*In a flow, run mode decides…*, below). Otherwise it
   queued only for a user with Modify All Data *and* Customize Application, whether run by the
   flow action in a Default-mode autolaunched flow the user starts or by
   `POST /services/data/v68.0/actions/standard/refreshDecisionTable` [Measured:
   2026-11-18, 264, scratch, one org]. Modify All Data alone, Customize Application alone, each
   of Rule Engine Designer, Salesforce Pricing Design Time User and `RLM_DecisionTableManager`
   alone, and all three sets together, were refused. REST returned HTTP 400
   `INSUFFICIENT_ACCESS_OR_READONLY` ("Unsupported action type: REFRESH_DECISION_TABLE"). A flow
   took its fault path: "We couldn't execute the ... action element of the refreshDecisionTable
   type. Review your action name and version and try again.", which
   names no permission, so check both permissions on the running user. Two-of-three subsets of the
   sets were not run [Measured: 2026-11-18, 264, scratch, one org]. A schedule-triggered flow ran as
   the admin who deployed and scheduled it, not as Automated Process, and its refresh queued
   [Measured: 2026-11-18, 264, scratch, one org]. Whether a later edit or activation by another user
   changes the running user was not tested. [Open: whether a schedule-triggered flow refreshes when a
   non-admin scheduled it]
   **In a flow, run mode decides whether that check applies** [Measured: 2026-11-19, 264, scratch,
   one org]. For a user with neither admin permission, a one-step autolaunched flow calling the
   action took its fault path in Default mode and in System Context With Sharing, and refreshed
   (`LastSyncDate` moved) in System Context Without Sharing. Started with `Flow.Interview`, the
   Default-mode `RLM_Refresh_Decision_Tables_Bulk` queued nothing for that user from a `with
   sharing` Apex class, as the Manager is, and queued from a `without sharing` one. The
   contract-activation (record-triggered) and order-activation (Platform Event) flows set no run
   mode, and both refreshed for that user. Activating a contract
   (`RLM_Contract_Activation_Refresh_Pricing_Tables`) refreshed its three tables within 13 seconds;
   the order-activation flow took about four minutes (above). Inferred: a Default-mode flow takes
   its caller's context, and record-triggered and Platform Event flows run in system context without
   sharing, which would explain both activation flows. Inferred: the check is skipped for any
   running user in system context without sharing, so anyone who can start or trigger such a flow,
   or call `without sharing` Apex that starts a Default-mode refresh flow, refreshes the tables it
   names.
   A Connect resource has a different gate: `POST /services/data/v68.0/connect/decision-table/refresh`
   with `{"decisionTableId": "<Id>"}` returned 201 `Queued` for a user with Rule Engine Designer alone,
   for one with Salesforce Pricing Design Time User alone, for one with Modify All Data and Customize
   Application together and no designer set, and for the three-set user the action refused; a user with
   none of these, or with either admin permission alone, got 403 `FUNCTIONALITY_NOT_ENABLED`
   [Measured: 2026-11-18, 264, scratch, one org]. The 264 Help and developer guide document no such
   resource, so use the action in build code, flows and tasks, and the route only for an ad-hoc API
   refresh by a designer or Design Time user without both admin permissions. A second request while a
   refresh of the same table was pending returned 201 with `status` `Failed` and no `errorMessage`
   [Measured: 2026-11-18, 264, scratch, one org]. Don't resend: poll freshness. Whether the hourly
   refresh limit returns the same shape is not established. Refreshes queued through the route moved
   `LastIncrementalSyncDate`, not `LastSyncDate` [Measured: 2026-11-18, 264, scratch, one org]; the
   request had no refresh-type field, and the type is chosen by the platform (*Release 264 chooses the
   refresh type* in `lifecycle-and-refresh.md`). Versioned CSV tables were not tried.
   **Setup's Refresh button** (a table's detail page, Setup → Decision Tables) calls an Aura action,
   not the flow action. What follows was measured on an Active table [Measured: 2026-11-19, 264,
   scratch, one org]. Every user needed read access to the table's source object: without it the
   detail page opened two error dialogs that blame the source object's configuration, with no
   button. Modify All Data plus Customize Application had that access with no permission set. The
   measured table was a rate card table, whose source object is `RateCardEntry`; separate test users
   (Standard User, no rating or pricing permission set) with only Customize Application, or only
   Modify All Data, got `NOT_FOUND` from `sf sobject describe RateCardEntry`, and the one with both
   could describe it [Measured: 2026-11-19, 264, scratch, one org]. Inferred: the page checks that
   same read access. With that read access, the button showed for Customize Application or Modify
   All Data, and the click admitted the same users as the Connect route above. Customize Application
   alone, and Modify All Data alone, got the refusal toast ("We can't refresh the decision
   table..."). Modify All Data plus Customize Application, and Customize Application plus Rule
   Engine Designer or Salesforce Pricing Design Time User, refreshed (`LastIncrementalSyncDate`
   moved, not `LastSyncDate`). Either designer set without Customize Application had no button. The
   list page (Decision Tables in the Setup tree) showed for Modify All Data plus Customize
   Application; Customize Application, Modify All Data, Rule Engine Designer, and Customize
   Application with read access saw only Settings. Salesforce Pricing Design Time User, alone or
   with Customize Application, and Rule Engine Designer with Customize Application, were not
   checked.
   **Sync Pricing Data** (Setup → Salesforce Pricing Setup) is gated separately [Measured:
   2026-11-19, 264, scratch, one org; the same users]. It ran for Modify All Data plus Customize
   Application (13 tables queued) and for Customize Application plus Salesforce Pricing Design Time
   User (12). Customize Application, and Customize Application plus Rule Engine Designer, got "You
   don't have access to Salesforce Pricing setup"; Modify All Data, and either designer set without
   Customize Application, got "Page not found". Because Modify All Data alone gets "Page not found",
   the page can't show whether it would pass the pricing check behind it. The pricing recipe API
   can: `GET /services/data/v68.0/connect/core-pricing/recipe` returned `FUNCTIONALITY_NOT_ENABLED`
   to the Standard User test users above with only Customize Application or only Modify All Data,
   and recipes to the one with both [Measured: 2026-11-19, 264, scratch, one org]. So the pair, not
   Modify All Data, passes that check; that the page uses the same check is inferred.
   The Manager shows freshness to any user with `RLM_DecisionTableManager` but disables Refresh unless the user has both Modify All
   Data and Customize Application [Repo: `RLM_DecisionTableManagerController.canRefreshTables`].
2. **Check freshness headlessly** — `cci task run check_decision_table_freshness --org "your-cci-alias"`.
   Add `-o param1 strict` to fail a build on any stale table, or `-o param1 json` for the
   dependency map as JSON (Examples). Without `strict` the task exits 0 even when tables
   are Stale, so read the counts it prints [Repo: `scripts/apex/checkDecisionTableFreshness.apex`]. On a Trialforce-spun org,
   `cci flow run check_org_readiness --org "your-cci-alias"` also checks that the search
   index was built in this org (`check_search_index_readiness`).
3. **Freshness is measured against EVERY object a table reads**, not just its source
   object. A table that pulls a column across a lookup goes stale when that lookup's
   record changes, with no row of its own touched.
4. **A refresh must fire when the table's source CRITERIA become true**, not when the
   triggering row is written. See *The timing rule*.
5. **Discover tables from the org; do not trust a hardcoded list** as an inventory.
   `cumulusci.yml`'s `dt_*_decision_tables` lists are refresh *instructions* scoped by
   feature flag, not a census of what exists. `manage_decision_tables -o operation validate_lists`
   compares them to the org and attributes each missing name to the `when:` of the flow
   step that uses its list: a flag-off absence reads as expected, a flag-on one as
   unexpected (`-o strict true` fails on those).
6. **"Not comparable" is a refusal, not a failure.** It means the freshness check
   declined to guess. Only **Stale** is a positive finding.
7. **Definition and data are separate layers.** Editing columns or source bindings does
   not synchronize source rows; refresh (or CSV upload, where applicable) updates the
   materialized data layer.
8. **Deactivate before modifying an Active definition.** Run deactivate, update, and
   activate as separate commands so each platform failure returns independently. All
   mutators preview by default and require `--confirm` to write.

## DO NOT

- **DO NOT** `insert`/`update`/`delete` a `DecisionTable` from Apex. It is a setup object
  and DML on it is rejected **at compile time**, not at runtime — `DML operation Update
  not allowed on List<DecisionTable>`. There is no exception to catch and no runtime
  fallback to write: the class will not deploy. Use Setup, the Metadata API, or the REST
  API.
- **DO NOT** call the `refreshDecisionTable` action from Apex. It is invocable from
  **Flow and REST only**. Apex must bridge through a flow —
  `Flow.Interview.createInterview(...).start()` — which is what
  `RLM_Refresh_Decision_Tables_Bulk` exists for.
- **DO NOT** identify a table by `MasterLabel`. On `DecisionTable` that field is the
  constant string `"Decision Tables"` for every row. Use `DeveloperName` (API name) or
  `SetupName` (display label).
- **DO NOT** hook a refresh to a record's creation when the table's source criteria
  filter on a state that record reaches later.
- **DO NOT** treat a `LastSyncDate` as proof the table holds current rows if the sync
  predates the org. A Trialforce spin inherits the template's timestamps.
- **DO NOT** add a name to a `dt_*_decision_tables` list without confirming the table
  exists in an org **built with that feature flag on**.
- **DO NOT** run destructive toolkit probing against `beta`; use a disposable scratch
  org. Read-only list/describe/diff/trace operations are safe.
- **DO NOT** pass access tokens to toolkit scripts. They delegate authentication to the
  `sf` CLI and take an SF CLI alias via `--target-org`, not a CCI alias.
- **DO NOT** use the raw Connect Definitions POST/PATCH/DELETE resources as a
  toolkit authoring path. Definition writes are Metadata/Tooling-only; Connect is
  used for CSV data/version resources.

## Entry Conditions

Use this skill when you are:

- refreshing decision tables, or deciding whether a refresh is needed
- diagnosing pricing/rating that is correct in the data and wrong at runtime
- adding a decision table, or wiring one into `cumulusci.yml`
- building automation that must fire a refresh at the right moment
- maintaining an org headlessly and needing its readiness state
- inspecting, diffing, tracing, creating, updating, activating, or deleting a definition
- sampling source-backed rows or uploading data to a `CsvUpload` table
- changing `manage_decision_tables` or the `refresh_dt_*` task code (read
  `lifecycle-and-refresh.md` → *The CCI refresh tasks* first)

Not this skill: authoring the pricing procedures that *consume* a lookup
(`.cursor/skills/pricing-wiring/SKILL.md`), or expression-set overlays
(`.cursor/skills/expression-sets/SKILL.md`).

## Toolkit and authoring routes

The standalone toolkit complements the CCI org-build tasks; it does not replace them.
All mutators preview by default and write only with `--confirm`.

| Goal | Route |
|---|---|
| Inventory or inspect definitions | `list_decision_tables.py`, `describe_decision_table.py` |
| Compare orgs/specs | `diff_decision_tables.py` |
| Trace recipe-table mappings | `trace_decision_table.py` |
| Sample the materialized data layer | `dump_decision_table_data.py` |
| Upload `CsvUpload` rows | `upload_decision_table_data.py` |
| Create/update/activate/deactivate/delete | Preview-by-default Tooling commands under `scripts/decision_tables/` |
| Build-critical deploy and refresh | CCI tasks and flows in `cumulusci.yml` |

Start with:

```bash
SF_ORG="your-sf-alias"
TABLE="your-decision-table-api-name"

python scripts/decision_tables/list_decision_tables.py --target-org "$SF_ORG"
python scripts/decision_tables/describe_decision_table.py \
  --target-org "$SF_ORG" --developer-name "$TABLE"
```

Decision tables have two independently managed layers:

1. **Definition** — columns, source binding, criteria, hit policy, and execution shape.
   Metadata API represents it as `.decisionTable-meta.xml`; Tooling spreads it across
   five setup objects. The toolkit writes org definitions through Tooling;
   source-controlled definitions use native Metadata XML with standard `sf` or
   CCI deployment.
2. **Data** — rows copied from source sObjects, uploaded from CSV, or hydrated from a
   Context Definition. The engine does not re-read those rows after materialization.

The complete setup-object model, ID prefixes, metadata shape, and enums are in
`authoring-and-data-model.md`. Deployment paths, active-edit
restrictions, CSV upload, async refresh, and recipe mapping validation are in
`lifecycle-and-refresh.md`. Exhaustive API/error detail lives in
`docs/references/decision-table-api-reference.md`.

## Discovery — what this org actually has

Always start here. Counts and names differ per release and per feature flag.

> ⚠ **The 5 Decision Table setup objects are on Tooling — and, on 264, on the
> standard data API too.** `DecisionTable`, `DecisionTableParameter`,
> `DecisionTableSourceCriteria`, `DecisionTableDatasetLink` and
> `DecisionTblDatasetParameter` all answer a standard `sf data query` (no `-t`) on a
> built 264 org and on a fresh 264 build (measured 2026-10-02), and
> `DecisionTable.Status` is updatable through it —
> `deactivate_changed_decision_tables` relies on that. Older guidance here called
> them Tooling-only (`sObject type 'DecisionTable' is not supported` without `-t`);
> treat that as a possible older-release or feature-off behavior. The queries below
> keep `--use-tooling-api` (`-t`), which works either way. The toolkit inspectors
> (`list_decision_tables.py`, `describe_decision_table.py`) already route through the
> Tooling surface, so prefer them when you have the toolkit on PATH.

```bash
sf data query -t -q "SELECT DeveloperName, SetupName, DataSourceType, SourceObject, UsageType, Status, LastSyncDate FROM DecisionTable ORDER BY UsageType, SetupName" --target-org "your-sf-alias"
```

> `SetupName` (the human label) and `DataSourceType` (`SingleSobject` /
> `MultipleSobjects` / `CsvUpload`) are top-level Tooling-queryable columns. Don't confuse
> them with `MasterLabel`, which on `DecisionTable` is the constant object label
> `"Decision Tables"` on every row (useless for sorting/identifying a specific
> table) — use `SetupName` to label and order.

What a table reads **besides** its source object — the columns it materialises across
lookups, which is where most surprise staleness comes from:

```bash
sf data query -t -q "SELECT DecisionTableId, FieldPath, DomainObject FROM DecisionTableParameter" --target-org "your-sf-alias"
```

The filter a table applies to its source, if any:

```bash
sf data query -t -q "SELECT DecisionTableId, SourceFieldName, Operator, Value, ValueType FROM DecisionTableSourceCriteria" --target-org "your-sf-alias"
```

### Reading `DecisionTableParameter` correctly

Two important edge cases:

- ⚠ **`DomainObject` can hold the literal string `'null'`** for a column that
  comes from the table's own object. `String.isBlank` does **not** catch it.
- ⚠ **`DomainObject` names only the object that owns the FINAL field of a path.** For
  `AssetRateCardEntryId.RateCardEntryId.RateUnitOfMeasureName` it says `RateCardEntry`
  and never mentions `AssetRateCardEntry` — yet re-pointing that intermediate's lookup
  changes what a refresh materialises. Resolve **every hop of `FieldPath`**, not just
  `DomainObject`.

## Freshness — what the verdicts mean

`check_decision_table_freshness` and the **Decision Table Manager** component share one
implementation (`RLM_DecisionTableManagerController`); the task calls the same method the
component does, so they cannot disagree.

| Verdict | Means |
|---|---|
| **Fresh** | The last sync — full or incremental, whichever is later — is later than the newest change **visible to the running user** in *every* object the table reads. Scoped on purpose — see limit 3 below. The reason says which sync it rests on. |
| **Stale** | Something the table reads changed **at or after** the sync. The reason names the object that drove it, and says so explicitly when the two timestamps tie. |
| **Not comparable** | The check refused to guess — a source criterion it could not faithfully reproduce, a dependency it could not check, sharing that can hide rows of an object it reads from the running user (limit 3), or no sObject behind the table at all (`CsvUpload`, `ContextDefinition`, whose freshness is the upload or the Context Definition, not a record timestamp). Compare by hand. |
| **Unknown** | The source could not be read: no source object recorded, the object missing from this org, no permission on it, or its probe failed. |

Two limits apply to **every** verdict, by construction. A third is listed and **closed**,
so it is not reintroduced:

1. A **deleted** source row leaves no timestamp behind.
2. ✅ **Closed.** A row edited **out of** a filter takes its timestamp with it, so a
   filtered probe stops seeing it while the table still holds the copy made before the
   edit — a false Fresh. The unfiltered probe is now folded into the change comparison,
   so the edit is seen. The cost is over-reporting Stale when a row the table *excludes*
   changes, which is the sanctioned direction. A filtered table's **row count** still
   covers only matching rows; its **change comparison** covers the whole object.
3. Probes run in `USER_MODE`, so they see only rows the running user can see. ⚠ **Run the
   check as an operator with org-wide read.** A row hidden from the caller by sharing and
   modified after the sync is invisible to the probe, and the failure direction is the bad
   one — Fresh while stale. Every verdict says "visible" for this reason. The Manager is on
   the shared Home page, so a restricted persona can run it and get a verdict scoped to
   their own view. **Narrowed:** Fresh is withdrawn to Not comparable, naming the object,
   when a table reads an object whose sharing can hide rows from the caller (Private, or
   controlled by a Private master) and the caller lacks View All. On 264 that is IndexRate
   and BindingObjectRateCardEntry for the salesrep persona (7 tables). Every probed object
   counts, including those a source criterion traverses. Still unchecked: restriction rules
   and external users' sharing.

Within what its probes can observe, the design deliberately trades coverage for not
guessing: an unnecessary refresh is cheap, a false all-clear is not. Over-refusing into
"Not comparable" is the intended failure direction.

⚠ **That is a scoped claim, not a guarantee, and the two open limits above are exactly
why.** A deleted source row and a row hidden from the caller by sharing are both invisible
to a timestamp probe, so either can leave a genuinely stale table reported **Fresh**. No
amount of refusing helps there — the check never sees the change to refuse over it. Treat
a Fresh verdict as a readiness signal about what the caller can see, not as proof the
table is current, and **do not present it as one**: it is not a substitute for refreshing
after a known data load or a deletion. The same principle settles the boundary:
a sync stamped at the **same instant** as the newest change reads **Stale**, because a
tie establishes no ordering — nothing says whether the sync's read snapshot included
that write. The reasoning behind each refusal is documented in the controller's class
header — read it there rather than re-deriving it.

## Refreshing

| Path | Use when |
|---|---|
| `cci flow run refresh_all_decision_tables --org "your-cci-alias"` | After a build, a data load, or any catalog/pricing change. Flag-scoped. |
| The **Decision Table Manager** component (Home page, utilities accordion) | Interactive: per-table refresh (admin only, see rule 1), status polling, why a table is stale. |
| Setup → Decision Tables | One Active table, manually. Refresh worked for Customize Application plus one of Modify All Data, Rule Engine Designer or Salesforce Pricing Design Time User (with a designer set, the user also needed read access to the table's source object); neither admin permission alone worked, with or without read access (rule 1). |
| `RLM_Refresh_Decision_Tables_Bulk` flow | From Apex or another flow — the only way Apex can reach the refresh action. Measured from a `with sharing` Apex class that starts it as the Manager does: queued for an admin, not for a user with neither admin permission; from `without sharing` Apex it queued for that user (rule 1). |

An **incremental** sync advances `LastIncrementalSyncDate` and usually does not move
`LastSyncDate` (a first incremental was measured stamping both). ⚠ In Release 264 a **full request can run as incremental**: unless
incremental is requested, the platform chooses the type itself (org preference
`AutoSelectRefreshDT`, whose Setup toggle is an opt-out). So judge a refresh by the
later of the two stamps; see `lifecycle-and-refresh.md` → *Release 264 chooses the
refresh type*.

### Wait for fresh tables before pricing

`refresh_all_decision_tables` returns before the tables are fresh. The table refreshes it
queues finish later (`lifecycle-and-refresh.md` → *Queued is not refreshed*), and so did the
cost book table, which none of those refreshes names.
Measured on two fresh 264 `ent-sb0` scratch orgs on 2026-11-11:

- On one, the tier, bundle-adjustment and cost tables stayed Stale for about three minutes after
  the flow returned, then reached zero Stale.
- On the other, a quote priced about half a minute after the flow returned got empty volume and
  cost lookups, while its bundle adjustment applied. The volume step ran and left the price
  unchanged, the line had no unit cost, and no error was raised.

Why a lookup returns nothing while a refresh runs is not established. Source reading shows each
refresh's data is kept separately, keyed by table and refresh time, and the superseded copy is
normally removed after the new one completes (purging is disabled in some paths). It did not show whether a lookup during a refresh reads the
old, an empty or a partial copy. `[Platform behaviour, traced in part]` Treat the empty result
above as measured only, and do not assume stale-but-complete data while a refresh is running.

Before pricing, rerun `check_decision_table_freshness` until the tables your pricing reads (here
the volume tier, bundle adjustment and cost book tables) are no longer Stale.

## The timing rule

> **A refresh must fire when the table's source criteria become TRUE — not when the
> triggering row is written.**

For example, if a table filters on
`...ContractId.StatusCode = 'Activated'`, refreshing at contract creation excludes
those rows and still advances `LastSyncDate`. Refresh when the contract becomes
Active instead.

Before wiring any automatic refresh:

1. Read the table's `DecisionTableSourceCriteria`.
2. Ask what state a source row must be in to satisfy them.
3. Fire the refresh when a row **reaches** that state, not when it is created.

⚠ Also: an unhandled fault in a record-triggered **after-save** flow rolls back the
triggering DML. A refresh that fails must not take the contract with it.

## Wiring a new table into the build

1. Add the metadata under the appropriate `unpackaged/post_*/decisionTables/`.
2. Add its **`DeveloperName`** to the matching `dt_*_decision_tables` anchor in
   `cumulusci.yml` — the one whose feature flag gates the same functionality.
3. Verify against an org built **with that flag on**. A name in a flag-gated list is
   absent from an org where the flag is off, and that is correct, not drift.
4. Regenerate the CCI reference: `python scripts/ai/generate_cci_reference.py`.

## Platform facts worth not re-discovering

| Fact | Consequence |
|---|---|
| `DecisionTable` is a setup object | Apex DML on it is rejected **at compile time**, so the class will not deploy at all; in-memory test fixtures need `JSON.deserialize`. |
| `refreshDecisionTable` is Flow/REST-invocable only | Apex bridges through a flow. |
| The flow action's refusal of a non-admin is a generic fault | It names no permission: see Quick Rule 1. |
| `MasterLabel` is a constant | Never a table identifier. |
| A parent edit does not touch the child's `LastModifiedDate` | Criteria that traverse a lookup cannot be verified from child timestamps alone. |
| `SourceConditionLogic` is a non-filterable textarea | Cannot be used in a `WHERE`; read it and inspect. It is populated on every table with criteria (the platform writes `"1"`, `"1 AND 2"`), so "not blank" does **not** mean custom logic. |
| `DecisionTableDataset` / `DecisionTableRecordset` reject aggregates and partial filters | A table's **own** row count is not queryable. Only source counts exist — and those are `USER_MODE`, so a **zero** source count means "nothing *you* can see", never "nothing". |
| `CalculationMatrix.DecisionMatrixType` joins `Name` ↔ `SetupName` | The only way to tell a Decision Table from a Decision Matrix. |
| A Trialforce spin inherits the template's `LastSyncDate` | A sync predating `Organization.CreatedDate` proves the table was never built in this org. |

## Examples

**Is this org ready after a build?**

```bash
cci task run check_decision_table_freshness --org "your-cci-alias"
```

**Gate a build on it** (only where no data load follows the refresh):

```bash
cci task run check_decision_table_freshness --org "your-cci-alias" -o param1 strict
```

**Which tables read this object?** `json` prints one `DECISION_TABLE_MAP_JSON` line: per table,
`apiName`, `label`, `usageType`, `sourceObject`, `readsObjects`, `contributingObjects`, the latest
sync, the verdict, and `criteriaApplied` / `unreproducedCriteria` (a Stale verdict may be
over-reported when a source criterion wasn't reproduced). CCI's console wraps long lines, so widen
it. `pipefail` and `grep` make a missing line an error rather than an empty answer:

```bash
( set -o pipefail
  COLUMNS=200000 cci task run check_decision_table_freshness --org "your-cci-alias" -o param1 json \
    | grep -o 'DECISION_TABLE_MAP_JSON .*' | cut -d' ' -f2- \
    | jq -r '.[] | select(.readsObjects | index("RateCardEntry")) | .apiName' )
```

Combine modes as `"strict,json"`; with `pipefail` a strict failure still fails the pipeline.

**Pricing looks wrong and the data looks right.** Run the check first. A Stale verdict
naming the object you just edited is the answer; refresh, wait for the tables (*Wait for fresh
tables before pricing*), and re-test before debugging anything else. A skipped discount or a
missing unit cost with no error is what pricing too soon after a refresh looks like.

**Adding a rate to an existing card.** `RateCardEntry` feeds several tables. After the
load, refresh — the check will name every table that went stale, including ones you did
not know read that object.

## Validation Checks

- `python tests/test_decision_tables_toolkit.py` passes offline.
- `python scripts/ai/skill_manifest.py --check` resolves this skill and its sub-files.
- `cci task run check_decision_table_freshness --org "your-cci-alias"` reports every table with a
  verdict, and the count matches the `DecisionTable` row count in the org.
- After `refresh_all_decision_tables` and its refreshes finish, no table is Stale.
- A table you deliberately made stale (edit any object it reads) flips to Stale and the
  reason names that object.
- Any name added to a `dt_*_decision_tables` list resolves to a real `DeveloperName` in
  an org built with that feature flag on.

## Related

- `.cursor/skills/decision-tables/authoring-and-data-model.md` — Tooling setup objects,
  metadata shape, enums, and the definition/data model.
- `.cursor/skills/decision-tables/lifecycle-and-refresh.md` — explicit lifecycle,
  deployment, upload, refresh, and recipe-table mappings. Its *The CCI refresh tasks*
  section is the one record of why `manage_decision_tables` and `refresh_dt_*` are built
  as they are; read it before changing either task.
- `scripts/decision_tables/README.md` — standalone toolkit commands and safety model.
- `docs/references/decision-table-api-reference.md` — exhaustive API and error reference.
- `docs/references/decision-table-examples.md` — CCI operations cookbook.
- `.cursor/skills/pricing-wiring/SKILL.md` — the procedures and plans that consume these
  lookups, and the timing rule in its pricing context.
- `.cursor/skills/troubleshooting/SKILL.md` — build and deploy failures.
- `RLM_DecisionTableManagerController` class header — the freshness reasoning in full,
  including why each refusal exists.
