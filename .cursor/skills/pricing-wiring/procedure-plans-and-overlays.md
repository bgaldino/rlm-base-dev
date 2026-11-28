# Procedure plans and overlays

> Sub-file of `.cursor/skills/pricing-wiring/SKILL.md`. Plan concepts, orchestration setting, what a plan
> runs: [`../pricing-procedures/operations-and-troubleshooting.md`](../pricing-procedures/operations-and-troubleshooting.md).

## Overlay contract
Procedure-plan overlays should be JSON-driven and reusable across feature
packs. Treat the JSON as the behavioral contract and keep the task generic.

Runtime contract:

1. deactivate plan version inside the same task that applies the overlay
2. create or patch declared sections
3. compute final section order from the current org state
4. resequence sections through a collision-safe temporary range
5. resolve parent IDs with SOQL instead of relying on traversal upsert keys
6. create or patch options, then criteria if present
7. verify exact overlay invariants
8. in a guarded `finally` path, reactivate the plan version if it was active before, or activate it if `activate_after_apply` is true

When an overlay changes section order and adds a new section into an existing
sequence, declare placement by anchor (`placement.afterSubSectionType`) rather
than hard-coding the final numeric sequence:

```json
{
  "subSectionType": "MyFeatureSection",
  "placement": {
    "afterSubSectionType": "DefaultPricing"
  }
}
```

The task verifies dynamically from the JSON:

- sections: exactly one row per declared `subSectionType`
- placement: placed sections appear immediately after their declared anchor
- options: exactly one row per resolved section ID plus `priority`, with the
  expected expression set
- criteria: exactly one row per resolved option ID plus `sequence`, `fieldPath`,
  and `operator`

Criteria are optional. Omit the `criteria` array, or set it to `[]`, for
overlays that only add sections/options.

Avoid SFDMU relationship-traversal upserts for procedure-plan children unless
that exact traversal key has already been validated as idempotent in target
orgs.

Independent overlays that target the same anchor still need an ordering
convention if their relative order matters. Without a shared ordering key or a
single combined overlay declaration, run order is the only available signal.
If order matters across independently shipped overlays, add a stable ordering
model before relying on arbitrary execution order.

Repo examples:

- `tasks/rlm_create_procedure_plan_def.py`
- `tasks/rlm_apply_procedure_plan_overlay.py`
- `datasets/procedure_plan_overlays/`

## Testing your own plan

- **A second Quote/Default plan cannot be created.** The shipped definition allows one version (the
  error reads "a procedure plan version already exists for the procedure plan definition"). A new
  definition with ProcessType `RevenueCloud` saves, but its version is refused; without a SubType it
  fails "Specify a valid subtype". [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build, one org] To test your own plan on quotes, add sections to the shipped
  inactive Quote plan version, activate it, and set `skipOrgSttPricing=true`. With the repo default
  `false`, the Revenue Settings default procedure runs again after an active plan and re-prices (see
  `datasets/sfdmu/procedure-plans/README.md` -> *Activation*), so your sections' effect is overwritten.
  A 2026-11-26 run on the same build saw the default procedure alone, with a full waterfall, with
  the setting false, which does not match the Activation measurements.
  [Open: which behaviour holds with the setting false; settle by repeating the run and reading the waterfall against the Activation measurements]
- With two added sections the line waterfall held only the last section's execution. Two sections that
  both re-read the price book are last-wins. A trailing distribution section kept the earlier price
  and showed a one-step waterfall. [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build, one org] A later procedure with no price-book step compounds on the earlier
  section (9,400 became 4,700): a plan chains prices when later procedures continue from the price
  rather than re-price. Restore afterwards: remove your sections, deactivate the version, set the
  setting back to `false`. [Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build, one org]
- Do not repoint a shipped plan option to a clone to test; build your own section instead.

## An Order plan

No shipped Order plan exists. A custom Order plan (version active) made every Place order fail with
"couldn't fetch the data for RLM_SalesTransactionContext" (3 of 3); with the plan inactive the same order
priced. [Measured: 2026-11-26, 264, org kind not recorded] The cause was the procedure content, not the plan, the two-section sequencing, the custom
attribute, or an Order mapping rule with no `sObjectField` (shipped Order rules also have none):

- A clone of the default procedure in both sections priced.
- A procedure whose list-group filter included the criteria `ItemSubscriptionTerm IsNotNull` and
  `ItemSubscriptionTermUnit IsNotNull` failed with the generic message. The same procedure with only
  `NetUnitPrice IsNotNull`, or with criteria on `SellingModelType`, `PricingTermUnit`,
  `ItemPricingSource` and `NetUnitPrice`, priced.
- A malformed filter returns the rule engine's real message instead, so the generic text points to
  hydration.

Rule: a procedure on an active Order plan must not filter on tags the Order context does not hydrate;
bisect by re-importing variants. The guess is that those tags are not hydrated on the Order path.
[Open: which of the two term criteria fails, and why; settle by pricing an Order with each criterion alone] A commitment-term group that filters on them
([`../pricing-procedures/elements/commitment-term-discount.md`](../pricing-procedures/elements/commitment-term-discount.md))
therefore needs an Order variant without those criteria.
