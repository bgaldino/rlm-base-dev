# Price Revision Policies and Index Rates

> Sub-file of `.cursor/skills/pricing-setup/SKILL.md`. Release 264 / API v68.0. Sources:
> `ind.pricing_understand_price_revisions.htm`, `ind.pricing_apply_policy_driven_price_revisions.htm`,
> `ind.pricing_use_the_price_revision_element_in_a_pricing_procedure.htm`,
> `ind.qocal_consumer_price_index_and_price_uplifts.htm`, `ind.qocal_considerations_ramp_deals.htm`; repo: `../pricing-wiring/price-revision-cpi.md`.
> Mostly not live-verified; renewal rows measured in
> [`../asset-lifecycle-changes/change-policy-mapping.md`](../asset-lifecycle-changes/change-policy-mapping.md).

A Price Revision Policy holds the uplift formula and validity; an Index Rate holds a benchmark
(for example CPI) per region and period. The Price Revision element reads both to uplift renewal prices.
Element fields: [`../pricing-procedures/elements/price-revision.md`](../pricing-procedures/elements/price-revision.md).
Repo CPI data load, expected results, verification: [`../pricing-wiring/price-revision-cpi.md`](../pricing-wiring/price-revision-cpi.md).

## When you need it

- Renewal uplifts tied to inflation (CPI plus a negotiated spread) or a fixed percentage.
- Price Index (CPI) policies are not supported on ramped products or with compound uplift; per-segment ramp uplift itself is a Price Revision feature (see repo file). Not supported for Partner/Customer Community users. [Help]

## Set it up

Permission: users renewing with CPI uplifts need the **Renew Assets** user permission. [Help: `ind.qocal_consumer_price_index_and_price_uplifts.htm`]

1. **Region values.** Setup > Object Manager > Index Rate > Fields & Relationships > Region > Region Picklist Values > New; add each region (country). Do this before policies and rates. [Help]
2. **Price Revision Policy.** App Launcher > Price Revision Policies > New. Name, Type, Effective From/To, Region, Formula. Build the formula with the function/resource pickers: pick `MAX`, replace the contents with `10,`, add resource `PriceIndex`, operator `+`, then `5`. Result `MAX(10, PriceIndex + 5)` = CPI plus 5%, floor 10%. All numbers are percentages. [Help]
3. **Index Rates.** App Launcher > Index Rates > New: Name, Rate (e.g. 8), Valid Start/End Date, Region, Usage Type = Pricing. One record per period. [Help]
4. **Activate the Index Rate decision table.** Orgs updated to Winter '26 with Price Tracking may have it deactivated: Setup > Decision Tables > Index Rate > activate. Refresh it after rate changes. [Help]
5. **Procedure.** Add the Price Revision element bound to the Index Rate table (element file).
6. **Expose on lines.** Add Price Revision Policy to the Pricing Information section of the Quote Line Item, Order Product and Asset State Period layouts, and Unit Price Uplift to Quote Line Item and Order Product; add Unit Price Uplift to the Transaction Line Editor display columns on the Quote record page (Lightning App Builder) and Details/Fields on the Order page. [Help: `ind.qocal_consumer_price_index_and_price_uplifts.htm`]

## Fields and rules

| UI label | API name | Rules |
|---|---|---|
| Name | `PriceRevisionPolicy.Name` | e.g. US CPI. |
| Type | `PolicyType` | **Flat** (manual uplift value, no table) or **Price Index** (rate from Index Rate table). [Help] |
| Formula | `Formula` | Resources include `PriceIndex`; line `UnitPriceUplift` appears as `PolicyAdjustment` in the repo's formulas [Repo]. |
| Region | `Region` | Picklist; selects which Index Rate applies. |
| Effective From / To | `EffectiveFrom`, `EffectiveTo` | Same-region ranges can't overlap unless the org is multi-currency. [Help] |
| Index Rate Rate | `IndexRate.Rate` (percent) | CPI value for the period. |
| Valid Start / End Date | `ValidStartDate`, `ValidEndDate` | Pricing date must fall inside; no overlap per region (non multi-currency). [Help] |
| Region | `IndexRate.Region` | Picklist; add values first. |
| Usage Type | `UsageType` | `Pricing` for this use. |
| Active | `IsActive` | Present on the object; Help does not discuss it. |

Assignment: sales reps pick the policy on the quote or order line (`PriceRevisionPolicyId`) and a spread in **Unit Price Uplift** (`UnitPriceUplift`), e.g. +5. Example: CPI 2.7% + 5 = 7.7%. [Help]

## How pricing uses it

- Renewal arithmetic [Help]: with pricing source Last Transaction Price and uplift type CPI/Variable, net unit price = last transaction price x (1 + CPI% + uplift%), e.g. $100 x 1.055 = $105.50. A rep's extra discount can override the net unit price.
- The renewal needs an Index Rate matching the effective date; if none is found an error occurs. [Help]
- Flat: the uplift value comes from the line, no table lookup. Price Index: rate from the Index Rate decision table matched on Region and date.
- Element, conditions, compound ramp path: [`../pricing-procedures/elements/price-revision.md`](../pricing-procedures/elements/price-revision.md). Refresh mechanics: [`../decision-tables/SKILL.md`](../decision-tables/SKILL.md).

## Data and automation

Objects `PriceRevisionPolicy`, `IndexRate` load by API/import like any custom-style object; keep ranges non-overlapping per region. This repo ships `qb-price-revision` data and a CPI verification recipe: [`../pricing-wiring/price-revision-cpi.md`](../pricing-wiring/price-revision-cpi.md). Annual CPI anniversary amendments (year 2 and 3 priced automatically with a customer notification) are described in Help; the mechanism is not specified. [Help]

## Verify

```bash
sf data query --target-org <sf_alias> -q "SELECT Name, PolicyType, Formula, Region, EffectiveFrom, EffectiveTo FROM PriceRevisionPolicy ORDER BY Region, EffectiveFrom"
sf data query --target-org <sf_alias> -q "SELECT Name, Rate, Region, UsageType, ValidStartDate, ValidEndDate, IsActive FROM IndexRate ORDER BY Region, ValidStartDate"
```
Then Simulate with an in-range Valid Start Date and region; the waterfall shows a Price Revision entry. If wrong, refresh the Index Rate table. [Help]

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| No revision or zero rate | Index Rate table inactive or stale; region/date out of range | Activate, refresh, check ranges |
| Overlap error saving policy/rate | Same-region date overlap | Re-date; multi-currency orgs are exempt |
| Region value rejected | Picklist lacks the value (or is restricted) | Add the value first; repo notes behavior varies by org |
| Renewal errors on date | No Index Rate for effective date | Add the rate for that period |
| Policy missing on line | Field not on layout | Add Price Revision Policy / Unit Price Uplift to layouts |
| Custom profile sees nothing | No access to the entities | Grant object/field access [Help] |

## Open questions

- Help's CPI article names "uplift type CPI/Variable" and an asset-level CPI type with no field API names; the schema for those is not confirmed here.
- Help element article uses tag names `..PolicyName_std` and the repo uses `ItemPriceRevisionPolicy__std`; the bound tag is a context choice (see element file).
- Whether `IsActive` on `IndexRate` gates the decision table is not documented.
