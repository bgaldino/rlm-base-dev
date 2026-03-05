## Amendment/Renewal Summary Module (`post_arc_summary`)

Deploys a Lightning Web Component and supporting Apex that provides an Amendment/Renewal deal breakdown on the Quote record page. For Amendment and Renewal quotes, the component classifies line-item revenue into **Renewal**, **Expansion**, **Attrition**, and **Net New Adds** buckets, and surfaces an asset-level detail table showing the change type and amounts for each asset.

**Contributor:** Aaron Long ([@aaronlong78](https://github.com/aaronlong78)) — aaron.long@salesforce.com

> **Dependency:** This module requires `post_quote_summary` to be deployed first. The `RLM_Quote_Record_Page` flexipage (owned by this module) embeds the `rlmQuoteSummary` LWC from `post_quote_summary`. Enabling `arc_summary: true` without `quote_summary: true` will cause the flexipage deployment to fail.

---

### What It Deploys

| Type | API Name | Purpose |
|---|---|---|
| LWC | `rlmAmendmentRenewalSummary` | Quote record page component — summary buckets + asset detail table |
| Flexipage | `RLM_Quote_Record_Page` | Quote record page hosting both `rlmQuoteSummary` and `rlmAmendmentRenewalSummary` |
| Flow | `RLM_QuoteOriginalActionType` | Stamps `RLM_OriginalActionType__c` on Quote when an Amendment/Renewal quote is created |
| Flow | `RLM_PopulatePreviousAmountOnQLI` | Orchestration flow — calls the Apex invocable to persist previous asset amounts before quote saves |
| Flow | `RLM_PopulatePreviousAmount` | Sub-flow invoked by the above |
| Apex | `RLM_PopulatePreviousAmount` | Invocable Apex — queries AssetStatePeriods and writes `RLM_PreviousAmount__c` to each QLI |
| Field | `Quote.RLM_OriginalActionType__c` | Text(50) — stores the quote action type (Amendment / Renewal) |
| Field | `QuoteLineItem.RLM_PreviousAmount__c` | Currency — previous period amount for each QLI, written by flow before quote save |
| Permission Set | `RLM_AmendRenewSummary_Fields` | FLS read/write access for both custom fields |

---

### Feature Flag

```yaml
# cumulusci.yml → project.custom
arc_summary: true         # Requires quote_summary: true
quote_summary: true       # Must be enabled alongside arc_summary
```

Set `arc_summary: false` to skip deployment. Setting `arc_summary: true` while `quote_summary: false` is a no-op — both `prepare_arc_summary` steps are gated by `and project_config.project__custom__quote_summary`.

---

### CCI Tasks and Flows

**Deploy only:**
```bash
cci task run deploy_post_arc_summary --org <alias>
```

**Deploy + assign permission set:**
```bash
cci flow run prepare_arc_summary --org <alias>
```

`prepare_arc_summary` is also called automatically by `prepare_rlm_org` (step 22, after `prepare_quote_summary` at step 21) when both flags are `true`.

---

### Apex Architecture

```
RLM_AmendmentRenewalController   (@AuraEnabled — LWC entry point)
  └── RLM_AmendmentRenewalService  (orchestration, shared context builder)
        └── RLM_AmendmentRenewalRepository  (all SOQL)

RLM_PopulatePreviousAmount       (@InvocableMethod — called by flow)
  └── RLM_AmendmentRenewalRepository  (asset/ASP queries)

DTOs (returned to LWC via @AuraEnabled):
  RLM_AmendmentRenewalDTO        { subtotal, discount, total, originalActionType,
                                   renewalAmount, expansionAmount, attritionAmount,
                                   netNewAddsAmount, netChange }
  RLM_ExpansionAttritionDTO      { assetId, assetName, previousAmount, currentAmount,
                                   changeAmount, changeType, assetActionType }
```

#### Service: `RLM_AmendmentRenewalService`

All SOQL is executed once inside a private `buildContext(quoteId)` factory method, which populates a private `AmendmentContext` inner class. Both public methods share this context to avoid duplicate queries.

**`getAmendmentRenewalSummary(quoteId)`** — returns one `RLM_AmendmentRenewalDTO` with:
- **Renewal** — asset revenue with no measurable change
- **Expansion** — asset revenue that increased (by amount for Renewal quotes; by quantity direction for Amendment quotes)
- **Attrition** — asset revenue that decreased
- **Net New Adds** — revenue from products that have no prior Asset (new products added mid-term)
- **Net Change** = Expansion − Attrition + Net New Adds

**`getExpansionAttritionDetails(quoteId)`** — returns one `RLM_ExpansionAttritionDTO` per asset with previous amount, current amount, change amount, and change type (`No Change` / `Expansion` / `Attrition`).

Both methods return empty/zero results for non-Amendment/Renewal quotes without throwing.

#### Previous Amount Resolution (3-Priority Fallback)

For each asset, the service resolves the "previous" amount using this priority order:

1. **`QuoteLineItem.RLM_PreviousAmount__c`** — written by the `RLM_PopulatePreviousAmountOnQLI` flow before the quote is saved. Most authoritative; skips renewal normalization.
2. **`AssetStatePeriod.Amount`** — normalized to the quote's subscription term. Active periods (EndDate = null) are prioritized over ended periods.
3. **`Asset.CurrentAmount`** or **`Asset.CurrentMrr × termMonths`** — last-resort fallback when no state period exists.

For Renewal quotes where neither priority 1 nor a prior ASP is available, a normalization heuristic is applied: if the resolved previous amount differs from the current amount by more than 10%, it is overridden with the current amount (treating the line as a pure renewal with no change). This prevents spurious expansion/attrition from term-length mismatches.

#### Amendment vs. Renewal Classification

| Quote Type | Change Amount | Expansion/Attrition Trigger |
|---|---|---|
| Amendment | `currentAmount` (mirrors the line) | Quantity change direction (product-level) |
| Renewal | `currentAmount − previousAmount` | Amount change direction |

For Amendment quotes, revenue is only classified as Expansion or Attrition if the product-level quantity (derived from `QuoteLineItem.EndQuantity`, `StartQuantity + Quantity`, or `Quantity` in that priority) measurably changed vs. the asset's prior quantity from AssetStatePeriod.

---

### LWC: `rlmAmendmentRenewalSummary`

Placed on the Quote record page via `RLM_Quote_Record_Page`. The component is conditionally rendered:

- For **Amendment / Renewal** quotes: shows the five-bucket summary (Renewal, Expansion, Attrition, Net New Adds, Net Change) plus a collapsible asset detail table.
- For **all other** quote types: renders nothing (hidden via the `originalActionType` check in the DTO).

---

### Flows

#### `RLM_QuoteOriginalActionType`
A record-triggered Flow on `Quote` (After Save, on create) that stamps `RLM_OriginalActionType__c` with the RLM-provided action type (e.g., `Amendment`, `Renewal`). This field is the gating condition used throughout the Apex layer to determine whether any amendment/renewal logic should execute.

#### `RLM_PopulatePreviousAmountOnQLI` + `RLM_PopulatePreviousAmount`
A record-triggered Flow on `Quote` (Before Save) that invokes `RLM_PopulatePreviousAmount` (invocable Apex) to write `RLM_PreviousAmount__c` on each related QuoteLineItem. Running before save ensures the previous amounts are persisted and available when the LWC later calls `getAmendmentRenewalSummary` / `getExpansionAttritionDetails`.

The Apex:
1. Validates the quote is Amendment or Renewal; exits early otherwise.
2. Resolves `AccountId` from the Quote, or falls back to the most common AccountId across related Assets.
3. Fetches related Assets → AssetStatePeriods → resolves previous amounts using the same 3-priority fallback described above.
4. Distributes the product-level previous amount equally across QuoteLineItems for the same product.
5. Only writes to QLIs where `RLM_PreviousAmount__c` is not already populated (idempotent).

---

### Custom Fields

#### `Quote.RLM_OriginalActionType__c`
- **Type:** Text(50)
- **Population:** `RLM_QuoteOriginalActionType` flow (after Quote create)
- **Values:** `Amendment`, `Amend`, `Renewal`, `Renew` (all treated equivalently by Apex)

#### `QuoteLineItem.RLM_PreviousAmount__c`
- **Type:** Currency
- **Population:** `RLM_PopulatePreviousAmountOnQLI` flow (before Quote save) via invocable Apex
- **Purpose:** Persists the pre-amendment/pre-renewal asset amount on the QLI so it survives quote saves and is available for comparison without re-querying the AssetStatePeriod at display time.

---

### Flexipage: `RLM_Quote_Record_Page`

Replaces or supplements the default Quote record page. Contains two components in order:

1. `rlmQuoteSummary` (from `post_quote_summary`) — header totals and segment table
2. `rlmAmendmentRenewalSummary` (from this module) — amendment/renewal bucket summary and asset detail

Because the flexipage references the `rlmQuoteSummary` LWC, `post_quote_summary` **must be deployed before `post_arc_summary`**.

---

### Notes

- Orgs without Amendment or Renewal quote types can safely deploy this module. The LWC, flows, and Apex all guard on `RLM_OriginalActionType__c` and return empty results for standard quotes.
- `AccountId` on the Quote is optional for asset resolution. If null, the Apex finds the most-common `AccountId` across assets related to the quote's products — useful in orgs where the Quote is not always linked to an Account at creation time.
- The `getAssetStatePeriods` query orders by `AssetId, EndDate DESC NULLS FIRST`, ensuring active (open-ended) periods are always processed first, which correctly populates `latestPeriodsByAsset` in the in-memory deduplication loop.
