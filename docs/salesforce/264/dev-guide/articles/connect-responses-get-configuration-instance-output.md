---
page_id: connect-responses-get-configuration-instance-output
title: Configuration Get Instance
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-get-configuration-instance-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: product-configurator-business-apis-responses
legacy_page_id: connect_responses_get_configuration_instance_output.htm
fetched_at: 2026-11-25
---

# Configuration Get Instance

Output representation of the request to retrieve the configuration instance.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Error Response](https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/connect_responses_error_response.htm) | List of errors, which contains an error code and a message. | Small, 60.0 | 60.0 |
| `success` | Boolean | Indicates whether the call was successful (`true`) not (`false`). | Small, 60.0 | 60.0 |
| `transaction` | Map<String, Object> | Transaction JSON payload representing an object in an external system that’s used to create a session. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-get-configuration-instance-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
