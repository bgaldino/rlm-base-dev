---
article_id: ind.sf_contracts__create_new_contract_status_values.htm
title: Create New Contract Status Values
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts__create_new_contract_status_values.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_workflow_to_configure_new_contract_status_values_and_map_to_contract_object_state_definition.htm
fetched_at: 2026-11-23
---

# Create New Contract Status Values

You can create new contract status values from Setup and reorder the sequence of the contract statuses

From Setup, click Object Manager.
Type Contract in the Quick Find box.
Click Contract and then click Fields & Relationships.
Click Status and scroll to the Contract Status Picklist Values section.
Add a new status value:
Click New.
Enter the Label and API Name.
Select a default status category from the list.
Select the record type name that you want to associate the new status value with.
Save the changes.
Reorder the picklist value:
Click Reorder.
Use the arrow keys to reorder the picklist values.
Save your changes.
Verify Record Type Reflects the New Status Value:
From Setup, click Object Manager.
Type Contract in the Quick Find box.
Click Contract and then click Record Types.
Contract Lifecycle Management is the default contract record type.
Select the record type to which you added the contract status value.
Click Edit, next to the Status field.
Verify the new contract status value is listed in the Selected Values list.
Click Cancel to close the window.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.sf_contracts__create_new_contract_status_values.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
