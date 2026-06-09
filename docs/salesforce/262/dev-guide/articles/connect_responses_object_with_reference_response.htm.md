---
page_id: connect_responses_object_with_reference_response.htm
title: Object Reference
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_object_with_reference_response.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_responses.htm
fetched_at: 2026-06-09
---

# Object Reference

Output representation of an sObject with a reference ID along with any potential
error.

Sample Response
:   ```
    {
      "referenceid": "refQuote",
      "record": {
        "attributes": {
          "type": "Quote",
          "method": "POST"
        },
        "quantity": "2"
      },
      "error": {
        "errorCode": "INVALID_API_INPUT",
        "message": "Reference Id format is irrelevant."
      }
    }
    ```

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `referenceId` | String | ID that identifies the specific Salesforce object that’s returned in the API response. | Small, 59.0 | 59.0 |
| `record` | Map<String, Object> | The sObject record data represented as a map of attribute names to their values. | Small, 59.0 | 59.0 |
| `error` | [https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/connect\_responses\_error\_response.htm](https://developer.salesforce.com/docs/atlas.en-us.262.0.chatterapi.meta/chatterapi/connect_responses_error_response.htm "HTML (New Window)")[] | Detailed information about any error associated with the sObject in the response. | Small, 59.0 | 59.0 |
