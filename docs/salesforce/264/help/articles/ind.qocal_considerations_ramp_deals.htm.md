---
article_id: ind.qocal_considerations_ramp_deals.htm
title: Considerations for Ramp Deals
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_considerations_ramp_deals.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_ramp_deals_complex_long_term_multiple_products.htm
fetched_at: 2026-09-04
---

# Considerations for Ramp Deals

Review these known considerations and limitations for the Ramp Deals feature.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license, the Revenue Cloud Advanced license, or the Revenue Cloud Billing license.
Ramp Deals for Lines
Transaction Management supports ramp deals for term-defined products. You can't use bundle products.
You can't renew a ramp deal before its end date.
You can't create a price-only amendment for a ramp deal.
You can configure up to 10 ramp segments per transaction line.
Uneven subscription terms round to full years, and the remaining months go in the last segment with prorated pricing.
Transaction lines require start and end dates.
Segment start and end dates can't have gaps or overlaps.
In an initial sale, you can edit the start date of the first annual ramp segment.
After you configure and save ramp segments on a transaction line, you can't change the start and end dates of the transaction line.
When you create an amendment transaction, you can't add or delete ramp deals.
In an amendment transaction, the Ramp Deal window shows the changes in the total price of the transaction.
Generated quote PDFs that include ramp deals don't show any difference between the ramped transaction lines and other transaction lines.
Ramped line items support the GMT time zone only. Non-GMT time zones aren't supported.
Ramp Deals for Groups

Transaction Management doesn't create ramps for all products in group ramp segments. A group ramp segment contains ramped lines and non-ramped Lines. When assetized, ramped lines become a single consolidated ramped asset, with associated asset state periods representing individual segments. Non-ramped lines become standard non-ramped assets.

