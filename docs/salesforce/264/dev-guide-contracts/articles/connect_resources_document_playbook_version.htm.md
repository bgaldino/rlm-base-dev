---
page_id: connect_resources_document_playbook_version.htm
title: Document Playbook Version (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_document_playbook_version.htm
release: 264
release_name: Winter '27
deliverable: clm_developer_guide
section: Salesforce Contracts
parent_page: connect_resources_document_playbook_resources.htm
fetched_at: 2026-11-23
---

# Document Playbook Version (POST)

Create a playbook version and link it to a content
document.

This resource validates the input, creates a `DocumentPlaybookVersion` record for the specified playbook, and creates a
`ContentDocumentLink` record that links the new playbook
version to the specified content document.

## Special Access Rules

Playbook must be enabled in your org, and you must have the Playbook Designer
permission.

## Resource

```
/connect/document-playbook/document-playbook-version
```

## Resource Example

```
https://YOUR_INSTANCE.salesforce.com/services/data/v68.0/connect/document-playbook/document-playbook-version
```

## Available Version

68.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
  "playbookId" : "0RDxx0000004C92GAE",
  "description" : "Initial version of the contract playbook",
  "contentDocumentId" : "069xx0000004C92GAE"
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contentDocument​Id` | String | ID of the content document. | Required | 68.0 |
| `description` | String | Description of the playbook version. | Optional | 68.0 |
| `playbookId` | String | ID of the playbook. | Required | 68.0 |

## Response Body for POST

[Playbook Version
Details](./connect_responses_playbook_version_details.htm.md "Output representation that contains the ID of the created playbook version.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.clm_developer_guide.meta/clm_developer_guide/connect_resources_document_playbook_version.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
