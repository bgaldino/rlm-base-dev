---
article_id: ind.dro_submit_order_with_validation_flow.htm
title: Handle Conflicts During Asset Date Amendments by Using Submit Order with Validation Flow
source_url: https://help.salesforce.com/s/articleView?id=ind.dro_submit_order_with_validation_flow.htm&type=5&release=262
release: 262
release_name: Summer '26
area: dro
fetched_at: 2026-05-12
---

# Handle Conflicts During Asset Date Amendments by Using Submit Order with Validation Flow

It's common to request adjustments to license subscription start dates, either moving them earlier if your users are ready to use them or delaying them if they are not. However, if the order that created the asset has incomplete steps in its fulfillment plan, submitting an asset amendment can result in two orders updating the asset simultaneously. Identify and handle incomplete steps in the fulfillment plan by using the Submit Order with Validation flow.

REQUIRED EDITIONS
Available in: Both Salesforce Classic (not available in all orgs) and Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS
NEEDED
To run the Submit Order with Validation Flow:	

Fulfillment Designer

OR

DRO Admin User

Use the flow to discard future-dated or pending steps that are no longer relevant in the existing fulfillment plan, so asset amendments are processed without conflicts.

The Submit Order with Validation flow uses the Get Steps from Order subflow, that retrieves the incomplete steps from an order. The order is identified using the orderID passed to the subflow. Both the flows are available as out-of-the-box template flows.

NOTE The Submit Order with Validation flow is designed for orders containing up to 200 order line items. To work with larger orders, contact your Salesforce admin.

To use the Get Steps from Order subflow in the Submit Order with Validation flow, follow these steps:

From Setup, find and select Flows.
Find and select Get Steps from Order.
Save the Get Steps from Order template as a new flow and activate it.
Find and select Submit Order with Validation.
Save the Submit Order with Validation template as a new flow.
Replace the Get Steps from Order subflow step in the Submit Order with Validation flow with a call to the newly created active Get Steps from Order subflow.
Assign the same input and output variables that were used in the old subflow.
Activate the Submit Order with Validation flow.
When you call the Submit Order with Validation flow using the orderId of an order with an incomplete fulfillment plan, the incomplete steps found in the order are shown. Review the steps and remove those that you don’t want to discard. Then, you can choose to discard the remaining incomplete steps and submit the order. Now, any future amendments to the asset can be processed without issues.
