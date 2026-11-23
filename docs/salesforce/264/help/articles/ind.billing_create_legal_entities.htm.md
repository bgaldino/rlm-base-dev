---
article_id: ind.billing_create_legal_entities.htm
title: Create Legal Entities in Revenue Cloud
source_url: https://help.salesforce.com/s/articleView?id=ind.billing_create_legal_entities.htm&type=5&release=264
release: 264
release_name: Winter '27
area: billing
parent_article: ind.billing_legal_entities_manage.htm
fetched_at: 2026-11-23
---

# Create Legal Entities in Revenue Cloud

Create legal entities to manage the billing and tax information for order products.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Enterprise, Unlimited, and Developer Editions with the Revenue Cloud Advanced license or the Revenue Cloud Billing license
USER PERMISSIONS
NEEDED
To create legal entities:	Billing Admin permission set

Before you create a legal entity record, make sure that the Status field is visible on the Legal Entities page layout. If it isn't, add the field to the page layout.

From the App Launcher, find and select Legal Entities.
Click New.
Enter a name for the new legal entity.
Select Active as the status.
Enter the details as needed.
NOTE

To generate billing schedules with correct addresses after State and Country/Territory Picklists are enabled, edit each legal entity that already has an address. Select the country and state from the picklists, and then save the record. Country Code and State Code aren’t filled in from an address that was saved before the picklists were enabled.

If Country Code and State Code are blank, the Order to Billing Schedule flow can’t be completed. Billing copies the legal entity address to the billing schedule group’s Ship From address without valid codes.

See Enable State and Country/Territory Picklists.

If multiple currencies are enabled in your Salesforce org, select a currency ISO code.
If you don't select a currency ISO code, your personal currency is considered as the currency ISO code of the record. You can't edit the currency ISO code after a Legal Entity record is created.
Select an email template.
Use Default Invoice Email Template or clone and customize the email template based on your business needs.
To send an invoice PDF document with the email, select Attach Invoice Document to Email.
Save your changes.
To save the new legal entity, the status must be either Active or Inactive.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.billing_create_legal_entities.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
