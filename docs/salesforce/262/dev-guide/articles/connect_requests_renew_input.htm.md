---
page_id: connect_requests_renew_input.htm
title: Renewal Input
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_requests_renew_input.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Transaction Management
parent_page: qoc_api_requests.htm
fetched_at: 2026-06-09
---

# Renewal Input

Input representation of the details of the request to initiate the renewal of an
asset.

JSON example
:   ```
    {
      "assetIds": [
        "02iSG0000003NMhYAM",
        "02iSG0000006DvSYAU"
      ],
      "contractId": "800SG00000CFpepYAD",
      "opportunityId": "006SG000004W5tVYAS",
      "outputRecordId": "801SG00000DX1jWYAT",
      "outputRecordType": "Quote",
      "renewalEndDate": "2024-10-03T23:59:59",
      "renewalStartDate": "2023-10-04T00:00:00"
    }
    ```

Properties
:   | Name | Type | Description | Required or Optional | Available Version |
    | --- | --- | --- | --- | --- |
    | `assetIds` | String[] | IDs of the assets that you want to renew. | Required | 62.0 |
    | `contractId` | String | ID of the Contract record that you want to sync with the renewal of the Quote or Order record. | Optional | 62.0 |
    | `opportunity​Id` | String | ID of the Opportunity record that you want to sync with the renewal quote. | Optional | 62.0 |
    | `output​RecordId` | String | ID of the Quote or Order record that you want to renew. | Optional | 62.0 |
    | `output​RecordType` | String | Type of renewal record that you want to create. | Required | 62.0 |
    | `renewal​EndDate` | String | End date of the renewal process for the assets. | Optional | 62.0 |
    | `renewal​StartDate` | String | Start date of the renewal process for the assets. Required for early asset renewals and renewing expired assets, using today’s date or a future date. | Optional | 62.0 |
