# Deep Clone of a Quote — Routes and What Carries Over

Read this before cloning a quote to start a new negotiation round, or before writing
automation that clones. Parent: [quote-negotiation-rounds](SKILL.md).

## Routes

| Route | How | Notes |
|---|---|---|
| UI | **Deep Clone** action on the quote or order record page [Help: `ind.qocal_clone_quotes_and_orders`] | Needs **Clone Quotes and Orders** on in Revenue Settings and the action on the page. The setting controls only the UI action [Help: `ind.qocal_clone_quotes_and_orders`]. This repo's base quote page lists `DeepCloneAction` in its highlights-panel actions [Repo: `templates/flexipages/base/RLM_Quote_Record_Page.flexipage-meta.xml`], and the build sets `enableTransactionCloning` [Repo: `unpackaged/pre/1_settings/RevenueManagement.settings-meta.xml`] |
| Connect API | `POST /services/data/v68.0/connect/rev/sales-transaction/actions/clone` with `recordIds` (exactly one id) and `salesTransactionId` [Dev guide: `connect_resources_clone_sales_transaction`] | Clones a Quote, Order, QuoteLineItem, OrderItem, QuoteLineGroup or OrderItemGroup. Optional `options` (v65+): `recordTypeId` and `lineScope` [Dev guide: `connect_requests_clone_options_input`]. Works with the Revenue Settings toggle off [Help: `ind.qocal_clone_quotes_and_orders`] |
| Invocable action | `deepCloneSalesTransaction` (`/actions/standard/deepCloneSalesTransaction`), API 67.0+, output `newRecordId` [Dev guide: `actions_obj_deep_clone_sales_transaction`] | On one 264 scratch org with `enableTransactionCloning` on, REST answered `Invalid Action Type: deepCloneSalesTransaction` and `/actions/standard` did not list it [Measured: 2026-11-10, 264]. Use the Connect API until it resolves on your org |
| Line or group in the editor | Select a line and **Clone**, or a group and **Clone Group** [Help: `ind.qocal_clone_quotes_and_orders`] | Copies inside the same quote; not a new round |
| Repo Apex | `RLM_CloneSalesTransaction` (invocable Apex behind the MCP `cloneSalesTransaction` tool) [Repo: `unpackaged/post_mcp_custom/`] | Deployed by `deploy_post_mcp_custom`, part of the `prepare_mcp` flow; see `mcp-integration`. In Apex, `ConnectApi.CloneSalesTransactionConnect` is not visible unless `enableCoreCPQ` and `enableTransactionCloning` are on (`mcp-integration`), so the toggle is not UI-only for Apex callers: keep it on |

`/connect/pcm/deep-clone` is a different API: it clones a `Product2` and its related catalog
records, not a quote [Dev guide: `connect_resources_deep_clone`].

To clone a whole quote, pass the quote id as both `recordIds[0]` and `salesTransactionId`.
That is the form measured below; the dev guide's examples show a line id in `recordIds`.

## Response and completion

- The dev guide documents `{ requestId, salesTransactionId, success, errors }`, with
  `success` covering only the synchronous part and `requestId` for the async status
  [Dev guide: `connect_responses_clone_sales_transaction_output`].
- Measured on two whole-quote clones: the response also carried `trackerId` and
  `trackerUrl` (the `ramped-quotes` skill, written from the dev guide, says there is no
  `trackerId`); `requestId`, `trackerId` and `trackerUrl` were all null;
  `salesTransactionId` was the **new** quote's id. After the first clone, the new quote read
  `CalculationStatus = CompletedWithPricing` on the first query, about 5 seconds later
  [Measured: 2026-11-10, 264].
- `Quote.CalculationStatus` has `QueuedForClone`, `CloneInProgress` and `CloneFailed`
  values on 264 [Measured: 2026-11-10, 264, describe]. Before reading or changing a
  clone, poll until it is no longer in a clone or saving state. The `ramped-quotes`
  skill does the same for group clones.
- Limits: up to 6,000 records per transaction; for more than 1,000 lines, contact
  Salesforce to raise the limit. `ISCLONE()` is not supported for these clones, so
  formulas, validation rules and flows can't use it to detect a deep clone
  [Help: `ind.qocal_clone_quotes_and_orders`].

## What carries over

Documented [Help: `ind.qocal_clone_quotes_and_orders`]:

- Field values, related records from standard and custom objects, bundles, standalone
  and grouped lines, and the actions on lines.
- Group ramp schedules keep their structure, and amendment and renewal quotes keep their
  ramp and segment relationships. Amendment, renewal and cancellation quotes can be cloned.
- The clone is created in **Draft** status. Approval work items aren't copied.
- "To clone custom objects and custom fields, configure the context definition for the
  sales transaction"; custom child objects need `ParentReference` mapped to the parent
  record id. Measured below, custom header fields that no context plan mapped did not
  behave alike: `RLM_Payment_Terms__c` copied on the 2026-11-10 org, while on the 2026-11-12
  org a picklist came back as its default and a checkbox came back false.

