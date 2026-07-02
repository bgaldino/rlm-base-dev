---
page_id: connect_requests_integration_procedure_service_run_options.htm
title: Integration Procedure Service Run Options
source_url: https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/connect_requests_integration_procedure_service_run_options.htm
release: 262
release_name: Summer '26
deliverable: industries_reference
section: Omnistudio
parent_page: omnistudio_integration_procedure_apis_requests.htm
fetched_at: 2026-06-25
---

# Integration Procedure Service Run Options

Input representation of the optional parameters to customize and refine the execution of
the integration procedure.

JSON example
:   ```
    {
      "options": {
        "ignoreCache": false,
        "resetCache": true
      }
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `chainable` | Boolean | Indicates whether the integration procedure is executed in multiple chained calls (`true`) or as a single call (`false`). If the `chainable` property is set to `true`, the integration procedure automatically splits into smaller, sequentially executed pieces to avoid exceeding Salesforce governor limits or configured timeout thresholds.  The default value is `false`. | Optional | 64.0 |
    | `ignoreCache` | Boolean | Indicates whether to ignore the cache during the execution of the integration procedure (`true`) or not (`false`). The default value is `false`. | Optional | 64.0 |
    | `isDebug` | Boolean | Indicates whether to display the debugging details in the response (`true`) or not (`false`). The default value is `false`. | Optional | 64.0 |
    | `queueable​Chainable` | Boolean | Indicates whether the integration procedure executes the multiple chained calls asynchronously in the background as a queueable job (`true`) or not (`false`). The default value is `false`. | Optional | 64.0 |
    | `resetCache` | Boolean | Indicates whether to reset the cache during the execution of the integration procedure (`true`) or not (`false`). If set to `true`, data will be fetched from the database instead of the cache.  The default value is `false`. | Optional | 64.0 |
    | `shouldSend​LegacyResponse` | Boolean | Indicates whether response is displayed in the legacy Apex object format (`true`) or not (`false`). The default value is `false`. | Optional | 64.0 |
    | `useFuture` | Boolean | Indicates whether the integration procedure should run asynchronously as a fire-and-forget Apex job without returning a response (`true`) or not (`false`). The default value is `false`. | Optional | 64.0 |
    | `useQueueable` | Boolean | Indicates whether the integration procedure should run asynchronously by using a queueable Apex job that returns a job ID in the response (`true`) or not (`false`). The default value is `false`. | Optional | 64.0 |
    | `useQueueable​ApexRemoting` | Boolean | Indicates whether to run the operation in a queueable Apex job with no chaining (`true`) or not (`false`). The default value is `false`. | Optional | 64.0 |
    | `vlcApex​Response` | Boolean | Indicates whether the response payload must be displayed (`true`) or not (`false`). If set to `true`, the response payload is displayed that contains the fields, such as `vlcStatus`, `vlcIPData`, and `vlcMessage` to manage and track the execution state of a chainable process.  The default value is `false`. | Optional | 64.0 |
    | `vlcIPData` | String | Unique key that represents the saved execution state of a chainable integration procedure. This key is included in the subsequent calls to resume processing from where the execution of the integration procedure left off. | Optional | 64.0 |
    | `vlcMessage` | String | Contains error messages or additional information that's returned by the integration procedure. The value is `null` if there are no messages returned by the integration procedure. | Optional | 64.0 |
    | `vlcStatus` | String | Current status of the execution process of the integration procedure. | Optional | 64.0 |
