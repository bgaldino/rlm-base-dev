# Procedure Plan Overlays

JSON declarations consumed by `apply_procedure_plan_overlay` and future
procedure-plan overlay tasks.

These files are not SFDMU datasets. They are applied by
`tasks.rlm_apply_procedure_plan_overlay.ApplyProcedurePlanOverlay`, which
resolves parent IDs with SOQL and creates or updates
`ProcedurePlanSection`, `ProcedurePlanOption`, and `ProcedurePlanCriterion`
records directly through the Salesforce REST API.

## PRM Pricing

`prm_pricing.json` applies the `RLM_Quote_Pricing_Procedure_Plan` overlay used
by `prepare_prm_pricing`:

- upsert `IFPartnerDistributorOnQuote` after `DefaultPricing`
- automatically resequence existing sections, including `HeaderDistribution`
- upsert the priority `1` option for `RLM_PRM_DISTI_Pricing_Procedure`
- upsert the `PartnerAccount.BillingAddress IsNotNull` criterion

The CCI task wraps the apply in a guarded
deactivate/apply/verify/reactivate sequence so a mid-task failure does not leave
the procedure plan inactive.

## JSON Schema

Top-level shape:

```json
{
  "developerName": "ProcedurePlanDefinitionVersionDeveloperName",
  "sectionMoves": [],
  "sections": [],
  "options": [],
  "criteria": []
}
```

Fields:

- `developerName` is required unless the CCI task supplies a `developerName`
  option override.
- `sectionMoves` is optional and should be rare. Prefer `placement` on
  `sections` for reusable overlays.
- `sections`, `options`, and `criteria` are optional arrays. An overlay can
  create a section and option without any criteria by omitting `criteria` or
  setting it to `[]`.

### Sections

```json
{
  "subSectionType": "MyFeatureSection",
  "description": null,
  "phase": 0,
  "resolutionType": "RuleBased",
  "sectionType": "PricingProcedure",
  "placement": {
    "afterSubSectionType": "DefaultPricing"
  }
}
```

Required:

- `subSectionType`

Optional:

- `description`
- `phase`
- `resolutionType`
- `sectionType`
- `sequence`
- `placement.afterSubSectionType`

Use either `sequence` or `placement`, not both. If neither is provided, new
sections are appended after the current highest sequence and existing sections
are patched without changing their sequence.

### Section Moves

```json
{
  "subSectionType": "ExistingSection",
  "sequence": 3
}
```

`sectionMoves` exists for explicit one-off migrations. It is less reusable than
anchored placement because it hard-codes a numeric sequence.

### Options

```json
{
  "sectionSubSectionType": "MyFeatureSection",
  "priority": 1,
  "criteriaLogic": "1",
  "expressionSetDeveloperName": "My_Pricing_Procedure",
  "readContextMapping": "QuoteEntitiesMapping",
  "saveContextMapping": "QuoteEntitiesMapping"
}
```

Required:

- `sectionSubSectionType`
- `priority`
- `expressionSetDeveloperName`

Optional:

- `criteriaLogic`
- `readContextMapping`
- `saveContextMapping`

Options are matched by resolved section ID plus `priority`.

### Criteria

```json
{
  "sectionSubSectionType": "MyFeatureSection",
  "optionPriority": 1,
  "sequence": 1,
  "operator": "IsNotNull",
  "objectField": "BillingAddress",
  "fieldPath": "PartnerAccount.BillingAddress",
  "actualValue": null,
  "dataType": "Text"
}
```

Required when a criterion is declared:

- `sectionSubSectionType`
- `optionPriority`
- `sequence`
- `operator`
- `fieldPath`

Optional:

- `objectField`
- `actualValue`
- `dataType`

Criteria are matched by resolved option ID plus `sequence`. If an overlay does
not need criteria, omit the `criteria` array entirely or use an empty array.

## Section Placement

Prefer declarative placement over hard-coded sequence moves:

```json
{
  "subSectionType": "MyFeatureSection",
  "placement": {
    "afterSubSectionType": "DefaultPricing"
  }
}
```

The task creates or patches all declared sections, then resolves the final
section order in the target org and resequences the full plan version. This lets
the overlay run against clean orgs, rerun safely, and insert into plans that
already have additional sections. Multiple sections in the same overlay that
target the same anchor are inserted in JSON order.

Gaps to account for when layering independent overlays:

- If two separate overlays both target the same anchor, final relative order is
  determined by run order unless the overlays share a higher-level ordering
  convention.
- Anchors must be stable `SubSectionType` values and must exist before the
  overlay runs.
- The task assumes `SubSectionType` is unique within a plan version. Duplicate
  section types fail fast because deterministic placement would be ambiguous.
