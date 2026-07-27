# Decision Tables — Manage, Refresh and Verify

Decision tables are materialised lookups. A refresh reads their source objects and
**copies** rows in; nothing re-reads the source afterwards. So a decision table is a
cache with no invalidation, and every symptom below is the same bug:

> pricing is right in the data and wrong in the quote · a tier does not apply · a
> contracted price is ignored · a new SKU prices as if it did not exist

Use this skill when refreshing, diagnosing, adding, or wiring a decision table, and
whenever an agent is maintaining an org this toolchain built and needs to know whether
its lookups still reflect the data.

## Quick Rules

1. **Refresh after any catalog, pricing, rate or contract change.** `prepare_rlm_org`
   ends with `refresh_all_decision_tables` then `rebuild_search_index` for this reason.
   A build that loads data after those steps leaves stale tables behind.
2. **Check freshness headlessly** — `cci task run check_decision_table_freshness --org <alias>`.
   Add `-o param1 strict` to fail a build on any stale table.
3. **Freshness is measured against EVERY object a table reads**, not just its source
   object. A table that pulls a column across a lookup goes stale when that lookup's
   record changes, with no row of its own touched.
4. **A refresh must fire when the table's source CRITERIA become true**, not when the
   triggering row is written. See *The timing rule* — this one has already shipped a bug.
5. **Discover tables from the org; do not trust a hardcoded list** as an inventory.
   `cumulusci.yml`'s `dt_*_decision_tables` lists are refresh *instructions* scoped by
   feature flag, not a census of what exists.
6. **"Not comparable" is a refusal, not a failure.** It means the freshness check
   declined to guess. Only **Stale** is a positive finding.

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

## Entry Conditions

Use this skill when you are:

- refreshing decision tables, or deciding whether a refresh is needed
- diagnosing pricing/rating that is correct in the data and wrong at runtime
- adding a decision table, or wiring one into `cumulusci.yml`
- building automation that must fire a refresh at the right moment
- maintaining an org headlessly and needing its readiness state

Not this skill: authoring the pricing procedures that *consume* a lookup
(`.cursor/skills/pricing-wiring/SKILL.md`), or expression-set overlays
(`.cursor/skills/expression-sets/SKILL.md`).

## Discovery — what this org actually has

Always start here. Counts and names differ per release and per feature flag.

```bash
sf data query -q "SELECT DeveloperName, SetupName, SourceObject, DataSourceType, UsageType, LastSyncDate FROM DecisionTable ORDER BY UsageType, SetupName" --target-org <alias>
```

What a table reads **besides** its source object — the columns it materialises across
lookups, which is where most surprise staleness comes from:

```bash
sf data query -q "SELECT DecisionTableId, FieldPath, DomainObject FROM DecisionTableParameter" --target-org <alias>
```

The filter a table applies to its source, if any:

```bash
sf data query -q "SELECT DecisionTableId, SourceFieldName, Operator, Value, ValueType FROM DecisionTableSourceCriteria" --target-org <alias>
```

### Reading `DecisionTableParameter` correctly

Two traps, both live, both already shipped as bugs once:

- ⚠ **`DomainObject` holds the literal four-character STRING `'null'`** for a column that
  comes from the table's own object — on a stock build, 206 of 309 parameters, against 14
  genuine SQL nulls. `String.isBlank` does **not** catch it.
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
| **Fresh** | The last full sync is later than the newest change **visible to the running user** in *every* object the table reads. Scoped on purpose — see limit 3 below. |
| **Stale** | Something the table reads changed **at or after** the sync. The reason names the object that drove it, and says so explicitly when the two timestamps tie. |
| **Not comparable** | The check refused to guess — a source criterion it could not faithfully reproduce, a dependency it could not check, or no sObject behind the table at all (`CsvUpload`, `ContextDefinition`, whose freshness is the upload or the Context Definition, not a record timestamp). Compare by hand. |
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
   one — Fresh while stale. Every verdict says "visible" for this reason; nothing here
   proves the caller sees every row. The Manager is on the shared Home page, so a
   restricted persona can run it and get a verdict scoped to their own view.

