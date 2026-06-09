---
page_id: connect_responses_get_configuration_instance_output.htm
title: Configuration Get Instance
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_responses_get_configuration_instance_output.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Product Configurator
parent_page: product_configurator_business_apis_responses.htm
fetched_at: 2026-06-09
---

# Configuration Get Instance

Output representation of the request to retrieve the configuration instance.

| Property Name | Type | Description | Filter Group and Version | Available Version |
| --- | --- | --- | --- | --- |
| `errors` | [Error Response](https://developer.salesforce.com/docs/atlas.en-us.262.0.chatterapi.meta/chatterapi/connect_responses_error_response.htm "HTML (New Window)") | List of errors, which contains an error code and a message. | Small, 60.0 | 60.0 |
| `success` | Boolean | Indicates whether the call was successful (`true`) not (`false`). | Small, 60.0 | 60.0 |
| `transaction` | Map<String, Object> | Transaction JSON payload representing an object in an external system that’s used to create a session. | Small, 60.0 | 60.0 |
