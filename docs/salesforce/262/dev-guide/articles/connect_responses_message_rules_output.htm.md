---
page_id: connect_responses_message_rules_output.htm
title: Message Rules
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_message_rules_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: connect_responses_config_rule_output.htm
fetched_at: 2026-06-09
---

# Message Rules

Output representation of the details of the message rules.

JSON example
:   ```
    {
      "message": "Constraints is running for laptop",
      "messageType": "Info",
      "primaryRecordId": "0QLxx0000004CU0GAM",
      "relatedRecordId": "0QLxx0000004CU1GAM"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `message` | String | List of message strings to display to the user. | Small, 67.0 | 67.0 |
| `messageType` | String | Severity level of the message. Valid values are:   - `INFO` - `WARNING` - `ERROR` | Small, 67.0 | 67.0 |
| `primaryRecordId` | String | ID of the primary sales transaction item record. | Small, 67.0 | 67.0 |
| `relatedRecordId` | String | ID of the related record. | Small, 67.0 | 67.0 |
