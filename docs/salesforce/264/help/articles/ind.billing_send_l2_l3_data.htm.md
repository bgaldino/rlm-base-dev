---
article_id: ind.billing_send_l2_l3_data.htm
title: Send Level 2 and Level 3 Payment Data Through Your Payment Gateways
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_send_l2_l3_data.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_payments.htm
fetched_at: 2026-09-04
---

# Send Level 2 and Level 3 Payment Data Through Your Payment Gateways

Level 2 and Level 3 processing data are the additional line-item and transaction-level details passed during credit card authorization. Use Level 2 and Level 3 data mainly for business-to-business and business-to-government corporate card transactions to lower fraud risk and get richer reporting. When Level 2 and Level 3 data support is enabled, Billing automatically includes additional transaction data in payment requests that you send through native and third-party payment gateways.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To send Level 2 and Level 3 data:	

Payment Admin permission set

OR

Payment Operations User permission set

Billing sends Level 2 and Level 3 data automatically to native payment gateways, such as Stripe and Adyen. Billing populates the Level 2 and Level 3 fields from the invoice and invoice lines with a fixed mapping.

Quantity, unit price, and line amount are derived from the invoice line.
Ship-from postal code, that’s part of Level 2 data, is derived from the postal code of the invoice’s legal entity.

For third-party payment gateways, Billing sends Level 2 and Level 3 data through Apex adapter classes. You can customize the adapter classes to map additional fields to send data beyond the standard set. For more information, see the Apex Reference Guide.

Supported Level 2 and Level 3 Fields

In payment transactions, Level 1 data includes basic information such as transaction amount, currency ISO code, and merchant account name.

Level 2 data includes Level 1 data and this information.

LEVEL 2 FIELDS	DEFAULT VALUE
DiscountAmount	0
DutyAmount	0
ReferenceId	 
SalesTaxAmount	 
ShipFromZip	 
ShippingAmount	 
ShipToCountry	 
ShipToZip	 
TotalTaxAmount	0

Level 3 data includes Level 2 data and these detailed line items.

LEVEL 3 FIELDS	DEFAULT VALUE
CommodityCode	 
Description	 
Discount	0
DiscountIndicator	false
GrossNetIndicator	"N"
LineItemTotal	 
Quantity	 
Sku	 
TaxAmount	 
TaxRate	 
Uom (unit of measure)	 
UnitPrice	 
NOTE For Stripe, Billing includes Level 3 line data for invoices with up to 200 lines. For an invoice with more than 200 lines, the payment still processes, but Billing sends only Level 2 data and omits the Level 3 line data. Adyen has no such line limit.
Process a Payment That Includes Level 2 and Level 3 Data
Send a payment through a native or third-party payment gateways with enhanced data attached, and verify the Level 2 and Level 3 fields in the payment gateway logs.
