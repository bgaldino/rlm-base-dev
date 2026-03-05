## Quote Summary Module (`post_quote_summary`)

Deploys a Lightning Web Component and supporting Apex that surfaces quote-level financial totals and a per-segment breakdown on the Quote record page. Designed for orgs using RLM ramp deals with named segments.

**Contributor:** Aaron Long ([@aaronlong78](https://github.com/aaronlong78)) — aaron.long@salesforce.com

---

### What It Deploys

| Type | API Name | Purpose |
|---|---|---|
| LWC | `rlmQuoteSummary` | Quote record page component — header totals + segment table |
| Flow | `RLM_QLISegmentFieldsforSummary` | Populates `RLM_RampKey__c` / `RLM_SegmentKey__c` / `RLM_SegmentLabel__c` on each QuoteLineItem at save time |
| Field | `Quote.RLM_TotalDiscountAmount__c` | Roll-up sum of `QuoteLineItem.TotalAdjustmentAmount` |
| Field | `QuoteLineItem.RLM_RampKey__c` | Text(50) — ramp identifier stamped by flow |
| Field | `QuoteLineItem.RLM_SegmentKey__c` | Text(50) — segment identifier stamped by flow |
| Field | `QuoteLineItem.RLM_SegmentLabel__c` | Text(80) — human-readable segment name stamped by flow |
| Permission Set | `RLM_QuoteSummary_Fields` | FLS read access for all four custom fields |

---

### Feature Flag

```yaml
# cumulusci.yml → project.custom
quote_summary: true
```

Set to `false` to skip deployment entirely.

---

### CCI Tasks and Flows

**Deploy only:**
```bash
cci task run deploy_post_quote_summary --org <alias>
```

**Deploy + assign permission set:**
```bash
cci flow run prepare_quote_summary --org <alias>
```

`prepare_quote_summary` is also called automatically by `prepare_rlm_org` (step 21) when `quote_summary: true`.

---

### Apex Architecture

```
RLM_QuoteSummaryController   (@AuraEnabled — LWC entry point)
  └── RLM_QuoteSummaryService  (orchestration)
        └── RLM_QuoteSummaryRepository  (all SOQL)

DTOs (returned to LWC via @AuraEnabled):
  RLM_QuoteSummaryDTO        { subtotal, discount, total }
  RLM_SegmentSummaryDTO      { rampId, segmentId, segmentLabel, subtotal, discount, total }
```

**`getQuoteSummary(quoteId)`** — returns one `RLM_QuoteSummaryDTO` with header-level totals sourced directly from the Quote roll-up fields.

**`getSegmentSummaries(quoteId)`** — returns a list of `RLM_SegmentSummaryDTO`, one per ramp/segment combination. Aggregates `QuoteLineItem` rows using a dynamic SOQL `GROUP BY RLM_RampKey__c, RLM_SegmentKey__c, RLM_SegmentLabel__c`. Shadow/bundle QLI rows (where `RLM_SegmentKey__c` is null) are filtered out post-aggregation in Apex, not in the WHERE clause, to avoid RLM's non-segmented row behavior.

---

### LWC: `rlmQuoteSummary`

Placed on the Quote record page. Renders two sections:

1. **Header card** — Subtotal, Total Discount, and Grand Total sourced from `getQuoteSummary`.
2. **Segment table** — One row per ramp/segment from `getSegmentSummaries`, showing Ramp, Segment, Subtotal, Discount, and Total columns. Only rendered when segment data is present (ramp deal quotes).

The component is also embedded in the `RLM_Quote_Record_Page` flexipage deployed by `post_arc_summary`. The Quote record page **must be deployed after** `post_quote_summary` so the LWC already exists when the flexipage references it.

---

### Flow: `RLM_QLISegmentFieldsforSummary`

A record-triggered Flow on `QuoteLineItem` (After Save) that populates the three segment fields (`RLM_RampKey__c`, `RLM_SegmentKey__c`, `RLM_SegmentLabel__c`) by reading the corresponding RLM segment context from the platform. These values drive the `GROUP BY` aggregation in the repository.

---

### Custom Fields

#### `Quote.RLM_TotalDiscountAmount__c`
- **Type:** Summary (Roll-Up Sum)
- **Summarized field:** `QuoteLineItem.TotalAdjustmentAmount`
- **Purpose:** Provides a single discount figure for the LWC header card without requiring an Apex query on the parent Quote; also used by `post_arc_summary` to surface discount on Amendment/Renewal quotes.

#### `QuoteLineItem.RLM_RampKey__c` / `RLM_SegmentKey__c` / `RLM_SegmentLabel__c`
- **Type:** Text (50 / 50 / 80)
- **Population:** Set by the `RLM_QLISegmentFieldsforSummary` flow at QLI save.
- **Note:** Non-segmented QLI rows (bundle parents, RLM shadow rows) will have null values — these are intentionally skipped in the repository aggregation.

---

### Notes

- The module is safe to deploy to orgs that do not use ramp deals. The LWC header card renders regardless; the segment table simply renders no rows when all QLIs have null segment keys.
- `RLM_TotalDiscountAmount__c` is a Summary field on Quote, so it is always current without any Apex trigger dependency.
