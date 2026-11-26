# Constraint model size and other limits

The product shows no size indicator for a constraint model, and the limit is not the same
number on every org. Read this before importing a large catalog into CML, and when a save
fails with "You reached the size limit for this constraint model."

## The size limit is an org value

- Help states a limit of 6MB per constraint model `[Help: product_configurator_limits, 264]`.
- The save check compares the model's byte length with the org's Apex code size limit,
  which defaults to 6MB; it is not a constant `[Platform behaviour, traced]`.
- On a 264 Enterprise scratch org the threshold was exactly 10,000,000 bytes: saves of
  5.5, 6.0 and 6.5 MiB, 9 MiB and 9,999,999 / 10,000,000 bytes passed, and 10,000,001
  bytes and larger failed `[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build]`.
  Do not copy 10,000,000 to another org; measure it or pass it to the size tool.
- The Apex code size limit could not be set on a scratch org, so raising it, and whether
  the CML check follows the change, was not tested
  `[Open: Support-adjusted org value; not testable on a scratch org]`.

## The check runs on one path only

| Path | Size check |
|---|---|
| `PATCH` of the constraint-version resource with a `constraintModel` body (what Constraint Builder saves through) | Yes. HTTP 200 with `success: false`, `UNKNOWN_EXCEPTION`, "You reached the size limit for this constraint model." |
| sObject `PATCH` of `ExpressionSetDefinitionVersion.ConstraintModel` (what `import_cml` does) | No. A 13 MiB model was stored with no error |
| Activation of that stored model through the constraint-version resource | No size error; the model deployed |

`[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build]`. So an oversized
`import_cml` succeeds, and the limit only bites when someone later saves the model in
Constraint Builder or through the resource. A model that imports cleanly can therefore
become impossible to save. Check the size at authoring time:

```bash
python scripts/constraint_models/cml_tool.py size --target-org <sf_alias_or_username> [--limit <bytes>]
```

It prints each constraint model version's byte length and its share of the limit, and exits
1 when any is over ([tooling.md](tooling.md)). The shipped models are far below the limit: the repo files are 8,774 and 21,541 bytes, and
the active models read back from an org at 9,694 and 24,899 bytes
`[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build]`.

## What counts, and what else is limited

- The save check measures the submitted model text only. Whether imported table records
  (`SalesforceTable`) count at activation was not measured `[Open: needs a decision table
  and a constraint fixture]`.
- A separate org value, `MaxConstraintModelSize` (default 25MB, range 1 to 200MB, for all
  constraint models in the org), feeds the solver deploy limit, not the per-version save
  check `[Platform behaviour, traced]`.
- Table constraints: up to 10,000 records per imported table `[Help: product_configurator_limits, 264]`.
- A relation's cardinality above 9,999 needs `maxRelationSize`
  ([quantities-from-attributes.md](quantities-from-attributes.md#raising-the-9999-cap-maxrelationsize)).

## Staying under the limit

- Split by product line into several models; the trade-off is that rules cannot span
  models `[Help: product_configurator_model_large_catalogs, 264]`. Do not activate
  overlapping models (Quick Rule 7 in [SKILL.md](SKILL.md)).
- Drop unused imported types and attributes, and factor reusable structure with
  relationships and associations `[Help: product_configurator_model_large_catalogs, 264]`.
- Keep rule data that changes often in table constraints, so the model text stays small
  (table data added after activation still needs a deactivate and reactivate;
  [import-and-deploy.md](import-and-deploy.md)).
