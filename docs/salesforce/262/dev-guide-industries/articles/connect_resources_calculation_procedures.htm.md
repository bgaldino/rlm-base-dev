---
page_id: connect_resources_calculation_procedures.htm
title: Calculation Procedures
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_calculation_procedures.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_resources.htm
fetched_at: 2026-06-25
---

# Calculation Procedures

Get a list of expression sets (also known as calculation procedure)
based on a search text. The API returns a maximum of ten expression set records that contain
the specified keyword.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

This API has been deprecated as of API version 55.0.
In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

Resource
:   ```
    /connect/omnistudio/evaluation-services
    ```

Example URI
:   ```
    /services/data/v53.0/connect/omnistudio/evaluation-services?searchKey=Expression
    ```

Available version
:   53.0

Requires Chatter
:   No

HTTP methods
:   GET

Request parameters for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `searchKey` | String | The user-entered search text to retrieve a list of expression sets. | Required | 53.0 |

Response body for GET
:   [Calculation Procedure List Output](./connect_responses_calculation_procedure_list_output.htm.md "Output representation of the expression set result list.")