Separate assets are created for each line for these products.
Supported Ramp Deal Products
PRODUCT TYPE	SUPPORTED
Term-defined standard	
Term-defined standard usage	
Standalone one-time	
Standalone evergreen	
Bundle with a parent and all children termed defined	
Bundle with a parent term-defined, but any child is one-time or evergreen, and Quantity Scale Method (QSM) = Proportional	
Bundle with a parent term-defined, but any child is one-time or evergreen, QSM = None or Constant, and Allow Quantity Edit = True	
Bundle with a parent term-defined, any child is one-time or evergreen, QSM = None or Constant, and Allow Quantity Editing = False	
Bundle with a one-time evergreen parent, and a term-defined child	
Nested bundle with a term-defined parent, and other parents are term-defined	
If you add derived pricing products to a ramp deal for groups, their prices don't calculate correctly.
With only Ramp Deals for Groups enabled (Multiple Ramp Schedules off), create only 1 ramp schedule per transaction. The ramp schedule is implicit—the entire transaction is part of a single ramp schedule.
When Multiple Ramp Schedules Per Transaction is on, you can create up to 10 ramp schedule groups in a quote or order.
You can create up to 12 group ramp segments in a ramp schedule.
After converting a group into a ramp segment within a schedule, you can clone the ramp segment to add more segments. You can't convert any other group within the schedule into a ramp segment.
When you turn on Multiple Ramp Schedules Per Transaction, you can't add non-ramped groups within ramp schedule groups.
You can't create a group ramp schedule for groups that contain child groups.
You can't create nested groups in group ramp segments.
You can't apply renewal price uplifts tied to the Consumer Price Index (CPI) to ramped products.
You can't create ramp deals for groups and ramp deals for lines in the same quote or order.
Product Configuration in Ramp Deals
For line-level ramps, configuration stays consistent across all ramp segments.
For group-level ramps, most configuration changes that you make in a ramp segment apply to the current and subsequent segments. Previous segments remain unchanged to preserve data integrity.
Root or component quantity updates apply only to the current segment and don't propagate to other segments.
When you include or exclude a child product within a bundle in one segment, that change propagates to all subsequent segments. If you remove a child product from a segment that remains in previous segments, you can't add it back again in subsequent segments. This restriction prevents gaps in the ramp schedule.
Attribute changes made to a child product propagate only to the subsequent segments that include that child product.
Configuration rules override your manual ramp segment configurations and evaluate for each segment.
Configuration rules don't recognize quote or order groups. Rules that add standalone products to a ramp segment don't automatically ramp them or add them to subsequent segments. However, this behavior doesn't affect child products of a ramped parent product. When a rule adds a child product to a previously ramped parent, it also ramps the child product and adds it to subsequent segments.
When initiating Browse Catalog from a ramp segment, configuration for non-rampable products isn't available.
Amend, Renew, and Cancel Ramped Assets
With Ramp Deals for Groups enabled, amending, or canceling ramped assets automatically creates groups.
With Single Ramp Schedule (Groups ON, Multiple OFF), you can amend multiple ramped assets in a single transaction only if the start and end dates of all their asset state period (ASP) records match. Don't add or delete ramp segments during amendments.
With Multiple Ramp Schedules (Groups ON, Multiple ON, you can amend multiple ramped and non-ramped assets in one transaction, even if their ASP start and end dates don't match. Transaction Management groups assets into a ramp schedule when the asset lifecycle and all ASP dates match. Don't add or delete segments for existing assets. However, you can create group ramp schedules on amendment, renewal, and cancellation quotes or orders to generate other ramp deals.
You can't change the start and end dates of auto-generated segments. To make structural changes, create a separate amendment.
During the renewal of a ramped asset, the price uplift from the final segment becomes the renewal uplift.
You can't use these capabilities when amending, renewing, or canceling ramped assets: lot-based renewal, asset transfer, early renewal (except via the dedicated early renewal flow), and rolling back the most recent amendment.
Editing the start date of the first segment of an amendment quote or order in the Edit Ramp Schedule page requires the date to be within the original segment's date window. You can't have any future dated amendments, renewals, or cancellations scheduled.
Ramp Segments
START DATE	END DATE
1/1/2026 (initial sale)	12/31/2026
1/1/2027	12/31/2027
1/1/2028	12/31/2028

If you amend the deal on 6/1/2026, you can only edit the amendment start date to be between 1/1/2026 and 12/31/2026.

You can only delete newly cloned segments in an amendment quote or order.
You can only clone the last segment. If you prorate the last segment, then the second to last segment is the segment you can clone. Segment cloning differs from segment extension because an extension is always applied to the last segment, regardless of segment type.
You can clone or change the end date of the last segment, but you can't do both in a single amendment transaction per ramp schedule. For example, you can't use the Clone segment action if you extended the end date on the auto-generated ramp schedule in the current transaction, and vice versa.
You can't change start or end dates during amendments on ramp schedules containing usage-based assets. You can only clone those segments.
If there's only one auto-generated segment in the amendment quote or order, you can't clone that segment.
Compound Uplift in Ramp Deals
Compound uplift is available only when you turn on Advanced Detail Line Pricing in Revenue Settings. Without this preference turned on, you only see standard uplift. Make sure to sync your context definition.
Ramp uplift type applies to the ramp schedule group level and propagates to all lines in that group. For initial sales, you can't set the ramp mode per line.
Ramp uplift type is read-only on individual quote line items and order products. You can update the ramp uplift type on quote line group and order item group. The value on the parent group applies, and group-level changes cascade to every ramped line.
New ramped lines added to the transaction inherit the ramp uplift type from its group. After a quote line is assetized, the mode recorded in the asset state period can't change. Amendments and renewals inherit the original mode for asset-sourced lines. Uplift percentages update, but you can't change the mode to standard or compound.
All ramped line items in a single initial sale transaction have the same ramp uplift type for initial sales. Amendment and renewal quotes can contain a mix of standard and compound asset-sourced lines. Each line keeps the type from its own asset state period.
The first segment of any ramp deal has no preceding segment to compound from. That segment is always priced at the baseline with an applied uplift equal to the unit price uplift on the line item.
On renewal, the compound uplift resets. Year 1 of the new term becomes the new baseline.
For amendments, the previous segment uplift is used to calculate the applied uplift percentage. The previous segment uplift is the preceding asset state period in chronological order.
Existing ramped records created before Winter ’27 use standard uplifts. Compound mode applies only when set on new transactions.
You can't use compound uplift with Consumer Price Index (CPI) uplifts, usage-based products, or derived pricing products.
The default pricing procedure templates in Revenue Management don't automatically update for compound uplift. Update your pricing procedure's price revision element to support compound uplift. See Salesforce Help for configuration guidance.
The price revision element is used to apply compound ramp uplift to ramped lines. Refer to the Apply Uplifts to Ramped Subscription Items section in the Revenue Management Default Pricing Procedure Template. Review Build Your Expression Set From a Template.
Turning off Advanced Detail Line Pricing after quotes, orders, or assets exist with compound ramp uplift causes pricing calculations, amendments, and renewals to return incorrect prices.
Dynamic Revenue Orchestrator (DRO) and Ramp Deals
Turn on the rampDealForQocal setting in your org and make sure that your order line items include ramp and segment identifiers.
For amend, renew, and cancel orders. DRO applies the same order action to all segments, even if a specific segment hasn't changed. DRO applies order line item actions to fulfillment order lines and processes them.
DRO skips Staged Assetize steps in ramp order fulfillment plans and assetizes all segments at plan completion.
