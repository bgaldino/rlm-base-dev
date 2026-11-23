---
page_id: apex_connectapi_input_ramp_option.htm
title: ConnectApi.RampOptionInputRepresentation
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_ramp_option.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: transaction_management_apex_input_classes.htm
fetched_at: 2026-11-23
---

# ConnectApi.RampOptionInputRepresentation

Input representation of the ramp option details during an asset renewal.

This Apex class is used by the `rampOptionDetails` Apex-defined input variable. See [Initiate Renewal Action](./actions_obj_renew_assets.htm.md "HTML (New Window)").

| Property | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `durationInMonths` | Double | Maximum duration of all ramp segments. | Required | 67.0 |
| `segmentCount` | Double | Number of created ramp segments based on the specified duration. | Required if you specify `Custom` value for the `segmentType` property. | 67.0 |
| `segmentType` | `ConnectApi.RampSegmentType` | Type of ramp schedule. Valid values are: `Custom`—Specifies the number of segments. The total duration is divided equally across segments; or `Yearly`—Creates 12-month segments. If the total duration isn't a multiple of 12, the last segment covers the remaining months. If the duration divided by the number of months has a remainder, that segment is listed first as a prorated segment. | Required | 67.0 |

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/apex_connectapi_input_ramp_option.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
