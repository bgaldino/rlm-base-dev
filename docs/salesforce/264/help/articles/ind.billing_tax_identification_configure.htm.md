---
article_id: ind.billing_tax_identification_configure.htm
title: Configure Additional Tax Identification Details
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_tax_identification_configure.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_partner_or_custom_tax_engine.htm
fetched_at: 2026-09-04
---

# Configure Additional Tax Identification Details

Send additional tax identification details to your external tax engine. Meet regional tax compliance requirements by storing tax identification and exemption information on the Billing Account and passing it to the tax engine.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To define tax details in a picklist:	Billing Admin permission set

For more information, see Add or Edit Picklist Values and Know Your Incoterms.

In Setup, find and select Object Manager.
Open Billing Accounts.
Select Fields & Relationships.
Click Tax Exemption Status.
In the Tax Exemption Status Picklist Values section, click New.
Enter the values that align with your tax engine, such as Exempt, Not Applicable, and Partial.
Save your changes.
Return to Fields & Relationships, click Delivery Terms, and repeat the same steps.
Go to Page Layouts.
Open the Billing Account Layout, add the additional tax identification details, and save the changes.
Only Tax Exemption Status and Delivery Terms are picklists. Add all six tax identification fields to the layout.
Tax Identification Number
Tax Identification Details
Tax Exemption Number
Tax Exemption Status
Exemption Expiration Date
Delivery Terms

After adding the required fields, you can open a Billing Account and verify the changes. When Billing calculates taxes, it automatically retrieves additional tax identification details from the default Billing Account associated with the Account. This information is passed to the configured external tax engine as part of the tax calculation request.

Tax identification support applies only to invoices, credit memos, and debit memos. Tax identification information isn’t used during tax calculation for quotes or orders.
