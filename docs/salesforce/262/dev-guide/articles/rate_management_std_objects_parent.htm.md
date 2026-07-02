---
page_id: rate_management_std_objects_parent.htm
title: Rate Management Standard Objects
source_url: https://developer.salesforce.com/docs/atlas.en-us.revenue_lifecycle_management_dev_guide.meta/revenue_lifecycle_management_dev_guide/rate_management_std_objects_parent.htm
release: 262
release_name: Summer '26
deliverable: revenue_lifecycle_management_dev_guide
section: Rate Management
parent_page: rate_management_overview.htm
fetched_at: 2026-06-09
---

# Rate Management Standard Objects

The Rate Management data model provides objects and fields to manage rates and discounts
for a product's resource consumption.

- **[BindingObjectCustomExt](./sforce_api_objects_bindingobjectcustomext.htm.md)**  
  Represents the external or custom target object that's bound to the entitlements granted with the sellable product. This object is available in API version 64.0 and later.
- **[BindingObjectRateAdjustment](./sforce_api_objects_bindingobjectrateadjustment.htm.md)**  
  Represents the rate adjustments of the usage resource associated with the binding object that's used to charge over consumption. This object is available in API version 64.0 and later.
- **[BindingObjectRateCardEntry](./sforce_api_objects_bindingobjectratecardentry.htm.md)**  
  Represents the rate card entry details of the usage resource associated with the binding object that's used to charge over consumption. This object is available in API version 64.0 and later.
- **[PriceBookRateCard](./sforce_api_objects_pricebookratecard.htm.md)**  
  Represents a junction between price book and rate card objects. This object is available in API version 62.0 and later.
- **[RateAdjustmentByAttribute](./sforce_api_objects_rateadjustmentbyattribute.htm.md)**  
  Represents the adjustments that determine the rate of a resource based on its rate-impacting attributes. These attributes are linked to the usage product record. Rates are then influenced by conditions specified in the Attribute Based Adjustment Condition object. Finally, the charge rate is determined by using the Attribute Based Adjustment Rule object. This object is available in API version 62.0 and later.
- **[RateAdjustmentByTier](./sforce_api_objects_rateadjustmentbytier.htm.md)**  
  Represents the adjustments for the rate of a resource that’s determined based on the specified tiers. This object stores information about the type of adjustment used, the value of the adjustment type, and any applicable boundaries. This object is available in API version 62.0 and later.
- **[RateCard](./sforce_api_objects_ratecard.htm.md)**  
  Represents the rules used to rate the consumption of a group of resources within a product. Usage of a resource is billed at a specified rate if the user consumes more than their allowance for a time period. This object is available in API version 62.0 and later.
- **[RateCardEntry](./sforce_api_objects_ratecardentry.htm.md)**  
  Represents a rule that determines the charge rate for using a product's resource. Each entry is linked to one rate card exclusively, and its activation or deactivation can be controlled by assigning effective dates. This object is available in API version 62.0 and later.
- **[RatingFrequencyPolicy](./sforce_api_objects_ratingfrequencypolicy.htm.md)**  
  Represents the policy that defines the frequency at which rating is triggered for the ratable summary records. This object is available in API version 62.0 and later.
- **[RatingRequest](./sforce_api_objects_ratingrequest.htm.md)**  
  Represents the common run-time parameters, such as context definition and rating procedure for a set of records in the rateable summary table. This object is available in API version 62.0 and later.
- **[RatingRequestBatchJob](./sforce_api_objects_ratingrequestbatchjob.htm.md)**  
  Represents a junction between the rating request and batch job objects. This object is available in API version 62.0 and later.

#### See Also

- [*Object Reference for the Salesforce Platform*: Overview of Salesforce Objects
  and Fields](https://developer.salesforce.com/docs/atlas.en-us.262.0.object_reference.meta/object_reference/sforce_api_objects_concepts.htm "Object Reference for the Salesforce Platform: Overview of Salesforce Objects
         and Fields  - HTML (New Window)")
- [*SOAP API Developer Guide*: Introduction to SOAP API](https://developer.salesforce.com/docs/atlas.en-us.262.0.api.meta/api/sforce_api_quickstart_intro.htm "SOAP API Developer Guide: Introduction to SOAP API - HTML (New Window)")
