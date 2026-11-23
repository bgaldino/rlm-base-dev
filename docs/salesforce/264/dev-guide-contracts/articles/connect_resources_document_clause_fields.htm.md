---
page_id: connect_resources_document_clause_fields.htm
title: Document Clause Fields
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_document_clause_fields.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_clause_library_resources.htm
fetched_at: 2026-11-23
---

# Document Clause Fields

Get distinct document clause values for a given fieldName parameter.

## Resource

```
/connect/clause-library/document-clauses/fields
```

## Example URI

```
https://YOUR_INSTANCE.salesforce.com/services/data/68.0/connect/clause-library/document-clauses/fields?clauseSetId={id}
```

## Available Version

57.0

## HTTP Methods

GET

## Query Parameters for GET

| Parameter Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `clauseSetId` | String | The ID of the document clause set. | Required | 57.0 |
| `fieldName` | String | Specifies language and name. Value is case-sensitive. Possible values are `Language` or `Name`. | Required | 57.0 |
| `language` | String | The language for the clauseSetId parameter. | Required | 57.0 |
| `name` | String | The name for the clauseSetId parameter. | Required | 57.0 |
| `status` | String | Displays records based on the status. | Required | 57.0 |

## Response Body for GET

[Document Clause Fields Response](./connect_responses_document_clause_fields_respons.htm.md "Output representation for the list of document clause fields.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_document_clause_fields.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
