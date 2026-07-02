---
page_id: connect_requests_decision_matrix_row_input.htm
title: Decision Matrix Row Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_decision_matrix_row_input.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_apis_requests_1.htm
fetched_at: 2026-06-25
---

# Decision Matrix Row Input

Input representation of the information required to add, update, or
delete rows in a decision matrix version.

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `action` | String | Type of action you want to perform on a row. Possible values are:  - `delete` - `update` | Required Note Note Leave this field blank if you’re adding a row in a decision matrix version. | 53.0 |
    | `id` | String | The ID of the row record to be updated or deleted. | Required Note Note Leave this field blank if you’re adding a row to a decision matrix version. | 53.0 |
    | `name` | String | Name of the row. | Optional | 53.0 |
    | `rowData` | Map<String, Object> | The key-value pair for the row. All column values are required for update and delete operations. | Required | 53.0 |
