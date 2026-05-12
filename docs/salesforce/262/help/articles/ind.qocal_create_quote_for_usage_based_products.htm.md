---
article_id: ind.qocal_create_quote_for_usage_based_products.htm
title: Build a Quote for Usage-Based Products
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_create_quote_for_usage_based_products.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Build a Quote for Usage-Based Products

Create quotes for usage-based products that meet your customer’s needs. Review the resources included with the product, including the granted quantity and rates.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To create quotes:	Create on Quotes
From the App Launcher, find and select Quotes.
Select a quote.
Click Browse Catalogs.
Select a pricebook, and save your changes.
Select a product, and click Add.
To add a product with a future date, add the product to the quote line item by using the Related tab. Before refreshing the price, edit the quote line item record and update the start date to the required future date. The related grants and policy records are created based on the specified start date.
The product is added to the quote as a quote line item.
On the quote line item for the product that you added, click Manage Usage Resources.
Under Line Item Details, select the binding type.
	
Self	Binds the line item with the same product that the line item is added to. This option is available only for Anchor products.
Target	Binds the line item with a product, account, contract, or custom object. When you select a target, you must select a binding target type and the binding target that the line item is to be bound to. This option is available only when the product in the line item is of the usage model type Anchor or Pack.
NOTE When you create a quote by converting an opportunity, the quote details are automatically populated with the account name. If you add a product as a line item to this quote and attempt to bind the line item product to the same account on the Manage Usage Resources page, the account name doesn't populate automatically as the binding target. You must manually select the account name as the binding target.
If you select Binding Type as the target, then select the binding target type.
	
Product	

Binds the usage to a specific product. When you select this binding type, you can either set Binding Scope to the existing asset or line item. With this option, you have the flexibility to bind the current line item to another line item, which is part of the same quote or order.


Custom	Binds the usage to a custom object. This is for use cases where you want to track the usage against a unique object that isn't a standard Salesforce object.
Account	Binds the usage to a specific account, which is useful for tracking all usage associated with an account.
Contract	Binds the usage to a specific contract that makes sure that usage is billed according to the terms of a specific agreement.
Review the usage resources that are included in the product and their rates.

If you have trouble viewing rates for usage resources, check that your rating discovery procedure includes the latest elements. If your procedure doesn't have the latest elements, clone the Default Rating Discovery Procedure and reapply your customizations. For more information, see Clone the Default Rating Discovery Procedure.

If necessary, to update and apply the negotiated rates, select Override Rate.
To view details of a specific usage resource, click the usage resource.
A pane on the right side shows the details of the rate cards, tier rates, and policies, such as rollover, refresh, and aggregation policies, governing that resource.
Save your changes.
EXAMPLE Let’s say you’re a salesperson and you've successfully negotiated a special deal with Tech Innovators. Tech Innovators, a leading company in data-driven solutions, uses the Acme suite of products. The final quote reflects these key points:
A discount on your Acme Analytics API, which is a token-rated anchor product. The customer wants more calls at a lower rate.
A special discount on their Acme Cloud Storage, which is a token commitment product. They’ve agreed to a monthly token commitment in exchange for a percentage discount.
A per-unit rate for your Data Processing Suite, which normally uses tiered pricing. The customer wants a simple, consistent price, no matter the volume.

Here’s how you use the Manage Usage Resources interface to modify the negotiated rates.

For Acme Analytics API—on Manage Usage Resources page, in the Usage Resources table, update the grant quantity from 10,000 to 15,000 tokens and the applicable rate from $0.50 to $0.45 per token.
For Acme Cloud Storage—on Manage Usage Resources page, in the Commitment Rate column, update the value to 10%.
For Data Processing Suite—on the Manage Usage Resources page, under Resources and Grants, select Override Rate. Then, enter your negotiated per-unit price of $7.50 per GB.
SEE ALSO
Quotes in Revenue Cloud
Amending, Renewing, and Canceling Assets
Considerations for Managing Usage Selling Assets
View Rate Cards for Usage-Based Assets
