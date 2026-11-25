---
page_id: connect-resources-context-definition-upgrades
title: Context Definition Upgrade (PATCH)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-definition-upgrades.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-context-definition-management
legacy_page_id: connect_resources_context_definition_upgrades.htm
fetched_at: 2026-11-25
---

# Context Definition Upgrade (PATCH)

Upgrade a context definition. Once an extended definition is created from a base standard definition, use this API to reflect any updates made to the base standard definition in the extended definition.

## Resource

```
/connect/context-definitions/upgrades
```

## Example for PATCH

```
https://{yourInstance}.salesforce.com/services/data/v64.0/connect/context-definitions/upgrades
```

{yourInstance} is the domain name of your Salesforce instance.

## Available Version

64.0

## HTTP Methods

PATCH

## Request Body for PATCH

### JSON Example

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

### Properties

- 
- 
- 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `contextDefinitionId` | String | ID of this context definition to be upgraded. | Required | 64.0 |
| `upgradeMode` | String | The upgrade mode enum. Possible values are:*Sync**Preview**Override* The default value is *Sync*. | Optional | 64.0 |

## Response Body for PATCH

[Context Definition Information](./connect-responses-context-definition-info.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-definition-upgrades.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
