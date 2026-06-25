---
page_id: connect_resources_store_discovery_framework_structure.htm
title: Omniscript
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_store_discovery_framework_structure.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Discovery Framework
parent_page: dfdt_apis_resources.htm
fetched_at: 2026-06-25
---

# Omniscript

Get the discovery framework structure stored as OmniProcess.

Use this API to get the assessment form layout and submit the assessment data through any
custom-built UI. You can show the questionnaire form, capture assessment responses, and save
the assessment.

Resource
:   ```
    /connect/omniscript/omniScriptId
    ```

    The
    `omniScriptId` property is the ID of the Omniscript
    to get the discovery framework structure stored as an OmniProcess.

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v60.0/connect/omniscript/CreditCard_DisputeTransaction_English_1?customType=DiscoveryFramework
    ```

Available version
:   60.0

HTTP methods
:   GET

Request parameters for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `customType` | String | Custom type of Omniscript. For example, Discovery Framework. | Required | 60.0 |

Response body for GET
:   [Omniscript Output](./connect_responses_omniscript_output.htm.md "Output representation of the details of the Omniscript.")
