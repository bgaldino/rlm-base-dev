---
page_id: connect_resources_create_billing_schedules.htm
title: Create Billing Schedules for Orders (POST)
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_create_billing_schedules.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_business_apis_resources.htm
fetched_at: 2026-11-23
---

# Create Billing Schedules for Orders (POST)

Generate billing schedules for orders by using context service.

## Special Access Rules

The org must have the standard billing context definition with the target mapping. This context definition is available in orgs with Billing enabled. Additionally, you need the Create Billing Schedules From Billing Transactions API permission set and the Context Service Runtime permission set to use this API.

See these [requirements](https://help.salesforce.com/s/articleView?id=ind.billing_schedules_create.htm&language=en_US "HTML (New Window)") to learn more about the configuration prerequisites.

## Resource

```
/commerce/invoicing/billing-schedules/actions/create
```

## Resource Example

```
https://yourInstance.salesforce.com/services/data/v68.0/commerce/invoicing/billing-schedules/actions/create
```

## Available Version

62.0

## HTTP Methods

POST

## Request Body for POST

**JSON Example**

```
{
    "billingTransactionIds": [ "801xx000003H1H9AAK"]
}
```

**Properties**

| Name | Type | Description | Required or Optional | Available Version |
| --- | --- | --- | --- | --- |
| `billing​Transaction​Ids` | String[] | ID of the billing transaction. This property value is the ID of the order if the source of the billing request is for the Order object. If the order product associated with the specified order ID doesn't have an associated billing treatment ID, the API considers the default billing treatment ID. The generated billing schedule group has the default billing treatment ID. The API supports only one billing transaction ID in the input. | Required | 62.0 |

## Response Body for POST

[Context-Aware Billing Schedule](./connect_responses_context_aware_billing_schedule_output.htm.md "Output representation of the context-aware billing schedule.")

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/connect_resources_create_billing_schedules.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
