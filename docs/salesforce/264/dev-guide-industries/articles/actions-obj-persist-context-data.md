---
page_id: actions-obj-persist-context-data
title: Persist Context Data Action
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/actions-obj-persist-context-data.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-invocable-actions-parent
legacy_page_id: actions_obj_persist_context_data.htm
fetched_at: 2026-11-25
---

# Persist Context Data Action

Store cached context data associated with a context mapping ID in a Salesforce record.

This action is available in API version 59.0 and later.

## Special Access Rules

Available in Developer, Enterprise, Professional, and Unlimited editions for Industries clouds where Context Service is enabled.

## Supported REST HTTP Methods

**URI:** `/services/data/vXX.X/actions/standard/persistContextData`

Where `XX.X` is the latest API version.

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where `TOKEN` is a variable.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `contextId` | string | Required. The ID of the context data record with cached data that’s to be stored in the database. |
| `contextMappingId` | string | Optional. The Context Mapping record ID or Name that’s used to transform cached context data into the associated fields of the related Salesforce record. |
| `trackingId` | string | Optional. The ID of a Context Mapping record that’s used to transform cached context data into the associated fields of the related Salesforce record. |

## Outputs

| Output | Type | Description |
| --- | --- | --- |
| `referenceId` | string | The ID of a response event that’s used to track the request processing status and to get the full request response. |

## Usage

Persist Context Data invocable action is a wrapper over Persist Context data Connect API. It provides the ability to store the context data present in cache to database. Any update in context data can be persisted in database, if required.

## Example

**POST**

: 

This sample request is for the Persist Context Data action.

```
{
  "inputs": [
    {
      "contextId": "0000000a07da09100251752497651022c35b6150a4d04cd6a84bf1a0439cc609",
      "contextMappingId": "16Pxx0000004CCGEA2",
      "trackingId": "16Pxx0000004CCGEA2"
    }
  ]
}
```

This sample response is for the Persist Context Data action.

```
{
  "actionName": "persistContextData",
  "errors": null,
  "invocationId": null,
  "isSuccess": true,
  "outputValues": {
    "referenceId": "16Pxx0000004CAeEAM"
  },
  "sortOrder": -1,
  "version": 1
}
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/actions-obj-persist-context-data.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
