---
article_id: ind.qocal_ramp_deal_compound_uplift_sales_reps.htm
title: Create Ramp Deals with Standard or Compound Price Uplifts
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_ramp_deal_compound_uplift_sales_reps.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_ramp_deals_for_groups_considerations.htm
fetched_at: 2026-09-04
---

# Create Ramp Deals with Standard or Compound Price Uplifts

Ramp deals break a multi-year contract into segments so that price, quantity, and terms can change over the life of the deal. Standard uplifts apply to the original list price, which works well for predictable contracts. However, many enterprise customers negotiate agreements where the annual increase applies to the prior year's net price rather than the list price. Compound uplifts reflect the growing value of a subscription over time and are common in multi-year contracts.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license, the Revenue Cloud Advanced license, or the Revenue Cloud Billing license.
USER PERMISSIONS NEEDED
For sales reps to use Ramp Uplift Type:	

Price and Tax Calculation for Quoting and Manage Revenue Lifecycle Management permissions

AND

Create Orders from Quotes permission set

Without compound uplift, sales reps calculate compounded prices in spreadsheets. Deal desk analysts can't easily audit the math, and a risk for finance teams is that they forecast the deal at the wrong contract value. With compound uplift, Salesforce automates the calculation, sets the applied unit price uplift for each segment, and preserves the uplift type in amendments and renewals. As a result, Sales reps present what they conclude is a fair, predictable price to the customer. Deal desk analysts can approve deals faster because the price waterfall shows exactly how the compounded price calculates. Sales operations managers can forecast revenue with confidence.

The ramp uplift type is set at the ramp schedule group level. When a sales rep changes the type on a ramp schedule group, the new type propagates to every group segment and ramped line item, repricing the transaction.

To select standard or compound uplift for a ramp deal, sales reps complete these steps.

Open the quote or order in Sales Transaction Line Editor (STLE).
Add a ramp schedule group and its segments, or open an existing ramp schedule group.
The new ramp schedule group inherits the default ramp uplift type from Revenue Settings.
Click the ramp schedule group name to open the side panel.
Set Ramp Uplift Type to Standard or Compound.
Set this value on the parent ramp schedule group only. For individual segments and line items, the ramp uplift type is read-only. If Multiple Ramp Schedules Per Transaction is off, set the type on the single ramp schedule segment. In both cases, Transaction Management cascades the change to every ramped line in the schedule.
Enter the Unite Price Uplift % for each segment.
The first segment always acts as the baseline. Segments with a zero percent uplift or with no uplift entered react the same way. The prior segment's cumulative multiplier carries over and no new uplift applies.
Save your changes.
Transaction Management applies the ramp uplift type on every ramped segment and line item, and Native Global Pricing (NGP) reprices the transaction. For a compound ramp schedule, NGP reprices every line in the group because each segment's price depends on the segment before it. For a standard schedule, only the segments that you change reprice. NGP populates the applied unit price uplift on each line item with the effective percentage used to calculate the net price. Confirm the values in the price waterfall.
EXAMPLE

Compare Standard and Compound Uplifts.

Consider a 3-year ramp deal with a $50.00 list price and a 10% annual uplift. These tables show how the two modes produce different prices.

Standard Uplift

SEGMENT	LIST PRICE	SEGMENT UPLIFT %	NET UNIT PRICE
Year 1	$50.00	0%	$50.00
Year 2	$50.00	10%	$55.00
Year 3	$50.00	10%	$55.00

Compound Uplift

SEGMENT	LIST PRICE	SEGMENT UPLIFT %	CUMULATIVE MULTIPLIER CALCULATION	APPLIED UNIT UPLIFT %	NET UNIT PRICE
Year 1	$50.00	0%	Baseline (1.0000)	0%	$50.00
Year 2	$50.00	10%	1.0000 × 1.10 = 1.1000	10%	$55.00
Year 3	$50.00	10%	1.1000 × 1.10 = 1.2100	21%	$60.50

In standard mode, Year 3 yields $55.00. In compound mode, Year 3 yields $60.50. The 21% applied unit price uplift in Year 3 reflects the geometric effect of two compounded 10% uplifts: (1.10 × 1.10) − 1 = 21%.

A segment with a zero percent compound uplift is a carryover. The prior cumulative multiplier remains rather than resetting, so the segment maintains the compounded gain from earlier segments.
