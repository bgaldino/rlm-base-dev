---
article_id: ind.collections_compliance_setup.htm
title: Setup and Configuration for Call Compliance Checks
source_url: https://help.salesforce.com/s/articleView?id=ind.collections_compliance_setup.htm&type=5&release=264
release: 264
release_name: Winter '27
area: collections
parent_article: ind.collections_setup.htm
fetched_at: 2026-11-23
---

# Setup and Configuration for Call Compliance Checks

Collections specialists can make informed decisions about contacting borrowers by using call compliance checks. Turn on Financial Account Management Standard Objects, and Context Definitions.

REQUIRED EDITIONS
Available in: Lightning Experience
Available in: View product and edition availability.
Enable Financial Account Management Standard Objects and Configure Context Definitions
To use the Financial Account and related standard objects, enable Financial Account Management Standard Objects. To access and configure context definitions, enable Context Definitions.
Create and Configure an External Client App
Create an external client app that enables a compliance application to integrate with Salesforce by using the relevant API. External client apps provide single sign-on (SSO) and use OAuth protocols to authorize third-party apps.
Create and Configure Integration Definitions and Named Credentials
To connect Salesforce with an external system, create integration definitions. APIs work with the integration definitions to perform operations in both Salesforce and the external system. Link the prebuilt APEX class to the integration definition.
Customize Lightning Pages to View Compliance Check Information
To show the outbound call compliance details for the borrowers associated with the collection plan, add the CallComplianceDetailsForBorrowers component to the collection plan record page.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce Help content ([source](https://help.salesforce.com/s/articleView?id=ind.collections_compliance_setup.htm&type=5&release=264)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
