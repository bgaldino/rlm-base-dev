---
page_id: connect-resources-context-definition-id
title: Context Definition Id (GET, PATCH, DELETE)
source_url: https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-definition-id.html
release: 264
release_name: Winter '27
deliverable: industries_reference
api_version: 68.0
section: Context Service
parent_page: context-service-context-definition-management
legacy_page_id: connect_resources_context_definition_id.htm
fetched_at: 2026-11-25
---

# Context Definition Id (GET, PATCH, DELETE)

Query, update, and delete a context definition using an ID.

## Resource

```
/connect/context-definitions/{contextDefinitionId}
```

The {contextDefinitionId} parameter is the ID of the context definition.

## Example for GET

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-definitions/{contextDefinitionId}
```

{yourInstance} is the domain name of your Salesforce instance.

## Example for PATCH

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-definitions/{contextDefinitionId}
```

## Example for DELETE

```
https://{yourInstance}.salesforce.com/services/data/v59.0/connect/context-definitions/{contextDefinitionId}
```

## Available Version

59.0

## Requires Chatter

No

## HTTP Methods

GET, PATCH, DELETE

## Response Body for GET

[Context Definition Output](./connect-responses-context-definition.md)

## Request Body for PATCH

### JSON Example

```
{
"definition": "Example Defintion patch",
"description": "Example Description patch"
}
```

## Response Body for PATCH

[Context Definition Information](./connect-responses-context-definition-info.md)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/industries/industries-common-dev/guide/connect-resources-context-definition-id.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
