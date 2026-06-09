---
page_id: connect_requests_frequency_cadence_options.htm
title: Frequency Cadence Options
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_frequency_cadence_options.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_requests.htm
fetched_at: 2026-06-09
---

# Frequency Cadence Options

Input representation of the frequency cadence options for an invoice
scheduler.

JSON example
:   ```
      "frequencyCadenceOptions": {
            "recurringSubType" : "Every",
            "recursOn" : "First",
            "recursOnDay" : "Sunday",
            "shouldExcludeWkendAndHldy": true
        }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `recurring​Sub​Type` | String | Subtype of the recurring frequency for the invoice run. Valid values are:  - `Every`—Specifies if the   invoice scheduler must generate the invoices on a recurring frequency on a   specific cadence. Use this value to generate invoices on a specific day of   the month. For example, you can specify that the invoice scheduler must   generate the invoices every first Monday of the month. - `SpecificDate`—Specifies if   the invoice scheduler must generate the invoices on a recurring frequency   on a specific date. Use this value to generate invoices on a monthly basis   on a specific date. | Required if the `frequency​Cadence` property is set to `Monthly`. | 62.0 |
    | `recurs​On` | String | Cadence that specifies when the invoice scheduler must generate the invoices on a recurring frequency. For example, you can specify that the invoice scheduler must generate the invoices every first Monday of the month. Valid values are:  - `First` - `Second` - `Third` - `Fourth` - `Last` | Required if the `frequency​Cadence` property is set to `Monthly`. | 62.0 |
    | `recursOn​Date` | String | Date when the invoice scheduler must generate the invoices on a specific date. The supported values are:  - 1 through 28—Specify any date from 1 through 28. - `L`—Specifies that the invoice   scheduler must generate the invoices on the last day of the month. - `L-1`—Specifies that the   invoice scheduler must generate the invoices on the second to last day of   the month. - `L-2`—Specifies that the   invoice scheduler must generate the invoices on the third to last day of   the month. | Required if the `recurring​Sub​Type` property is set to `SpecificDate`. | 62.0 |
    | `recursOn​Day` | String | Day of the week when the invoice scheduler must generate the invoices on a recurring frequency. For example, you can specify that the invoice scheduler must generate the invoices every Monday or every first Monday of a month. Valid values are:  - `Sunday` - `Monday` - `Tuesday` - `Wednesday` - `Thursday` - `Friday` - `Saturday` | Required if the `frequency​Cadence` property is set to `Weekly` or `Monthly`. | 62.0 |
    | `should​Exclude​Wkend​AndHldy` | Boolean | Indicates whether to exclude weekends and holidays from the billing schedule (`true`) or not (`false`). | Required if the `frequency​Cadence` property is set to `Monthly`. | 62.0 |
