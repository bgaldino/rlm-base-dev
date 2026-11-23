---
page_id: deployment_industries_common_components_metadata.htm
title: Industries Common Component Metadata
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_industries_common_components_metadata.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Management Deployment
parent_page: deployment_appendix_B.htm
fetched_at: 2026-11-23
---

# Industries Common Component Metadata

This table provides the metadata deployment reference for Industries common components
in Revenue Management, including setup paths and configuration details.

| Type | Label | Setup Path | Details |
| --- | --- | --- | --- |
| Setup | Context Service | Context Service > Context Service Settings | Enable |
| Permission Sets | Permission Sets | Setup > Users > Permission Sets | Data Pipeline User |
| Permission Sets | Permission Sets | Setup > Users > Permission Sets | Data Cloud Admin |
| Data Processing Engine (DPE) Definition | datasources -> sourceName | v{}/tooling/sobjects/BatchCalcJobDefinition | Read permission to the user who is creating the Data Processing Engine (DPE) with the data sources and fields. |
| Data Processing Engine (DPE) Definition | datasources -> sourceName | v{}/tooling/sobjects/BatchCalcJobDefinition | Read permission to the Analytics Integration User with the data sources and fields. |
| Data Processing Engine (DPE) Definition | writebacks -> targetObjectName | v{}/tooling/sobjects/BatchCalcJobDefinition | Create, update, or delete permission on the targetObjectName object based on the operationType value defined in the writebacks. |
| Data Processing Engine (DPE) Definition | writebacks -> writebackUser | v{}/tooling/sobjects/BatchCalcJobDefinition | Delete this value if it exists. |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_industries_common_components_metadata.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
