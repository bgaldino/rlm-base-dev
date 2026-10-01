# Expression set overlays

Declarative JSON patches that add, remove, update or reorder steps and variables
in an existing **expression set** (pricing procedure) version, without rewriting
the whole definition. The overlay is merged into a live GET of the version and
sent back as one Connect full-graph PATCH.

Not to be confused with `datasets/procedure_plan_overlays/`, which patches
procedure plans (a different object, applied by `apply_procedure_plan_overlay`).

## Overlays

| File | Target | What it adds | Runs |
|------|--------|--------------|------|
| `approval_flags.json` | `RLM_DefaultPricingProcedure_V1` | Per-line discount approval flags: resets every line to level 0 and a blank indicator, then sets level 1 Manager (15% to under 25%), 2 Director (25% to under 35%) or 3 VP (35% to under 100%) from `ItemDiscountPercentage`. Writes `RLM_Approval_Level_Calc__c` and `RLM_Approval__c` on QuoteLineItem, or on OrderItem when an Order is priced. 12 steps, 8 constants. | **In the build.** `apply_approval_flags_overlay` in the `prepare_approvals_pricing` flow (part of `prepare_rlm_org`), when the `quantumbit` and `approvals` flags are both on. |
| `discount_distribution.json` | `RLM_DefaultPricingProcedure_V1` | Header-discount block: amount-based and percentage-based header discount and header price override `ListGroup`s, then the `DiscountDistributionService` element that spreads the header discount to lines. 10 steps, 4 `Constant_DDS_*` constants. | **Manual only.** Worked example; its steps already ship in the `force-app` procedure. |
| `map_line_item.json` | `RLM_DefaultPricingProcedure_V1` | The `MapLineItemtoDetailItem` step for Advanced Detail Line Pricing. 1 step. | **Manual only.** Worked example; the step already ships in the `force-app` procedure. |

Against the shipped procedure, a manual-only overlay just replays steps that
already exist (see *Existing steps* below). Its use is as a template for new
overlays, or on a clone that lacks those steps.

### When `approval_flags.json` runs

It must run after the procedure exists and its context can carry the target
fields, and before procedure plans are wired to the procedure:

1. `activate_and_deploy_expression_sets` deploys and activates
   `RLM_DefaultPricingProcedure`.
2. `apply_context_approvals` maps the two `QuoteLineItem` fields into
   `RLM_SalesTransactionContext` (`datasets/context_plans/Approvals`). The
   fields themselves ship in `unpackaged/post_approvals`.
3. `apply_approval_flags_overlay` applies this overlay.
4. `prepare_procedureplans` runs afterwards, so the apply does not
   cascade through procedure plans.

Repricing users need `RLM_Approvals`, which grants edit access to both stored
approval outputs on quote lines and order products. Repricing resets and
recalculates those values, including any manual edits.

## Applying an overlay

```bash
cci task run apply_expression_set_overlay --org <cci_alias> \
    -o overlay_file datasets/expression_set_overlays/<file>.json
cci task run apply_expression_set_overlay --org <cci_alias> \
    -o overlay_file datasets/expression_set_overlays/<file>.json -o dry_run true
```

The standalone toolkit does the same without CCI:
`python scripts/expression_sets/apply_expression_set_overlay.py --target-org <sf_alias> --overlay <file>`.

Normal CCI logs summarize automatically handled HTML-encoding and server-field
validation warnings once before PATCH. Step/variable transformation messages are
at DEBUG; actionable warnings and validation errors remain visible.
HTML-encoding warnings remain warnings when normalization is off.

The CCI task:

1. validates the overlay and the merged graph locally, **before** touching the org;
2. deactivates the version (and any referencing procedure plan versions, when
   `cascade_deactivate_procedure_plan` is true);
3. GETs the live definition, merges the overlay, PATCHes it, and verifies the
   stored graph against what was sent (`verify`);
4. restores the readable step labels (see *Step labels*) while deactivated;
5. reactivates the version (`activate_after_apply`, default true).

A failed PATCH leaves the version **deactivated** rather than reactivating a
possibly half-applied definition.

## Structure

```json
{
  "expressionSetApiName": "RLM_DefaultPricingProcedure",
  "versionApiName": "RLM_DefaultPricingProcedure_V1",
  "description": "What the overlay does and why.",
  "addVariables": [ { "name": "MyConstant", "type": "Constant", "dataType": "Text", "value": "..." } ],
  "addSteps": [
    { "name": "MyGroup", "label": "My Group", "stepType": "ListGroup",
      "placement": { "afterStep": "ExistingStepName" } },
    { "name": "MyFilter", "label": "My Filter", "stepType": "AdvancedListFilter",
      "parentStep": "MyGroup", "sequenceNumber": 1 }
  ],
  "externalDependencies": {
    "customFields": ["Object.Field__c (why it is needed)"],
    "note": "What the target org must already have, and where it comes from."
  }
}
```

