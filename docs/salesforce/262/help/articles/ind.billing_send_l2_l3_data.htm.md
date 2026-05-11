---
article_id: ind.billing_send_l2_l3_data.htm
title: Send Level 2 and Level 3 Payment Data via Your Payment Gateways
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_send_l2_l3_data.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Send Level 2 and Level 3 Payment Data via Your Payment Gateways

Include Level 2 and Level 3 payment metadata in the payment requests you make via payment gateways. Level 2 data includes transaction-level details such as tax amount and invoice reference number, while level 3 data includes detailed information such as product code, quantity, and unit price. Billing sends this data directly to third-party payment gateways through Apex adapter classes.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To send Level 2 and Level 3 data:	

Payment Admin permission set

OR

Payment Operations User permission set

To send enhanced payment metadata via your payment gateway, in Setup, find and select Billing Settings, and then turn on Level 2 and Level 3 Data Support.

To verify what data was sent to the payment gateway, check the payment gateway logs.

NOTE You can currently send Level 2 and Level 3 data only via third-party payment gateways that use Apex adapters.
Supported Level 2 and Level 3 Fields

In payment transactions, level 1 data includes basic information such as transaction amount, currency, card number or token, and merchant information.

Level 2 data includes level 1 data and the following additional information.

LEVEL 2 FIELDS
Tax amount
Total discount amount
Invoice / order reference number/purchase order number
Customer postal code/ Merchant info (zip/state)
Customer Reference Number - Invoice Number
Sales Tax Amount - Total tax for all lines
Freight Amount - Based on all products that bill for shipping
Duty Amount - Not sending
Destination Zip Code - Account Level Billing Address
Destination Country Code - Account Level Billing Address
Ship From Zip Code - Company Info at the Legal Entity
Discount Amount - ?
Tax Amount - This is the total tax
Tax Rate - Total Payment Request / Total Tax

Level 3 data includes level 2 data and the following detailed line items.

LEVEL 3 FIELDS
Line item details: product code/SKU or Charge Code
Quantity
Unit price
Line-level tax
Commodity code
Unit of measure
Extended line item totals
Shipping/duty fields (gateway dependent)