Traced mechanism [Platform behaviour, traced]: all three routes (UI action, Connect API,
invocable) end in the same clone service. It does not copy the quote row. It builds a context
from the source through the context definition's quote mapping, sets `Status` to the first value
of the Status picklist (normally Draft) and appends ` Copy` to the name, translates the context
back to records through the same mapping (restricted fields removed), restores the related-quote,
related-quote-type and original-action-type fields from the source, and saves the result through
Place Sales Transaction. The mechanism therefore predicts that a quote or line
field carries over only if the active context definition maps it, and that an unmapped custom
header field comes back at its default (a picklist at its default value, a checkbox `false`)
whichever route you use. That matches the measured picklist and checkbox, but one
unmapped-looking field copied, unexplained by the repo's plans (see below), and the org's active definition was not
read, so treat this as the expected rule, not a guarantee
[Platform behaviour, traced in part]. To make a field carry, add it to the context definition
and its quote mapping, or set it on the new quote after the clone. Line-side
rewrites: the metering field is nulled, ramp and segment identifiers are regenerated (an
action line other than Add may keep the originals when a platform gate is open), the action
lookup is re-pointed to new actions, and foreign keys are re-pointed to the cloned records.
The clone code reviewed has no reference to an approval status or `IsSyncing` (a keyword
search of the clone module; the save through Place Sales Transaction was not traced)
[Platform behaviour, traced in part]. Not traced: the large (async)
transaction path, which may carry fields differently, and whether a mapped field that is
non-editable, formula or output-only is dropped.

Measured on one org, from a source quote with one group, two evergreen lines of one
product (line discounts 20% and 10%), one attribute row on the 20% line, synced to its
opportunity and with an approval submission in progress [Measured: 2026-11-10, 264]:

| Item | On the clone |
|---|---|
| `Name` | Source name plus ` Copy` |
| `Status` | `Draft`, for a source in `Draft` and for one in `Presented` |
| `OpportunityId` | Same opportunity |
| `IsSyncing` | `false`; the opportunity's `SyncedQuoteId` stayed on the source |
| Group | Recreated, same name; both lines in it |
| Lines | Same `Quantity`, `Discount`, `UnitPrice`, `ListPrice`, `NetUnitPrice`, `TotalPrice`, `StartDate`, `BillingFrequency` |
| Attributes | One row on **each** line: the source line without an attribute row got one, holding the product's default value |
| `RLM_Payment_Terms__c` (custom, editable by the user) | Copied |
| `RLM_Approval_Status__c` (custom, read-only to the user through `RLM_Approvals`) | Blank (source: `Pending`) |
| `RLM_Approval_Level__c` (roll-up of the line level) | Same value, from the cloned lines |
| `Description`, `ExpirationDate` | Blank (source: set) |
| `ApprovalSubmission`, `ApprovalWorkItem` | None |
| `RelatedQuoteId` | Blank |

Measured again on a second org, cloning whole quotes of a multi-line deal with the
Connect API [Measured: 2026-11-12, 264]:

| Item | On the clone |
|---|---|
| A custom header picklist that no context plan mapped | The picklist's **default**, not the source's value. A source already holding the default looked as if it copied |
| A custom header checkbox that no context plan mapped (the internal-round flag) | `false` (source: `true`) |
| Two custom header fields the rounds compared (mapped in the context plan), and `StartDate` | Same as the source; the two custom fields held their defaults on every source, so this run doesn't show whether they copy |
| `RLM_Payment_Terms__c` | Same as the source, but every source held `Net 30`, the picklist default, so this run doesn't show whether it copies |
| Line `Discount` and a custom line field mapped in the context definition | Copied on every line |

Not measured: price adjustments other than the line `Discount` field (the source had no
`QuoteLinePriceAdjustment` rows), bundles, ramp segments, header discounts, custom child
objects, orders. `RLM_Payment_Terms__c` copied on the 2026-11-10 org although no context plan
maps it in this repo (one field copied, unexplained by the repo's plans); the org's active
definition was not read, so a mapping there is the first thing to check. On the second org
every source held its default, so that run doesn't tell. A custom picklist and a custom checkbox did not copy, nor did two
editable standard fields; the traced rule above explains these when the definition does not map
them. The mapped fields on the 2026-11-12 org held their defaults, so that run doesn't test
mapping. After each clone, compare every header field a round depends on with the source and
write back the ones that differ ([SKILL.md](SKILL.md) → Validation Checks).

## Relating a clone to its source

- No documented field records "cloned from". `Quote.RelatedQuoteId` exists but is neither
  createable nor updateable, its type picklist `RelatedQuoteType` holds only
  `TransferQuote`, and a clone leaves it blank [Measured: 2026-11-10, 264, describe and run].
- What a clone does keep is the opportunity, so the opportunity is the natural parent of
  every round. Rename each clone to its round as soon as it settles.
