---
page_id: connect_responses_calculation_procedure_output.htm
title: Calculation Procedure Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_calculation_procedure_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses.htm
fetched_at: 2026-06-25
---

# Calculation Procedure Output

Output representation of the expression sets details.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

This API has been deprecated as of API version 55.0.
In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

Sample Response
:   ```
    {
       "calculationProcedures" : [ {
          "id" : "0k0x0000000008ZAAQ",
          "description" : "Test calculation set",
          "name" : "Expression_Set_1"
       }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `description` | String | The description of the expression set. | Small, 53.0 | 53.0 |
| `id` | String | The ID of the expression set record. | Small, 53.0 | 53.0 |
| `name` | String | The name of the expression set. | Small, 53.0 | 53.0 |
