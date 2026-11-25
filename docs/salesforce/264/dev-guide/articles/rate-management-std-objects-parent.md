---
page_id: rate-management-std-objects-parent
title: Rate Management Standard Objects
source_url: https://developer.salesforce.com/docs/revenue/revenue-management/guide/rate-management-std-objects-parent.html
release: 264
release_name: Winter '27
deliverable: revenue_lifecycle_management_dev_guide
api_version: 68.0
section: Rate Management
parent_page: rate-management-overview
legacy_page_id: rate_management_std_objects_parent.htm
fetched_at: 2026-11-25
---

# Rate Management Standard Objects

The Rate Management data model provides objects and fields to manage rates and discounts for a product’s resource consumption.

- 

**[BindingObjectCustomExt](./sforce-api-objects-bindingobjectcustomext.md)**

Represents the external or custom target object that’s bound to the entitlements granted with the sellable product. This object is available in API version 64.0 and later.

- 

**[BindingObjectRateAdjustment](./sforce-api-objects-bindingobjectrateadjustment.md)**

Represents the rate adjustments of the usage resource associated with the binding object that’s used to charge over consumption. This object is available in API version 64.0 and later.

- 

**[BindingObjectRateCardEntry](./sforce-api-objects-bindingobjectratecardentry.md)**

Represents the rate card entry details of the usage resource associated with the binding object that’s used to charge over consumption. This object is available in API version 64.0 and later.

- 

**[PriceBookRateCard](./sforce-api-objects-pricebookratecard.md)**

Represents a junction between price book and rate card objects. This object is available in API version 62.0 and later.

- 

**[RateAdjustmentByAttribute](./sforce-api-objects-rateadjustmentbyattribute.md)**

Represents the adjustments that determine the rate of a resource based on its rate-impacting attributes. These attributes are linked to the usage product record. Rates are then influenced by conditions specified in the Attribute Based Adjustment Condition object. Finally, the charge rate is determined by using the Attribute Based Adjustment Rule object. This object is available in API version 62.0 and later.

- 

**[RateAdjustmentByTier](./sforce-api-objects-rateadjustmentbytier.md)**

Represents the adjustments for the rate of a resource that’s determined based on the specified tiers. This object stores information about the type of adjustment used, the value of the adjustment type, and any applicable boundaries. This object is available in API version 62.0 and later.

- 

**[RateCard](./sforce-api-objects-ratecard.md)**

Represents the rules used to rate the consumption of a group of resources within a product. Usage of a resource is billed at a specified rate if the user consumes more than their allowance for a time period. This object is available in API version 62.0 and later.

- 

**[RateCardEntry](./sforce-api-objects-ratecardentry.md)**

Represents a rule that determines the charge rate for using a product’s resource. Each entry is linked to one rate card exclusively, and its activation or deactivation can be controlled by assigning effective dates. This object is available in API version 62.0 and later.

- 

**[RatingFrequencyPolicy](./sforce-api-objects-ratingfrequencypolicy.md)**

Represents the policy that defines the frequency at which rating is triggered for the ratable summary records. This object is available in API version 62.0 and later.

- 

**[RatingRequest](./sforce-api-objects-ratingrequest.md)**

Represents the common run-time parameters, such as context definition and rating procedure for a set of records in the rateable summary table. This object is available in API version 62.0 and later.

- 

**[RatingRequestBatchJob](./sforce-api-objects-ratingrequestbatchjob.md)**

Represents a junction between the rating request and batch job objects. This object is available in API version 62.0 and later.

**See Also**

- [*Object Reference for the platform*: Overview of Salesforce Objects and Fields](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_concepts.htm)

- [*SOAP API Developer Guide*: Introduction to SOAP API](https://developer.salesforce.com/docs/atlas.en-us.api.meta/api/sforce_api_quickstart_intro.htm)

---

> **Source attribution and limited-use note.** This file is a captured copy of publicly readable Salesforce developer documentation ([source](https://developer.salesforce.com/docs/revenue/revenue-management/guide/rate-management-std-objects-parent.html)), © Salesforce, Inc., kept in this repository as grounding material for people and AI agents. It is not an official or authoritative copy: the source URL is the system of record, and if this text differs from the live page, the live page wins. Do not republish it elsewhere without confirming Salesforce's terms.
