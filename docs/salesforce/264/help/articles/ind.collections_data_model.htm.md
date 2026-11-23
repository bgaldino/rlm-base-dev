---
article_id: ind.collections_data_model.htm
title: Collections and Recovery Data Model
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_data_model.htm&type=5&release=264
release: 264
release_name: Winter '27
area: collections
parent_article: ind.collections.htm
fetched_at: 2026-11-23
---

# Collections and Recovery Data Model

The Collections data model includes Collection Plan and related objects that facilitate the record creation for collection activities.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.

Banks or financial institutions can configure their systems to insert ‌collection-related details into the Collection Plan and related object records. They can easily import large volumes of Collections data from CSV files into Collection Plan and related objects. They can also automate Collections data import processes, ensuring data consistency and integrity by using the Composite Graph API. Using a single Composite Graph API request, they can create collection plans, collection plan items, contacts, and other related object records in one go.

Collection Plan: Stores the details about the outstanding amounts linked to financial accounts, billing accounts, contacts, or accounts associated with individuals or an organization.
Collection Plan Item: Represents an instance of a collection plan. Stores the delinquency details for an invoice or a financial account statement.
Collection Plan Reason: Stores the reason for initiating the collection process, including non-payment of bills, bankruptcy, outstanding invoices, and deceased account holders.

Here’s the Collections data model.

SEE ALSO
Salesforce Developer Documentation: Collections and Recovery Standard Objects

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.collections_data_model.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
