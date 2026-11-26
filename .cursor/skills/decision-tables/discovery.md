# Decision Tables - Discovery

Detail for the *Discovery* section of [SKILL.md](SKILL.md).

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
