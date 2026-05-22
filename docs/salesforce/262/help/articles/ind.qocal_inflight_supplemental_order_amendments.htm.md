---
article_id: ind.qocal_inflight_supplemental_order_amendments.htm
title: Modify Activated Orders Before Fulfillment in Agentforce Revenue Management
source_url: https://help.salesforce.com/s/articleView?id=ind.qocal_inflight_supplemental_order_amendments.htm&type=5&release=262
release: 262
release_name: Summer '26
area: transaction_mgmt
fetched_at: 2026-05-12
---

# Modify Activated Orders Before Fulfillment in Agentforce Revenue Management

Use in-flight amendments or supplemental change orders to modify existing orders after activation but before fulfillment. This feature captures changes in a linked order to establish a unified order view, streamline order modification, and improve accuracy.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions of Revenue Cloud where Transaction Management is enabled
USER PERMISSIONS NEEDED
To place supplemental orders:	

Place Supplemental Orders permission set

AND

Sales Operations Rep permission group

Prerequisites for Supplemental Orders

Before modifying orders, perform these setup tasks.

For the Order object, configure a new Superseded status. For more help, see Create a Custom Picklist Field.
Add the Change button to the order page layout. To modify an object's page layout, see Customize Page Layouts with the Enhanced Page Layout Editor.
IMPORTANT Review these impacts when you submit an original order to DRO.
Salesforce locks line items when the fulfillment process reaches the point of no return (PONR).
The system locks the fulfillment plan associated with the original order.
Submitting the supplemental order updates the original fulfillment plan instead of creating one.
Change an Activated Order

Update products and quantities for an activated but unfulfilled order by creating a supplemental order.

On the order page, select an activated order and click Change.
Salesforce creates a copy of the original order in Draft status.
The system copies all products, application usage assignments, order actions, relationships, attributes, and custom child entities.
The supplemental order appears under the Related Order list of the original order with the Related Order Type set to supplemental order.
From the order line dropdown, select Configure to reconfigure an order item.
Edit the product attributes.
Select Save & Exit.
The Supplemental Change Type column updates to Amend for edited products or quantity changes.
New order items receive the Add type.
Items without updates show the No Change type.
Pricing preference defaults to Skip.
Activate the order.
The original order status changes to Superseded and the new supplemental order replaces it.
