---
article_id: ind.qocal_considerations_ramp_deals.htm
title: Considerations for Ramp Deals for Lines In Quotes and Orders
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_considerations_ramp_deals.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Considerations for Ramp Deals for Lines In Quotes and Orders

Correct configuration of ramp deals is crucial to make sure they function as intended in Transaction Management. Review the considerations before you create or update ramp deals.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
Transaction Management supports ramp deals for term-defined products.
You can’t create a ramp deal for a bundle product.
You can't renew a ramp deal before it's end date.
You can’t create a price-only amendment for a ramp deal.
You can configure up to 10 ramp segments for a transaction line such as a quote line item or an order product.
If a transaction’s subscription term doesn’t equal a full-year term, the Ramp Deals feature rounds it off when it determines the number of segments to be created. For example, the last three months of a 15-month subscription term without a free trial are housed in the second segment, with two total ramp segments created. Then the price is prorated to match the 3-month term.
The transaction line that you want to ramp must have start and end dates.
The start date and end date fields of segments can’t have any gaps or overlaps.
In an initial sale, you can edit the start date of the first annual ramp segment of the deal.
After you configure and save ramp segments on a transaction line, you can’t change the start and end dates of the transaction line. Similarly, you can’t change the dates in an amendment.
When you create an amendment transaction, you can’t add or delete ramp deals.
In an amendment transaction, the Ramp Deal window shows the changes in the total price of the transaction.
The generated quote PDFs that include ramp deals don’t show any difference between the ramped transaction lines and other transaction lines.
