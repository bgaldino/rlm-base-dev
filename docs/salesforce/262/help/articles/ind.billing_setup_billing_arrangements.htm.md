---
article_id: ind.billing_setup_billing_arrangements.htm
title: Configure Billing Arrangements for Billing Schedule Groups
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_setup_billing_arrangements.htm&type=5&release=262
release: 262
release_name: Summer '26
area: billing
parent_article: ind.billing_billing_arrangements.htm
fetched_at: 2026-05-11
---

# Configure Billing Arrangements for Billing Schedule Groups

Route invoices with the appropriate allocated charges to the correct billing accounts by configuring billing arrangements on billing schedule groups.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Performance, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS NEEDED
To configure billing arrangements:	

Billing Admin permission set

OR

Billing Operations User permission set

Enable field-level security on the PaymentTerm and BillToContact fields of the Billing Account object.

Go to the Billing Schedule Group record.
In the Billing Arrangements tab, click Manage Billing Arrangements.
Enter a name for the billing arrangement.
Click Add Account to add a new billing arrangement line.
Select a billing account.
Optionally, select Remainder to indicate whether to bill the remainder percentage to the billing account.
Repeat steps 4 and 5 to add up to five billing arrangement lines.
Optionally, select Bill Remainder to Owning Account to allocate any remainder percentage to the owning account.
Any percentage of the billing amount that isn’t assigned to any of the billing accounts is displayed as remainder billing percentage.
Save your changes.
NOTE If the remainder percentage isn’t allocated to the owning account or any of the billing accounts, then the same is automatically allocated to the first billing account in the billing arrangement.
