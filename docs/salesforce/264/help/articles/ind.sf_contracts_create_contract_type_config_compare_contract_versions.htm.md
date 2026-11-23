---
article_id: ind.sf_contracts_create_contract_type_config_compare_contract_versions.htm
title: Create Contract Type Config to Compare Contract Versions
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_contract_type_config_compare_contract_versions.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_system_administration_for_salesforce_contracts.htm
fetched_at: 2026-11-23
---

# Create Contract Type Config to Compare Contract Versions

To enable existing customers to compare contract versions, create the Compare Contract Versions Enabled setting in the contract type configuration and set its value to Yes. For new customers, this setting is pre-configured, but its default value is set to No. You must set it to Yes to compare contract versions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: Professional, Enterprise, Unlimited, and Developer Editions
USER PERMISSIONS NEEDED
To create a contract type config:	

CLM Admin

From Setup, in the Quick Find box, enter Contract Type Config, and then select Contract Type Config.
Click New.
Enter the values for the compare contract versions contract type config.
In Contract Type, select Default or any contract type that you prefer.
In Usage Type, select Document Setting.
In Config Type, select Compare Contract Versions Enabled.
In Config Value, enter Yes.
Click Create.

See Also

Comparing Contract Document Versions

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.sf_contracts_create_contract_type_config_compare_contract_versions.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
