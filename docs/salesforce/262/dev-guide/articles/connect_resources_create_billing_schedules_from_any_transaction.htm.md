---
page_id: connect_resources_create_billing_schedules_from_any_transaction.htm
title: Create Standalone Billing Schedules (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_create_billing_schedules_from_any_transaction.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-06-09
---

# Create Standalone Billing Schedules (POST)

Generate billing schedules from any internal or external transaction
by using context service.

You can create a billing schedule from any sObject such as WorkOrder, Cart, Order,
Opportunity, and insurance policy. Or, you can also generate billing schedules from order
items.

The Create Standalone Billing Schedules (POST) API uses the StandaloneBillingContext context
definition to hydrate the context of the transaction. The context definition
includes these mappings.

- The TransactionMapping maps the fields of the transaction to the attributes of the
  Transaction node.
- The BSGEntitiesMapping maps the attributes of the Billing Schedule node, the Billing
  Schedule Group node, and Billing Schedule Group Relationship node to the fields of the
  corresponding Salesforce objects.

For the StandaloneBillingContext context definition to hydrate all the required data, transaction
data for the mandatory context tags are required. Here are the topics that mention
the mandatory and optional tags, sample transaction details, and sample payloads for
various types of transactions.

- [One-Time New Sale Transaction](./connect_requests_billing_schedule_input_for_one_time_new_sale.htm.md "Understand the required values and key considerations before you create a billing schedule for a new sale transaction with the OneTime selling model type.")
- [Term-Defined New Sale
  Transaction](./connect_requests_billing_schedule_input_for_termed_new_sale.htm.md "Understand the required values and key considerations before you create a billing schedule for a new sale transaction with the TermDefined selling model type.")
- [Evergreen New Sale Transaction](./connect_requests_billing_schedule_input_for_evergreen_new_sale.htm.md "Understand the required values and key considerations before you create a billing schedule for a new sale transaction with the Evergreen selling model type.")
- [New Sale Transaction With
  Bundled Products](./connect_requests_billing_schedule_input_for_bundled_products_new_sale.htm.md "Understand the required values and key considerations before you create a billing schedule for a new sale transaction with bundled products.")
- [New Sale Transaction With
  Ramped Products](./connect_requests_billing_schedule_input_for_ramps_new_sale.htm.md "Understand the required values and key considerations before you create a billing schedule for a new sale transaction with ramped products.")
- [New Sale Transaction With Usage
  Products](./connect_requests_billing_schedule_input_for_usage_new_sale.htm.md "Understand the required values and key considerations before you create a billing schedule for a new sale transaction with usage-based products.")
- [Amended Transaction](./connect_requests_billing_schedule_input_for_amendment.htm.md "Learn how amendments update quantity, price, and end date in billing schedules along with delta-only price transactions and billing-frequency changes at the billing schedule level.")
- [Renewal Transaction](./connect_requests_billing_schedule_input_for_renewal.htm.md "Create a renewal billing schedule for termed subscriptions that continues without a gap, starting the day after the current billing schedule group ends and running for the same term length.")
- [Early Renewal
  Transaction](./connect_requests_billing_schedule_input_for_early_renewal.htm.md "Early Renewal ends the current term at an effective date and starts a renewed term to a new end date, creating two billing schedules in one request. The request creates a negative segment for the remaining original term and a positive segment for the renewal term.")
- [Canceled
  Transaction](./connect_requests_billing_schedule_input_for_cancellation.htm.md "Cancel an entire billing schedule from a specified date. Specify only the cancellation date and billing schedule group identifier. The API computes the logic to split the cancellation across overlapping billing schedules and creates one cancel transaction per segment.")

Special Access Rules
:   This API is available with the Revenue Cloud Billing license.

Resource
:   ```
    /commerce/invoicing/standalone/billing-schedules/actions/create
    ```

Resource example
:   ```
    https://yourInstance.salesforce.com/services/data/v67.0/commerce/invoicing/standalone/billing-schedules/actions/create
    ```

Available version
:   64.0

HTTP methods
:   POST

Request body for POST
:   JSON example
    :   ```
        {
          "transactionDetails": "{\"nodeName\": [{\"id\":\"801Az00000aynKZIAY\", \"businessSobjectType\": \"Order\"}]}",
          "transactionContextDetails": {
            "contextDefinitionName": "StandaloneBillingContext",
            "intraContextCustomMappingName": "CustomContextMapping",
            "readContextMappingName": "OrderTransactionMapping",
            "saveContextMappingName": "BSGEntitiesMapping"
          }
        }
        ```

    Properties
    :   | Name | Type | Description | Required or Optional | Available Version |
        | --- | --- | --- | --- | --- |
        | `transaction​ContextDetails` | [Standalone Billing Schedule Metadata Input](./connect_requests_context_aware_standalone_billing_schedule_metadata_input.htm.md "Input representation of the metadata details to create a billing schedule. This representation includes the name of the context definition and context mapping along with the mapping details of the transaction, billing schedule, and billing schedule group.")[] | Details of the context definition and its mappings that are used to hydrate the transaction data and save it in the appropriate Billing fields. | Required | 64.0 |
        | `transaction​Details` | String | Input JSON data that includes the ID of the transaction record for which the billing schedule must be created and other additional transaction details.  The API request supports a single mapping ID. You can send separate requests for line items and line details by using their respective mapping IDs. However, this approach can result in duplicate billing schedules for the same line items and line details. | Required | 64.0 |

Response body for POST
:   [Context-Aware Billing
    Schedule](./connect_responses_context_aware_billing_schedule_output.htm.md "Output representation of the context-aware billing schedule.")

#### See Also

- [Salesforce Help: Context Service](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions.htm&language=en_US "Salesforce Help: Context Service - HTML (New Window)")
- [Industries Common Resources Developer Guide: Context Service](https://developer.salesforce.com/docs/atlas.en-us.262.0.industries_reference.meta/industries_reference/context_service_overview.htm "Industries Common Resources Developer Guide: Context Service - HTML (New Window)")
- [BillingScheduleGroup](https://developer.salesforce.com/docs/./sforce_api_objects_billingschedulegroup.htm.md "BillingScheduleGroup - HTML (New Window)")
