---
article_id: ind.qocal_configure_ramp_segments.htm
title: Configure Ramp Segments in Ramp Deals for Lines
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_configure_ramp_segments.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Configure Ramp Segments in Ramp Deals for Lines

Divide a transaction line such as a quote line item or an order product into multiple ramp segments, each with its own unique price and quantity over different time periods.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS
NEEDED
To configure ramp segments in quotes:	Create on Quotes
To configure ramp segments in orders:	Create on Orders

Before you begin, make sure that you have enabled Ramp Deals for Lines in Quotes and Orders and configured a product ramp segment. See Create a Product Ramp Segment.

From the App Launcher, find and select Quotes.
You can also configure ramp deals for an order.
From the Quotes list view, select the quote that contains the rampable product as a quote line item.
Open the tab with the Transaction Line Editor component.
From the quick action menu on the rampable quote line item, select Ramp.
The ramp deal window opens where you can configure your ramp segment details.
Enter the details for your segments.
Enter a subscription term in months for the ramped quote line item.
Select the segment type.
The segment type can be Annual or Custom.
If a trial segment is enabled for your product, enter a trial term in days.
Generate your segments.
Edit the discount and quantity details of the segments as required.
To recalculate prices for your segments, click Update Segments.
Save your changes.

To view your updated pricing details, check the Line Item Details tab or hover over the transaction line’s Total Price field on the Transaction Line Editor component.
