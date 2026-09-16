---
article_id: ind.dro_ramp_deal_decomposition.htm
title: Decompose and Fulfill Ramp Deal Orders
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_ramp_deal_decomposition.htm&type=5&release=264
release: 264
release_name: Winter '27
area: dro
parent_article: ind.qocal_ramp_deals_complex_long_term_multiple_products.htm
fetched_at: 2026-09-05
---

# Decompose and Fulfill Ramp Deal Orders

Use Dynamic Revenue Orchestrator (DRO) to decompose, orchestrate, and assetize ramp deal orders across time segments. DRO sequences fulfillment steps, creates fulfillment assets, and processes amendments based on each segment's effective dates and values. A ramp deal contains standalone order line items divided into time segments whose price, quantity, discount, and other attributes can vary.

REQUIRED EDITIONS
Available in: Enterprise, Unlimited, and Developer Editions
Decompose Ramp Deal Orders

DRO decomposes each ramp segment into fulfillment order line items (FOLIs). The subscription, term, and quantity defined in a segment determine the FOLIs generated for that period. When time-awareness is on, DRO maps the FOLIs and Fulfillment Asset State Period records to each segment's effective dates. As a result, a change to one segment updates only that period.

For more information about time-aware behavior, see Order Fulfillment With Time-Awareness.

Orchestrate Ramp Deal Fulfillment

DRO sequences fulfillment steps chronologically across ramp segments according to the configured dependencies and scopes. For example, steps for the first year run before steps for the second year. DRO also resolves dependencies across time segments to prevent fulfillment plans from stalling and to support multiyear subscription provisioning. To sequence fulfillment across ramp segments, configure the fulfillment steps and dependencies with the scopes required by your fulfillment design. The configured scopes determine which fulfillment order line items a step processes and how dependencies connect steps within and across segments.

For more control over execution timing, see Configure Steps for Future Execution.

Assetize Ramp Deal Orders

Assetize Ramp Deal Orders DRO handles assetization for ramp deal orders based on whether time awareness is on.

When time awareness is on, DRO constructs a fulfillment asset timeline using each ramp segment's effective dates and values. It creates a Fulfillment Asset State Period (FASP) for every segment using its corresponding fulfillment order line item as the source. If an amendment alters the order timeline, DRO supersedes the affected FASPs and creates updated FASPs to reflect the new dates, quantities, and attributes.

When time awareness is off, DRO processes fulfillment order line items using standard, time-agnostic assetization rules without constructing a FASP timeline. Segment effective dates do not establish separate asset state periods.

By using a staged assetize step, DRO creates assets during fulfillment plan execution rather than waiting until the plan fully completes. This step keeps asset creation aligned with delivery and revenue-recognition schedules for multiyear deals. The staged assetize step supports ramped products sourced from order line items or fulfillment order line items. DRO uses the product's ramp segments as source line items to create assets and asset state periods during execution.

Staged assetization of ramp segments is supported only for time-aware fulfillment assets. Commercial assetization requires all segments of a multisegment ramp to be assetized together. For source behavior, limitations, and setup information, see Staged Assetize Step.

Amend Ramp Deal Assets

When you amend a ramped asset, DRO detects time-based changes, generates fulfillment order line items with the applicable actions, and updates the related fulfillment assets during technical assetization. You can make these changes to a ramped asset:

Add one or more segments during an amendment. A new segment can retain the quantity and attributes of the previous segment or use different values.
Cancel the last segment or multiple future segments. Cancellation sets the quantity of each canceled segment to 0. You can't cancel a segment that falls between two existing segments.

DRO fulfills these amendments whether or not time-awareness is on.

For information about how additions, cancellations, and other dated changes affect fulfillment assets, see Considerations for Backdated Changes in Dynamic Revenue Orchestrator.
