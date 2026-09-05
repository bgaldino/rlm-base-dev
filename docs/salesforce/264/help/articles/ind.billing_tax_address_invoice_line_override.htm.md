---
article_id: ind.billing_tax_address_invoice_line_override.htm
title: Override Addresses on Invoice Lines
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_tax_address_invoice_line_override.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_tax_additional_configuration.htm
fetched_at: 2026-09-04
---

# Override Addresses on Invoice Lines

When you separately bill certain order products of an account, you can specify different tax addresses on the invoices of those order products. This flexibility ensures accurate tax calculations and compliance with regional tax regulations because the tax address is important for calculating tax. Also, your customers benefit from the enhanced accuracy in their financial documentation.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To modify billing schedule groups and set history tracking:	Billing Admin permission set
Change Addresses of Billing Schedule Groups

The addresses of your accounts appear as addresses on the related billing schedule groups. The addresses of your billing schedule groups appear as addresses on the related invoice tax lines. So, to specify different tax addresses on the invoices of order products that you’re billing, change the shipping and billing addresses of the billing schedule groups that are related to the order products.

From the App Launcher, find and select Billing Schedule Groups.
Open the Billing Schedule Group record that you want to modify.
Change the shipping address and billing address.
Save your changes.

When invoice runs process the billing schedule groups, the invoice runs generate invoices with invoice line taxes that show the changed addresses of the billing schedule groups.

Track Changes to Billing Schedule Group Addresses

Your Billing admin can enhance the accountability of your billing processes by enabling field history tracking for the Billing Schedule Group object’s address fields. Billing specialists can then monitor and audit any modifications made to these fields.

From the object management settings for billing schedule groups, go to Fields & Relationships.
Click Set History Tracking.
Select Billing Address and Shipping Address from the list of fields.
Save your changes.

Customize the Billing Schedule Group’s page layout to include the History related list. All the changes that you make to the Billing Schedule Group address fields are added to the History related list on the Billing Schedule Group records.