The design deliberately trades coverage for never emitting a confident wrong answer: an
unnecessary refresh is cheap, a false all-clear is not. Over-refusing into "Not
comparable" is the intended failure direction. The same principle settles the boundary:
a sync stamped at the **same instant** as the newest change reads **Stale**, because a
tie establishes no ordering — nothing says whether the sync's read snapshot included
that write. The reasoning behind each refusal is documented in the controller's class
header — read it there rather than re-deriving it.

## Refreshing

| Path | Use when |
|---|---|
| `cci task run refresh_all_decision_tables --org <alias>` | After a build, a data load, or any catalog/pricing change. Flag-scoped. |
| The **Decision Table Manager** component (Home page, utilities accordion) | Interactive: per-table refresh, status polling, why a table is stale. |
| Setup → Decision Tables | One table, manually. |
| `RLM_Refresh_Decision_Tables_Bulk` flow | From Apex or another flow — the only way Apex can reach the refresh action. |

An **incremental** sync advances only `LastIncrementalSyncDate`. It does **not** move
`LastSyncDate`, and freshness is measured against the full sync.

## The timing rule

> **A refresh must fire when the table's source criteria become TRUE — not when the
> triggering row is written.**

Learned the expensive way. A refresh was hooked to contract *creation*. Both tier tables
filter their source on `...ContractId.StatusCode = 'Activated'`, so at creation time the
rows were excluded — the refresh ran, **excluded the rows, and stamped `LastSyncDate`
anyway**. The table then read Fresh while holding nothing: worse than visibly stale. A
third table with no such filter did pick up its rows, so 2 of 3 failed and it looked like
it worked.

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
| `MasterLabel` is a constant | Never a table identifier. |
| A parent edit does not touch the child's `LastModifiedDate` | Measured 200/200. This is why criteria that traverse a lookup cannot be verified from child timestamps alone. |
| `SourceConditionLogic` is a non-filterable textarea | Cannot be used in a `WHERE`; read it and inspect. It is populated on every table with criteria (the platform writes `"1"`, `"1 AND 2"`), so "not blank" does **not** mean custom logic. |
| `DecisionTableDataset` / `DecisionTableRecordset` reject aggregates and partial filters | A table's **own** row count is not queryable. Only source counts exist — and those are `USER_MODE`, so a **zero** source count means "nothing *you* can see", never "nothing". |
| `CalculationMatrix.DecisionMatrixType` joins `Name` ↔ `SetupName` | The only way to tell a Decision Table from a Decision Matrix. |
| A Trialforce spin inherits the template's `LastSyncDate` | A sync predating `Organization.CreatedDate` proves the table was never built in this org. |

## Examples

**Is this org ready after a build?**

```bash
cci task run check_decision_table_freshness --org <alias>
```

**Gate a build on it** (only where no data load follows the refresh):

```bash
cci task run check_decision_table_freshness --org <alias> -o param1 strict
```

**Pricing looks wrong and the data looks right.** Run the check first. A Stale verdict
naming the object you just edited is the answer; refresh and re-test before debugging
anything else.

**Adding a rate to an existing card.** `RateCardEntry` feeds several tables. After the
load, refresh — the check will name every table that went stale, including ones you did
not know read that object.

## Validation Checks

- `cci task run check_decision_table_freshness --org <alias>` reports every table with a
  verdict, and the count matches the `DecisionTable` row count in the org.
- After `refresh_all_decision_tables`, no table is Stale.
- A table you deliberately made stale (edit any object it reads) flips to Stale and the
  reason names that object.
- Any name added to a `dt_*_decision_tables` list resolves to a real `DeveloperName` in
  an org built with that feature flag on.

## Related

- `.cursor/skills/pricing-wiring/SKILL.md` — the procedures and plans that consume these
  lookups, and the timing rule in its pricing context.
- `.cursor/skills/troubleshooting/SKILL.md` — build and deploy failures.
- `RLM_DecisionTableManagerController` class header — the freshness reasoning in full,
  including why each refusal exists.
