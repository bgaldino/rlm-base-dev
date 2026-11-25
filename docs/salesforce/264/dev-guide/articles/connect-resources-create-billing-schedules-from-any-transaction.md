---
page_id: connect-resources-create-billing-schedules-from-any-transaction
title: Create Standalone Billing Schedules (POST)
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-create-billing-schedules-from-any-transaction.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Billing
parent_page: billing-business-apis-resources
legacy_page_id: connect_resources_create_billing_schedules_from_any_transaction.htm
fetched_at: 2026-11-25
---

# Create Standalone Billing Schedules (POST)

Generate billing schedules from any internal or external transaction by using context service.

You can create a billing schedule from any sObject such as WorkOrder, Cart, Order, Opportunity, and insurance policy. Or, you can also generate billing schedules from order items.

The Create Standalone Billing Schedules (POST) API uses the StandaloneBillingContext context definition to hydrate the context of the transaction. The context definition includes these mappings.

- The TransactionMapping maps the fields of the transaction to the attributes of the Transaction node.

- The BSGEntitiesMapping maps the attributes of the Billing Schedule node, the Billing Schedule Group node, and Billing Schedule Group Relationship node to the fields of the corresponding Salesforce objects.

For the StandaloneBillingContext context definition to hydrate all the required data, transaction data for the mandatory context tags are required. Here are the topics that mention the mandatory and optional tags, sample transaction details, and sample payloads for various types of transactions.

- [One-Time New Sale Transaction](./connect-requests-billing-schedule-input-for-one-time-new-sale.md)

- [Term-Defined New Sale Transaction](./connect-requests-billing-schedule-input-for-termed-new-sale.md)

- [Evergreen New Sale Transaction](./connect-requests-billing-schedule-input-for-evergreen-new-sale.md)

- [New Sale Transaction With Bundled Products](./connect-requests-billing-schedule-input-for-bundled-products-new-sale.md)

- [New Sale Transaction With Ramped Products](./connect-requests-billing-schedule-input-for-ramps-new-sale.md)

- [New Sale Transaction With Usage Products](./connect-requests-billing-schedule-input-for-usage-new-sale.md)

- [Amended Transaction](./connect-requests-billing-schedule-input-for-amendment.md)

- [Renewal Transaction](./connect-requests-billing-schedule-input-for-renewal.md)

- [Early Renewal Transaction](./connect-requests-billing-schedule-input-for-early-renewal.md)

- [Canceled Transaction](./connect-requests-billing-schedule-input-for-cancellation.md)

## Special Access Rules

This API is available with the Revenue Cloud Billing license.

## Resource

```
/commerce/invoicing/standalone/billing-schedules/actions/create
```

## Resource Example

```
https://{yourInstance}.salesforce.com/services/data/v68.0/commerce/invoicing/standalone/billing-schedules/actions/create
```

## Available Version

64.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
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

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `transaction​ContextDetails` | [Standalone Billing Schedule Metadata Input](./connect-requests-context-aware-standalone-billing-schedule-metadata-input.md)[] | Details of the context definition and its mappings that are used to hydrate the transaction data and save it in the appropriate Billing fields. | Required | 64.0 |
| `transaction​Details` | String | Input JSON data that includes the ID of the transaction record for which the billing schedule must be created and other additional transaction details. The API request supports a single mapping ID. You can send separate requests for line items and line details by using their respective mapping IDs. However, this approach can result in duplicate billing schedules for the same line items and line details. | Required | 64.0 |

## Response Body for POST

[Context-Aware Billing Schedule](./connect-responses-context-aware-billing-schedule-output.md)

**See Also**

- [Salesforce Help: Context Service](https://help.salesforce.com/s/articleView?id=ind.context_service_context_definitions.htm)

- [Industries Common Resources Developer Guide: Context Service](https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/context_service_overview.htm)

- [BillingScheduleGroup](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_billingschedulegroup.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/connect-resources-create-billing-schedules-from-any-transaction.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
