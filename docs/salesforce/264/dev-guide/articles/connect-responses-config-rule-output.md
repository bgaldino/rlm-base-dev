---
page_id: connect-responses-config-rule-output
title: Configuration Rule Response
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-config-rule-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: product-configurator-business-apis-responses
legacy_page_id: connect_responses_config_rule_output.htm
fetched_at: 2026-11-25
---

# Configuration Rule Response

Output representation of the details of the configuration rule response.

## JSON Example

```
{
  "errors": [],
  "messageRules": [
    {
      "message": "You have a 128GB LRDIMM QLI",
      "messageType": "error",
      "primaryRecordId": "0Q0VW000000z8yN0AQ"
    },
    {
      "message": "You have a 16GB RDIMM QLI",
      "messageType": "warning",
      "primaryRecordId": "0Q0VW000000z8yN0AQ"
    },
    {
      "message": "You have a 32GB RDIMM QLI",
      "messageType": "info",
      "primaryRecordId": "0Q0VW000000z8yN0AQ"
    },
    {
      "message": "128GB LRDIMM disables 16GB RDIMM",
      "messageType": "info",
      "primaryRecordId": "0Q0VW000000z8yN0AQ"
    },
    {
      "message": "Additional API disables Additional API Gov",
      "messageType": "info",
      "primaryRecordId": "0Q0VW000000z8yN0AQ"
    },
    {
      "message": "Disable All other API Products",
      "messageType": "info",
      "primaryRecordId": "0Q0VW000000z8yN0AQ"
    },
    {
      "message": "32GB RDIMM disables 128GB LRDIMM",
      "messageType": "info",
      "primaryRecordId": "0Q0VW000000z8yN0AQ"
    },
    {
      "message": "API Access Requests AEH disables Additional API Prod",
      "messageType": "info",
      "primaryRecordId": "0Q0VW000000z8yN0AQ"
    }
  ],
  "productRecommendationRules": [
    {
      "message": "32GB RDIMM recommends 16GB RDIMM",
      "productIds": [
        "01tVW000003l7uaYAA"
      ],
      "recordType": "Type",
      "referenceId": "0Q0VW000000z8yN0AQ"
    },
    {
      "message": "32GB RDIMM recommends 64GB RDIMM",
      "productIds": [
        "01tVW000003l7v6YAA"
      ],
      "recordType": "Type",
      "referenceId": "0Q0VW000000z8yN0AQ"
    }
  ],
  "success": true,
  "transactionContextId": "0000000r25tq18g00291775730228818e689c3c5756e409fb3f886f68937ab13",
  "visibilityRules": [
    {
      "message": "128GB LRDIMM disables 16GB RDIMM",
      "productIds": [
        "01tVW000003l7uaYAA"
      ],
      "scope": "virtual",
      "target": "product",
      "type": "disable"
    },
    {
      "message": "Additional API disables Additional API Gov",
      "productIds": [
        "01tVW000003l7tzYAA"
      ],
      "scope": "virtual",
      "target": "product",
      "type": "disable"
    },
    {
      "message": "Disable All other API Products",
      "productIds": [
        "01tVW000003l7u0YAA",
        "01tVW000003l7u1YAA"
      ],
      "scope": "virtual",
      "target": "product",
      "type": "disable"
    },
    {
      "message": "32GB RDIMM disables 128GB LRDIMM",
      "productIds": [
        "01tVW000003l7v5YAA"
      ],
      "scope": "virtual",
      "target": "product",
      "type": "disable"
    },
    {
      "message": "API Access Requests AEH disables Additional API Prod",
      "productIds": [
        "01tVW000003l7u1YAA"
      ],
      "scope": "virtual",
      "target": "product",
      "type": "disable"
    }
  ]
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Config Rule Errors](./connect-responses-config-rule-errors-output.md)[] | List of error messages from the configuration rule evaluation, if any. | Small, 67.0 | 67.0 |
| `message​Rules` | [Message Rules](./connect-responses-message-rules-output.md)[] | List of message rules that were evaluated during configuration. | Small, 67.0 | 67.0 |
| `product​Recommendation​Rules` | [Product Recommendation Rules](./connect-responses-product-recommendation-rules-output.md)[] | List of product recommendation rules that were evaluated during configuration. | Small, 67.0 | 67.0 |
| `success` | Boolean | Indicates whether the API request is successful (`true`) or not (`false`). | Small, 67.0 | 67.0 |
| `transaction​ContextId` | String | ID of the transaction context for this configuration rule evaluation. | Small, 67.0 | 67.0 |
| `visibility​Rules` | [Visibility Rules](./connect-responses-visibility-rules-output.md)[] | List of visibility rules that were evaluated during configuration. | Small, 67.0 | 67.0 |

- 

**[Configuration Rule Errors](./connect-responses-config-rule-errors-output.md)**

Output representation of the error details, if applicable, when you run config rules.

- 

**[Message Rules](./connect-responses-message-rules-output.md)**

Output representation of the details of the message rules.

- 

**[Product Recommendation Rules](./connect-responses-product-recommendation-rules-output.md)**

Output representation of the details of the product recommendation rules.

- 

**[Visibility Rules](./connect-responses-visibility-rules-output.md)**

Output representation of the details of the visibility rules.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-config-rule-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
