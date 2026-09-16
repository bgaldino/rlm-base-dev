---
article_id: ind.qocal_field_and_pricing_amendments.htm
title: Manage Assets with Field and Price Amendments
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_field_and_pricing_amendments.htm&type=5&release=264
release: 264
release_name: Winter '27
area: transaction_mgmt
parent_article: ind.qocal_advanced_amendment_and_renewal_features.htm
fetched_at: 2026-09-04
---

# Manage Assets with Field and Price Amendments

Update asset details and adjust pricing without changing quantities, attributes, or bundle configurations by using Field Amendments and Price Amendments. Use Field Amendments to modify standard and custom fields, such as billing frequency. Use Price Amendments to update the Sales Price on quote lines or the Unit Price on order lines.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Management (formerly Revenue Cloud) where Transaction Management is enabled
USER PERMISSIONS NEEDED
To apply field and pricing amendments:	

InitiateAmendment API permission set

AND

Sales Rep persona permissions

Apply a Field Amendment

Field Amendments trigger a formal amendment when you modify a designated field on a quote line item (QLI), changing the quote status from No Change to Amend. Upon activation, the system assetizes the change and adds a Field Amendment asset action subtype to provide a clear audit trail. You can update standard QLI fields and custom fields mapped to the asset state period (ASP).

When you initiate an amendment and change only a price-impacting field, the system performs a cancel and reprice action for the remainder of the term. Assetization creates a cancel line for the remaining term based on the previous value and a reprice line for the new value.

From App Launcher, find and select Accounts.
Select an asset from the Assets tab, and click Amend.
Update a field value in the Transaction Line Table or on the QLI record, such as changing billing frequency from Quarterly to Monthly.
Confirm that the quote action changes to Amend and the subtype updates to Field Amendment.
Complete the Quote-to-Order and order activation processes to create an order with the Amend action.
Assetize the order by using a flow to record the Field Amendment subtype and update the ASP with the new field value.
See Automate Asset Creation from Orders.
EXAMPLE Net Unit Price Increase

A user sells 100 units of an asset at a net unit price of 100. In the middle of the subscription term, the user changes a price-impacting custom field. This change triggers a field amendment effective from the date of the field change.

Assetization creates a cancel line for the remaining term based on the previous custom field value and a reprice line for the remaining term.

Apply a Price Amendment

Price Amendments help you adjust pricing without changing the quantity, attributes, or bundle configuration of an existing asset. You can update the Sales Price on a quote line or the Unit Price on an order line, or apply a discount amount or discount percent. Updated prices are reflected throughout the standard order and billing processes.

NOTE Before you can set a new price by using a Price Amendment, turn on Sales Price Amendments in Revenue Settings. See Set Up Price Amendments.
Select an asset from the Assets tab of the Account page, and click Amend.
Select an effective date for the price change.
To set a new price, enter the new Sales Price or Unit Price. To apply a discount instead, enter a discount percentage or discount amount.
Save your changes.
An amendment quote is created with a delta quantity of zero, and the quote action is updated to Amend.
The total price reflects a prorated credit for the old price and a new charge for the updated price starting from the effective date.
Assetize the order by using a flow.
The creation of an offsetting asset action source (AAS) record cancels the original price and applies the new price
The asset action updates to Upsell for higher total prices or Downsell for lower total prices.
The ASP updates to reflect the new monthly recurring revenue starting from the amendment effective date.
EXAMPLE Decrease the Sales Price

A customer owns 50 CloudSQL seats at a sales price of $50 per user per month for a 3-month subscription. During the term, the sales rep agrees to lower the price to $45 per user per month.

The rep starts a price amendment, sets the effective date, changes the sales price to $45, and leaves the quantity unchanged. The amendment reprices the 50 seats at $45 per user per month for the remainder of the term. The quote line item detail records show a credit for the previous price and a charge for the new price, and the totals roll up to the quote line item and subtotal levels.
