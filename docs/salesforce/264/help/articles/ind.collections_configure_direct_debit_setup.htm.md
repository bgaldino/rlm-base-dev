---
article_id: ind.collections_configure_direct_debit_setup.htm
title: Set Up Mulesoft Integration for Direct Debit Request
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_configure_direct_debit_setup.htm&type=5&release=264
release: 264
release_name: Winter '27
area: collections
parent_article: ind.collections_setup.htm
fetched_at: 2026-11-23
---

# Set Up Mulesoft Integration for Direct Debit Request

Help your collections specialists ‌submit a direct debit request to the core banking system. Collections specialists can request for a direct debit using the Request Direct Debit bulk action on a collections actionable list page. The action initiates a new debit from the customer’s mandated bank account.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
To specify an authentication protocol, create an external credential, and then specify a named credential as the callout endpoint.
Create and activate an integration definition. When creating the integration definition, you must specify these details, and save the changes.
Type	Apex Defined
Name	PostDebitInstructions
Apex Class	fsc_collection_apex.RequestDirectDebitIntegrationProvider
To ensure users can make callouts by using the named credential, link the external credential principals to permission sets or user profiles.
Clone and customize the prebuilt Omniscript, CollectionsRequestDirectDebitForCollectionPlans.
Customize the Prebuilt Omniscript for Direct Debit Request
Create a new version of the prebuilt Omniscript, CollectionsRequestDirectDebitForCollectionPlans, set the submit status values for the collection plan status and actionable list member status.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.collections_configure_direct_debit_setup.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
