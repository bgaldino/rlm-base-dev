---
article_id: ind.sf_contracts_support_for_designer_in_core_and_ss_document_generation.htm
title: Support for Template Designer in Core and Server-Side Document Generation
source_url: https://help.salesforce.com/s/articleView?id=ind.sf_contracts_support_for_designer_in_core_and_ss_document_generation.htm&type=5&release=264
release: 264
release_name: Winter '27
area: salesforce_contracts
parent_article: ind.sf_contracts_integrate_salesforce_contracts_in_vlocity_managed_packages.htm
fetched_at: 2026-11-23
---

# Support for Template Designer in Core and Server-Side Document Generation

The combinations of managed packages that support the transition from the manage package designer to the document template designer in Salesforce core. In core, the designer is named Design Document Templates.

COMBINATION	MANAGED PACKAGE RUNTIME SETTING	TRANSITION TO DOCGEN DESIGNER IN CORE	DOCUMENT TEMPLATE


Omnistudio for Vlocity

+

{INS or CME package}

	N/A	Not Supported	Use the document templates created in the INS and CME packages to generate documents by using the server-side mechanism.


Omnistudio Standard

+

{INS or CME package}

	
Turned Off

Turned On

	Supported	

Use the document templates created in the INS and CME packages to generate documents by using the server-side mechanism.

In addition, use the document templates created in core to generate documents by using the server-side mechanism.




Omnistudio Standard

+

Omnistudio Package

	N/A	Supported	

Use the document templates created in the Omnistudio package to generate documents by using the server-side mechanism.

In addition, use the document templates created in core to generate documents by using the server-side mechanism.

Also, the document template supports client-side document generation, Omnistudio Omniscripts, and Integration Procedures.


Omnistudio Standard without any package	N/A	Supported	Use the document templates created in core to generate documents by using the server-side mechanism.


Omnistudio Standard

+

INS or CME Package and Omnistudio Package (side-by-side package installation)

	Turned On or Turned Off	Not Supported	

Not Recommended.

Important: The installation of the Omnistudio Standard and Salesforce Industries packages in the same org can result in errors.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.sf_contracts_support_for_designer_in_core_and_ss_document_generation.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
