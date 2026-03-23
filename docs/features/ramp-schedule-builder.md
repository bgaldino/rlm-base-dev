# Ramp Schedule Builder — Feature Documentation

> **Target release:** API v66.0 (Spring '26)
> **Deployment path:** `unpackaged/post_ramp_builder`

---

## Overview

The Ramp Schedule Builder is a custom Salesforce feature that enables sales reps to apply a
multi-segment ramp schedule to a Quote directly from the Quote record page. It creates a
`QuoteLineGroup` hierarchy — one parent `RampScheduleGroup` with N child segment groups —
without requiring the rep to navigate the native Ramp Schedule UI or touch the catalog.

The builder is surfaced as a Lightning Screen Flow (`RLM_Create_Ramp_Schedule_V4`) launched
from a Quick Action on the Quote record page.

---

## Key Constraints

**The builder is designed for quotes with no products yet.** The primary workflow is:

1. Create a new Quote.
2. Launch the ramp builder — it creates the empty group structure.
3. Add products from the catalog; the platform natively distributes them across all segments.

Applying a ramp to a quote that already has products uses an alternate async path
(`useDmlApproach = false`) which is more complex and experimental.

---

## Known Limitations

### Trial segments are not currently supported for order activation

Trial segments use `SegmentType = 'Custom'` on `QuoteLineGroup` and `OrderItemGroup`. While
`Custom` is the correct picklist value for non-year-duration segments (Salesforce enforces that
`Yearly` segments must span exactly 1 year), `Custom` segments created via DML fail order
activation with:

> `We can't change the status of the order to Activated. Make sure that segment [id] and all
> its ramped line items have the same segment type, start date, and end date, and try again.`

The activation validator appears to require additional internal metadata on `Custom` segments
that is only set when segments are created through the platform's `EditGroup` API (not DML).
Standard `Yearly` segments do not have this requirement.

**Impact:** Quotes built with a trial segment via this builder will produce orders that cannot
be activated in the standard activation flow. The trial toggle defaults to **No** until a fix
is identified.

**Workaround:** Build the ramp without a trial segment. Yearly segments activate correctly.

---

## Architecture

### Primary path — DML (empty quote, synchronous)

Used when `useDmlApproach = true` (the default).

| Step | What happens |
|------|-------------|
| 1 | `RLM_RampScheduleService` creates the parent `QuoteLineGroup` (`Type = RampScheduleGroup`, `IsRamped = false`) via DML. |
| 2 | Creates segment 0 group (`IsRamped = true`, `SegmentType` set per segment definition). |
| 3 | Creates segment 1..N groups similarly. |
| 4 | Returns all group IDs to the Flow synchronously. |

No products are moved — the quote should be empty. After the builder completes, the rep adds
products from the catalog and the platform natively distributes them across every segment group.

### Secondary path — API migration (existing QLIs, async)

Used when `useDmlApproach = false`. Intended for applying a ramp to a quote that already has
products on it. This path is experimental.

| Step | What happens |
|------|-------------|
| 1 (sync) | `RLM_RampScheduleService` creates parent group + segment 0 via DML. Moves existing `QuoteLineItem`s into segment 0, setting `QuoteLineGroupId`, `SegmentType`, `StartDate`, `EndDate`, `Discount`, `UnitPriceUplift`. |
| 2 (sync) | Enqueues `RLM_RampMigrationQueueable`. |
| 3 (async) | Queueable calls `EditGroup` on segment 0 → platform stamps `RampIdentifier` / `SegmentIdentifier` on all QLIs. |
| 4 (async) | Queueable calls `CloneSalesTransaction` × (N−1) → creates segments 1..N with products cloned and ramp identifiers linked. |
| 5 (async) | Calls `EditRampSchedule` to fix segment dates and names. |
| 6 (async) | DML updates `SegmentType`, `Discount`, `RLM_UpliftPercent__c` on all groups and QLIs per their segment definition. Deletes `OneTime` QLIs from non-primary segments. |

> **Why async?** Salesforce prohibits HTTP callouts after uncommitted DML in the same
> transaction. The sync phase commits first, then the Queueable runs in a fresh transaction
> with callout access.

---

## Components

### Apex classes

| Class | Role |
|-------|------|
| `RLM_RampScheduleFlowAction` | `@InvocableMethod` entry point called by the Flow. Deserializes segment JSON and delegates to the service. |
| `RLM_RampScheduleService` | Core service — validates, routes to DML or API path, creates `QuoteLineGroup` records. |
| `RLM_RampScheduleRequest` | Input DTO — carries `quoteId`, `scheduleHeader`, `segments[]`, `useDmlApproach`. |
| `RLM_RampScheduleResponse` | Output DTO — carries `success`, `groupIds`, `errors[]`, `jobId`. |
| `RLM_RampScheduleValidator` | Validates the request: segment continuity, no gaps/overlaps, yearly duration, trial/pro-rata placement rules. |
| `RLM_RampMigrationQueueable` | Async job that performs the API-based migration (EditGroup → CloneSalesTransaction → EditRampSchedule). |
| `RLM_RampScheduleStatusController` | LWC controller — polled by `rlmRampScheduleStatus` to check Queueable job completion. |
| `RLM_QuoteLineItemDiscountUpliftHandler` | Before-insert/update trigger handler — copies `Discount` and `RLM_UpliftPercent__c` from the parent `QuoteLineGroup` to its `QuoteLineItem`s. |
| `RLM_QuoteLineItemRampModeHandler` | Before-insert/update trigger handler — copies `RLM_RampMode__c` from `QuoteLineGroup` to `QuoteLineItem`. |

### Trigger

| Trigger | SObject | Events |
|---------|---------|--------|
| `QuoteLineItemRampTrigger` | `QuoteLineItem` | `before insert`, `before update` |

Fires `RLM_QuoteLineItemRampModeHandler` and `RLM_QuoteLineItemDiscountUpliftHandler` to keep
line items in sync with their group's ramp configuration.

### Lightning Web Components

| LWC | Role |
|-----|------|
| `rlmRampScheduleForm` | Main form — collects schedule name, start date, number of segments, schedule type (Yearly/Custom), ramp mode. Orchestrates the child components and submits the request to the Flow. |
| `rlmRampScheduleTrialSection` | Trial period configuration — toggle (defaults to **No**), duration in days, discount %. Publishes state via LMS for the preview table. |
| `rlmRampSchedulePreviewTable` | Live preview — renders the segment table as the user edits form values. Subscribes to LMS for trial state. |
| `rlmRampScheduleStatus` | Post-submit status component — polls the Queueable job status and shows a spinner until the async migration completes (API path only). |
| `rlmRampScheduleFlowModalAction` | Wrapper LWC used inside the Flow screen — bridges Flow variable bindings to the form component. |
| `rlmRampRefreshPage` | Success screen component — provides a "View Quote" button that navigates back to the Quote record page (using `backgroundContext` from the Quick Action URL), triggering a full page refresh so the new groups appear. |

### Flow

**`RLM_Create_Ramp_Schedule_V4`** — Screen Flow launched from the Quote Quick Action.

Key screens:
- **Input screen** — hosts `rlmRampScheduleFlowModalAction` (which renders the full builder form).
- **Confirmation screen** (`DML_Confirmation_Screen`) — shows a success message and hosts `rlmRampRefreshPage` with the footer hidden.

The Flow passes `recordId` (Quote ID) into the form component and receives back `segmentsJson`,
`scheduleName`, and other parameters to pass to `RLM_RampScheduleFlowAction`.

---

## Custom Fields

### `QuoteLineGroup`

| Field | API Name | Type | Purpose |
|-------|----------|------|---------|
| Ramp Mode | `RLM_RampMode__c` | Picklist | Identifies whether the group uses Standard or Staggered ramp mode. Copied to `QuoteLineItem` via trigger. |
| Uplift Percent | `RLM_UpliftPercent__c` | Percent | Stores a positive price uplift % for uplift-mode segments. Copied to `QuoteLineItem.UnitPriceUplift` via trigger. |

### `QuoteLineItem`

| Field | API Name | Type | Purpose |
|-------|----------|------|---------|
| Ramp Mode | `RLM_RampMode__c` | Text | Copied from parent group via trigger. Mapped to `OrderItem.RLM_RampMode__c` via `OrderEntitiesMapping` context. |

### `OrderItemGroup`

| Field | API Name | Type | Purpose |
|-------|----------|------|---------|
| Ramp Mode | `RLM_RampMode__c` | Text | Copied from `QuoteLineGroup.RLM_RampMode__c` during quote-to-order conversion via the `OrderEntitiesMapping` pricing context. |

### `OrderItem`

| Field | API Name | Type | Purpose |
|-------|----------|------|---------|
| Ramp Mode | `RLM_RampMode__c` | Text | Copied from `QuoteLineItem.RLM_RampMode__c` via pricing context mapping. |

---

## Segment Types

| Segment type constant | `QuoteLineGroup.SegmentType` | Notes |
|-----------------------|------------------------------|-------|
| `YEARLY` | `Yearly` | Standard — segment spans exactly 1 year. |
| `TRIAL` | `Custom` | ⚠️ **Not supported for order activation.** See [known limitations](#known-limitations). |
| `CUSTOM` | `Custom` | ⚠️ Non-standard duration — same activation constraint as Trial. |
| `PRO-RATED` | `Custom` | ⚠️ Same activation constraint. |

> `Yearly` segments produced by this builder activate correctly. `Custom` segments fail order
> activation in the DML-created path due to a platform constraint on how internal ramp metadata
> is initialized.

---

## Approval Level Integration

`QuoteLineItem.RLM_Approval_Level_Calc__c` is a formula field that determines the discount
approval tier for each line item. Lines with `Discount >= 1` (i.e., 100% discount — trial
lines) return `0` so they are excluded from the approval workflow.

```
IF(Discount >= 1, 0,
  IF(Discount < 0.15, 0,
    IF(Discount < 0.25, 1,
      IF(Discount < 0.35, 2, 3))))
```

---

## Order Activation — What Works

| Configuration | Activates? |
|---------------|-----------|
| Ramp with Yearly segments only | ✅ Yes |
| Ramp with Yearly segments + consumption products | ✅ Yes |
| Ramp with Yearly segments + OneTime products (outside ramp groups) | ✅ Yes |
| Ramp with a Trial (Custom) segment | ❌ No — platform activation validation fails |

---

## Deployment

The builder is deployed as part of the `post_ramp_builder` unpackaged directory. Key CCI tasks:

```bash
# Deploy the ramp builder metadata
cci task run deploy_post_ramp_builder --org <alias>

# Apply the RampMode context attributes to SalesTransactionContext
cci task run apply_context_ramp_mode --org <alias>
```

The permission set `RLM_RampSchedule` grants access to the custom fields, the Flow, and the
Quick Action.
