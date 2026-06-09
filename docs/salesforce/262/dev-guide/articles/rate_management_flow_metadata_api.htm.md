---
page_id: rate_management_flow_metadata_api.htm
title: Flow for Rate Management
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/rate_management_flow_metadata_api.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Rate Management
parent_page: rate_management_metadata_api_parent.htm
fetched_at: 2026-06-09
---

# Flow for Rate Management

Represents the metadata associated with a flow. With Flow, you can create an
application that takes users through a series of pages to query and update the records in the
database. You can also run logic and provide branching capability based on user input to build
dynamic applications.

## FlowActionCall

Rate Management exposes additional actionType values for the FlowActionCall metadata
type.

| Field Name | Field Type | Description |
| --- | --- | --- |
| actionType | InvocableActionType (enumeration of type string) | Required.  The action type. Additional valid values for Rate Management include:   - `invokeRatingService`—Invoke the rating service to rate the usage records. |
