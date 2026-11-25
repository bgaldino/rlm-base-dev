---
page_id: sforce-api-objects-productsellingmodel
title: ProductSellingModel
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productsellingmodel.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Salesforce Pricing
parent_page: pricing-std-objects-parent
legacy_page_id: sforce_api_objects_productsellingmodel.htm
fetched_at: 2026-11-25
---

# ProductSellingModel

Defines one method by which a product can be sold; for example, as a one-time sale, an evergreen subscription, or a termed subscription. If the product is sold on subscription, this object defines the subscription’s term. A product can have multiple product selling models.  This object is available in API version 60.0 and later.

## Supported Calls

`create()`, `delete()`, `describeLayout()`, `describeSObjects()`, `getDeleted()`, `getUpdated()`, `query()`, `retrieve()`, `search()`, `undelete()`, `update()`, `upsert()`

## Fields

### LastReferencedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: Indicates when the user last referred to this record.

### LastViewedDate

- **Type**: dateTime

- **Properties**: Filter, Nillable, Sort

- **Description**: Indicates when the user last viewed this record.

### Name

- **Type**: string

- **Properties**: Create, Filter, Group, idLookup, Sort, Update

- **Description**: The name given to the product selling model.

### PricingTerm

- **Type**: int

- **Properties**: Create, Filter, Group, Nillable, Sort, Update

- **Description**: The number of pricing term units in the pricing term. Used with PricingTermUnit to define the length of the pricing term. For example, if PricingTermUnit is Months and this field is 1, the subscription is priced monthly.If the selling model is one-time, this field must be null.

### PricingTermUnit

- **Type**: picklist

- **Properties**: Create, Filter, Group, Nillable, Restricted picklist, Sort, Update

- **Description**: The unit of time used to define the pricing term. Used with PricingTerm to define the length of the pricing term. For example, if this field is Months and PricingTerm is 1, the subscription is priced monthly. If the selling model is one-time, this field must be null. Possible values are `Months`, `Quarterly`, `Semi-Annual`, or `Annual`

### SellingModelType

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: Indicates whether the product is sold as a one-time sale, an evergreen subscription, or a subscription with a defined term. Possible values are `Evergreen`, `OneTime`, or `TermDefined` The default value is `OneTime`.

### Status

- **Type**: picklist

- **Properties**: Create, Defaulted on create, Filter, Group, Restricted picklist, Sort, Update

- **Description**: The status of the product selling model. Possible values are `Active`, `Draft`, or `Inactive` The default value is `Draft`.

## Associated Objects

This object has the following associated objects. If the API version isn’t specified, they’re available in the same API versions as this object. Otherwise, they’re available in the specified API version and later.

[ProductSellingModelFeed](./sforce-api-associated-objects-feed.md): Feed tracking is available for the object.

[ProductSellingModelHistory](./sforce-api-associated-objects-history.md): History is available for tracked fields of the object.

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/sforce-api-objects-productsellingmodel.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
