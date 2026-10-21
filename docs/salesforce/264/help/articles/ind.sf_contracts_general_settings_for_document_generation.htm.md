---
article_id: ind.sf_contracts_general_settings_for_document_generation.htm
title: Document Generation Settings for Salesforce Contracts
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_general_settings_for_document_generation.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_system_administration_for_salesforce_contracts.htm
fetched_at: 2026-10-13
---

# Document Generation Settings for Salesforce Contracts

Understand the impact of the general setting options you select for the document generation users in your organization.

You can access General Settings from Setup, Document Generation | General Settings.

OPTION	WHAT IT DOES
Design Document Templates in Salesforce	Use the Design Document Template to design and generate documents from templates in Microsoft Word (.docx), Microsoft 365 Word (.docx), and Microsoft PowerPoint (.pptx) formats without a managed package. When you enable this setting, the application automatically creates the Docgen Document Template Library if not available.
Salesforce Contracts Connector for Word (Microsoft 365)	

To use Microsoft 365 Word features such as:

Design and maintain document templates.

Create and edit contract documents in the Microsoft 365 editor. Ensure the Microsoft Word 365 permission set license is provisioned.


Document Templates Export	

In Winter 24, this setting is intended exclusively for internal use by Salesforce applications to export standard document templates via the Metadata and Tooling API.

Enabling the setting introduces a few limitations for the document template naming: the name can't start with a number, the use of spaces and special characters aren't allowed, and the developer name can't exceed 38 characters.