| Key | Purpose |
|-----|---------|
| `expressionSetApiName`, `versionApiName` | The set and version to patch. Override with the `expression_set_api_name` / `version_api_name` task options. |
| `addSteps` | New steps. A **top-level** step needs `placement` (`afterStep`, `beforeStep` or `sequenceNumber`) and no `sequenceNumber`. A **child** step carries `parentStep` and its own `sequenceNumber` (numbered per parent, from 1) and no `placement`. List a parent before its children. Anchors name steps by their spaceless `name`, not their label. |
| `label` (on an `addSteps` or `updateSteps` entry) | Readable name shown in the UI. Overlay-only: stripped before the Connect PATCH and written through the Tooling API afterwards. A top-level `labels` map (`{name: label}`) works too; the per-step value wins. |
| `removeSteps`, `updateSteps`, `reorderSteps`, `removeVariables` | Remove, edit, or move existing steps and variables. |
| `addVariables` | **Input** version variables the new steps consume (constants, scratch variables). Never a step's own output: the platform creates that, and declaring it again fails with `A context variable with the name ... already exists`. |
| `externalDependencies` | Documentation of what the overlay does **not** create: custom fields, custom context nodes and fields the target must already have. Ignored by the apply; the validator uses it to silence its custom-reference warning. |

### Step labels

A step has a spaceless `name` (its API identifier and the `parentStep` key) and a
readable `label`. Connect has no `label` field, so every Connect PATCH resets all
labels in the version to their names. Both the CCI task and the toolkit
snapshot labels before the PATCH and restore them afterwards. CCI restores them
before reactivation; the standalone toolkit uses a second deactivate → Tooling
API PATCH → reactivate cycle. A new step gets the `label`
the overlay gives it; without one it shows its `name`. Turn restoring off with
`-o preserve_labels false` (CCI) or `--no-preserve-labels` (toolkit).

In CCI, a label read/write failure is logged as a warning and does not fail the
apply. Deactivation, reactivation, and procedure-plan restoration failures fail
the task.
To recover this overlay's labels, combine the base metadata labels with its
new step labels (which are absent from the base XML):

```bash
python -c 'import json; p=json.load(open("datasets/expression_set_overlays/approval_flags.json")); print(json.dumps({s["name"]:s["label"] for s in p["addSteps"] if s.get("label")}, ensure_ascii=False))' > /tmp/approval-step-labels.json
python scripts/expression_sets/relabel_expression_set.py --target-org <sf_alias> --expression-set RLM_DefaultPricingProcedure --from-metadata force-app/main/default/expressionSetDefinition/RLM_DefaultPricingProcedure.expressionSetDefinition-meta.xml --labels-file /tmp/approval-step-labels.json --confirm
```

### Existing steps

Adding a step whose `name` already exists replays it: the apply accepts it only
if the stored step already matches, and otherwise fails **before** deactivating
anything. Use `updateSteps` to change an existing step, or `reorderSteps` to
move one. Details: [existing-step and verification rules](../../scripts/expression_sets/README.md#existing-steps-and-verification).

## Authoring a new overlay

Capture, don't hand-write: export the step from an org that already has it,
which also classifies its dependencies into `addVariables` and
`externalDependencies`:

```bash
python scripts/expression_sets/export_expression_set_overlay.py --target-org <sf_alias> \
    --developer-name RLM_DefaultPricingProcedure --step "<step name>" \
    --after "<anchor step name>" --with-labels --out datasets/expression_set_overlays/<file>.json
```

Then validate it offline, and apply it to a disposable clone before a shipped
procedure:

```bash
python tests/test_expression_set_schema.py
```

That suite validates every `*.json` in this directory. Wire a new overlay into
the build with a dedicated task in `cumulusci.yml` (copy
`apply_approval_flags_overlay`), and add it to the table above.

## Related

- Authoring rules (placement, dependency scopes, ordering constraints, resets):
  `.cursor/skills/expression-sets/authoring-and-overlays.md`
- Skill entry point: `.cursor/skills/expression-sets/SKILL.md`
- Toolkit guide: `scripts/expression_sets/README.md`
- Connect API reference: `docs/references/expression-set-connect-api-reference.md`
