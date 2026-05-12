---
article_id: ind.qocal_renewal_of_a_usage_based_product.htm
title: Proration for Usage Amendments and Cancellations
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_renewal_of_a_usage_based_product.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Proration for Usage Amendments and Cancellations

Understand how the system recalculates grants when you change quantities or cancel services early.

Grant Recalculation

When a line item quantity changes, the system automatically recalculates and prorates grants based on the asset's lifecycle. View the proration message and the net-applicable grants in the Manage Usage Resources window.

Early Cancellations

Cancel usage resources early to ensure that the system prorates grants based on the asset's actual lifecycle. The system counts consumption until the date of cancellation and reduces it by the number of prorated grants.

Calculation Logic

Consider an asset with an initial count of 10 units and 100 grants per unit. During a mid-month amendment, the quantity increases by 5 units, and the new grant is 200 per unit.

QUANTITY	RATE	CALCULATION


Current Month (Prorated)

10 existing units + 5 new units

	100 grants/unit (existing) + 200 grants/unit (new)	(10 x 100) + (5 x 200 / 2) = 1500 grants


Next Month (Full)

10 existing units + 5 new units

	100 grants/unit (existing) + 200 grants/unit (new)	(10 x 100) + (5 x 200) = 2000 grants (full)

For more information, refer to these resources.

Renew Assets with the Managed Asset Viewer
Cancel Assets with the Managed Asset Viewer
