---
page_id: dynamic_revenue_orchestrator_integration_definition_for_standard_fulfillment_provider.htm
title: Integration Definition for Standard Fulfillment Provider
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/dynamic_revenue_orchestrator_integration_definition_for_standard_fulfillment_provider.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Dynamic Revenue Orchestrator
parent_page: dynamic_revenue_orchestrator_default_order_fulfillment_provider.htm
fetched_at: 2026-06-09
---

# Integration Definition for Standard Fulfillment Provider

Use supported attribute values of an integration definition for a Standard Fulfillment
Provider to implement features as per your requirement.

The Standard Fulfillment Provider supports these attribute values.

![Integration Definition for Standard Fulfillment Provider](/docs/resources/img/en-us/262.0?doc_id=dev_guides%2Frev_lifecycle_mgmt%2Fdynamic_revenue_orchestrator%2Fimages%2Fdynamic_revenue_orchestrator_integration_definition_standard_fulfillment_provider.png&folder=revenue_lifecycle_management_dev_guide)

| Attribute Name | Description |
| --- | --- |
| Named Credentials | API name of the associated named credentials. |
| Path | Additional string that's added to the URL specified in the named credential endpoint. |
| Timeout (ms) | Number of milliseconds to set as a timeout parameter for the HTTP connection. |
| Callback URI | Attribute used by a third party as the callback to process steps in case of a async callout. Additionally, this attribute also indicates these scenarios.  - The configured callout is an async callout. - If callback URI is defined, then it's included as the `ResponseUri` parameter value in the default payload   for Standard Fulfillment Provider. For example, a `ResponseUri` parameter value as `/services/apexrest/async/callout`. - The executor expects 202 response code from the remote destination. - The 202 response code keeps the Fulfillment Step state as Running whereas 200   response code completes it. |
| Input Processor | `Type_Subtype` or `Id` of OmniProcess to process the input payload. |
| Output Processor | `Type_Subtype` or `Id` of OmniProcess to process the output payload. |
| Item Encoding Style | Required.  Encoding style for fulfillment transaction items and sales transaction items. Valid values are:   - `Flat`—Includes a list of fulfillment   transaction items and sales transaction items without any hierarchy details in the   payload. - `Structure`—Includes a list of all   child line items if the step's source line item has a hierarchy of line items   associated with it. If item encoding style is configured as `Structure` on a fulfillment order line item or a   sales transaction item, then the payload contains the details of the line item   that the fulfillment order line item or sales transaction item is decomposed   from.  If the fulfillment order line item or sales transaction item is   decomposed from the root of a bundle order line item or sales transaction item,   then the payload contains the entire order line item or sales transaction item   bundle structure.   The default value is `Flat`. |
| Attribute Encoding Style | Required.  Generates the payload for attributes based on the specified encoding style. Valid values are:   - `Flat`—Includes specific details in   key-value pair format that doesn't include granular details of attributes. - `Structure`—This payload structure   includes granular details of attributes.   The default value is `Structure`. |
| Send Empty Attributes | If this checkbox is selected, the request payload includes empty attribute values wherever applicable. |
| Send Payload | If this checkbox is selected, a default request payload is generated to optimize processing performance. If this checkbox isn't selected, a value for the input processor is required. |
