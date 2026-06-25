---
page_id: connect_requests_data_mapper_execute_input_data.htm
title: Data Mapper Execute Input Data
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_data_mapper_execute_input_data.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_data_mapper_apis_requests.htm
fetched_at: 2026-06-25
---

# Data Mapper Execute Input Data

Input representation of the list of custom data for the execution of the data
mapper.

JSON example
:   ```
    {
      "inputs": [
        {
          "Name": "Get Account Details"
        }
      ]
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `inputs` | String[] | List of configuration details for executing the data mappers. | Required | 64.0 |
