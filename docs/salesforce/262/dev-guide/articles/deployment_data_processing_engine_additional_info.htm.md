---
page_id: deployment_data_processing_engine_additional_info.htm
title: Data Processing Engine Additional Information
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/deployment_data_processing_engine_additional_info.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Revenue Cloud Deployment
parent_page: deployment_appendix_C.htm
fetched_at: 2026-06-09
---

# Data Processing Engine Additional Information

Get to know additional deployment information for Data Processing Engine in Revenue
Cloud.

## Deployment Considerations

- Data Processing Engine objects have `Draft` and
  `Active` states.
- The objects must be created in `Draft` state and
  activated later. The activation is done through API.
- Configuration can’t be changed after an object is updated to `Active` state.
- Set the state of the object to `Inactive` for any
  modifications, and then set the state to `Active`.

## Other Information

- Data Processing Engine has dependencies on these components.
  - CRM Analytics or Data Cloud
  - Bulk API
- You can deploy Data Processing Engine definitions from one organization to another. Both
  organizations must be on the same Salesforce release version.
