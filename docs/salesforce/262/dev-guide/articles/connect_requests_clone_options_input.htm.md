---
page_id: connect_requests_clone_options_input.htm
title: Clone Options Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_clone_options_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-06-09
---

# Clone Options Input

Input representation of the options to clone a sales transaction.

JSON example
:   This is a sample request to clone all line items in a ramped group within a sales
    transaction.

    ```
    {
      "recordIds": ["0QLxx0000004CBYGA2"],
      "salesTransactionId": "0Q0xx0000004CE0CAM",
      "options": {
        "lineScope": "AllLines"
      }
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `recordTypeId` | String | ID of the record type related to the record to clone. | Optional | 65.0 |
    | `lineScope` | String | Specifies the scope for cloning a ramp segment. You can clone only the last ramp segment. This property determines which line items must be cloned and added to the cloned segment. Valid values are:   - `AllLines`—Specifies whether   all line items in a ramped group must be cloned. - `RampedLinesOnly`—Specifies   whether only the ramped line items must be cloned.   A segment identifier is created for the newly cloned line items, ensuring date continuity between the existing and cloned segment. | Optional | 65.0 |
