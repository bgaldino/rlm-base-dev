---
page_id: connect_requests_context_definition_upgrade.htm
title: Context Definition Upgrade Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_definition_upgrade.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Context Service
parent_page: context_service_apis_requests.htm
fetched_at: 2026-11-23
---

# Context Definition Upgrade Input

Input representation of context definition upgrade.

## JSON Example

```
{
  "contextDefinitions": [
    {
      "contextDefinitionId": "11Oxx0000006PfZEAU",
      "upgradeMode": "Sync"
    }
  ]
}
```

## Properties

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinitionId` | String | ID of this context definition to be upgraded. | Required | 64.0 |
| `upgradeMode` | String | The upgrade mode enum. Possible values are:  - Sync - Preview - OverrideThe default value   is Sync. | Optional | 64.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_definition_upgrade.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
