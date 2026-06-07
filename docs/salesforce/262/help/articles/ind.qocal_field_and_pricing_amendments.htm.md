---
article_id: ind.qocal_field_and_pricing_amendments.htm
title: Manage Assets with Field and Price Amendments
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_field_and_pricing_amendments.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Manage Assets with Field and Price Amendments

Update asset details and adjust pricing without changing quantities, attributes, or bundle configurations by using Field Amendments and Price Only Amendments. Use these features to modify standard and custom fields, such as billing frequency, while ensuring changes remain officially recorded, approved, and auditable.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To apply field and pricing amendments:	

InitiateAmendment API permission set

AND

Sales Rep persona permissions

Field Amendments trigger a formal amendment when you modify a designated field on a quote line item (QLI), changing the quote status from No Change to Amend. Upon activation, the system assetizes the change and adds a Field Amendment asset action subtype to provide a clear audit trail. You can update standard QLI fields and custom fields mapped to the asset state period (ASP).

When you initiate an amendment and change only a price-impacting field, the system performs a cancel and reprice action for the remainder of the term. Assetization creates a cancel line for the remaining term based on the previous value and a reprice line for the new value.

To initiate a field amendment, from App Launcher, find and select the Accounts.
Select an asset from the Assets tab, and click Amend.
Update a field value in the Transaction Line Table or on the QLI record, such as changing billing frequency from Quarterly to Monthly.
Confirm the quote action changes to Amend and the subtype updates to Field Amendment.
Complete the Quote-to-Order and order activation processes to create an order with the Amend action.
Assetize the order by using a flow to record the Field Amendment subtype and update the ASP with the new field value.
See Automate Asset Creation from Orders.
To initiate a price only amendment, select an asset on the Assets tab of the Account page and click Amend.
Select an effective date for the price change.
Apply a discount percentage or discount amount and save your changes.
The system generates an amendment quote with a delta quantity of zero and updates the quote action to Amend.
The total price reflects a prorated credit for the old price and a new charge for the updated price starting from the effective date.
Assetize the order using a flow.
The system generates an offsetting asset action source record to cancel the original price and apply the new price.
The asset action updates to Upsell for higher total prices or Downsell for lower total prices.
The ASPs update to show the new monthly recurring revenue from the amendment effective date.
EXAMPLE Net Unit Price Increase

Let's assume a user sells 100 units of an asset at a net unit price of 100. In the middle of the subscription term, the user changes a price-impacting custom field. This change triggers a field amendment effective from the date of the field change.

Assetization creates a cancel line for the remaining term based on the previous custom field value and a reprice line for the remaining term.
