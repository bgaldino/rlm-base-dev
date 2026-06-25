---
page_id: connect_responses_current_value.htm
title: Current Value
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_current_value.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_responses.htm
fetched_at: 2026-06-25
---

# Current Value

Output representation of the current value of the guardrail at a row level.

```
{
  "values": {
    "currentValue": "50"
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `currentValue` | String | Current value at a row-level. | Small, 63.0 | 63.0 |
|  | String | Unique identifier name of the sObject that the current value is provided from. | Small, 63.0 | 63.0 |
