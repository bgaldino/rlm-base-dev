---
page_id: connect-responses-field-data-output
title: Field Data
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-field-data-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Catalog Management
parent_page: product-catalog-management-api-responses
legacy_page_id: connect_responses_field_data_output.htm
fetched_at: 2026-11-25
---

# Field Data

Output representation of the field data.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errorCode​ToErrorMap` | Map<String, [Unit Of Measure Error](./connect-responses-unit-of-measure-error-output.md)> | Error codes mapped to their details. | Small, 63.0 | 63.0 |
| `fieldApiName` | String | Unique API Name of the field. | Small, 63.0 | 63.0 |
| `isRounding​Applicable` | Boolean | Indicates whether data rounding is applicable to the decimal (`true`) or not (`false`). | Small, 63.0 | 63.0 |
| `original​Value` | String | Original value of the field. | Small, 63.0 | 63.0 |
| `rounded​Value` | String | Rounded field value that corresponds to the original value, if data rounding is applicable. | Small, 63.0 | 63.0 |
| `unitOf​MeasureId` | String | ID of the unit of measure record that’s associated to the field. | Small, 63.0 | 63.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-field-data-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
