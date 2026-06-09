---
page_id: connect_requests_category_details_input.htm
title: Category Details Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_category_details_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Catalog Management
parent_page: product_discovery_api_requests.htm
fetched_at: 2026-06-09
---

# Category Details Input

Input representation of the request to get category details.

JSON example
:   ```
    {
      "correlationId": "9cbb9650-48c5-11ed-96d1-0afcf185843b",
      "userContext": {
          "accountId": "001xx0000000001AAA",
          "contactId": "003xx00000000D7AAI"
      }
    }
    ```

    This example shows a sample request to get category details with eligible
    promotions.

    ```
    {
      "correlationId": "9cbb9650-48c5-11ed-96d1-0afcf185843b",
      "userContext": {
        "accountId": "001xx0000000001AAA",
        "contactId": "003xx00000000D7AAI"
      },
      "usePromotions": true
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `additional​ContextData` | [Context Data Input](./connect_requests_context_data_input.htm.md "Input representation of the context data.") | Additional nodes that are added to the custom or default context definition. The maximum number of supported nodes is 10. | Optional | 60.0 |
    | `catalog​Id` | String | ID of the catalog. If the catalog ID is specified, then the API returns the list of offers from the catalog with the pricing details related to the catalog. | Optional | 60.0 |
    | `context​Definition` | String | API name of the custom context definition that’s sent for context creation. If this property isn’t specified, then the default context definition is used. | Optional | 60.0 |
    | `context​Mapping` | String | Default context mapping of the context definition. If a context mapping is specified, then the API checks whether the mapping belongs to the specified context definition to process the details for hydration. | Optional | 60.0 |
    | `customFields` | String[] | List of category fields to retrieve in the response. | Optional | 60.0 |
    | `correlation​Id` | String | Unique identifier value that’s attached to the requests and messages, and accepts references to a particular transaction or event chain. | Optional | 60.0 |
    | `enable​Qualification` | Boolean | Indicates whether to enable qualification rules for the categories (`true`) or not (`false`). The default value is `true`. The **Qualification Procedure** toggle from the Product Discovery Settings page from Setup overrides this property. For example, if the **Qualification Procedure** toggle is disabled, then setting the `enableQualification` property to `true` has no effect and the `qualificationContext` property in the API response isn’t returned. | Optional | 60.0 |
    | `filter` | [Filter Input](./connect_requests_filter_input.htm.md "Input representation of the request to filter records.") | Filters records based on supported criteria.  The supported property is `name`.  The supported operators are:   - `eq` - `in` - `contains` - `gt`—Specifies a greater than   criteria. Available from API version 63.0 and later for Number, Date, and   Datetime data types only. - `lt`—Specifies a less than criteria.   Available from API version 63.0 and later for Number, Date, and Datetime   data types only. - `gte`—Specifies a greater than or   equal to criteria. Available from API version 63.0 and later for Number,   Date, and Datetime data types only. - `lte`—Specifies a less than or equal   to criteria. Available from API version 63.0 and later for Number, Date,   and Datetime data types only.   If multiple criteria are specified, then the resultant criteria are combined by using the `and` operator. | Optional | 60.0 |
    | `qualification​Procedure` | String | API name of the custom qualification procedure that’s used for the qualification process. If this property isn’t specified, then the default qualification procedure is executed. | Optional | 60.0 |
    | `user​Context` | [User Context Input](./connect_requests_user_context_input.htm.md "Input representation of the details with the user context.") | User context details. For example, account ID or contact ID. | Optional | 60.0 |
    | `usePromotions` | Boolean | Indicates whether to fetch eligible promotions from Global Promotion Management (GPM) for the requested category and its products (`true`) or not (`false`). If Promotion feature is enabled in the org and this property isn't specified, then the default value is `true`. If the Promotion feature isn't enabled, the default value is `false`. | Optional | 66.0 |
