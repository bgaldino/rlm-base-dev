---
page_id: connect_responses_assets_arc_error.htm
title: ARC Base Error
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_assets_arc_error.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# ARC Base Error

Output representation of the error response related to the amendment, renewal,
or
cancellation of assets.

```
    "errors": [ 
        { 
            "errorCode": "REQUIRED_FIELD_MISSING",
            "errorMessage": "Specify a value for quantityChange, and try again."
        } 
    ]
```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `error​Code` | String | Code for the resultant error. | Big, 62.0 | 62.0 |
| `error​Message` | String | Error message for the resultant error. | Big, 62.0 | 62.0 |
