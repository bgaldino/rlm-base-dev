---
page_id: connect_resources_cc_user_contract_doc_version.htm
title: Contract Document Version for Customer Community User (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_cc_user_contract_doc_version.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_customer_community_user.htm
fetched_at: 2026-11-23
---

# Contract Document Version for Customer Community User (GET)

Get latest details of a contract document version based on a
contract ID.

## Resource

```
/connect/clm/cc/contract/${contractId}/contract-document-version
```

## Resource Example

```
https://YOUR_INSTANCE.salesforce.com/services/data/v68.0/connect/clm/cc/contract/${contractId}/contract-document-version?showDetails=true
```

## Available Version

60.0

## HTTP Methods

GET

## Request Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `showDetails` | Boolean | Indicates whether to include detailed information about attachments in the response. (`true`) or not `(false`). The default value is `false`. | Required | 60.0 |

## Response Body for GET

[Contract Document
Version CC Response](./connect_responses_contract_document_version_c_c.htm.md "Output representation of the latest details of a contract document version, including its ID, status, and associated documents and attachments.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_cc_user_contract_doc_version.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
