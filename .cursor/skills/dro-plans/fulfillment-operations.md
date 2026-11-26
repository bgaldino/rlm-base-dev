# DRO Plans - Operating Fulfillment: Monitoring, Tasks, Expiry and Limits

Day-2 facts for people who run orders through Dynamic Revenue Orchestrator after the plan is
built: what each screen shows, how manual tasks are made, what happens when an asset expires,
and what the platform does not do. Read it before promising a customer a view, an event or a
retry. Setup and data loading are in [authoring-and-deployment.md](authoring-and-deployment.md)
and [csv-and-sfdmu.md](csv-and-sfdmu.md); in-flight changes are in
[updates-and-runtime.md](updates-and-runtime.md). Facts below carry their source; nothing here
was run on a DRO-loaded org unless a tag says so, so anything tagged Open needs a live check first.

## Decomposition rules: what can be a source

A rule takes a commercial product or a product classification and breaks it into technical
products [Help: ind.dro_define_how_a_product_decomposes]. Rules whose source is itself a technical
product (multi-level, technical to technical) are not documented for DRO in 264; the Help
describes only commercial or classification sources [Help: ind.dro_define_how_a_product_decomposes].
Design consequences:
- Flatten: each commercial product (or classification) lists every leaf technical product.
- Key rules on a **classification** so one rule set serves every commercial product in it; a change
  to a shared sub-assembly then still means editing each classification rule set that includes it
  [Open: reuse benefit inferred from the Help, not built].
- A technical bundle groups the resulting fulfillment line items under a root; it does not add
  rules, and each child still needs its own qualifying rule from the commercial side
  [Help: ind.dro_technical_bundles].
- A request that cites an old item about "multilevel" decomposition may refer to Industries Order
  Management (fulfillment request lines), a different product from RCA DRO; check the product
  before treating it as DRO delivery.

## What each monitoring surface shows

| Need | Surface | Limit |
|---|---|---|
| Lines and their rule | Decomposition viewer on the order (Fulfillment Lines tab) | Fixed columns: Product, Fulfillment Order, Action, plus a Subaction column when a line has one; no design properties to add columns [Help: ind.dro_monitor_decomposition_during_fulfillment]. A line's attribute names and values open per selected product, not for the whole order [Help: ind.dro_monitor_decomposition_during_fulfillment] |
| Steps of a plan | View Orchestration Plan from the viewer; Fulfillment Steps list views | Step fields (state, type, name, planned and requested completion, assignee) live on FulfillmentStep, not in the line grid [Open: object fields not re-checked against a describe] |
| Manual-task activity for the whole order | Setting "Link Task to Source Step" (Setup, Dynamic Revenue Orchestrator Settings) | Shows upcoming and overdue manual-task activities at order level [Help: ind.dro_turn_on_feature_to_link_task_to_step_source] |
| Analytics | Order Analysis and Order Details dashboards | Need analytics enabled [Help: ind.dro_configure_dynamic_revenue_orchestrator_analytics_dashboards] |

For one table of every line's attributes, or of steps per line, a custom report type over
`FulfillmentLineAttribute` (with the fulfillment line) or `FulfillmentStep` with
`FulfillmentStepSource` is the configuration route; whether the attribute label or the polymorphic
source line is reportable is [Open: report-type reachability not built]. `FulfillmentLineAttribute`
stores the attribute code in `AttributeName` [Open: object fields not re-checked against a describe], so a report shows
codes unless it reaches the attribute definition.

## Manual-step tasks

Assignment rules route manual tasks to a user or queue by priority and condition
[Help: ind.dro_create_a_fulfillment_task_assignment_rule]. The Link Task to Source Step setting ties
a Task to the step's source record [Help: ind.dro_turn_on_feature_to_link_task_to_step_source].
What the Task's subject, WhatId and ActivityDate hold by default is [Open: read from core code
during desk research, not measured on an org; build a manual-step plan and read the Task before
promising a title format]. If the subject must show the product, a record-triggered Flow on Task
insert is the candidate route; whether the step's source rows are visible to it at insert is
[Open: not measured].

## Auto Task errors and retry

DRO retries errors that a flow returns through the Auto Task Fault Path, and does not retry raw or
unhandled Apex exceptions; to make an Apex failure retryable, handle it in the flow's Fault Path and
return the required Auto Task output variables [Help: ind.dro_fallout_design_and_management].
An unmatched error code ends FATALLY_FAILED without retry; fallout rules need a decision table
refresh [Help: ind.dro_fallout_design_and_management].

## Expiry and non-renewal

The Help documents no event or plan that runs when an asset's end date passes; DRO acts on orders
[Open: absence in the Help snapshot, not measured on an org].
What does happen: DRO reconciles fulfillment assets every 24 hours, adjusting quantity and validity
from the related assets' state periods, and marks a fulfillment asset inactive only after all its links to related
assets are inactive [Help: ind.dro_assetization_in_dynamic_revenue_orchestrator].
Patterns for a deprovision signal, in order of preference:
1. A record-triggered Flow on `FulfillmentAsset` (Status changed to Inactive) that publishes an
   event, calls out or creates a task; latency is up to about a day
   [Open: whether a flow fires on the reconciliation job's update is not established; test with a
   backdated end date and a manual Status update as the positive control].
2. A scheduled flow on the commercial asset's end date (the shape of the renewal flow templates),
   checking that no renewal or later state period exists; a renewal that moves the end date must
   cancel or reschedule the pending path [Open: not built].
3. Avoid forcing a cancel plan with a cancellation dated near the end date: how the platform treats
   a cancel dated at or after the end date, and its effect on the asset's end state, is
   [Open: not measured; see asset-lifecycle-changes].
A DRO Custom Date step at the line end date keeps every plan open for the whole term and is
rejected [Open: reasoning only].

## Not in 264

- Submitting only the ready root offerings of an order (partial order submission) is a 266 feature;
  there is no 264 page [Open: confirm the preference name and behavior on a 266 org after it is
  available].
