---
page_id: cml-best-practice-pricing-fields
title: Pricing Fields Not Supported in CML
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-best-practice-pricing-fields.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: cml-cml-best-practices
legacy_page_id: cml_best_practice_pricing_fields.htm
fetched_at: 2026-11-25
---

# Pricing Fields Not Supported in CML

Pricing fields, such as ListPrice and NetUnitPrice, aren’t supported in CML and shouldn’t be used in constraint models.

Pricing fields, such as ListPrice, NetUnitPrice, and others, are not supported in CML and should not be used in constraint models. CML is designed to enforce configuration logic for products, not to perform pricing calculations. Attempting to reference or manipulate pricing fields in CML code leads to errors and unexpected behaviors in the constraint engine. Use dedicated pricing or calculation mechanisms outside of the CML constraint model for such functionality.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/cml-best-practice-pricing-fields.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
