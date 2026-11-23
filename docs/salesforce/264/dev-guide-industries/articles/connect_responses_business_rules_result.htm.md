---
page_id: connect_responses_business_rules_result.htm
title: Business Rules Results
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_business_rules_result.htm
release: 264
release_name: Winter '27
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_responses.htm
fetched_at: 2026-11-23
---

# Business Rules Results

Output representation of executing an expression set.

## JSON Example

```
{
  "outputs": [
    {
      "result": {
        "Premium": "1200",
        "Tax": "100"
      },
      "variables": {
        "age": "25",
        "state": "CA"
      },
      "error": {
        "stepId": "<stepId>",
        "errorMessage": "The rule is missing inputs: ['var1', 'var2'] and 3 more steps have 5 error"
      }
    },
    {
      "result": {
        "Premium": "2400",
        "Tax": "300"
      }
    },
    {
      "result": {
        "Premium": "500",
        "Tax": "25"
      }
    }
  ],
  "aggregationResults": {
    "result": {
      "TotalPremium": "4100",
      "TotalTax": "425"
    },
    "error": {
      "stepId": "<stepId>",
      "errorMessage": "The rule is missing inputs: ['var1', 'var2'] and 3 more steps have 5 error"
    }
  }
}
```

## Properties

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `aggregationResults` | [Business Rule Aggregation Results Output](./connect_responses_business_rule_aggregation_results_output.htm.md "Output representation of expression set results.") | The result of the aggregation step in an expression set. | Small, 55.0 | 55.0 |
| `outputs` | [Rule Result](./connect_responses_rule_result.htm.md "Output representation of the result of executing a single input in an expression set.")[] | List of outputs returned by an expression set. | Small, 55.0 | 55.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_business_rules_result.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
