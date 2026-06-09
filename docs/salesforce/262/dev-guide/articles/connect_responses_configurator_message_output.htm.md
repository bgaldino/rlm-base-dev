---
page_id: connect_responses_configurator_message_output.htm
title: Configurator Message
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_configurator_message_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Configurator Message

Output representation of the messages of a product configurator.

JSON example
:   ```
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
| `category` | String | Category or type of the error message. Valid values are:   - `ArcResolutionService` - `ArcValidationService` - `BundleValidation` - `ConfigurationRules` - `Pricing` | Small, 60.0 | 60.0 |
| `group​ByValue` | String | Specifies the value from Constraint Modeling Language rule action details. | Small, 67.0 | 67.0 |
| `message` | String | Message that contains the error details. | Small, 60.0 | 60.0 |
| `message​Type` | String | Type of error message. Valid values are:   - `Error` - `Info` - `Warning` | Small, 60.0 | 60.0 |
| `primary​RecordId` | String | Primary record ID that contains the error. | Small, 60.0 | 60.0 |
| `related​RecordId` | String | Related record ID for the error, if any. | Small, 60.0 | 60.0 |
