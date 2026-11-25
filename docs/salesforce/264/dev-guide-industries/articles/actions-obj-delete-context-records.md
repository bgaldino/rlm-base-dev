---
page_id: actions-obj-delete-context-records
title: Delete Context Records Action
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/actions-obj-delete-context-records.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-invocable-actions-parent
legacy_page_id: actions_obj_delete_context_records.htm
fetched_at: 2026-11-25
---

# Delete Context Records Action

Deletes one or more records from a context instance.

This action is available in API version 67.0 and later.

## Special Access Rules

Available in Developer, Enterprise, Professional, and Unlimited editions for Industries clouds where Context Service is enabled.

## Supported REST HTTP Methods

**URI:** `/services/data/vXX.X/actions/standard/deleteContextRecords`

Where `XX.X` is the latest API version.

**Formats:** JSON, XML

**HTTP Methods:** POST

**Authentication:** `Authorization: Bearer TOKEN`

Where `TOKEN` is a variable.

## Inputs

| Input | Type | Description |
| --- | --- | --- |
| `contextId` | string | Required. ID of the context instance from which records are deleted. |
| `dataPaths` | List<String> | Required. A collection of data path objects that identify the records to delete from the context instance. Each object contains a `dataPath` field whose value is a list of strings representing the hierarchical path from the root to the target record in the context. |
| `isPermanent​Delete` | boolean | Optional. Indicates whether the record is permanently deleted (`true`) or not (`false`). The default value is `false`. |

## Usage

Use this action to delete one or more records from a context instance. By default, records are soft deleted. To permanently delete the records, set `isPermanentDelete` to `true`.

## Example

**POST**

: 

This sample request is for the Delete Context Records action.

```
{
  "inputs": [
    {
      "contextId": "0000000a07da091002517526756248297be68492e6b442e8ad80182d518e45aa",
      "dataPaths": [
        { "dataPath": ["001xx000003GbMhAAK", "003xx000004Wia5AAC"] }
      ],
      "isPermanentDelete": false
    }
  ]
}
```

This sample response is for the Delete Context Records action.

```
[
  {
    "actionName": "deleteContextRecords",
    "errors": null,
    "isSuccess": true,
    "outputValues": {}
  }
]
```

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/actions-obj-delete-context-records.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
