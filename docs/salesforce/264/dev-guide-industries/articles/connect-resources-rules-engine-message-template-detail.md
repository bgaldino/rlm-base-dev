---
page_id: connect-resources-rules-engine-message-template-detail
title: Explainability Message Template Details (GET)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-rules-engine-message-template-detail.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Business Rules Engine
parent_page: decision-explainer-bre-resources
legacy_page_id: connect_resources_rules_engine_message_template_detail.htm
fetched_at: 2026-11-25
---

# Explainability Message Template Details (GET)

Retrieves the details of an explainability message template for a specified template ID.

## Resource

```
/connect/business-rules/explainability/message-templates/${messageTemplateId}
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/connect
/business-rules/explainability/message-templates/8U8x00000000027CAA
```

{yourInstance} is the domain name of your Salesforce instance.

## Available Version

56.0

## Requires Chatter

No

## HTTP Methods

GET

## Response Body for GET

[Message Template Details](./connect-responses-message-template-detail-output.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-rules-engine-message-template-detail.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
