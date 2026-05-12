---
article_id: ind.qocal_header_adjustments_use.htm
title: Apply Header Adjustments to Quotes and Orders
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_header_adjustments_use.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Apply Header Adjustments to Quotes and Orders

Provide amount and percent discounts or override the total amount for an entire quote or order. Transaction Management automatically distributes these discounts equally or proportionally among line items based on your selected distribution method. The price waterfall shows the specific discount applied to each line item to ensure pricing transparency.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To use header discounts:	Salesforce Pricing Run Time User permission set
NOTE Complete the setup for header adjustments, to apply header adjustments to your transactions. See Set Up Header Adjustments.

Modify the total price of a transaction by selecting an adjustment type and distribution logic within the Manage Header Adjustment interface.

Open a quote or an order.
Click Manage Header Adjustment.
Select an adjustment type.
Amount: Distributes a specific currency amount among all lines based on the selected distribution logic.
Percentage: Applies a specified discount percentage to every line item.
Amount Override: Calculates the difference between your specified value and the current total price, then distributes that difference among all lines.
Enter an adjustment value.
Select adjustment distribution logic.
Equal: Distributes the discount value equally among all line items.
Proportionate: Distributes the discount proportionally based on the List Price Total (List Price * Quantity) of each line.
Click Reprice All if the Delta Pricing for Quotes and Orders setting is turned on.
The system applies adjustments correctly and shows accurate prices for all lines.
SEE ALSO
Discount Distribution Service
Set Up Delta Pricing for Quotes and Orders
