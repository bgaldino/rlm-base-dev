---
page_id: apex_connectapi_input_ramp_option.htm
title: ConnectApi.RampOptionInputRepresentation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_ramp_option.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: transaction_management_apex_input_classes.htm
fetched_at: 2026-06-09
---

# ConnectApi.RampOptionInputRepresentation

Input representation of the ramp option details during an asset renewal.

This Apex class is used by the `rampOptionDetails`
Apex-defined input variable. See [Initiate Renewal Action](https://developer.salesforce.com/docs/./actions_obj_renew_assets.htm.md "HTML (New Window)").

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `durationInMonths` | Double | Maximum duration of all ramp segments. | Required | 67.0 |
| `segmentCount` | Double | Number of created ramp segments based on the specified duration. | Required if you specify `Custom` value for the `segmentType` property. | 67.0 |
| `segmentType` | `ConnectApi.RampSegmentType` | Type of ramp schedule. Valid values are:  - `Custom`—Specifies the number of   segments. The total duration is divided equally across segments. - `Yearly`—Creates 12-month segments.   If the total duration isn't a multiple of 12, the last segment covers the   remaining months.  If the duration divided by the number of months has a remainder, that segment is listed first as a prorated segment. | Required | 67.0 |
