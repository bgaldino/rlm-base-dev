---
page_id: connect_resources_create_context.htm
title: Context Service (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_create_context.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Context Service
parent_page: runtime_context_intance_management.htm
fetched_at: 2026-06-25
---

# Context Service (POST)

Create new context records by submitting metadata and associated JSON data. After
validating the data, the system generates a new context ID. Context objects created using this
API apply only to a single request. They cannot be used to pass data across multiple
requests.

Resource
:   ```
    /connect/contexts
    ```

Example
:   ```
    https://yourInstance.salesforce.com/services/data/v66.0/connect/contexts
    ```

Available version
:   59.0

Requires Chatter
:   No

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "metadata": {
            "contextDefinitionId": "11Oxx0000006VjNEAU",
            "mappingId": "11jxx0000004Q83AAE"
          },
          "data": "{\"Order\":[{\"id\":\"TestOrder123\",\"businessObjectType\":\"Order\",\"Name\":\"Test Order\",\"Status\":\"SHIPPED\",\"AccountName\":\"Kroger\",\"OrderItems\":[{\"id\":\"TestOrderItem1\",\"businessObjectType\":\"OrderItem\",\"ProductName\":\"Coke\"},{\"id\":\"TestOrderItem2\",\"businessObjectType\":\"OrderItem\",\"ProductName\":\"Pepsi\"}]}]}"
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `data` | String | Payload containing context-specific information. | Required | 59.0 |
        | `metadata` | [Context MetaData Input](./connect_requests_context_meta_data_input.htm.md "Input representation of context metadata.") | Metadata information about context. | Required | 59.0 |

Response body for POST
:   [Context
    Info](./connect_responses_context_info.htm.md "Output representation containing detailed information about a context.")
