---
page_id: connect_responses_calculation_procedure_variable_output.htm
title: Calculation Procedure Variable Output
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_responses_calculation_procedure_variable_output.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_responses.htm
fetched_at: 2026-06-25
---

# Calculation Procedure Variable Output

Details of the variables of an expression set.

![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

#### Note

This API has been deprecated as of API version 55.0.
In API version 55.0 and later, use the new [Business APIs in Business Rules Engine](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/business_rules_engine_connect_apis.htm).

Sample Response
:   ```
    {
          "dataType" : "Number",
          "name" : "var2"
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `dataType` | String | The data type of the variable. | Small, 53.0 | 53.0 |
| `name` | String | The name of the variable. | Small, 53.0 | 53.0 |
