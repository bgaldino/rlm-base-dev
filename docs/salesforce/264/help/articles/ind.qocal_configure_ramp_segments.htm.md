---
article_id: ind.qocal_configure_ramp_segments.htm
title: Configure Ramp Segments in Ramp Deals for Lines
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_configure_ramp_segments.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.understanding_ramp_deals.htm
fetched_at: 2026-09-04
---

# Configure Ramp Segments in Ramp Deals for Lines

Divide transaction lines into ramp segments with varying prices and quantities over time.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) with the Revenue Cloud Growth license, the Revenue Cloud Advanced license, or the Revenue Cloud Billing license.
USER PERMISSIONS
NEEDED
To configure ramp segments in quotes:	Create on Quotes
To configure ramp segments in orders:	Create on Orders

Ensure Ramp Deals for Lines in Quotes and Orders is turned on and the product has a ramp segment configured.

From the App Launcher, find and select Quotes or Orders.
Open the quote or order that contains the rampable product as a line item.
Open the tab with the Transaction Line Editor component.
From the quick action menu on the rampable quote line item, select Ramp.
The Ramp Deal window opens.
Enter a subscription term in months for the ramped line item.
Select a segment type-Annual or Custom.
Enter a trial term in days if you enabled a trial segment for the product.
Click to generate your segments.
Edit the discount and quantity details for each segment as required.
Click Update Segments to recalculate prices.
Save your changes.

View pricing in the Line Item Details tab or hover over Total Price in Transaction Line Editor.

Create a Product Ramp Segment
A ramp deal is a type of sales agreement where price and volume vary across time periods. A ramp segment is a specific period within a ramp deal during which certain prices and volume are in effect.
