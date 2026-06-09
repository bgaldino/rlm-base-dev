---
page_id: connect_resources_retrieve_binding_object_details.htm
title: Binding Object Usage Details (GET)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_retrieve_binding_object_details.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Usage Management
parent_page: usage_management_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Binding Object Usage Details (GET)

Get details of grants, resources, rates, and any configured policies
for a specified binding object.

Use this API to display the details for a binding object during the selling journey.
Additionally, display the details after assetization on the selected binding objects.

The supported binding objects are Account, Contract, BindingObjectCustomExt, or Anchor Asset
that's not bound to a target.

Resource
:   ```
    /revenue/usage-management/binding-objects/bindingObjectId/actions/usage-details
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/revenue/usage-management/binding-objects/1BRxx0000004C9EGAU/actions/usage-details?effectiveDate=2025-08-07
    ```

Available version
:   65.0

HTTP methods
:   GET

Path parameter for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `bindingObjectId` | String | ID of the binding object. | Required | 65.0 |

Query parameter for GET
:   | Parameter Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `effectiveDate` | String | Date filter that's used to retrieve the grants, rates, and applicable policies as of the specified date in `yyyy-MM-dd` format. | Required | 65.0 |

Response body for GET
:   [Binding Object Usage
    Detail](./connect_responses_usage_detail_binding_object_output.htm.md "Output representation of the usage details of a binding object.")
