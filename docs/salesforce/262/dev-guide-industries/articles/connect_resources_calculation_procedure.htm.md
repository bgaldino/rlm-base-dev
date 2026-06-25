---
page_id: connect_resources_calculation_procedure.htm
title: Calculation Procedure
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_resources_calculation_procedure.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_resources.htm
fetched_at: 2026-06-25
---

# Calculation Procedure

Retrieve the details for a given expression set (also known as
calculation procedure) record.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

This API has been deprecated as of API version 55.0.
In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

Resource
:   ```
    /connect/omnistudio/evaluation-services/${id}
    ```

Example
:   ```
    /services/data/v53.0/connect/omnistudio/evaluation-services/0k0x000000000BQAAY
    ```

Available version
:   53.0

Requires Chatter
:   No

HTTP methods
:   GET

Response body for GET
:   [Calculation Procedure Detail Output](./connect_responses_calculation_procedure_detail_output.htm.md "Output representation of the expression set details.")
