---
article_id: ind.sf_contracts_create_contract_record_type.htm
title: Create Contract Record Type
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_contract_record_type.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_contract_types_contract_record_types_and_contract_type_configs.htm
fetched_at: 2026-11-23
---

# Create Contract Record Type

A contract record type can have only one contract type object as its parent, but a contract type object can have multiple contract record types as its child.

From Setup, click Object Manager. Type Contract in the Quick Find box.
Click Contract and then click Record Types.
Contract Lifecycle Management is the default contract record type.
Click New.
Enter these details:

Existing Record Type: Master

Name: Enter a name for the contract record type.

Active: Select the Active checkbox.

Make Available: Select the user profiles that you want to provide the ability to create and clone records of this record type, or assign this record type to an existing record. To make the new record type the default for a profile, select Make Default. Users assigned to this record type can still view and edit records associated with record types not available for their profiles.

Click Next.
Select Contract Layout in Apply one layout to all profiles.
Save your changes.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_contract_record_type.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
