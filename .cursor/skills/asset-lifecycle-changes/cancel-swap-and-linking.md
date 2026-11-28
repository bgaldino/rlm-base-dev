# Asset Lifecycle Changes — Cancellation, evergreen credits, swaps, linking

> Sub-file of `.cursor/skills/asset-lifecycle-changes/SKILL.md`. Read it before promising a cancellation or swap
> number, or when a flow must link a renewal or amendment to an Opportunity, an open quote or a contract.

All [Measured: 2026-11-26, 264, fresh `ent-sb0` harness build] unless tagged otherwise. Dollar values are illustrative
(a 3,240 per year Term Defined product, quantity 2, term 2025-07-01 to 2028-06-30; an Evergreen product at 2,000
per month, swapped to one at 1,000 per month).

## Term Defined cancellation: the credit counts periods from the asset start

`initiateCancellation` on a Term Defined top-level asset, dated 2026-11-16, credited **-10,510.03**: periods
anchored on the **asset start**: 227/365 of the current period (2026-11-16 to 2027-06-30) plus the next whole year, not calendar years from 1 January (a
calendar-year count gave -10,518.95, which is wrong for a non-1-January start). The quote had one detail row at -2 x
3,240 for 2026-11-16 to 2028-06-30 and a null parent `UnitPrice`/`NetUnitPrice`; the billing schedule totalled
-10,510.03; the asset state period ended 2026-11-15. A +1 amendment on the same asset used the same anchor (5,255.01).
This settles the "Term Defined cancellation" item in [verification.md](verification.md) → Open.

## Evergreen: the quote credit is not the invoice credit

| Change (Evergreen, 2,000 per month) | Quote | Invoice |
|---|---|---|
| Reduce 3 to 2 | -2,000 (one period) | **-1,000.00**, the month prorated by day (11-16 to 11-30) |
| Swap to a 1,000 per month product (outgoing 2,000 per month) | -2,000 / +1,000 | nets **0.00**: the outgoing line is credited by day, the incoming line bills a full month in advance from the swap date |

A Term Defined add or cancel invoiced by day too (135.00 for 11-16 to 11-30 on the +1). So **state the quote credit
and the invoice credit separately** in any plan; billing detail: `rlm-business-apis` → `backdated-asset-lifecycle.md`.

## Swaps

- A swap acts as an add plus a negative amendment [Help: `ind.qocal_fdo_examples_of_amendment_types_and_results`]; values
  co-term by day (a separate asset from the cancel example: quantity 1, 3,240 per year Term Defined, swapped to a
  45 per year product dated 2026-12-01 with 360 of 365 days of its term year left, so its period ended 2027-11-25;
  priced -3,195.62 / +44.38, which is each price x 360/365).
- **A swap of a bundle component asset is refused:** "We couldn't process the swap request because the asset is a
  bundle child. Provide the bundle's parent-level asset." Swap the top-level asset.
- **Usage-based assets cannot be swapped** ("You can't swap usage-based assets."), so a rule that needs a usage product
  cannot be exercised through a swap.
- **Constraints on a bundle-less swap quote are silent.** A rule "product A requires product B" did not message: it
  added the required line (B at its price, `configure` success, no message, no error log). The added line was dated
  today, not the swap date, and carried no `QuoteAction`; ordered and activated it became a new asset from today. Read
  every line's date and action after a swap with rules on.

## Cancelling a bundle root

A future-dated root cancel (quote only) credited each Term Defined child by day (12,000 x 165/365 = -5,424.66), the
One-Time child in full (-62,500) and the root 0. Default children had one-year terms under a three-year root, so read
each child's term rather than the root's.

## Attribute reset on amendment: not reproduced

On a current build the amendment line **inherits** `RLM_ConstraintEngineNodeStatus__c` from the asset, so a rules-on
quantity edit kept the attribute (Gov). Blanking the field on a new amendment line and repeating the edit reset it to
the default (Flex). So the reset follows a **missing node status**, which the repo's rule and trigger prevent
([amendments-and-attributes.md](amendments-and-attributes.md), Quick Rule 2) [Open: the cause is inferred, not core-traced].
Also measured in the UI:
- **Restore:** on an amendment line reset to Flex, line editor, row action Configure: the configurator opens at Flex,
  the Summary marks "Type Gov to Flex" against the asset, and selecting Gov clears the marker; Save & Exit wrote Gov.
- **UI amend path:** Account, Managed Assets, Amend, Submit, inline quantity 0 to 1: the line kept Gov, with node
  status `User`. Headless restore: a Place PATCH of the `QuoteLineItemAttribute` with Force and rules on.
- **Test-data trap:** an asset created with "today" as the UTC date shows a Lifecycle Start the previous evening in a
  Pacific org, and Amend's default date is then refused ("Specify an amendment date on or after the Lifecycle Start
  Date"). Derive "today" in the org's time zone in headless scripts.

## Reprice after activation also zeroes a cancellation

Repricing an activated cancellation quote (pricing `Force`, configuration `Skip`) set the line and quote total to 0
(detail quantity 0); the amend-add and Evergreen-reduce quotes did not change; order and asset were unchanged.
Read quote values before activation for cancellations as well as renewals.

## Linking a renewal or amendment

[Measured: 2026-11-26, 264 (USA796), ent-sb0 harness build]
- **Opportunity:** Generate Renewal Quote run on a template forecast record links the quote to that Opportunity and
  creates no new one (a run without the id gave an unlinked quote). `initiateAmendment` with `amendOpportunityId`
  returns a linked, priced quote in the same call. Sync drops `OpportunityLineItem.AssetId` on renewal forecast records.
- **Add to an open quote:** `initiateAmendment` accepts `amendRecordId` as an **input** (the dev guide lists it as
  output only) and then adds the selected assets to that quote, so a flow can do it with no Apex. The server refuses duplicates.
- **Renewal stacking:** a second renewal of an asset that already has one was refused live with "already renewed", even
  though Help describes the future-dated case; the gate is a release control, so test it on the target org.
- **Renewal quantity:** editing a renewal line's quantity through Place (Skip, then Force) reprices at the prior net,
  with one positive detail row and no negative row. A flow that needs this pairs an apply-renewal-quantity invocable
  with an async after-commit flow on `CalculationStatus`.
- **Contract scope:** the contract viewer is scoped per contract; Amend from it sets `ContractId`; Add Assets is then
  contract-scoped. Asset-contract relationships are created automatically only for an order linked to an active
  contract with an `AppUsageAssignment`; order activation needs addresses and an active contract.
- **Partial transfer of a bundle** needs every component on Proportional quantity scale; Constant or null components are
  refused with "Transfer the entire quantity of the bundle".

## Desk-researched, not measured here

[Open: each needs a live check before it is stated as fact]
- A renewal line's quantity is editable in standard Revenue Cloud (blocked only in Communications promotions orgs
  unless an edit-on-amend setting is on); the renew API takes no quantity.
- An inactive price book entry blocks cancel, amend and renew line inserts; a qualification rule is the end-of-sale lever.
- Removing a one-time line on a renewal counts as a cancellation with full credit.
- Asset, state period and contract-relationship starts derive from the order item start; the relationship must start
  on or after the contract start.
- Managed Asset Viewer buttons launch one org-wide flow set in Revenue Settings, each following the user's matching
  permission; Upgrade and Downgrade are API-only on 264. A swap group uses `ReplacementGroupId`
  (AssetAction, AssetActionSource, OrderItem).
- Usage grants on amendment (null versus stamped value comparison), temporary now-plus-future price patterns, and
  promotion commitment periods: wave 2 (usage and billing lines), not covered here.
