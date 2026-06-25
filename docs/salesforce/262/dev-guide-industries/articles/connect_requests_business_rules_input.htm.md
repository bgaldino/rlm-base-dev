---
page_id: connect_requests_business_rules_input.htm
title: Business Rules Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_business_rules_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Business Rules Engine
parent_page: expression_set_requests.htm
fetched_at: 2026-06-25
---

# Business Rules Input

Input representation of an expression set.

JSON example 1
:   ```
    {
      "inputs": [
        {
          "age": "25",
          "state": "CA",
          "PatientId": "001xx000003GYjnAAG"
        }
      ],
      "options": {
        "effectiveDate": "2022-12-03T10:15:30Z",
        "useDatesOnly": "true",
        "actionContextCode": "9QLxx0000004C92GAE",
        "explainabilitySpecName": "ES_One_Explainability"
      }
    }
    ```

JSON example 2
:   ```
    {
      "inputs": [
        {
          "age": "25",
          "state": "CA",
          "PatientId":"001xx000003GYjnAAG",
          "__actionContextCode":"001xx000003GYjnAAG"
        }
      ],
      "options": {
        "effectiveDate": "2022-12-03T10:15:30Z",
        "useDatesOnly": "true"
      }
    }
    ```

    ![Note](/docs/resources/img/en-us/262.0?doc_id=images%2Ficon_note.png&folder=industries_reference)

    #### Note

    You can use more than one `actionContextCode`
    for multiple sets of inputs, passed in a single API call.

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `inputs` | Map<String, Object>[] | List of inputs passed to an expression set. An input may contain multiple variables. Note Note - If the expression set uses a field alias as a variable, append Id to   the object alias to which the field alias belongs, and pass the ID of   the source object linked to the object alias. - If the expression set uses a context definition, append Id to the   context definition developer name and pass the context ID as the   value. | Required | 55.0 |
    | `options` | [Expression Set Options Input](./connect_requests_options.htm.md "Input representation of the options for executing an expression set.") | The options for executing an expression set. | Optional | 55.0 |
