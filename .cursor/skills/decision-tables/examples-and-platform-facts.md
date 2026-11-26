# Decision Tables - Platform Facts and Worked Examples

Companion to [SKILL.md](SKILL.md).

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
