---
page_id: sforce_api_objects_paymentretryruleset.htm
title: PaymentRetryRuleSet
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_paymentretryruleset.htm
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
section: Billing
parent_page: billing_std_objects_parent.htm
fetched_at: 2026-11-23
---

# PaymentRetryRuleSet

Represents the payment retry rule definition that defines how failed payments are retried based on the error codes across various retry categories. This object is available in API version 66.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### CanUseAltrnPaymentMethod

- **Type**: boolean
- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update
- **Description**: Indicates whether an alternate payment method can be used on the last retry of the failed payment schedule item (`true`) or not (`false`). When set to `true`, the mostly recently added payment method is used to retry payments on the failed payment schedule items.

The default value is `false`.

### DefaultIntervalUnit

- **Type**: picklist
- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update
- **Description**: The unit of time after which a payment batch run must retry the failed payments. The related payment retry rules inherit this value by default.

Valid values are `Days`, `Hours`, or `Minutes`.

### DefaultIntervalValue

- **Type**: string
- **Properties**: Create, Filter, Group, Sort, Update
- **Description**: The single or comma-separated numeric values, after which the payment batch run must retry the failed payments. The related payment retry rules inherit this value by default.

### DefaultMaximumRetryCount

- **Type**: int
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The maximum number of retries on the failed payment records. The related payment retry rules inherit this value by default.

### DefaultRetryIntervalType

- **Type**: picklist
- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update
- **Description**: Specifies whether the payment retry rule set must be applied to the failed payment records at fixed or staggered intervals of time. The related payment retry rules inherit this value by default.

Valid values are `Fixed` or `Staggered`.

### Description

- **Type**: string
- **Properties**: Create, Filter, Group, Nillable, Sort, Update
- **Description**: The description of the business details for the payment retry rule set.

### IsDefaultRuleSet

- **Type**: boolean
- **Properties**: Create, Defaulted on create, Filter, Group, Sort, Update
- **Description**: Indicates whether the payment retry rule must be set as default for the org (`true`) or not (`false`).

The default value is `false`.

### LastReferencedDate

- **Type**: dateTime
- **Properties**: Filter, Nillable, Sort
- **Description**: The timestamp when the current user last accessed the payment retry rule set record.

### LastViewedDate

- **Type**: dateTime
- **Properties**: Filter, Nillable, Sort
- **Description**: The timestamp when the current user last viewed the payment retry rule set record.

### Name

- **Type**: string
- **Properties**: Create, Filter, Group, idLookup, Sort, Update
- **Description**: The user-specified name for the payment retry rule set.

### Status

- **Type**: picklist
- **Properties**: Create, Filter, Group, Restricted picklist, Sort, Update
- **Description**: Specifies the status of the payment retry rule set.

Valid values are `Active` or `Draft`.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/sforce_api_objects_paymentretryruleset.htm)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
