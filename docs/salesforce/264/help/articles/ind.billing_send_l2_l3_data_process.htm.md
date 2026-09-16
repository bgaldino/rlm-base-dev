---
article_id: ind.billing_send_l2_l3_data_process.htm
title: Process a Payment That Includes Level 2 and Level 3 Data
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_send_l2_l3_data_process.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_send_l2_l3_data.htm
fetched_at: 2026-09-04
---

# Process a Payment That Includes Level 2 and Level 3 Data

Send a payment through a native or third-party payment gateways with enhanced data attached, and verify the Level 2 and Level 3 fields in the payment gateway logs.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To process payments and review payment gateway logs:	

Payment Admin permission set

OR

Payment Operations User permission set

Turn on Level 2 and Level 3 data support on the Billing Settings page, and confirm that you have a posted invoice with line-level detail. Each invoice line needs a product description, unit price, quantity, and line amount, because these fields form the Level 3 data that Billing sends to the gateway.

When you process a payment on a native gateway, Billing attaches Level 2 and Level 3 data automatically from the invoice and invoice lines.

Create a payment schedule for the invoice.
Create a payment schedule item, and link it to the saved payment method of your third-party or native payment gateway, such as Stripe or Adyen.
Set the payment schedule item status to Ready for Processing.
Run a payment batch run.
After the payment batch run completes, open the payment gateway logs and confirm that the payment transaction has succeeded.
The gateway log shows that Level 2 and Level 3 fields, such as quantity, unit price, and tax amount, have been passed to the payment gateway during the payment transaction.
