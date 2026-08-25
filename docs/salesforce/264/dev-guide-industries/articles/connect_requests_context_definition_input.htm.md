---
page_id: connect_requests_context_definition_input.htm
title: Context Definition Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_context_definition_input.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-08-24
---

Note: This release is in preview. Features described here don’t become generally available until the latest general availability date that Salesforce announces for this release. Before then, and where features are noted as beta, pilot, or developer preview, we can’t guarantee general availability within any particular time frame or at all. Make your purchase decisions only on the basis of generally available products and features.

# Context Definition Input

Input representation of the context definitions in an expression
      set.

**Root XML tag**

: `<ContextDefinitionInput>`

**JSON example**

: 
            

```

  "contextDefinitionList": {
      "contextDefinitions":[{
      "id":"11Oxx0000006PcLEAU"
      }]
  }
```

          

**Properties**

: 

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `id` | String | ID of the context definition. | Required | 58.0 |
| `name` | String | Developer name of the context definition. | Optional | 58.0 |
