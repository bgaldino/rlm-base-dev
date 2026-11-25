---
page_id: connect-responses-configurator-message-output
title: Configurator Message
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-configurator-message-output.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Product Configurator
parent_page: product-configurator-business-apis-responses
legacy_page_id: connect_responses_configurator_message_output.htm
fetched_at: 2026-11-25
---

# Configurator Message

Output representation of the messages of a product configurator.

## JSON Example

```
{
  "messages": {
    "0Q0xx0000004CDsCAM": [
      {
        "message": "This is a quote with warranty",
        "messageType": "Info",
        "category": "ConfigurationRules",
        "primaryRecordId": "0Q0xx0000004CDsCAM"
      },
      {
        "message": "It is a group 1C9xx0000004CCGCA2",
        "messageType": "Warning",
        "category": "ConfigurationRules",
        "primaryRecordId": "0Q0xx0000004CDsCAM",
        "groupByValue": "1C9xx0000004CCGCA2"
      },
      {
        "message": "We're in group virtual bundle",
        "messageType": "Warning",
        "category": "ConfigurationRules",
        "primaryRecordId": "0Q0xx0000004CDsCAM",
        "groupByValue": "1C9xx0000004CCGCA2"
      },
      {
        "message": "It is a group 1C9xx0000004CCOCA2",
        "messageType": "Warning",
        "category": "ConfigurationRules",
        "primaryRecordId": "0Q0xx0000004CDsCAM",
        "groupByValue": "1C9xx0000004CCOCA2"
      },
      {
        "message": "We're in group virtual bundle",
        "messageType": "Warning",
        "category": "ConfigurationRules",
        "primaryRecordId": "0Q0xx0000004CDsCAM",
        "groupByValue": "1C9xx0000004CCOCA2"
      }
    ],
    "stiId-Laptop1": [
      {
        "message": "Only laptop",
        "messageType": "Info",
        "category": "ConfigurationRules",
        "primaryRecordId": "0Q0xx0000004CDsCAM",
        "relatedRecordId": "stiId-Laptop1"
      }
    ]
  }
}
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `category` | String | Category or type of the error message. Valid values are `ArcResolutionService`, `ArcValidationService`, `BundleValidation`, `ConfigurationRules`, or `Pricing`. | Small, 60.0 | 60.0 |
| `group​ByValue` | String | Specifies the value from Constraint Modeling Language rule action details. | Small, 67.0 | 67.0 |
| `message` | String | Message that contains the error details. | Small, 60.0 | 60.0 |
| `message​Type` | String | Type of error message. Valid values are `Error`, `Info`, or `Warning`. | Small, 60.0 | 60.0 |
| `primary​RecordId` | String | Primary record ID that contains the error. | Small, 60.0 | 60.0 |
| `related​RecordId` | String | Related record ID for the error, if any. | Small, 60.0 | 60.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-responses-configurator-message-output.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
