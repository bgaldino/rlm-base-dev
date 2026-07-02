---
page_id: connect_responses_calculation_procedure_activation_output.htm
title: Calculation Procedure Activation Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_calculation_procedure_activation_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses.htm
fetched_at: 2026-06-25
---

# Calculation Procedure Activation Output

Output representation of the calculation procedure version record
activation.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

This API has been deprecated as of API version 55.0.
In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

JSON Response
:   ```
    {
       "code":"200",
       "isSuccess":true,
       "message":"Expression Set Version Activated",
       "versionId":"0k1xx00000000KzAAI"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `code` | String | The request response code. | Small, 53.0 | 53.0 |
| `isSuccess` | Boolean | Indicates whether the request is successful. | Small, 53.0 | 53.0 |
| `message` | String | The request response message. | Small, 53.0 | 53.0 |
| `versionId` | String | The ID of the activated calculation procedure version record. | Small, 53.0 | 53.0 |
