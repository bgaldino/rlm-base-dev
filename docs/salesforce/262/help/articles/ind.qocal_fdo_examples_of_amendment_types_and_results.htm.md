---
article_id: ind.qocal_fdo_examples_of_amendment_types_and_results.htm
title: Future-Dated Amendment Types and Results
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_fdo_examples_of_amendment_types_and_results.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Future-Dated Amendment Types and Results

Familiarize yourself with the various types of future-dated amendments and their impact on your asset records. Understanding these behaviors ensures that you accurately manage upsells, reductions, and attribute changes within your asset lifecycle.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
Positive Amendments: Upsell or Add Quantity

Increase the quantity of an asset by setting a positive change on the quote line item (QLI) or order item (OI).

The QLI or OI represents the quantity increase for the entire lifecycle of the amendment.
The process applies the delta quantity increase to all asset state periods (ASPs) that exist beyond the new amendment start date.
Termed assets don’t generate detail lines for positive increases.
Example: You add 10 licenses on May 1, even though you scheduled 5 more licenses for June 1.
Negative Amendments: Reduction or Downgrade

Reduce asset quantity by setting a negative change on the QLI or OI.

Quantity reductions follow a Last In, First Out (LIFO) strategy across the quantity of each asset action source (AAS) within affected ASPs.
A negative amendment creates a detail line for each future-dated ASP with dates corresponding to the generated ASPs.
If an ASP lacks sufficient quantity for the reduction, the system returns an over-reduction validation error.
Repricing and cancellations apply to all pricing reduction scenarios.
Termed Asset Reductions

For termed assets where the product selling model (PSM) is term defined, the reduction quantity applies LIFO per ASP.

Example: An asset has ASP I (Jan 1 to June 30, qty 10) and ASP II (July 1 to Dec 31, qty 15).
If you reduce the quantity by 7 starting Feb 1, the process creates three detailed lines:
One detailed line for ASP I: Feb 1 to June 30, quantity (-7).
Two detail lines for ASP II (by using LIFO): quantity (-5) and quantity (-2), both covering July 1 to Dec 31.
Non-Termed Asset Reductions

For non-termed assets where the PSM is one-time, evergreen, or empty, the reduction quantity follows LIFO order based on the current quantity.

Example: An asset starts Jan 1 with ASP I (qty 10), ASP II (qty 15 starting July 1), and ASP III (qty 20 starting Sept 1).
A reduction of 7 starting Feb 1 creates one detail line because the quantity at that lifecycle point is 10.
A reduction of 7 starting Aug 1 creates two detail lines of -5 and -2. This occurs because the initial quantity of 15 consists of 10 units from the previous Asset State Period and 5 units from an amended transaction.
Attribute or Field Amendments Requiring Repricing

Change attributes, such as upgrading from a basic to an enterprise edition, or modify fields that trigger repricing events.

You set the new attribute value on the order item and select a start date.
This amendment functions as a cancel and reprice operation.
The process creates multiple pairs of cancel and reprice detail lines for each impacted future ASP.
ASP updates apply from the new amendment start date onward.
If attributes differ among intersecting and future ASPs, the attribute value on the amendment line item overrides all future ASP attribute values.
Quantity changes for assets with future ASPs containing different attributes process as an attribute change, resulting in cancellation and repricing.
Early Renewal

Initiating a renewal transaction before the scheduled renewal date overrides all future ASPs, amendments, and renewals.

If you enable As-Is Renewals, the asset renews based on the latest Asset State Period (ASP) quantity. This process uses different prices and quantities than the original purchase price.
Cancellation

Canceling an asset before a future-dated ASP is a specialized reduction type.

Assetization of the cancellation order impacts all future-dated ASPs.
The cancellation places the asset in a terminal state; you can’t perform further ARC operations on a canceled asset.
Transfers and Swaps
Transfers
An asset transfer between accounts acts as an amendment and copies the ASP from the source account to the destination account. It creates a negative amendment (TransferFrom) for the source and adds the asset to the destination (TransferTo). You only transfer the minimum quantity available across all current and future ASPs.
Swaps
A product swap acts as both an add amendment and a negative amendment. Swapped products inherit the ASP and relevant actions, with the quantity reduction applying to all future-dated ASPs starting on the swap date.
