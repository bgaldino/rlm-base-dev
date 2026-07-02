---
page_id: connect_responses_custom_type_details.htm
title: Custom Type Details
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_custom_type_details.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: dfdt_apis_responses.htm
fetched_at: 2026-06-25
---

# Custom Type Details

Output representation of the custom type details of the Omniscript elements.

JSON example
:   ```
              "customTypeDetails" : {
                "discoveryFramework": {
                    "questionText": "Can you provide more details about the transaction"
                }
              }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `discovery​Framework` | [OS Element Discovery Framework](./connect_responses_os_element_discovery_framework_output.htm.md "Output representation of the custom type details of the Omniscript elements for Discovery Framework.")[] | Custom type details for the Omniscript element for Discovery framework. | Small, 60.0 | 60.0 |
