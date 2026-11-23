---
article_id: ind.billing_billing_arrangement_create.htm
title: Create Billing Arrangements and Billing Arrangement Lines
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_billing_arrangement_create.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_billing_arrangements.htm
fetched_at: 2026-11-23
---

# Create Billing Arrangements and Billing Arrangement Lines

Billing arrangements define how a transaction’s billable amount is invoiced to the relevant billing accounts.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Billing license. Contact your Salesforce account executive for more information.
USER PERMISSIONS
NEEDED
To create billing arrangements:	

Billing Admin permission set

OR

Billing Operations User permission set

NOTE

Starting Spring ’26, the Billing Arrangement Lines related list is enabled by default. For the Salesforce orgs created in or upgraded to Spring ’26, your Billing admin must perform a one-time task of adding the Billing Arrangement Lines related list to the Billing Arrangement page layout.

From the App Launcher, find and select Billing Arrangements.
Create a billing arrangement.
Click New.
Enter a name for the billing arrangement.
Select Draft as the status.
Save your changes.
Create billing arrangement lines for the billing arrangement.
In the Related tab of the billing arrangement, click New.
Select an account or create one.
Select a billing account or create one.
Enter a percentage of the billing amount to assign to the billing account.
If required, select Remainder to indicate whether to bill the remainder percentage to the billing account.
Save your changes.
You can set the billing arrangement as Active.

Alternatively, you can configure billing arrangements on the billing schedule groups by using the Billing Arrangements tab.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_billing_arrangement_create.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
