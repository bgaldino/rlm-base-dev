---
article_id: ind.billing_tax_identification_configure.htm
title: Configure Additional Tax Identification Details
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_tax_identification_configure.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
fetched_at: 2026-05-11
---

# Configure Additional Tax Identification Details

Send additional tax identification details to your external tax engine. Meet regional tax compliance requirements by storing tax identification and exemption information on the Billing Profile and passing it to.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS NEEDED
To define tax details in a picklist:	Billing Admin permission set

For more information, see Add or Edit Picklist Values and Know Your Intercoms.

In Setup, find and select Object Manager.
Open Billing Accounts.
Select Fields & Relationships.
Click Tax Exemption Status.
In the Values related list, click New.
Enter the values that align with your tax engine, such as Exempt, Not Applicable, Partial.
Save your changes.
Repeat these steps for the Delivery Terms field.
Go to Page Layouts.
Add the additional tax identification details to the Billing Profile layout and save the changes.
Tax Identification Number
Tax Identification Details
Tax Exemption Number
Tax Exemption Status
Exemption Expiration Date
Delivery Terms

After adding the required fields, you can open the Billing Profile and verify the changes. When Billing calculates taxes, it automatically retrieves additional tax identification details from the default Billing Profile associated with the Account. This information is passed to the configured external tax engine as part of the tax calculation request.

Tax identification support applies only to invoices, credit memos, and debit memos. Tax identification information isn't used during tax calculation for quotes or orders.
